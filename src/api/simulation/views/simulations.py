"""
Localized Epidemiological ABS API Simulation Views
"""

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..models import Simulation, Terrain
from ..serializers import SimulationSerializer, TerrainSerializer


class SimulationViewSet(viewsets.ModelViewSet):
    """
    Viewset for Simulation model
    """
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = [] #disables authentication
    permission_classes: list = [] #disables permission

    def create(self, request):
        serializer = SimulationSerializer(data=request.data)
        if serializer.is_valid():
            terrain = _validate(request.data.get('terrain', []))
            simulation = serializer.save()

            if terrain:
                for t in terrain:
                    simulation.terrain.add(t)
                simulation.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        terrain = _validate(request.data.get('terrain', []))
        if terrain:
            simulation = self.get_object()
            simulation.terrain.clear()

            for t in terrain:
                simulation.terrain.add(t)

        return super().partial_update(request, *args, **kwargs)


def _validate(terrain):
    if not isinstance(terrain, list):
        raise ValidationError({'terrain': 'must be passed as array'})

    for i, t in enumerate(terrain):
        if isinstance(t, (str, int)):
            try:
                Terrain.objects.get(id=t)
            except Terrain.DoesNotExist:
                raise ValidationError({'terrain': f'id `{t}` does not exist'})
        elif isinstance(t, dict):
            try:
                terrain[i] = Terrain.objects.get(name=t['name']).id
            except (Terrain.DoesNotExist, KeyError):
                serializer = TerrainSerializer(data=t)
                if serializer.is_valid():
                    t = serializer.save()
                    terrain[i] = t.id
                else:
                    raise ValidationError({'terrain': serializer.errors})
        else:
            raise ValidationError({'terrain': 'must provide valid terrain id or data', 'invalid': t})

    return terrain
