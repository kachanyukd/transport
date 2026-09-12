from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.models import User, Role
from apps.users.serializers import UserReadSerializer, UserWriteSerializer
from fleet.exceptions import custom_exception_handler  # noqa: F401


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view) and request.user.role == Role.ADMIN


class UserViewSet(viewsets.ModelViewSet):
    """
    User management — Admin only.
    DELETE deactivates the account (does not delete the row).
    """

    permission_classes = [IsAdmin]
    pagination_class = None  # return plain list, not cursor-paginated

    def get_queryset(self):
        return User.objects.select_related("driver").order_by("username")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return UserReadSerializer
        return UserWriteSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete — deactivate instead of hard delete."""
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Issues access + refresh tokens.
    Refresh token is set in httpOnly cookie; access token is returned in body.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.pop("refresh", None)
            if refresh_token:
                response.set_cookie(
                    key=settings.REFRESH_TOKEN_COOKIE_NAME,
                    value=refresh_token,
                    httponly=True,
                    secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                    samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
                    max_age=7 * 24 * 60 * 60,  # 7 days
                    path="/api/v1/auth/",
                )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Reads the refresh token from httpOnly cookie instead of request body.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if refresh_token:
            # Inject cookie token into mutable request data
            data = request.data.copy()
            data["refresh"] = refresh_token
            request._full_data = data
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Update cookie with the new rotated refresh token
            new_refresh = response.data.pop("refresh", None)
            if new_refresh:
                response.set_cookie(
                    key=settings.REFRESH_TOKEN_COOKIE_NAME,
                    value=new_refresh,
                    httponly=True,
                    secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                    samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
                    max_age=7 * 24 * 60 * 60,
                    path="/api/v1/auth/",
                )
        return response
