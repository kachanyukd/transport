"""
VehicleService — business logic for vehicle lifecycle management.
"""

import logging
from django.db import transaction
from apps.vehicles.models import Vehicle, VehicleStatus
from fleet.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)


class VehicleService:
    @staticmethod
    @transaction.atomic
    def decommission(*, vehicle_id: int) -> Vehicle:
        """
        Decommission a vehicle. Cannot decommission if an open maintenance record exists.
        """
        try:
            vehicle = Vehicle.objects.select_for_update().get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise BusinessLogicError(
                f"Vehicle {vehicle_id} not found.", code="vehicle_not_found"
            )

        if vehicle.status == VehicleStatus.DECOMMISSIONED:
            raise BusinessLogicError(
                "Vehicle is already decommissioned.", code="already_decommissioned"
            )

        # Check for open maintenance records
        has_open_maintenance = vehicle.maintenance_records.filter(closed_at__isnull=True).exists()
        if has_open_maintenance:
            raise BusinessLogicError(
                "Cannot decommission vehicle with open maintenance records. "
                "Close all maintenance records first.",
                code="open_maintenance_exists",
            )

        Vehicle.objects.filter(pk=vehicle_id).update(status=VehicleStatus.DECOMMISSIONED)
        vehicle.refresh_from_db()

        logger.info("Vehicle decommissioned: vehicle=%s", vehicle_id)
        return vehicle
