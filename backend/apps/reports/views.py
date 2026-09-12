from rest_framework.views import APIView
from rest_framework.response import Response

from apps.reports.permissions import ReportPermission
from apps.reports.services import ReportService


class BaseReportView(APIView):
    permission_classes = [ReportPermission]

    def _get_date_params(self, request):
        return {
            "date_from": request.query_params.get("from"),
            "date_to": request.query_params.get("to"),
        }


class FuelReportView(BaseReportView):
    def get(self, request):
        params = self._get_date_params(request)
        params["vehicle_id"] = request.query_params.get("vehicle")
        params["driver_id"] = request.query_params.get("driver")
        # Convert to int if provided
        if params["vehicle_id"]:
            params["vehicle_id"] = int(params["vehicle_id"])
        if params["driver_id"]:
            params["driver_id"] = int(params["driver_id"])
        data = ReportService.fuel_report(**params)
        return Response(data)


class MaintenanceReportView(BaseReportView):
    def get(self, request):
        params = self._get_date_params(request)
        vehicle_id = request.query_params.get("vehicle")
        if vehicle_id:
            params["vehicle_id"] = int(vehicle_id)
        data = ReportService.maintenance_report(**params)
        return Response(data)


class MileageReportView(BaseReportView):
    def get(self, request):
        params = self._get_date_params(request)
        vehicle_id = request.query_params.get("vehicle")
        if vehicle_id:
            params["vehicle_id"] = int(vehicle_id)
        data = ReportService.mileage_report(**params)
        return Response(data)


class SummaryReportView(BaseReportView):
    def get(self, request):
        params = self._get_date_params(request)
        data = ReportService.summary_report(**params)
        return Response(data)


class DashboardView(APIView):
    def get(self, request):
        data = ReportService.dashboard_stats()
        return Response(data)
