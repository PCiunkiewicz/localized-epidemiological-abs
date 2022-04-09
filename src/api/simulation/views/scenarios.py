"""
Localized Epidemiological ABS API Scenario Views
"""

from rest_framework import viewsets

from ..models import Scenario
from ..serializers import ScenarioSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    """
    Viewset for Scenario model
    """
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
