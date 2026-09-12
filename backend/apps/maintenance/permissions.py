from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Role


class MaintenancePermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role

        # Drivers have no access to maintenance
        if role == Role.DRIVER:
            return False

        # Dispatchers can only read
        if role == Role.DISPATCHER:
            return request.method in SAFE_METHODS

        # Admin and Manager have full access including close action
        return True
