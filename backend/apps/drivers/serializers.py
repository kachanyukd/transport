from rest_framework import serializers
from apps.drivers.models import Driver, VehicleAssignment


class DriverReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id",
            "full_name",
            "personnel_number",
            "date_of_birth",
            "phone",
            "license_category",
            "license_number",
            "license_issued_at",
            "license_expires_at",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class DriverWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "full_name",
            "personnel_number",
            "date_of_birth",
            "phone",
            "license_category",
            "license_number",
            "license_issued_at",
            "license_expires_at",
            "status",
        ]

    def validate(self, attrs):
        issued = attrs.get("license_issued_at")
        expires = attrs.get("license_expires_at")
        if issued and expires and expires <= issued:
            raise serializers.ValidationError(
                {"license_expires_at": "Expiry date must be after issue date."}
            )
        return attrs


class VehicleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAssignment
        fields = ["id", "vehicle", "driver", "assigned_at", "released_at", "is_active"]
        read_only_fields = ["id", "released_at", "is_active"]


class AssignVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    assigned_at = serializers.DateTimeField(required=False)
