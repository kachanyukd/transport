import factory
from factory.django import DjangoModelFactory
from apps.users.models import User, Role


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    role = Role.DISPATCHER
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")
        manager = cls._get_manager(model_class)
        user = manager.create_user(*args, password=password, **kwargs)
        return user


class AdminUserFactory(UserFactory):
    role = Role.ADMIN
    is_staff = True
    is_superuser = True


class ManagerUserFactory(UserFactory):
    role = Role.MANAGER


class DispatcherUserFactory(UserFactory):
    role = Role.DISPATCHER


class DriverUserFactory(UserFactory):
    role = Role.DRIVER
