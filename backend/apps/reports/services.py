"""
ReportService — aggregated reporting business logic.

All queries use ORM aggregations and are placed in the service layer,
not in views or models directly.
"""

from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth

from apps.fueling.models import FuelingRecord
from apps.maintenance.models import MaintenanceRecord
from apps.vehicles.models import Vehicle


class ReportService:
    @staticmethod
    def fuel_report(
        *,
        date_from=None,
        date_to=None,
        vehicle_id: int = None,
        driver_id: int = None,
    ) -> dict:
        """
        Aggregate fueling costs and consumption grouped by vehicle and month.
        """
        qs = FuelingRecord.objects.all()
        if date_from:
            qs = qs.filter(fueled_at__gte=date_from)
        if date_to:
            qs = qs.filter(fueled_at__lte=date_to)
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        if driver_id:
            qs = qs.filter(driver_id=driver_id)

        # Total cost expression
        total_cost_expr = ExpressionWrapper(
            F("fuel_liters") * F("price_per_liter"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        summary = qs.aggregate(
            total_liters=Sum("fuel_liters"),
            total_cost=Sum(total_cost_expr),
            avg_consumption=Avg("actual_consumption"),
            anomaly_count=Count("id", filter=Q(is_anomalous=True)),
            record_count=Count("id"),
        )

        by_month = (
            qs.annotate(month=TruncMonth("fueled_at"))
            .values("month")
            .annotate(
                liters=Sum("fuel_liters"),
                cost=Sum(total_cost_expr),
                records=Count("id"),
            )
            .order_by("month")
        )

        by_vehicle = (
            qs.values("vehicle_id", "vehicle__license_plate", "vehicle__make", "vehicle__model")
            .annotate(
                liters=Sum("fuel_liters"),
                cost=Sum(total_cost_expr),
                avg_consumption=Avg("actual_consumption"),
                anomaly_count=Count("id", filter=Q(is_anomalous=True)),
            )
            .order_by("-cost")
        )

        return {
            "summary": summary,
            "by_month": list(by_month),
            "by_vehicle": list(by_vehicle),
        }

    @staticmethod
    def maintenance_report(
        *,
        date_from=None,
        date_to=None,
        vehicle_id: int = None,
    ) -> dict:
        """
        Aggregate maintenance costs grouped by vehicle and record type.
        """
        qs = MaintenanceRecord.objects.all()
        if date_from:
            qs = qs.filter(opened_at__gte=date_from)
        if date_to:
            qs = qs.filter(opened_at__lte=date_to)
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)

        total_cost_expr = ExpressionWrapper(
            F("parts_cost") + F("labor_cost"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        summary = qs.aggregate(
            total_parts_cost=Sum("parts_cost"),
            total_labor_cost=Sum("labor_cost"),
            total_cost=Sum(total_cost_expr),
            open_count=Count("id", filter=Q(closed_at__isnull=True)),
            closed_count=Count("id", filter=Q(closed_at__isnull=False)),
            record_count=Count("id"),
        )

        by_type = (
            qs.values("record_type")
            .annotate(
                count=Count("id"),
                parts_cost=Sum("parts_cost"),
                labor_cost=Sum("labor_cost"),
                total_cost=Sum(total_cost_expr),
            )
            .order_by("-total_cost")
        )

        by_vehicle = (
            qs.values("vehicle_id", "vehicle__license_plate", "vehicle__make", "vehicle__model")
            .annotate(
                count=Count("id"),
                parts_cost=Sum("parts_cost"),
                labor_cost=Sum("labor_cost"),
                total_cost=Sum(total_cost_expr),
            )
            .order_by("-total_cost")
        )

        return {
            "summary": summary,
            "by_type": list(by_type),
            "by_vehicle": list(by_vehicle),
        }

    @staticmethod
    def mileage_report(
        *,
        date_from=None,
        date_to=None,
        vehicle_id: int = None,
    ) -> dict:
        """
        Mileage report: distance traveled per vehicle in the given period.
        Uses first and last odometer reading from fueling records in range.
        """
        qs = FuelingRecord.objects.all()
        if date_from:
            qs = qs.filter(fueled_at__gte=date_from)
        if date_to:
            qs = qs.filter(fueled_at__lte=date_to)
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)

        from django.db.models import Min, Max
        by_vehicle = (
            qs.values("vehicle_id", "vehicle__license_plate", "vehicle__make", "vehicle__model")
            .annotate(
                first_odometer=Min("odometer_at_fueling"),
                last_odometer=Max("odometer_at_fueling"),
                fueling_count=Count("id"),
            )
            .order_by("vehicle_id")
        )

        result = []
        total_distance = Decimal("0")
        for row in by_vehicle:
            distance = (row["last_odometer"] or 0) - (row["first_odometer"] or 0)
            total_distance += distance
            result.append({**row, "distance_km": distance})

        return {
            "summary": {"total_distance_km": total_distance, "vehicle_count": len(result)},
            "by_vehicle": result,
        }

    @staticmethod
    def summary_report(
        *,
        date_from=None,
        date_to=None,
    ) -> dict:
        """
        Combined cost summary: total fuel costs + total maintenance costs.
        """
        fuel = ReportService.fuel_report(date_from=date_from, date_to=date_to)
        maintenance = ReportService.maintenance_report(date_from=date_from, date_to=date_to)

        total_fuel_cost = fuel["summary"]["total_cost"] or Decimal("0")
        total_maint_cost = maintenance["summary"]["total_cost"] or Decimal("0")

        return {
            "total_fuel_cost": total_fuel_cost,
            "total_maintenance_cost": total_maint_cost,
            "total_cost": total_fuel_cost + total_maint_cost,
            "fuel_summary": fuel["summary"],
            "maintenance_summary": maintenance["summary"],
        }

    @staticmethod
    def dashboard_stats() -> dict:
        """
        Aggregated statistics for the dashboard.
        """
        from apps.vehicles.models import VehicleStatus
        from apps.drivers.models import DriverStatus

        vehicles = Vehicle.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=VehicleStatus.ACTIVE)),
            in_maintenance=Count("id", filter=Q(status=VehicleStatus.MAINTENANCE)),
            decommissioned=Count("id", filter=Q(status=VehicleStatus.DECOMMISSIONED)),
        )

        from apps.drivers.models import Driver
        drivers = Driver.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=DriverStatus.ACTIVE)),
        )

        # Anomalies in the last 30 days
        from django.utils import timezone
        import datetime
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        recent_anomalies = FuelingRecord.objects.filter(
            fueled_at__gte=thirty_days_ago, is_anomalous=True
        ).count()

        open_maintenance = MaintenanceRecord.objects.filter(closed_at__isnull=True).count()

        return {
            "vehicles": vehicles,
            "drivers": drivers,
            "recent_anomalies_30d": recent_anomalies,
            "open_maintenance_count": open_maintenance,
        }
