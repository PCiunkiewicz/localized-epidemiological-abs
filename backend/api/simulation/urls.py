"""Register all API endpoint urls."""

from rest_framework.routers import DefaultRouter

from api.simulation.views.agent_configs import AgentConfigViewSet
from api.simulation.views.runs import RunViewSet
from api.simulation.views.scenarios import ScenarioViewSet
from api.simulation.views.simulations import SimulationViewSet
from api.simulation.views.terrains import TerrainViewSet
from api.simulation.views.viruses import VirusViewSet

TERRAIN_ROUTER = DefaultRouter()
TERRAIN_ROUTER.register('terrains', TerrainViewSet)

SIMULATION_ROUTER = DefaultRouter()
SIMULATION_ROUTER.register('simulations', SimulationViewSet)

VIRUS_ROUTER = DefaultRouter()
VIRUS_ROUTER.register('viruses', VirusViewSet)

SCENARIO_ROUTER = DefaultRouter()
SCENARIO_ROUTER.register('scenarios', ScenarioViewSet)

AGENT_CONFIG_ROUTER = DefaultRouter()
AGENT_CONFIG_ROUTER.register('agent_configs', AgentConfigViewSet)

RUN_ROUTER = DefaultRouter()
RUN_ROUTER.register('runs', RunViewSet)

urlpatterns = []

urlpatterns += TERRAIN_ROUTER.urls
urlpatterns += SIMULATION_ROUTER.urls
urlpatterns += VIRUS_ROUTER.urls
urlpatterns += SCENARIO_ROUTER.urls
urlpatterns += AGENT_CONFIG_ROUTER.urls
urlpatterns += RUN_ROUTER.urls
