import factory
from factory.django import DjangoModelFactory
from django.utils import timezone

from apps.fueling.models import FuelingRecord
from apps.vehicles.tests.factories import VehicleFactory
from apps.drivers.tests.factories import DriverFactory


class FuelingRecordFactory(DjangoModelFactory):
    class Meta:
        model = FuelingRecord

    vehicle = factory.SubFactory(VehicleFactory)
    driver = factory.SubFactory(DriverFactory)
    fueled_at = factory.LazyFunction(timezone.now)
    fuel_liters = "45.00"
    price_per_liter = "42.50"
    station_name = "WOG Station"
    odometer_at_fueling = "1000.00"
    actual_consumption = None
    deviation_pct = None
    is_anomalous = None
