import factory
from factory.django import DjangoModelFactory
from django.utils import timezone

from apps.maintenance.models import MaintenanceRecord, MaintenanceType
from apps.vehicles.tests.factories import VehicleFactory


class MaintenanceRecordFactory(DjangoModelFactory):
    class Meta:
        model = MaintenanceRecord

    vehicle = factory.SubFactory(VehicleFactory)
    record_type = MaintenanceType.CURRENT_REPAIR
    opened_at = factory.LazyFunction(timezone.now)
    closed_at = None
    fault_description = "Engine oil leak detected during routine inspection."
    work_performed = ""
    contractor_name = "ServiceCo"
    parts_cost = "500.00"
    labor_cost = "300.00"
    odometer_at_closing = None
