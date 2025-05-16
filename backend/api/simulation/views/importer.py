"""Importer tool for already created simulation run config files."""

from __future__ import annotations

import traceback
from dataclasses import asdict
from pathlib import Path

from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from utilities import paths
from utilities.importer import ConfigImporter


class ListConfigs(APIView):
    """API View to list all simulation config files."""

    def get(self, request: Request) -> Response:
        """Handle GET request to list all simulation config files."""
        config_paths = [str(path) for path in paths.CFG.rglob('*.json')]
        return Response(config_paths, status=status.HTTP_200_OK)


class ImportConfig(APIView):
    """API View to import a simulation config file."""

    def post(self, request: Request) -> Response:
        """Handle GET request to import a simulation config file."""
        exist_ok: bool = request.data.get('exist_ok', False)
        if config_path := request.data.get('config_path'):
            if not (config_path := Path(config_path)).exists():
                return Response({'message': f'{config_path} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': '`config_path` required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            importer = ConfigImporter(config_path, exist_ok)
            importer.import_config()
        except IntegrityError:
            return Response(asdict(importer.info), status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            traceback.print_exc()
            return Response(asdict(importer.info), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        importer.summarize()
        return Response(asdict(importer.info), status=status.HTTP_201_CREATED)
