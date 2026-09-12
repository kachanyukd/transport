from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Role


class FuelingPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role

        # All authenticated can read (queryset limits Drivers to own records)
        if request.method in SAFE_METHODS:
            return True

        # Drivers cannot create fueling records
        if role == Role.DRIVER:
            return False

        # Admin, Manager, Dispatcher can create
        return True
