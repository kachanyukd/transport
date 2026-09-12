from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.drivers.models import Driver
from apps.drivers.serializers import (
    DriverReadSerializer,
    DriverWriteSerializer,
    VehicleAssignmentSerializer,
    AssignVehicleSerializer,
)
from apps.drivers.permissions import DriverPermission
from apps.drivers.services import DriverService
from fleet.exceptions import BusinessLogicError
from fleet.pagination import DriverCursorPagination
import django_filters


class DriverFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    license_category = django_filters.CharFilter(field_name="license_category")

    class Meta:
        model = Driver
        fields = ["status", "license_category"]


class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [DriverPermission]
    filterset_class = DriverFilter
    pagination_class = DriverCursorPagination
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return Driver.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return DriverReadSerializer
        if self.action == "assign":
            return AssignVehicleSerializer
        return DriverWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()
        read_serializer = DriverReadSerializer(driver, context=self.get_serializer_context())
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()
        read_serializer = DriverReadSerializer(driver, context=self.get_serializer_context())
        return Response(read_serializer.data)

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        driver = self.get_object()
        serializer = AssignVehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            assignment = DriverService.assign_vehicle(
                driver_id=driver.pk,
                vehicle_id=serializer.validated_data["vehicle_id"],
                assigned_at=serializer.validated_data.get("assigned_at"),
            )
        except BusinessLogicError as exc:
            raise ValidationError({"detail": exc.message, "code": exc.code})

        return Response(
            VehicleAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )
