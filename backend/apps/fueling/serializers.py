from rest_framework import serializers
from apps.fueling.models import FuelingRecord


class FuelingRecordReadSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    vehicle_info = serializers.SerializerMethodField()
    driver_info = serializers.SerializerMethodField()

    class Meta:
        model = FuelingRecord
        fields = [
            "id",
            "vehicle",
            "vehicle_info",
            "driver",
            "driver_info",
            "fueled_at",
            "fuel_liters",
            "price_per_liter",
            "total_cost",
            "station_name",
            "odometer_at_fueling",
            # Computed fields — read-only, set by FuelingService
            "actual_consumption",
            "deviation_pct",
            "is_anomalous",
            "created_at",
        ]
        read_only_fields = fields

    def get_vehicle_info(self, obj) -> str:
        v = obj.vehicle
        return f"{v.license_plate} — {v.make} {v.model}"

    def get_driver_info(self, obj) -> str:
        return obj.driver.full_name


class FuelingRecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelingRecord
        fields = [
            "vehicle",
            "driver",
            "fueled_at",
            "fuel_liters",
            "price_per_liter",
            "station_name",
            "odometer_at_fueling",
        ]

    def validate_fuel_liters(self, value):
        if value <= 0:
            raise serializers.ValidationError("Fuel liters must be positive.")
        return value

    def validate_price_per_liter(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per liter must be positive.")
        return value

    def validate_odometer_at_fueling(self, value):
        if value < 0:
            raise serializers.ValidationError("Odometer reading cannot be negative.")
        return value
