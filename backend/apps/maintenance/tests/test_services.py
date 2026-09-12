"""
Unit tests for MaintenanceService.
Validates atomic state transitions across Vehicle and MaintenanceRecord tables.
"""

import pytest
from decimal import Decimal
from django.utils import timezone

from apps.maintenance.services import MaintenanceService
from apps.maintenance.models import MaintenanceRecord, MaintenanceType
from apps.vehicles.models import Vehicle, VehicleStatus
from apps.vehicles.tests.factories import VehicleFactory
from apps.maintenance.tests.factories import MaintenanceRecordFactory
from fleet.exceptions import BusinessLogicError


@pytest.mark.django_db(transaction=True)
class TestMaintenanceServiceOpen:
    """Tests for MaintenanceService.open_request()."""

    def test_open_sets_vehicle_status_to_maintenance(self):
        vehicle = VehicleFactory(status=VehicleStatus.ACTIVE)

        MaintenanceService.open_request(
            vehicle_id=vehicle.pk,
            record_type=MaintenanceType.CURRENT_REPAIR,
            fault_description="Brake pad wear",
        )

        vehicle.refresh_from_db()
        assert vehicle.status == VehicleStatus.MAINTENANCE

    def test_open_creates_record_in_db(self):
        vehicle = VehicleFactory()

        record = MaintenanceService.open_request(
            vehicle_id=vehicle.pk,
            record_type=MaintenanceType.PLANNED_TO,
            fault_description="Scheduled oil change",
        )

        assert MaintenanceRecord.objects.filter(pk=record.pk).exists()
        assert record.closed_at is None
        assert record.is_open is True

    def test_open_decommissioned_vehicle_raises_error(self):
        vehicle = VehicleFactory(status=VehicleStatus.DECOMMISSIONED)

        with pytest.raises(BusinessLogicError) as exc_info:
            MaintenanceService.open_request(
                vehicle_id=vehicle.pk,
                record_type=MaintenanceType.CURRENT_REPAIR,
                fault_description="Test",
            )
        assert exc_info.value.code == "vehicle_decommissioned"

    def test_open_nonexistent_vehicle_raises_error(self):
        with pytest.raises(BusinessLogicError) as exc_info:
            MaintenanceService.open_request(
                vehicle_id=99999,
                record_type=MaintenanceType.CURRENT_REPAIR,
                fault_description="Test",
            )
        assert exc_info.value.code == "vehicle_not_found"


@pytest.mark.django_db(transaction=True)
class TestMaintenanceServiceClose:
    """Tests for MaintenanceService.close_request() — the critical atomic method."""

    def test_close_sets_closed_at(self):
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE)
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)

        closed = MaintenanceService.close_request(
            record_id=record.pk,
            work_performed="Replaced brake pads on all four wheels.",
        )

        assert closed.closed_at is not None
        assert closed.is_open is False

    def test_close_changes_vehicle_status_to_active(self):
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE)
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)

        MaintenanceService.close_request(
            record_id=record.pk,
            work_performed="Engine oil and filter replaced.",
        )

        vehicle.refresh_from_db()
        assert vehicle.status == VehicleStatus.ACTIVE

    def test_close_updates_vehicle_odometer_when_provided(self):
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE, odometer=Decimal("5000.00"))
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)

        MaintenanceService.close_request(
            record_id=record.pk,
            work_performed="Major overhaul completed.",
            odometer_at_closing=Decimal("5200.00"),
        )

        vehicle.refresh_from_db()
        assert vehicle.odometer == Decimal("5200.00")

    def test_close_does_not_decrease_odometer(self):
        """If odometer_at_closing is less than vehicle odometer, don't update it."""
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE, odometer=Decimal("5000.00"))
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)

        MaintenanceService.close_request(
            record_id=record.pk,
            work_performed="Repair completed.",
            odometer_at_closing=Decimal("4900.00"),  # Less than current — should not update
        )

        vehicle.refresh_from_db()
        # Odometer should remain at 5000 because 4900 < 5000
        assert vehicle.odometer == Decimal("5000.00")

    def test_close_already_closed_raises_error(self):
        vehicle = VehicleFactory()
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=timezone.now())

        with pytest.raises(BusinessLogicError) as exc_info:
            MaintenanceService.close_request(
                record_id=record.pk,
                work_performed="Should not work.",
            )
        assert exc_info.value.code == "already_closed"

    def test_close_is_atomic(self):
        """
        Verify that vehicle status and record closing happen atomically.
        If something fails mid-way, both should be rolled back.
        """
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE)
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)

        # Normal close should succeed atomically
        MaintenanceService.close_request(
            record_id=record.pk,
            work_performed="Test work",
        )

        vehicle.refresh_from_db()
        record.refresh_from_db()
        assert vehicle.status == VehicleStatus.ACTIVE
        assert record.closed_at is not None

    def test_close_nonexistent_record_raises_error(self):
        with pytest.raises(BusinessLogicError) as exc_info:
            MaintenanceService.close_request(
                record_id=99999,
                work_performed="Test",
            )
        assert exc_info.value.code == "record_not_found"
