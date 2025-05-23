"""Tools for managing execution of the simulation."""

import json
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from simulation.agent import BaseAgent
from simulation.scenario import BaseScenario
from utilities.paths import BACKEND
from utilities.types.agent import AgentSpec
from utilities.types.scenario import ScenarioSpec


class BaseModel(ABC):
    """Base Model class for simulation.

    Attributes:
        scenario: Scenario object for the simulation.
        sim: Simulation object for the scenario.
        population: List of agents in the simulation.
    """

    population: list[BaseAgent]

    def __init__(self, config: Path, agent_cls: type[BaseAgent], scenario_cls: type[BaseScenario]) -> None:
        """Initialize the model from a configuration file.

        Args:
            config: Path to the configuration file.
            agent_cls: Class of the agent to be used in the simulation.
            scenario_cls: Class of the scenario to be used in the simulation.
        """
        try:
            cfg = json.loads(config.read_text())  # TODO: use a dataclass
        except FileNotFoundError:
            cfg = json.loads(BACKEND / config.read_text())

        self.scenario: BaseScenario = scenario_cls(ScenarioSpec.from_dict(cfg['scenario']))
        self.sim = self.scenario.sim

        self.create_agents(cfg['agents'], agent_cls)

    def create_agents(self, config: dict, agent_cls: type[BaseAgent]) -> None:
        """Instantiate agents from configuration file.

        Args:
            config: Dictionary containing agent specifications.
            agent_cls: Class of the agent to be used in the simulation.
        """
        self.population: list[BaseAgent] = []
        for _ in range(config['random_agents']):
            spec = config['default'].copy()
            spec['info']['urgency'] = np.random.uniform(0.75, 0.99)
            agent = agent_cls(self.scenario, AgentSpec.from_dict(spec))
            self.population.append(agent)

        for i in range(config['random_infected']):
            self.population[i].infect()

        for custom_agent in config['custom']:
            spec = config['default'].copy()
            for key, val in custom_agent.items():
                spec[key].update(val)
            agent = agent_cls(self.scenario, AgentSpec.from_dict(spec))
            self.population.append(agent)

    def get_agents(self) -> np.ndarray:
        """Get position and status of all agents."""
        ret = []
        for p in self.population:
            ret.append((*p.state.pos, p.state.status.value))
        return np.array(ret, dtype=np.int16)

    @abstractmethod
    def model_step(self) -> None:
        """Logic for single model timestep."""
        pass

    @abstractmethod
    def simulate(self) -> None:
        """Run the simulation for a configured number of timesteps."""
        pass

    @abstractmethod
    def simulate_fast(self) -> None:
        """Run a lightweight optimized variant of the simulation."""
        pass
