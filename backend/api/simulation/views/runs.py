"""
Localized Epidemiological ABS API Run Views
"""

import json
import shutil
import subprocess

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import Run
from ..serializers import RunSerializer


class RunViewSet(viewsets.ModelViewSet):
    """
    Viewset for Run model
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes: list = [] #disables authentication
    permission_classes: list = [] #disables permission

    def create(self, request):
        serializer = RunSerializer(data=request.data)
        if serializer.is_valid():
            run = serializer.save()
            run.save_dir = settings.RUN_OUTPUT_DIR / f'{run.id:03}-{run.name}'
            run.logfile = settings.LOG_DIR / f'{run.id:03}-{run.name}.log'
            run.config = settings.RUN_CONFIG_DIR / f'{run.id:03}-{run.name}.json'
            run.save()

            with open(run.config, 'w') as file:
                json.dump(serializer.data, file, indent=2)

            launch(run)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        try:
            run = Run.objects.get(id=pk)
        except Run.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name', run.name)
        response = super().partial_update(request, pk=pk)

        if name != run.name:
            new_paths = {
                'save_dir': str(settings.RUN_OUTPUT_DIR / f'{run.id:03}-{name}'),
                'logfile': str(settings.LOG_DIR / f'{run.id:03}-{name}.log'),
                'config': str(settings.RUN_CONFIG_DIR / f'{run.id:03}-{name}.json')
            }

            for key, new_path in new_paths.items():
                request.data[key] = new_path
            response = super().partial_update(request, pk=pk)

            shutil.move(run.save_dir, new_paths['save_dir'])
            shutil.move(run.logfile, new_paths['logfile'])
            shutil.move(run.config, new_paths['config'])

        return response


def launch(run):
    """
    Execute simulation run async
    """
    method = 'run-parallel' if run.parallel else 'run-sim'

    with open(run.logfile, 'w') as logfile:
        subprocess.Popen(
            [
                'python',
                settings.BASE_DIR / 'launch.py',
                method,
                run.config,
                '-r', str(run.runs),
                '-s', run.save_dir
            ],
            stdout=logfile,
            stderr=logfile,
            cwd=settings.BASE_DIR,
            shell=False
        )

    run.status = run.Status.RUNNING
    run.save()
