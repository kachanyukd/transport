"""
FuelingService — central business logic for fueling registration.

All computation is performed atomically within a single transaction.
Computed fields (actual_consumption, deviation_pct, is_anomalous) are stored
in the database to avoid expensive LAG() window queries on report reads.
"""

import logging
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.fueling.models import FuelingRecord
from apps.vehicles.models import Vehicle
from fleet.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)

# Deviation threshold above which a fueling is flagged as anomalous
ANOMALY_THRESHOLD_PCT = Decimal("10.0")


class FuelingService:
    @staticmethod
    @transaction.atomic
    def register_fueling(
        *,
        vehicle_id: int,
        driver_id: int,
        fueled_at,
        fuel_liters: Decimal,
        price_per_liter: Decimal,
        station_name: str,
        odometer_at_fueling: Decimal,
    ) -> FuelingRecord:
        """
        Register a fueling event and atomically:
        1. Find the previous fueling record to get base odometer.
        2. Calculate actual_consumption (L/100km) and deviation_pct from norm.
        3. Flag as anomalous if deviation exceeds ANOMALY_THRESHOLD_PCT.
        4. Update the vehicle's current odometer.

        Uses select_for_update() on the vehicle row to prevent concurrent
        odometer updates from producing incorrect calculations.
        """
        # Lock vehicle row for the duration of this transaction
        try:
            vehicle = Vehicle.objects.select_for_update().get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise BusinessLogicError(f"Vehicle {vehicle_id} not found.", code="vehicle_not_found")

        if vehicle.status == "decommissioned":
            raise BusinessLogicError(
                "Cannot record fueling for a decommissioned vehicle.",
                code="vehicle_decommissioned",
            )

        if odometer_at_fueling < vehicle.odometer:
            raise BusinessLogicError(
                f"Odometer reading {odometer_at_fueling} is less than vehicle's current "
                f"odometer {vehicle.odometer}. Odometer cannot decrease.",
                code="odometer_regression",
            )

        # Step 1: find the previous fueling record for this vehicle
        previous = (
            FuelingRecord.objects.filter(vehicle_id=vehicle_id)
            .order_by("-fueled_at", "-id")
            .first()
        )

        # Step 2: calculate consumption metrics
        actual_consumption: Optional[Decimal] = None
        deviation_pct: Optional[Decimal] = None
        is_anomalous: Optional[bool] = None

        if previous is not None:
            distance = odometer_at_fueling - previous.odometer_at_fueling
            if distance > 0:
                actual_consumption = (fuel_liters / distance) * Decimal("100")

                # Determine norm based on current month (winter = Nov–Mar)
                month = (fueled_at.month if hasattr(fueled_at, "month") else timezone.now().month)
                is_winter = month in (11, 12, 1, 2, 3)
                norm = (
                    vehicle.norm_consumption_winter
                    if is_winter
                    else vehicle.norm_consumption_summer
                )

                if norm and norm > 0:
                    deviation_pct = ((actual_consumption - norm) / norm) * Decimal("100")
                    is_anomalous = abs(deviation_pct) > ANOMALY_THRESHOLD_PCT

        # Step 3: create the record
        record = FuelingRecord(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            fueled_at=fueled_at,
            fuel_liters=fuel_liters,
            price_per_liter=price_per_liter,
            station_name=station_name,
            odometer_at_fueling=odometer_at_fueling,
            actual_consumption=actual_consumption,
            deviation_pct=deviation_pct,
            is_anomalous=is_anomalous,
        )
        record.save()

        # Step 4: update vehicle odometer using .update() — only touches odometer column
        Vehicle.objects.filter(pk=vehicle_id).update(odometer=odometer_at_fueling)

        logger.info(
            "Fueling registered: vehicle=%s driver=%s liters=%s odometer=%s anomalous=%s",
            vehicle_id,
            driver_id,
            fuel_liters,
            odometer_at_fueling,
            is_anomalous,
        )
        return record
