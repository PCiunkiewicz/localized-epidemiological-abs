"""API URL Configuration."""

from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path(f'api/{settings.API_VERSION}/', include('api.simulation.urls')),
]
