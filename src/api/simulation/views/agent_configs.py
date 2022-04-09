"""
Localized Epidemiological ABS API Agent Config Views
"""

from rest_framework import viewsets

from ..models import AgentConfig
from ..serializers import AgentConfigSerializer


class AgentConfigViewSet(viewsets.ModelViewSet):
    """
    Viewset for Agent Config model
    """
    queryset = AgentConfig.objects.all()
    serializer_class = AgentConfigSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
