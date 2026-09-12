"""
Integration tests for /api/v1/vehicles/ endpoints.
"""

import pytest
from apps.users.tests.factories import AdminUserFactory, ManagerUserFactory, DriverUserFactory
from apps.vehicles.tests.factories import VehicleFactory
from apps.drivers.tests.factories import DriverFactory
from apps.drivers.models import VehicleAssignment
from django.utils import timezone
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestVehicleList:
    url = "/api/v1/vehicles/"

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_admin_sees_all_vehicles(self, api_client):
        VehicleFactory.create_batch(5)
        user = AdminUserFactory()
        api_client.force_authenticate(user=user)

        response = api_client.get(self.url)
        assert response.status_code == 200

    def test_driver_sees_only_assigned_vehicle(self, api_client):
        vehicle1 = VehicleFactory()
        vehicle2 = VehicleFactory()
        driver_profile = DriverFactory()

        # Assign vehicle1 to driver
        VehicleAssignment.objects.create(
            vehicle=vehicle1,
            driver=driver_profile,
            assigned_at=timezone.now(),
        )

        user = DriverUserFactory(driver=driver_profile)
        api_client.force_authenticate(user=user)

        response = api_client.get(self.url)
        assert response.status_code == 200
        results = response.data.get("results", [])
        assert len(results) == 1
        assert results[0]["id"] == vehicle1.pk


@pytest.mark.django_db
class TestVehicleCreate:
    url = "/api/v1/vehicles/"

    payload = {
        "license_plate": "AA1234BB",
        "vin": "1HGBH41JXMN109186",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "fuel_type": "petrol",
        "norm_consumption_summer": "8.50",
        "norm_consumption_winter": "10.00",
        "odometer": "0.00",
    }

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.url, self.payload, format="json")
        assert response.status_code == 401

    def test_driver_cannot_create_vehicle(self, api_client):
        driver_profile = DriverFactory()
        user = DriverUserFactory(driver=driver_profile)
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url, self.payload, format="json")
        assert response.status_code == 403

    def test_manager_can_create_vehicle(self, api_client):
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url, self.payload, format="json")
        assert response.status_code == 201
        assert response.data["license_plate"] == "AA1234BB"

    def test_admin_can_create_vehicle(self, api_client):
        user = AdminUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url, self.payload, format="json")
        assert response.status_code == 201


@pytest.mark.django_db
class TestVehicleDecommission:
    def test_unauthenticated_returns_401(self, api_client):
        vehicle = VehicleFactory()
        response = api_client.post(f"/api/v1/vehicles/{vehicle.pk}/decommission/")
        assert response.status_code == 401

    def test_driver_cannot_decommission(self, api_client):
        vehicle = VehicleFactory()
        user = DriverUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(f"/api/v1/vehicles/{vehicle.pk}/decommission/")
        assert response.status_code == 403

    def test_manager_can_decommission_active_vehicle(self, api_client):
        vehicle = VehicleFactory()
        user = ManagerUserFactory()
        api_client.force_authenticate(user=user)
        response = api_client.post(f"/api/v1/vehicles/{vehicle.pk}/decommission/")
        assert response.status_code == 200
        assert response.data["status"] == "decommissioned"
