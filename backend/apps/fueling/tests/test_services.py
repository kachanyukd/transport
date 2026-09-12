"""
Unit tests for FuelingService.
Uses real PostgreSQL (not mocked ORM) to validate transactions and constraints.

Three critical scenarios per thesis section 3.5:
1. First fueling record — computed fields remain null (no previous odometer)
2. Normal fueling — actual_consumption, deviation_pct calculated correctly
3. Anomalous fueling — deviation exceeds threshold → is_anomalous = True
"""

import pytest
from decimal import Decimal
from django.utils import timezone

from apps.fueling.services import FuelingService, ANOMALY_THRESHOLD_PCT
from apps.fueling.models import FuelingRecord
from apps.vehicles.models import Vehicle
from apps.vehicles.tests.factories import VehicleFactory
from apps.drivers.tests.factories import DriverFactory
from fleet.exceptions import BusinessLogicError


@pytest.mark.django_db(transaction=True)
class TestFuelingServiceFirstRecord:
    """Scenario 1: First fueling record for a vehicle."""

    def test_first_record_computed_fields_are_null(self):
        vehicle = VehicleFactory(odometer=Decimal("0"))
        driver = DriverFactory()

        record = FuelingService.register_fueling(
            vehicle_id=vehicle.pk,
            driver_id=driver.pk,
            fueled_at=timezone.now(),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Test Station",
            odometer_at_fueling=Decimal("100.00"),
        )

        assert record.actual_consumption is None
        assert record.deviation_pct is None
        assert record.is_anomalous is None

    def test_first_record_updates_vehicle_odometer(self):
        vehicle = VehicleFactory(odometer=Decimal("0"))
        driver = DriverFactory()

        FuelingService.register_fueling(
            vehicle_id=vehicle.pk,
            driver_id=driver.pk,
            fueled_at=timezone.now(),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Test Station",
            odometer_at_fueling=Decimal("500.00"),
        )

        vehicle.refresh_from_db()
        assert vehicle.odometer == Decimal("500.00")

    def test_first_record_is_saved_to_db(self):
        vehicle = VehicleFactory(odometer=Decimal("0"))
        driver = DriverFactory()

        record = FuelingService.register_fueling(
            vehicle_id=vehicle.pk,
            driver_id=driver.pk,
            fueled_at=timezone.now(),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Test Station",
            odometer_at_fueling=Decimal("100.00"),
        )

        assert FuelingRecord.objects.filter(pk=record.pk).exists()


@pytest.mark.django_db(transaction=True)
class TestFuelingServiceNormalRecord:
    """Scenario 2: Normal fueling — consumption within norm."""

    def setup_method(self):
        # Vehicle with summer norm of 10 L/100km
        self.vehicle = VehicleFactory(
            norm_consumption_summer=Decimal("10.00"),
            norm_consumption_winter=Decimal("12.00"),
            odometer=Decimal("0"),
        )
        self.driver = DriverFactory()

    def _make_fueling(self, odometer, fuel_liters=None, month=6):
        """Helper: create a fueling at a specific odometer."""
        import datetime
        fueled_at = timezone.now().replace(month=month, day=15)
        return FuelingService.register_fueling(
            vehicle_id=self.vehicle.pk,
            driver_id=self.driver.pk,
            fueled_at=fueled_at,
            fuel_liters=fuel_liters or Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Station",
            odometer_at_fueling=odometer,
        )

    def test_normal_consumption_calculates_correctly(self):
        # First record at odometer 0
        self._make_fueling(Decimal("0"))
        # Vehicle has odometer=0 after first record
        self.vehicle.refresh_from_db()

        # Second record: drove 400km, used 40L → 10 L/100km (exactly on norm)
        record = self._make_fueling(Decimal("400.00"), fuel_liters=Decimal("40.00"), month=6)

        assert record.actual_consumption is not None
        # 40L / 400km * 100 = 10 L/100km
        expected = Decimal("40.00") / Decimal("400.00") * Decimal("100")
        assert abs(record.actual_consumption - expected) < Decimal("0.01")

    def test_deviation_pct_within_threshold_not_anomalous(self):
        """5% deviation → not anomalous (threshold is 10%)."""
        self._make_fueling(Decimal("0"))

        # 400km, used 42L → 10.5 L/100km, deviation = 5%
        record = self._make_fueling(Decimal("400.00"), fuel_liters=Decimal("42.00"), month=6)

        assert record.deviation_pct is not None
        assert abs(record.deviation_pct) < ANOMALY_THRESHOLD_PCT
        assert record.is_anomalous is False

    def test_odometer_updated_after_second_fueling(self):
        self._make_fueling(Decimal("0"))
        self._make_fueling(Decimal("400.00"), month=6)

        self.vehicle.refresh_from_db()
        assert self.vehicle.odometer == Decimal("400.00")


