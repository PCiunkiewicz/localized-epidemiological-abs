"""Localized Epidemiological ABS API Terrain Views."""

from rest_framework import viewsets

from api.simulation.models import Terrain
from api.simulation.serializers import TerrainSerializer


class TerrainViewSet(viewsets.ModelViewSet):
    """Viewset for Terrain model."""

    queryset = Terrain.objects.all()
    serializer_class = TerrainSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission
