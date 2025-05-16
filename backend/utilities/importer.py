"""Importer tool for already created simulation run config files."""

from __future__ import annotations

import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path

from django.db import IntegrityError

from api.simulation import models
from utilities import paths
from utilities.types.config import ScenarioConfig


class ConfigImporter:
    """Importer class to handle importing simulation config files."""

    config_path: Path
    exist_ok: bool
    config: ScenarioConfig
    info: Info

    @dataclass
    class Info:
        """Messages for the Importer class."""

        summary: str = ''
        messages: list[str] = field(default_factory=list)
        warnings: list[str] = field(default_factory=list)
        traceback: list[str] = field(default_factory=list)

    def __init__(self, config_path: Path, exist_ok: bool = True) -> None:
        """Initialize the Importer with a config path."""
        self.config_path = config_path
        self.exist_ok = exist_ok

        self.config = ScenarioConfig.load(config_path, process_agents=False)
        self.info = ConfigImporter.Info()

    def import_config(self) -> models.Run:
        """Import the simulation config file."""
        self.import_new_terrains()
        self.import_new_simulation()
        self.import_new_virus()
        self.import_new_scenario()
        self.import_new_agent_config()
        return self.register_new_run()

    def import_new_terrains(self) -> None:
        """Save terrain data to the database."""
        terrains = []
        for terrain in self.config.scenario.sim.terrain:
            terrain = self._prepare(terrain, models.Terrain)
            terrains.append(self._generic_create(terrain, models.Terrain))

        self.config.scenario.sim.terrain = terrains

    def import_new_simulation(self) -> None:
        """Save simulation data to the database."""
        simulation = self._prepare(self.config.scenario.sim, models.Simulation)
        terrains = simulation.pop('terrain', [])
        self.config.scenario.sim = self._generic_create(simulation, models.Simulation)
        self.config.scenario.sim.terrain.set(terrains)

    def import_new_virus(self) -> None:
        """Save virus data to the database."""
        virus = self._prepare(self.config.scenario.virus, models.Virus)
        self.config.scenario.virus = self._generic_create(virus, models.Virus)

    def import_new_scenario(self) -> None:
        """Save scenario data to the database."""
        scenario = self._prepare(self.config.scenario, models.Scenario)
        self.config.scenario = self._generic_create(scenario, models.Scenario)

    def import_new_agent_config(self) -> None:
        """Save agent config data to the database."""
        agent_config = self._prepare(self.config.agents, models.AgentConfig)
        self.config.agents = self._generic_create(agent_config, models.AgentConfig)

    def register_new_run(self) -> models.Run:
        """Register a new run in the database."""
        run = {
            'name': self.config_path.stem,
            'status': models.Run.Status.CREATED,
            'save_dir': paths.OUTPUTS / self.config_path.stem,
            'config': self.config_path,
            'logfile': paths.LOGS / f'{self.config_path.stem}.log',
            'scenario': self.config.scenario,
            'agents': self.config.agents,
        }
        return self._generic_create(run, models.Run)

    def summarize(self) -> None:
        """Summarize the import process."""

        def _count(model: type[models.BaseModel]) -> int:
            return len([x for x in self.info.messages if model.__name__.capitalize() in x])

        self.info.summary = (
            f'Created {len(self.info.messages)} new objects with {len(self.info.warnings)} warnings:\n'
            f'  - Terrains: {_count(models.Terrain)}\n'
            f'  - Simulations: {_count(models.Simulation)}\n'
            f'  - Viruses: {_count(models.Virus)}\n'
            f'  - Scenarios: {_count(models.Scenario)}\n'
            f'  - Agent Configs: {_count(models.AgentConfig)}\n'
            f'  - Runs (Registered): {_count(models.Run)}'
        )

    def _prepare(self, data: dataclass, model: type[models.BaseModel]) -> dict:
        """Format and clean the data before saving to the database."""
        return {k: v for k, v in asdict(data).items() if model.contains_field(k)}

    def _generic_create(
        self,
        data: dict,
        model: type[models.BaseModel],
    ) -> models.BaseModel:
        """Generic helper method to create a model instance."""
        try:
            instance = model(**data)
            instance.save()
            self.info.messages.append(f'Created {model.__name__.capitalize()}(name={instance.name}, id={instance.id})')
            return instance
        except IntegrityError as e:
            if 'already exists' in str(e) and self.exist_ok:
                self.info.warnings.append(f'{model.__name__.capitalize()}(name={data.get("name")}): {e}')
                return model.objects.get(name=data.get('name'))
            self.info.summary = str(e)
            self.info.traceback = traceback.format_exc().splitlines()
            raise
        except Exception as e:
            self.info.summary = str(e)
            self.info.traceback = traceback.format_exc().splitlines()
            raise
