from django.db import models


class FuelingRecord(models.Model):
    """
    Fueling record with materialized computed consumption fields.

    actual_consumption, deviation_pct, is_anomalous are stored (not computed on read)
    to avoid expensive LAG() window queries on every report query.
    They are null for the first record per vehicle (no previous odometer to compare).
    These fields are read-only on the serializer — set only by FuelingService.
    """

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.PROTECT,  # Prevent silent deletion of financial data
        related_name="fueling_records",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.PROTECT,
        related_name="fueling_records",
    )
    # TIMESTAMPTZ — stored UTC, converted on read per session timezone
    fueled_at = models.DateTimeField()
    fuel_liters = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    station_name = models.CharField(max_length=255)
    odometer_at_fueling = models.DecimalField(max_digits=10, decimal_places=2)

    # Materialized computed fields — set by FuelingService, read-only on serializer
    actual_consumption = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True
    )
    deviation_pct = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True
    )
    is_anomalous = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fueling_records"
        verbose_name = "Fueling Record"
        verbose_name_plural = "Fueling Records"
        ordering = ["-fueled_at"]
        indexes = [
            # Composite index for report queries filtering both simultaneously
            models.Index(fields=["vehicle", "fueled_at"], name="idx_fueling_vehicle_date"),
            models.Index(fields=["driver", "fueled_at"], name="idx_fueling_driver_date"),
            models.Index(fields=["is_anomalous"], name="idx_fueling_anomalous"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fuel_liters__gt=0),
                name="chk_fueling_positive_liters",
            ),
            models.CheckConstraint(
                check=models.Q(price_per_liter__gt=0),
                name="chk_fueling_positive_price",
            ),
            models.CheckConstraint(
                check=models.Q(odometer_at_fueling__gte=0),
                name="chk_fueling_non_negative_odometer",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Fueling {self.vehicle} by {self.driver} on "
            f"{self.fueled_at.strftime('%Y-%m-%d')} — {self.fuel_liters}L"
        )

    @property
    def total_cost(self):
        return self.fuel_liters * self.price_per_liter
