from rest_framework import serializers
from apps.vehicles.models import Vehicle


class VehicleReadSerializer(serializers.ModelSerializer):
    """Read serializer — includes all fields, computed ones are read-only."""

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "license_plate",
            "vin",
            "make",
            "model",
            "year",
            "fuel_type",
            "norm_consumption_summer",
            "norm_consumption_winter",
            "odometer",
            "status",
            "registered_at",
        ]
        read_only_fields = fields


class VehicleWriteSerializer(serializers.ModelSerializer):
    """Write serializer — excludes server-managed fields."""

    class Meta:
        model = Vehicle
        fields = [
            "license_plate",
            "vin",
            "make",
            "model",
            "year",
            "fuel_type",
            "norm_consumption_summer",
            "norm_consumption_winter",
            "odometer",
        ]

    def validate_year(self, value: int) -> int:
        import datetime
        current_year = datetime.date.today().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1900 and {current_year + 1}."
            )
        return value

    def validate_norm_consumption_summer(self, value):
        if value <= 0:
            raise serializers.ValidationError("Norm consumption must be positive.")
        return value

    def validate_norm_consumption_winter(self, value):
        if value <= 0:
            raise serializers.ValidationError("Norm consumption must be positive.")
        return value
