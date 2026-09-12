from django.db import models


class MaintenanceType(models.TextChoices):
    PLANNED_TO = "planned_to", "Planned Technical Inspection"
    CURRENT_REPAIR = "current_repair", "Current Repair"
    MAJOR_REPAIR = "major_repair", "Major Repair"


class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.PROTECT,
        related_name="maintenance_records",
    )
    record_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    fault_description = models.TextField()
    work_performed = models.TextField(blank=True)
    contractor_name = models.CharField(max_length=255, blank=True)
    parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    odometer_at_closing = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_records"
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["vehicle", "opened_at"], name="idx_maint_vehicle_date"),
            models.Index(fields=["closed_at"], name="idx_maint_closed_at"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(parts_cost__gte=0),
                name="chk_maint_non_negative_parts",
            ),
            models.CheckConstraint(
                check=models.Q(labor_cost__gte=0),
                name="chk_maint_non_negative_labor",
            ),
        ]

    def __str__(self) -> str:
        status = "open" if self.closed_at is None else "closed"
        return f"Maintenance {self.vehicle} [{self.record_type}] ({status})"

    @property
    def is_open(self) -> bool:
        return self.closed_at is None

    @property
    def total_cost(self):
        return self.parts_cost + self.labor_cost
