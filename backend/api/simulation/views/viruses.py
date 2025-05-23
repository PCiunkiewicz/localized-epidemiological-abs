"""Localized Epidemiological ABS API Virus Views."""

from rest_framework import viewsets

from api.simulation.models import Virus
from api.simulation.serializers import VirusSerializer


class VirusViewSet(viewsets.ModelViewSet):
    """Viewset for Virus model."""

    queryset = Virus.objects.all()
    serializer_class = VirusSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission
