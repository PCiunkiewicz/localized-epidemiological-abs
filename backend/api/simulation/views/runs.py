"""Localized Epidemiological ABS API Run Views."""

import json
import shutil
from multiprocessing import Process
from typing import override

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from api.simulation.models import Run
from api.simulation.serializers import RunSerializer
from simulation.launcher import SimLauncher
from utilities import paths


class RunViewSet(viewsets.ModelViewSet):
    """API Viewset for Run model."""

    queryset = Run.objects.all()
    serializer_class = RunSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = []  # disables authentication
    permission_classes: list = []  # disables permission

    @override
    def create(self, request: Request) -> Response:
        serializer = RunSerializer(data=request.data)
        if serializer.is_valid():
            run: Run = serializer.save()
            run.save_dir = paths.OUTPUTS / f'{run.id:03}-{run.name}'
            run.logfile = paths.LOGS / f'{run.id:03}-{run.name}.log'
            run.config = paths.CFG / f'{run.id:03}-{run.name}.json'
            run.save()

            run.config.write_text(json.dumps(serializer.data, indent=2))

            launcher = SimLauncher(run)
            Process(target=launcher.start, daemon=True).start()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @override
    def partial_update(self, request: Request, pk: int) -> Response:
        try:
            run = Run.objects.get(id=pk)
        except Run.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name', run.name)
        response = super().partial_update(request, pk=pk)

        if name != run.name:
            new_paths = {
                'save_dir': str(paths.OUTPUTS / f'{run.id:03}-{name}'),
                'logfile': str(paths.LOGS / f'{run.id:03}-{name}.log'),
                'config': str(paths.CFG / f'{run.id:03}-{name}.json'),
            }

            for key, new_path in new_paths.items():
                request.data[key] = new_path
                shutil.move(getattr(run, key), new_path)
            response = super().partial_update(request, pk=pk)

        return response
