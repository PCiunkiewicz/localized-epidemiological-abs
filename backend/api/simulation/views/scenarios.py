"""Localized Epidemiological ABS API Scenario Views."""

from rest_framework import viewsets

from api.simulation.models import Scenario
from api.simulation.serializers import ScenarioSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    """Viewset for Scenario model."""

    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission
