"""Admin views for simulation management."""

from io import StringIO

from django.core.management import call_command
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ResetDB(APIView):
    """API View to list all simulation config files."""

    def get(self, request: Request) -> Response:
        """Handle GET request to list all simulation config files."""
        try:
            with StringIO() as buffer:
                call_command('resetdb', stdout=buffer, stderr=buffer)
                output = buffer.getvalue()
            return Response({'logs': output}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
