"""
DriverService — business logic for driver-vehicle assignment management.
"""

import logging
from django.db import transaction
from django.utils import timezone

from apps.drivers.models import Driver, VehicleAssignment
from apps.vehicles.models import Vehicle
from fleet.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)


class DriverService:
    @staticmethod
    @transaction.atomic
    def assign_vehicle(
        *,
        driver_id: int,
        vehicle_id: int,
        assigned_at=None,
    ) -> VehicleAssignment:
        """
        Assign a vehicle to a driver.
        - Closes any previous active assignment for the vehicle.
        - Creates a new VehicleAssignment record.
        """
        if assigned_at is None:
            assigned_at = timezone.now()

        try:
            driver = Driver.objects.get(pk=driver_id)
        except Driver.DoesNotExist:
            raise BusinessLogicError(f"Driver {driver_id} not found.", code="driver_not_found")

        if driver.status == "dismissed":
            raise BusinessLogicError(
                "Cannot assign vehicle to a dismissed driver.", code="driver_dismissed"
            )

        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise BusinessLogicError(f"Vehicle {vehicle_id} not found.", code="vehicle_not_found")

        if vehicle.status == "decommissioned":
            raise BusinessLogicError(
                "Cannot assign a decommissioned vehicle.", code="vehicle_decommissioned"
            )

        # Close any existing active assignment for this vehicle
        VehicleAssignment.objects.filter(
            vehicle_id=vehicle_id, released_at__isnull=True
        ).update(released_at=assigned_at)

        assignment = VehicleAssignment.objects.create(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            assigned_at=assigned_at,
        )

        logger.info(
            "Vehicle assigned: driver=%s vehicle=%s assignment=%s",
            driver_id,
            vehicle_id,
            assignment.pk,
        )
        return assignment
