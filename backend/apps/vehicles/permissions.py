from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Role


class VehiclePermission(BasePermission):
    """
    Level 1 RBAC: role-based permission check for the Vehicle resource.
    Level 2 (queryset filtering) is handled in get_queryset() of the ViewSet.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role

        # All authenticated roles can read
        if request.method in SAFE_METHODS:
            return True

        # decommission action — Admin and Manager only
        if view.action == "decommission":
            return role in (Role.ADMIN, Role.MANAGER)

        # Create/Update — Admin and Manager only
        return role in (Role.ADMIN, Role.MANAGER)
