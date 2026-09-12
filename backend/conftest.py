"""
pytest configuration.
Uses a real PostgreSQL test database — not mocked ORM.
This validates actual behavior of select_related, transactions, and constraints.
"""
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet.settings.development")


def pytest_configure(config):
    os.environ["DJANGO_SETTINGS_MODULE"] = "fleet.settings.development"
