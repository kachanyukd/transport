from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Role


class DriverPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role

        # Drivers cannot access driver management at all
        if role == Role.DRIVER:
            return False

        # Dispatchers can only read
        if role == Role.DISPATCHER:
            return request.method in SAFE_METHODS

        # Admin and Manager have full access
        return True
