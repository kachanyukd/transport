from django.contrib import admin
from apps.vehicles.models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["license_plate", "make", "model", "year", "fuel_type", "status", "odometer"]
    list_filter = ["status", "fuel_type"]
    search_fields = ["license_plate", "vin", "make", "model"]
