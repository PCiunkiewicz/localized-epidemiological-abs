"""Base agent class for simulation."""

from abc import ABC, abstractmethod
from collections import deque
from random import random

import numpy as np

from simulation.scenario import BaseScenario
from utilities.types.agent import AgentSpec, AgentStatus, AgentTime

# Unpacking is more efficient than attribute access
SUSCEPTIBLE, INFECTED, *_, UNKNOWN = AgentStatus


class BaseAgent(ABC):
    """Base agent class for simulation.

    Attributes:
        scenario: Scenario instance from simulation.scenario module.
        state: The infection state of the person.
        info: The agent's information.
        random: Numpy random number generator instance.
    """

    def __init__(self, scenario: BaseScenario, spec: AgentSpec) -> None:
        """Initialize the agent with a scenario and agent specification.

        Args:
            scenario: Scenario instance from simulation.scenario module.
            spec: AgentSpec instance from simulation.types.agent module.
        """
        self.scenario = scenario
        self.random = np.random.default_rng()
        self.state = spec.state
        self.info = spec.info

        if self.is_(UNKNOWN):
            if random() < self.scenario.virus.infection_rate:
                self.state.status = INFECTED
            else:
                self.state.status = SUSCEPTIBLE

        if self.info.start_zone:
            self.state.pos = self.scenario.get_idx(self.info.start_zone)

    @property
    def dt(self) -> AgentTime:
        """Get the current time step of the agent."""
        return self.state.dt

    def in_(self, zone: str) -> bool:
        """Check whether agent is in `zone`."""
        match zone:
            case 'WORK':
                zone = self.info.work_zone
            case 'HOME':
                zone = self.info.home_zone

        return self.scenario.sim.masks[zone][self.state.pos]

    def is_(self, status: AgentStatus) -> bool:
        """Check whether agent status is `status`."""
        return self.state.status is status

    def check_schedule(self) -> None:
        """Check whether a task is scheduled for the current time."""
        action = self.info.schedule.get(self.scenario.now)
        if action and self.dt.last_action_time != self.scenario.now:
            self.dt.last_action_time = self.scenario.now
            self.set_task(action)

    def set_task(self, zone: str | None = None, wait: int = 0) -> None:
        """Defines a new task / path for the Agent.

        Args:
            zone: The zone to pathfind to.
            wait: The number of time steps to wait before moving.
        """
        if wait > 0:
            self.state.path = deque([self.state.pos] * wait)
        elif zone is not None:
            match zone:
                case 'WORK':
                    zone = self.info.work_zone
                case 'HOME':
                    zone = self.info.home_zone

            idx = self.scenario.get_idx(zone)
            self.pathfind(idx)

            if zone == 'OPEN':
                wait_time = 300 // self.scenario.sim.t_step  # seconds
            else:
                wait_time = 3600 // self.scenario.sim.t_step  # seconds

            wait_time = int(wait_time * (1 + random()) * 0.5)
            self.state.path += [self.state.path[-1]] * wait_time

    def pathfind(self, idx: tuple[int, int, int]) -> None:
        """Computes the shortest path between two coordinates.

        Args:
            idx: `(x,y,z)` coordinate tuple to path to.
        """
        self.state.path = self.scenario.graph.pathfind(self.state.pos, idx)

    @abstractmethod
    def move(self) -> None:
        """Agent timestep logic."""
        pass

    @abstractmethod
    def infect(self) -> None:
        """Infect the agent."""
        pass
