"""
Localized Epidemiological ABS API Run Views
"""

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

    def create(self, request):
        serializer = RunSerializer(data=request.data)
        if serializer.is_valid():
            run = serializer.save()
            run.save_dir = settings.OUTPUT_DIR / f'{run.id}-{run.name}'
            run.save()# TODO: mkdir and validate
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
