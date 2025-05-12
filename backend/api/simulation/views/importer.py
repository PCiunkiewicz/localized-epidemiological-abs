"""Importer tool for already created simulation run config files."""

import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.simulation import models
from utilities.paths import CFG
from utilities.types.config import ScenarioConfig

Errors = Literal['raise', 'ignore', 'warn', 'coerce']


@dataclass
class ImporterInfo:
    """Messages for the Importer class."""

    summary: str = ''
    messages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    traceback: list[str] = field(default_factory=list)


class ListConfigs(APIView):
    """API View to list all simulation config files."""

    def get(self, request: Request) -> Response:
        """Handle GET request to list all simulation config files."""
        paths = [str(path) for path in CFG.rglob('*.json')]
        return Response(paths, status=status.HTTP_200_OK)


class ImportConfig(APIView):
    """API View to import a simulation config file."""

    def post(self, request: Request) -> Response:
        """Handle GET request to import a simulation config file."""
        if config_path := request.data.get('config_path'):
            if not (config_path := Path(config_path)).exists():
                return Response({'message': f'{config_path} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': '`config_path` required.'}, status=status.HTTP_400_BAD_REQUEST)

        info = ImporterInfo()
        exist_ok: bool = request.data.get('exist_ok', False)
        config = ScenarioConfig.load(config_path, process_agents=False)

        try:
            self.import_new_terrains(config, info, exist_ok)
            self.import_new_simulation(config, info, exist_ok)
            self.import_new_virus(config, info, exist_ok)
            self.import_new_scenario(config, info, exist_ok)
            self.import_new_agent_config(config, info, exist_ok)
        except IntegrityError:
            return Response(asdict(info), status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            traceback.print_exc()
            return Response(asdict(info), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        self._summarize(info)
        return Response(asdict(info), status=status.HTTP_201_CREATED)

    def import_new_terrains(self, config: ScenarioConfig, info: ImporterInfo, exist_ok: bool) -> None:
        """Save terrain data to the database."""
        terrains = []
        for terrain in config.scenario.sim.terrain:
            terrain = self._prepare(terrain, models.Terrain)
            terrains.append(self._generic_create(models.Terrain, terrain, info, exist_ok))

        config.scenario.sim.terrain = terrains

    def import_new_simulation(self, config: ScenarioConfig, info: ImporterInfo, exist_ok: bool) -> None:
        """Save simulation data to the database."""
        simulation = self._prepare(config.scenario.sim, models.Simulation)
        terrains = simulation.pop('terrain', [])
        config.scenario.sim = self._generic_create(models.Simulation, simulation, info, exist_ok)
        config.scenario.sim.terrain.set(terrains)

    def import_new_virus(self, config: ScenarioConfig, info: ImporterInfo, exist_ok: bool) -> None:
        """Save virus data to the database."""
        virus = self._prepare(config.scenario.virus, models.Virus)
        config.scenario.virus = self._generic_create(models.Virus, virus, info, exist_ok)

    def import_new_scenario(self, config: ScenarioConfig, info: ImporterInfo, exist_ok: bool) -> None:
        """Save scenario data to the database."""
        scenario = self._prepare(config.scenario, models.Scenario)
        self._generic_create(models.Scenario, scenario, info, exist_ok)

    def import_new_agent_config(self, config: ScenarioConfig, info: ImporterInfo, exist_ok: bool) -> None:
        """Save agent config data to the database."""
        agent_config = self._prepare(config.agents, models.AgentConfig)
        self._generic_create(models.AgentConfig, agent_config, info, exist_ok)

    def _generic_create(
        self,
        model: type[models.BaseModel],
        data: dict,
        info: ImporterInfo,
        exist_ok: bool,
    ) -> models.BaseModel:
        """Generic helper method to create a model instance."""
        try:
            instance = model(**data)
            instance.save()
            info.messages.append(f'Created {model.__name__.capitalize()}(name={instance.name})')
            return instance
        except IntegrityError as e:
            if 'already exists' in str(e) and exist_ok:
                info.warnings.append(f'{model.__name__.capitalize()}(name={data.get("name")}): {e}')
                return model.objects.get(name=data.get('name'))
            info.summary = str(e)
            info.traceback = traceback.format_exc().splitlines()
            raise
        except Exception as e:
            info.summary = str(e)
            info.traceback = traceback.format_exc().splitlines()
            raise

    def _summarize(self, info: ImporterInfo) -> None:
        """Summarize the import process."""

        def _count(model: type[models.BaseModel]) -> int:
            return len([x for x in info.messages if model.__name__.capitalize() in x])

        info.summary = (
            f'Created {len(info.messages)} new objects with {len(info.warnings)} warnings:\n'
            f'  - Terrains: {_count(models.Terrain)}\n'
            f'  - Simulations: {_count(models.Simulation)}\n'
            f'  - Viruses: {_count(models.Virus)}\n'
            f'  - Scenarios: {_count(models.Scenario)}\n'
            f'  - Agent Configs: {_count(models.AgentConfig)}'
        )

    def _prepare(self, data: dataclass, model: type[models.BaseModel]) -> dict:
        """Format and clean the data before saving to the database."""
        return {k: v for k, v in asdict(data).items() if model.contains_field(k)}
