"""
API endpoint urls
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.terrains import TerrainViewSet
from .views.simulations import SimulationViewSet
from .views.viruses import VirusViewSet
from .views.scenarios import ScenarioViewSet
from .views.agent_configs import AgentConfigViewSet
from .views.runs import RunViewSet

TERRAIN_ROUTER = DefaultRouter()
TERRAIN_ROUTER.register(f'terrains', TerrainViewSet)

SIMULATION_ROUTER = DefaultRouter()
SIMULATION_ROUTER.register(f'simulations', SimulationViewSet)

VIRUS_ROUTER = DefaultRouter()
VIRUS_ROUTER.register(f'viruses', VirusViewSet)

SCENARIO_ROUTER = DefaultRouter()
SCENARIO_ROUTER.register(f'scenarios', ScenarioViewSet)

AGENT_CONFIG_ROUTER = DefaultRouter()
AGENT_CONFIG_ROUTER.register(f'agent_configs', AgentConfigViewSet)

RUN_ROUTER = DefaultRouter()
RUN_ROUTER.register(f'runs', RunViewSet)

urlpatterns = [

]

urlpatterns += TERRAIN_ROUTER.urls
urlpatterns += SIMULATION_ROUTER.urls
urlpatterns += VIRUS_ROUTER.urls
urlpatterns += SCENARIO_ROUTER.urls
urlpatterns += AGENT_CONFIG_ROUTER.urls
urlpatterns += RUN_ROUTER.urls
