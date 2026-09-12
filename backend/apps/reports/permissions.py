from rest_framework.permissions import BasePermission
from apps.users.models import Role


class ReportPermission(BasePermission):
    """Only Admin and Manager can access reports."""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (Role.ADMIN, Role.MANAGER)
