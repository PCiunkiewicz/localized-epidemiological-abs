"""Tools for managing execution of the simulation."""

import json
from abc import ABC, abstractmethod
from multiprocessing import Queue
from multiprocessing.synchronize import Event
from pathlib import Path
from warnings import deprecated

import numpy as np

from simulation.agent import BaseAgent
from simulation.scenario import BaseScenario
from utilities.types.agent import AgentSpec
from utilities.types.scenario import ScenarioSpec


class BaseModel(ABC):
    """Base Model class for simulation.

    Attributes:
        trivial: Flag to indicate if the model is trivial.
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
        self.trivial = False

        cfg = json.loads(config.read_text())  # TODO: use a dataclass
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
        return np.array(ret)

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


@deprecated('Use parallel launchers and dask instead.')
def simulate_model(model_cls: type[BaseModel], config: Path, queue: Queue, event: Event, fast: bool = True) -> None:
    """Run SIR Model simulation.

    Simulation handlers are best handled by functions due to
    the way that objects are passed between processes when
    using multiprocessing.
    """
    model = model_cls(config)
    model.simulate_fast(queue, event) if fast else model.simulate(queue, event)
