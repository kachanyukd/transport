"""
Integration tests for /api/v1/fuel-records/ endpoints.
Each endpoint tested with at least 3 scenarios:
1. No auth → 401
2. Insufficient permission → 403
3. Legitimate request → 200/201
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone

from apps.users.tests.factories import (
    AdminUserFactory,
    ManagerUserFactory,
    DispatcherUserFactory,
    DriverUserFactory,
)
from apps.vehicles.tests.factories import VehicleFactory
from apps.drivers.tests.factories import DriverFactory
from apps.fueling.tests.factories import FuelingRecordFactory
from apps.drivers.models import VehicleAssignment


@pytest.fixture
def api_client():
    return APIClient()


def auth_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestFuelRecordList:
    url = "/api/v1/fuel-records/"

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_admin_sees_all_records(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        FuelingRecordFactory.create_batch(3, vehicle=vehicle, driver=driver)
        user = AdminUserFactory()
        auth_client(user, api_client)

        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data["count"] == 3 or len(response.data.get("results", [])) == 3

    def test_driver_sees_only_own_records(self, api_client):
        driver_profile = DriverFactory()
        other_driver = DriverFactory()

        user = DriverUserFactory(driver=driver_profile)
        auth_client(user, api_client)

        vehicle = VehicleFactory()
        FuelingRecordFactory.create_batch(2, vehicle=vehicle, driver=driver_profile)
        FuelingRecordFactory.create_batch(3, vehicle=vehicle, driver=other_driver)

        response = api_client.get(self.url)
        assert response.status_code == 200
        results = response.data.get("results", [])
        assert len(results) == 2

    def test_filter_by_is_anomalous(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        FuelingRecordFactory(vehicle=vehicle, driver=driver, is_anomalous=True)
        FuelingRecordFactory(vehicle=vehicle, driver=driver, is_anomalous=False)
        FuelingRecordFactory(vehicle=vehicle, driver=driver, is_anomalous=None)

        user = AdminUserFactory()
        auth_client(user, api_client)

        response = api_client.get(self.url, {"is_anomalous": "true"})
        assert response.status_code == 200
        results = response.data.get("results", [])
        assert all(r["is_anomalous"] is True for r in results)


@pytest.mark.django_db
class TestFuelRecordCreate:
    url = "/api/v1/fuel-records/"

    def _payload(self, vehicle, driver):
        return {
            "vehicle": vehicle.pk,
            "driver": driver.pk,
            "fueled_at": timezone.now().isoformat(),
            "fuel_liters": "40.00",
            "price_per_liter": "42.50",
            "station_name": "WOG",
            "odometer_at_fueling": "500.00",
        }

    def test_unauthenticated_returns_401(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        response = api_client.post(self.url, self._payload(vehicle, driver), format="json")
        assert response.status_code == 401

    def test_driver_cannot_create_fueling(self, api_client):
        vehicle = VehicleFactory()
        driver_profile = DriverFactory()
        user = DriverUserFactory(driver=driver_profile)
        auth_client(user, api_client)

        response = api_client.post(self.url, self._payload(vehicle, driver_profile), format="json")
        assert response.status_code == 403

    def test_dispatcher_can_create_fueling(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        user = DispatcherUserFactory()
        auth_client(user, api_client)

        response = api_client.post(self.url, self._payload(vehicle, driver), format="json")
        assert response.status_code == 201
        assert "id" in response.data

    def test_create_first_record_has_null_computed_fields(self, api_client):
        vehicle = VehicleFactory(odometer=Decimal("0"))
        driver = DriverFactory()
        user = ManagerUserFactory()
        auth_client(user, api_client)

        response = api_client.post(self.url, self._payload(vehicle, driver), format="json")
        assert response.status_code == 201
        assert response.data["actual_consumption"] is None
        assert response.data["is_anomalous"] is None

    def test_create_second_record_has_computed_fields(self, api_client):
        vehicle = VehicleFactory(
            odometer=Decimal("0"),
            norm_consumption_summer=Decimal("10.00"),
            norm_consumption_winter=Decimal("12.00"),
        )
        driver = DriverFactory()
        user = ManagerUserFactory()
        auth_client(user, api_client)

        # First fueling at odometer 0
        api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "driver": driver.pk,
            "fueled_at": "2025-06-01T10:00:00Z",
            "fuel_liters": "40.00",
            "price_per_liter": "42.50",
            "station_name": "WOG",
            "odometer_at_fueling": "0.00",
        }, format="json")

        # Second fueling at odometer 400 (drove 400km, used 40L → 10 L/100km)
        response = api_client.post(self.url, {
            "vehicle": vehicle.pk,
            "driver": driver.pk,
            "fueled_at": "2025-06-15T10:00:00Z",
            "fuel_liters": "40.00",
            "price_per_liter": "42.50",
            "station_name": "WOG",
            "odometer_at_fueling": "400.00",
        }, format="json")

        assert response.status_code == 201
        assert response.data["actual_consumption"] is not None


@pytest.mark.django_db
class TestFuelRecordDetail:
    def test_unauthenticated_returns_401(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        record = FuelingRecordFactory(vehicle=vehicle, driver=driver)
        response = api_client.get(f"/api/v1/fuel-records/{record.pk}/")
        assert response.status_code == 401

    def test_driver_gets_404_for_other_drivers_record(self, api_client):
        """Key test: Driver gets 404 not 403 for records not belonging to them."""
        other_driver = DriverFactory()
        my_driver = DriverFactory()
        vehicle = VehicleFactory()
        record = FuelingRecordFactory(vehicle=vehicle, driver=other_driver)

        user = DriverUserFactory(driver=my_driver)
        auth_client(user, api_client)

        response = api_client.get(f"/api/v1/fuel-records/{record.pk}/")
        # Must be 404, not 403 — does not reveal existence of resource
        assert response.status_code == 404

    def test_admin_can_see_any_record(self, api_client):
        vehicle = VehicleFactory()
        driver = DriverFactory()
        record = FuelingRecordFactory(vehicle=vehicle, driver=driver)

        user = AdminUserFactory()
        auth_client(user, api_client)

        response = api_client.get(f"/api/v1/fuel-records/{record.pk}/")
        assert response.status_code == 200
        assert response.data["id"] == record.pk
