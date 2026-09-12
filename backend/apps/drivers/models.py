from django.db import models


class DriverStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DISMISSED = "dismissed", "Dismissed"


class LicenseCategory(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"
    D = "D", "D"
    CE = "CE", "CE"
    DE = "DE", "DE"
    BC = "BC", "BC"


class Driver(models.Model):
    full_name = models.CharField(max_length=255)
    personnel_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    license_category = models.CharField(max_length=10, choices=LicenseCategory.choices)
    license_number = models.CharField(max_length=50, unique=True)
    license_issued_at = models.DateField()
    license_expires_at = models.DateField()
    status = models.CharField(
        max_length=20, choices=DriverStatus.choices, default=DriverStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "drivers"
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.personnel_number})"


class VehicleAssignment(models.Model):
    """
    Association entity implementing M:N between Vehicle and Driver over time.
    Separated from Vehicle to allow correct retrospective reporting
    when assignments change.
    """

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    assigned_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True, blank=True)  # NULL = currently active

    class Meta:
        db_table = "vehicle_assignments"
        verbose_name = "Vehicle Assignment"
        verbose_name_plural = "Vehicle Assignments"
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=models.Q(released_at__isnull=True),
                name="unique_active_vehicle_assignment",
            )
        ]
        ordering = ["-assigned_at"]

    def __str__(self) -> str:
        status = "active" if self.released_at is None else "released"
        return f"{self.vehicle} → {self.driver} ({status})"

    @property
    def is_active(self) -> bool:
        return self.released_at is None
