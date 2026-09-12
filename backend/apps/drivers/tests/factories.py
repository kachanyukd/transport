import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
import datetime

from apps.drivers.models import Driver, DriverStatus, LicenseCategory


class DriverFactory(DjangoModelFactory):
    class Meta:
        model = Driver

    full_name = factory.Faker("name")
    personnel_number = factory.Sequence(lambda n: f"EMP{n:05d}")
    date_of_birth = factory.LazyFunction(
        lambda: (datetime.date.today() - datetime.timedelta(days=365 * 35))
    )
    phone = factory.Faker("phone_number")
    license_category = LicenseCategory.B
    license_number = factory.Sequence(lambda n: f"LIC{n:08d}")
    license_issued_at = factory.LazyFunction(
        lambda: datetime.date.today() - datetime.timedelta(days=365 * 3)
    )
    license_expires_at = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=365 * 7)
    )
    status = DriverStatus.ACTIVE
