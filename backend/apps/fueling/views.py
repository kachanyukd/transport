from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.fueling.models import FuelingRecord
from apps.fueling.serializers import FuelingRecordReadSerializer, FuelingRecordWriteSerializer
from apps.fueling.permissions import FuelingPermission
from apps.fueling.services import FuelingService
from apps.users.models import Role
from fleet.exceptions import BusinessLogicError
from fleet.pagination import FuelingCursorPagination
import django_filters


class FuelingRecordFilter(django_filters.FilterSet):
    vehicle = django_filters.NumberFilter(field_name="vehicle_id")
    driver = django_filters.NumberFilter(field_name="driver_id")
    is_anomalous = django_filters.BooleanFilter(field_name="is_anomalous")
    fueled_at__gte = django_filters.DateTimeFilter(
        field_name="fueled_at", lookup_expr="gte"
    )
    fueled_at__lte = django_filters.DateTimeFilter(
        field_name="fueled_at", lookup_expr="lte"
    )

    class Meta:
        model = FuelingRecord
        fields = ["vehicle", "driver", "is_anomalous"]


class FuelingRecordViewSet(viewsets.ModelViewSet):
    """
    Fuel records — two-level RBAC:
    Level 1: FuelingPermission
    Level 2: get_queryset() — Drivers see only their own records.
             A Driver accessing another driver's record gets 404, not 403.
    """

    permission_classes = [FuelingPermission]
    filterset_class = FuelingRecordFilter
    pagination_class = FuelingCursorPagination
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FuelingRecord.objects.select_related("vehicle", "driver").all()

        # Level 2 RBAC: Drivers see only their own records → 404 for others
        if user.role == Role.DRIVER:
            if hasattr(user, "driver") and user.driver:
                qs = qs.filter(driver=user.driver)
            else:
                qs = qs.none()

        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FuelingRecordReadSerializer
        return FuelingRecordWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            record = FuelingService.register_fueling(
                vehicle_id=data["vehicle"].pk,
                driver_id=data["driver"].pk,
                fueled_at=data["fueled_at"],
                fuel_liters=data["fuel_liters"],
                price_per_liter=data["price_per_liter"],
                station_name=data["station_name"],
                odometer_at_fueling=data["odometer_at_fueling"],
            )
        except BusinessLogicError as exc:
            raise ValidationError({"detail": exc.message, "code": exc.code})

        read_serializer = FuelingRecordReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
