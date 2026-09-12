import factory
from factory.django import DjangoModelFactory
from apps.vehicles.models import Vehicle, VehicleStatus, FuelType


class VehicleFactory(DjangoModelFactory):
    class Meta:
        model = Vehicle

    license_plate = factory.Sequence(lambda n: f"AA{n:04d}BB")
    vin = factory.Sequence(lambda n: f"VIN{n:014d}")
    make = "Toyota"
    model = "Corolla"
    year = 2020
    fuel_type = FuelType.PETROL
    norm_consumption_summer = factory.Faker(
        "pydecimal", left_digits=2, right_digits=2, positive=True, min_value=6, max_value=12
    )
    norm_consumption_winter = factory.Faker(
        "pydecimal", left_digits=2, right_digits=2, positive=True, min_value=7, max_value=14
    )
    odometer = "0.00"
    status = VehicleStatus.ACTIVE
