"""
Integration tests for /api/v1/maintenance/ endpoints.
"""

import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from apps.users.tests.factories import AdminUserFactory, ManagerUserFactory, DispatcherUserFactory, DriverUserFactory
from apps.vehicles.tests.factories import VehicleFactory
from apps.maintenance.tests.factories import MaintenanceRecordFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestMaintenanceList:
    url = "/api/v1/maintenance/"

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_driver_cannot_access_maintenance(self, api_client):
        user = DriverUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_dispatcher_can_read_maintenance(self, api_client):
        VehicleFactory()
        MaintenanceRecordFactory.create_batch(3)
        user = DispatcherUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.get(self.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestMaintenanceCreate:
    url = "/api/v1/maintenance/"

    def test_unauthenticated_returns_401(self, api_client):
        vehicle = VehicleFactory()
        response = api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "record_type": "current_repair",
            "fault_description": "Test",
        }, format="json")
        assert response.status_code == 401

    def test_dispatcher_cannot_create(self, api_client):
        vehicle = VehicleFactory()
        user = DispatcherUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "record_type": "current_repair",
            "fault_description": "Test",
        }, format="json")
        assert response.status_code == 403

    def test_manager_can_create(self, api_client):
        vehicle = VehicleFactory()
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "record_type": "current_repair",
            "fault_description": "Brake pads worn",
            "parts_cost": "500.00",
            "labor_cost": "200.00",
        }, format="json")
        assert response.status_code == 201
        assert response.data["is_open"] is True

    def test_create_sets_vehicle_status_to_maintenance(self, api_client):
        vehicle = VehicleFactory()
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)
        api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "record_type": "planned_to",
            "fault_description": "Scheduled inspection",
        }, format="json")

        vehicle.refresh_from_db()
        assert vehicle.status == "maintenance"


@pytest.mark.django_db
class TestMaintenanceClose:
    def test_unauthenticated_returns_401(self, api_client):
        vehicle = VehicleFactory()
        record = MaintenanceRecordFactory(vehicle=vehicle)
        response = api_client.post(
            f"/api/v1/maintenance/{record.pk}/close/",
            {"work_performed": "Done"},
            format="json"
        )
        assert response.status_code == 401

    def test_dispatcher_cannot_close(self, api_client):
        vehicle = VehicleFactory()
        record = MaintenanceRecordFactory(vehicle=vehicle)
        user = DispatcherUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/maintenance/{record.pk}/close/",
            {"work_performed": "Done"},
            format="json"
        )
        assert response.status_code == 403

    def test_manager_can_close(self, api_client):
        from apps.vehicles.models import VehicleStatus
        vehicle = VehicleFactory(status=VehicleStatus.MAINTENANCE)
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=None)
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            f"/api/v1/maintenance/{record.pk}/close/",
            {"work_performed": "All repairs completed successfully."},
            format="json"
        )
        assert response.status_code == 200
        assert response.data["is_open"] is False

        vehicle.refresh_from_db()
        assert vehicle.status == VehicleStatus.ACTIVE

    def test_closing_already_closed_returns_error(self, api_client):
        vehicle = VehicleFactory()
        record = MaintenanceRecordFactory(vehicle=vehicle, closed_at=timezone.now())
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.post(
            f"/api/v1/maintenance/{record.pk}/close/",
            {"work_performed": "Should fail"},
            format="json"
        )
        assert response.status_code in (400, 422)