@pytest.mark.django_db(transaction=True)
class TestFuelingServiceAnomalousRecord:
    """Scenario 3: Anomalous fueling — deviation exceeds 10% threshold."""

    def setup_method(self):
        self.vehicle = VehicleFactory(
            norm_consumption_summer=Decimal("10.00"),
            norm_consumption_winter=Decimal("12.00"),
            odometer=Decimal("0"),
        )
        self.driver = DriverFactory()

    def test_high_consumption_flagged_as_anomalous(self):
        # First record
        FuelingService.register_fueling(
            vehicle_id=self.vehicle.pk,
            driver_id=self.driver.pk,
            fueled_at=timezone.now().replace(month=6, day=15),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Station",
            odometer_at_fueling=Decimal("0"),
        )

        # Second record: drove 200km, used 40L → 20 L/100km, deviation = 100%
        record = FuelingService.register_fueling(
            vehicle_id=self.vehicle.pk,
            driver_id=self.driver.pk,
            fueled_at=timezone.now().replace(month=6, day=20),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Station",
            odometer_at_fueling=Decimal("200.00"),
        )

        assert record.is_anomalous is True
        assert abs(record.deviation_pct) > ANOMALY_THRESHOLD_PCT

    def test_low_consumption_also_flagged_as_anomalous(self):
        """Significant under-consumption (possible odometer fraud) is also anomalous."""
        FuelingService.register_fueling(
            vehicle_id=self.vehicle.pk,
            driver_id=self.driver.pk,
            fueled_at=timezone.now().replace(month=6, day=15),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Station",
            odometer_at_fueling=Decimal("0"),
        )

        # Drove 2000km, used only 40L → 2 L/100km, deviation = -80%
        record = FuelingService.register_fueling(
            vehicle_id=self.vehicle.pk,
            driver_id=self.driver.pk,
            fueled_at=timezone.now().replace(month=6, day=25),
            fuel_liters=Decimal("40.00"),
            price_per_liter=Decimal("42.50"),
            station_name="Station",
            odometer_at_fueling=Decimal("2000.00"),
        )

        assert record.is_anomalous is True


@pytest.mark.django_db(transaction=True)
class TestFuelingServiceValidation:
    """Business rule validation in FuelingService."""

    def test_odometer_regression_raises_error(self):
        vehicle = VehicleFactory(odometer=Decimal("1000.00"))
        driver = DriverFactory()

        with pytest.raises(BusinessLogicError) as exc_info:
            FuelingService.register_fueling(
                vehicle_id=vehicle.pk,
                driver_id=driver.pk,
                fueled_at=timezone.now(),
                fuel_liters=Decimal("40.00"),
                price_per_liter=Decimal("42.50"),
                station_name="Station",
                odometer_at_fueling=Decimal("500.00"),  # Less than current
            )
        assert exc_info.value.code == "odometer_regression"

    def test_decommissioned_vehicle_raises_error(self):
        from apps.vehicles.models import VehicleStatus
        vehicle = VehicleFactory(status=VehicleStatus.DECOMMISSIONED, odometer=Decimal("0"))
        driver = DriverFactory()

        with pytest.raises(BusinessLogicError) as exc_info:
            FuelingService.register_fueling(
                vehicle_id=vehicle.pk,
                driver_id=driver.pk,
                fueled_at=timezone.now(),
                fuel_liters=Decimal("40.00"),
                price_per_liter=Decimal("42.50"),
                station_name="Station",
                odometer_at_fueling=Decimal("100.00"),
            )
        assert exc_info.value.code == "vehicle_decommissioned"

    def test_nonexistent_vehicle_raises_error(self):
        driver = DriverFactory()

        with pytest.raises(BusinessLogicError) as exc_info:
            FuelingService.register_fueling(
                vehicle_id=99999,
                driver_id=driver.pk,
                fueled_at=timezone.now(),
                fuel_liters=Decimal("40.00"),
                price_per_liter=Decimal("42.50"),
                station_name="Station",
                odometer_at_fueling=Decimal("100.00"),
            )
        assert exc_info.value.code == "vehicle_not_found"
