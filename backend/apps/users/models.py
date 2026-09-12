from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    DISPATCHER = "dispatcher", "Dispatcher"
    DRIVER = "driver", "Driver"


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, role: str = Role.DRIVER, **extra):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, role=role, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str, **extra):
        extra.setdefault("role", Role.ADMIN)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DRIVER)
    # Link to Driver profile — null for non-driver roles
    driver = models.OneToOneField(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_account",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_dispatcher(self) -> bool:
        return self.role == Role.DISPATCHER

    @property
    def is_driver_role(self) -> bool:
        return self.role == Role.DRIVER
