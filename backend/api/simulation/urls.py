"""Register all API endpoint urls."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from api.simulation import views

router = DefaultRouter()
router.register('terrains', views.TerrainViewSet)
router.register('simulations', views.SimulationViewSet)
router.register('viruses', views.VirusViewSet)
router.register('scenarios', views.ScenarioViewSet)
router.register('agent_configs', views.AgentConfigViewSet)
router.register('runs', views.RunViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('importer/configs/', views.ListConfigs.as_view()),
    path('importer/import/', views.ImportConfig.as_view()),
]
