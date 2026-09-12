from django.db import models


class FuelType(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"
    GAS = "gas", "Gas"
    ELECTRIC = "electric", "Electric"
    HYBRID = "hybrid", "Hybrid"


class VehicleStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    MAINTENANCE = "maintenance", "Maintenance"
    DECOMMISSIONED = "decommissioned", "Decommissioned"


class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices)
    # Normative fuel consumption — NUMERIC for exact arithmetic
    norm_consumption_summer = models.DecimalField(max_digits=6, decimal_places=2)
    norm_consumption_winter = models.DecimalField(max_digits=6, decimal_places=2)
    # Current odometer in km
    odometer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.ACTIVE
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicles"
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ["license_plate"]

    def __str__(self) -> str:
        return f"{self.license_plate} — {self.make} {self.model} ({self.year})"
