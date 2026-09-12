from rest_framework.pagination import CursorPagination


class VehicleCursorPagination(CursorPagination):
    """Vehicles sorted by registration date (newest first)."""
    page_size = 25
    ordering = "-registered_at"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    max_page_size = 100


class DriverCursorPagination(CursorPagination):
    """Drivers sorted by full name alphabetically."""
    page_size = 25
    ordering = "full_name"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    max_page_size = 100


class FuelingCursorPagination(CursorPagination):
    page_size = 25
    ordering = "-fueled_at"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    max_page_size = 100


class MaintenanceCursorPagination(CursorPagination):
    page_size = 25
    ordering = "-opened_at"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    max_page_size = 100


# Backward-compat alias
FleetCursorPagination = VehicleCursorPagination
