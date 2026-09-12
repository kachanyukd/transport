from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.maintenance.models import MaintenanceRecord
from apps.maintenance.serializers import (
    MaintenanceRecordReadSerializer,
    MaintenanceRecordWriteSerializer,
    CloseMaintenanceSerializer,
)
from apps.maintenance.permissions import MaintenancePermission
from apps.maintenance.services import MaintenanceService
from fleet.exceptions import BusinessLogicError
from fleet.pagination import MaintenanceCursorPagination
import django_filters


class MaintenanceFilter(django_filters.FilterSet):
    vehicle = django_filters.NumberFilter(field_name="vehicle_id")
    record_type = django_filters.CharFilter(field_name="record_type")
    is_open = django_filters.BooleanFilter(
        field_name="closed_at", lookup_expr="isnull"
    )
    opened_at__gte = django_filters.DateTimeFilter(
        field_name="opened_at", lookup_expr="gte"
    )
    opened_at__lte = django_filters.DateTimeFilter(
        field_name="opened_at", lookup_expr="lte"
    )

    class Meta:
        model = MaintenanceRecord
        fields = ["vehicle", "record_type"]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [MaintenancePermission]
    filterset_class = MaintenanceFilter
    pagination_class = MaintenanceCursorPagination
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return MaintenanceRecord.objects.select_related("vehicle").all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return MaintenanceRecordReadSerializer
        if self.action == "close":
            return CloseMaintenanceSerializer
        return MaintenanceRecordWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            record = MaintenanceService.open_request(
                vehicle_id=data["vehicle"].pk,
                record_type=data["record_type"],
                opened_at=data.get("opened_at"),
                fault_description=data["fault_description"],
                contractor_name=data.get("contractor_name", ""),
                parts_cost=data.get("parts_cost"),
                labor_cost=data.get("labor_cost"),
            )
        except BusinessLogicError as exc:
            raise ValidationError({"detail": exc.message, "code": exc.code})

        read_serializer = MaintenanceRecordReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = MaintenanceRecordWriteSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        read_serializer = MaintenanceRecordReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        record = self.get_object()
        serializer = CloseMaintenanceSerializer(
            data=request.data,
            context={"record": record, **self.get_serializer_context()},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            updated_record = MaintenanceService.close_request(
                record_id=record.pk,
                work_performed=data["work_performed"],
                parts_cost=data.get("parts_cost"),
                labor_cost=data.get("labor_cost"),
                odometer_at_closing=data.get("odometer_at_closing"),
                closed_at=data.get("closed_at"),
            )
        except BusinessLogicError as exc:
            raise ValidationError({"detail": exc.message, "code": exc.code})

        read_serializer = MaintenanceRecordReadSerializer(
            updated_record, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)
