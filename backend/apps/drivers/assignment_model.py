"""
VehicleAssignment is defined here to avoid circular imports.
Import it via: from apps.drivers.assignment_model import VehicleAssignment
"""
from django.db import models


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
        # Only one active assignment per vehicle at a time
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
