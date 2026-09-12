"""
MaintenanceService — business logic for maintenance request lifecycle.

close_maintenance() atomically:
  1. Closes the MaintenanceRecord (sets closed_at)
  2. Changes Vehicle.status back to 'active'
  3. Updates Vehicle.odometer if odometer_at_closing is provided
"""

import logging
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.maintenance.models import MaintenanceRecord
from apps.vehicles.models import Vehicle, VehicleStatus
from fleet.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)


class MaintenanceService:
    @staticmethod
    @transaction.atomic
    def open_request(
        *,
        vehicle_id: int,
        record_type: str,
        opened_at=None,
        fault_description: str,
        contractor_name: str = "",
        parts_cost: Decimal = Decimal("0"),
        labor_cost: Decimal = Decimal("0"),
    ) -> MaintenanceRecord:
        """
        Open a new maintenance request and set vehicle status to 'maintenance'.
        Uses select_for_update() to prevent concurrent status changes.
        """
        try:
            vehicle = Vehicle.objects.select_for_update().get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise BusinessLogicError(
                f"Vehicle {vehicle_id} not found.", code="vehicle_not_found"
            )

        if vehicle.status == VehicleStatus.DECOMMISSIONED:
            raise BusinessLogicError(
                "Cannot open maintenance for a decommissioned vehicle.",
                code="vehicle_decommissioned",
            )

        if opened_at is None:
            opened_at = timezone.now()

        record = MaintenanceRecord.objects.create(
            vehicle_id=vehicle_id,
            record_type=record_type,
            opened_at=opened_at,
            fault_description=fault_description,
            contractor_name=contractor_name,
            parts_cost=parts_cost,
            labor_cost=labor_cost,
        )

        # Set vehicle status to maintenance
        Vehicle.objects.filter(pk=vehicle_id).update(status=VehicleStatus.MAINTENANCE)

        logger.info(
            "Maintenance opened: record=%s vehicle=%s type=%s",
            record.pk,
            vehicle_id,
            record_type,
        )
        return record

    @staticmethod
    @transaction.atomic
    def close_request(
        *,
        record_id: int,
        work_performed: str,
        parts_cost: Optional[Decimal] = None,
        labor_cost: Optional[Decimal] = None,
        odometer_at_closing: Optional[Decimal] = None,
        closed_at=None,
    ) -> MaintenanceRecord:
        """
        Close a maintenance request atomically:
        1. Validate record is not already closed (pre-validated in serializer).
        2. Set closed_at, work_performed, and optional cost/odometer fields.
        3. Change Vehicle.status back to 'active'.
        4. Update Vehicle.odometer if odometer_at_closing is provided and higher.

        Note: The "is already closed" check is intentionally done in the
        serializer's validate() method, not here, per the architectural decision
        in the thesis. The service receives pre-validated data.
        """
        try:
            record = MaintenanceRecord.objects.select_for_update().select_related(
                "vehicle"
            ).get(pk=record_id)
        except MaintenanceRecord.DoesNotExist:
            raise BusinessLogicError(
                f"Maintenance record {record_id} not found.", code="record_not_found"
            )

        if record.closed_at is not None:
            raise BusinessLogicError(
                "Maintenance record is already closed.", code="already_closed"
            )

        if closed_at is None:
            closed_at = timezone.now()

        # Update record fields
        update_fields = {
            "closed_at": closed_at,
            "work_performed": work_performed,
        }
        if parts_cost is not None:
            update_fields["parts_cost"] = parts_cost
        if labor_cost is not None:
            update_fields["labor_cost"] = labor_cost
        if odometer_at_closing is not None:
            update_fields["odometer_at_closing"] = odometer_at_closing

        MaintenanceRecord.objects.filter(pk=record_id).update(**update_fields)

        # Atomically change vehicle status back to active
        vehicle_update = {"status": VehicleStatus.ACTIVE}
        if odometer_at_closing is not None and odometer_at_closing > record.vehicle.odometer:
            vehicle_update["odometer"] = odometer_at_closing

        Vehicle.objects.filter(pk=record.vehicle_id).update(**vehicle_update)

        # Refresh and return updated record
        record.refresh_from_db()

        logger.info(
            "Maintenance closed: record=%s vehicle=%s",
            record_id,
            record.vehicle_id,
        )
        return record
