"""Localized Epidemiological ABS API Simulation Views."""

from typing import override

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from api.simulation.models import Simulation, Terrain
from api.simulation.serializers import SimulationSerializer, TerrainSerializer


class SimulationViewSet(viewsets.ModelViewSet):
    """Viewset for Simulation model."""

    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission

    @override
    def create(self, request: Request) -> Response:
        serializer = SimulationSerializer(data=request.data)
        if serializer.is_valid():
            terrain = self._validate(request.data.get('terrain', []))
            simulation = serializer.save()

            if terrain:
                for t in terrain:
                    simulation.terrain.add(t)
                simulation.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @override
    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        terrain = self._validate(request.data.get('terrain', []))
        if terrain:
            simulation = self.get_object()
            simulation.terrain.clear()

            for t in terrain:
                simulation.terrain.add(t)

        return super().partial_update(request, *args, **kwargs)

    @staticmethod
    def _validate(terrain: list[Terrain]) -> list[Terrain]:
        """Validate terrain data."""
        if not isinstance(terrain, list):
            raise ValidationError({'terrain': 'must be passed as array'})

        for i, t in enumerate(terrain):
            if isinstance(t, str | int):
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
