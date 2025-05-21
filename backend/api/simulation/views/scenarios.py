"""Localized Epidemiological ABS API Scenario Views."""

from typing import override

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from api.simulation.models import Scenario
from api.simulation.serializers import NestedScenarioSerializer, ScenarioSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    """Viewset for Scenario model."""

    queryset = Scenario.objects.all()
    serializer_class = NestedScenarioSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission

    @override
    def list(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        serializer = ScenarioSerializer(queryset, many=True)
        return Response(serializer.data)
