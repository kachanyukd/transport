from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, CustomTokenObtainPairView, CustomTokenRefreshView
from apps.vehicles.views import VehicleViewSet
from apps.drivers.views import DriverViewSet
from apps.fueling.views import FuelingRecordViewSet
from apps.maintenance.views import MaintenanceRecordViewSet
from apps.reports.views import (
    FuelReportView,
    MaintenanceReportView,
    MileageReportView,
    SummaryReportView,
    DashboardView,
)
from rest_framework_simplejwt.views import TokenBlacklistView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"drivers", DriverViewSet, basename="driver")
router.register(r"fuel-records", FuelingRecordViewSet, basename="fuel-record")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("reports/fuel/", FuelReportView.as_view(), name="report_fuel"),
    path("reports/maintenance/", MaintenanceReportView.as_view(), name="report_maintenance"),
    path("reports/mileage/", MileageReportView.as_view(), name="report_mileage"),
    path("reports/summary/", SummaryReportView.as_view(), name="report_summary"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
