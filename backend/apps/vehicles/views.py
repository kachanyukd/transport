from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleReadSerializer, VehicleWriteSerializer
from apps.vehicles.permissions import VehiclePermission
from apps.vehicles.services import VehicleService
from apps.users.models import Role
from fleet.exceptions import BusinessLogicError
from fleet.pagination import VehicleCursorPagination
import django_filters


class VehicleFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    fuel_type = django_filters.CharFilter(field_name="fuel_type")
    make = django_filters.CharFilter(field_name="make", lookup_expr="icontains")

    class Meta:
        model = Vehicle
        fields = ["status", "fuel_type", "make"]


class VehicleViewSet(viewsets.ModelViewSet):
    """
    Vehicle resource — two-level RBAC:
    Level 1: VehiclePermission class
    Level 2: get_queryset() — Drivers see only vehicles assigned to them.
    """

    permission_classes = [VehiclePermission]
    filterset_class = VehicleFilter
    pagination_class = VehicleCursorPagination
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Vehicle.objects.all()

        # Level 2 RBAC: Drivers see only their assigned vehicle
        if user.role == Role.DRIVER:
            if hasattr(user, "driver") and user.driver:
                # Active assignment for this driver
                from apps.drivers.models import VehicleAssignment
                assigned_vehicle_ids = VehicleAssignment.objects.filter(
                    driver=user.driver,
                    released_at__isnull=True,
                ).values_list("vehicle_id", flat=True)
                qs = qs.filter(id__in=assigned_vehicle_ids)
            else:
                qs = qs.none()

        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return VehicleReadSerializer
        return VehicleWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        read_serializer = VehicleReadSerializer(vehicle, context=self.get_serializer_context())
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        read_serializer = VehicleReadSerializer(vehicle, context=self.get_serializer_context())
        return Response(read_serializer.data)

    @action(detail=True, methods=["post"], url_path="decommission")
    def decommission(self, request, pk=None):
        try:
            vehicle = VehicleService.decommission(vehicle_id=int(pk))
        except BusinessLogicError as exc:
            raise ValidationError({"detail": exc.message, "code": exc.code})
        serializer = VehicleReadSerializer(vehicle, context=self.get_serializer_context())
        return Response(serializer.data)
