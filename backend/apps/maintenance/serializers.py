from rest_framework import serializers
from apps.maintenance.models import MaintenanceRecord


class MaintenanceRecordReadSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    vehicle_info = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            "id",
            "vehicle",
            "vehicle_info",
            "record_type",
            "opened_at",
            "closed_at",
            "is_open",
            "fault_description",
            "work_performed",
            "contractor_name",
            "parts_cost",
            "labor_cost",
            "total_cost",
            "odometer_at_closing",
            "created_at",
        ]
        read_only_fields = fields

    def get_vehicle_info(self, obj) -> str:
        v = obj.vehicle
        return f"{v.license_plate} — {v.make} {v.model}"


class MaintenanceRecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = [
            "vehicle",
            "record_type",
            "opened_at",
            "fault_description",
            "contractor_name",
            "parts_cost",
            "labor_cost",
        ]


class CloseMaintenanceSerializer(serializers.Serializer):
    """Used for POST /maintenance/{id}/close/"""

    work_performed = serializers.CharField()
    parts_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    labor_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    odometer_at_closing = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    closed_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        # State validation: check if already closed
        record = self.context.get("record")
        if record and record.closed_at is not None:
            raise serializers.ValidationError(
                "This maintenance record is already closed."
            )
        return attrs
