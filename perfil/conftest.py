import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfil.settings")


def pytest_configure():
    settings.DEBUG = False
    django.setup()
