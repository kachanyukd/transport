from django.contrib import admin
from apps.drivers.models import Driver, VehicleAssignment

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["full_name", "personnel_number", "license_category", "status"]
    list_filter = ["status", "license_category"]
    search_fields = ["full_name", "personnel_number", "license_number"]

@admin.register(VehicleAssignment)
class VehicleAssignmentAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "driver", "assigned_at", "released_at"]
