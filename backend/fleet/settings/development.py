import environ
from .base import *  # noqa: F401, F403

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")  # noqa: F405

DEBUG = True
ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
CORS_ALLOW_ALL_ORIGINS = True

REFRESH_TOKEN_COOKIE_SECURE = False

# Faster password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
