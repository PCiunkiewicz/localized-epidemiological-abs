"""Localized Epidemiological ABS API Agent Config Views."""

from rest_framework import viewsets

from api.simulation.models import AgentConfig
from api.simulation.serializers import AgentConfigSerializer


class AgentConfigViewSet(viewsets.ModelViewSet):
    """Viewset for Agent Config model."""

    queryset = AgentConfig.objects.all()
    serializer_class = AgentConfigSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission
