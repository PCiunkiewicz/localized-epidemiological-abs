"""
The `agent` module contains code for defining simulation
agents. the base class `Agent` should be subclassed when
creating new agent types for different models.
"""

import datetime as dt
from abc import ABC, abstractmethod

import numpy as np

from pathfinding.core.grid import Grid
from pathfinding.finder.bi_a_star import BiAStarFinder
from simulation.types.agent import Status, AgentTime, AgentSpec
from simulation.scenario import VIRUS_SCALE
from simulation.scenario import Scenario


class Agent(ABC): # TODO: Set up as abstract base class
    """Base agent class for simulation.

        Attributes
        ----------
        scenario : Scenario
            Scenario instance from simulation.scenario module.
        x : integer
            The X coordinate.
        y : integer
            The Y coordinate.
        status : Status
            The infection state of the person
        access_level : int
            Not implemented.
        urgency : float
            Agent likelihood to progress to objective, domain [0, 1].
    """

    def __init__(self, scenario: Scenario, spec: AgentSpec):
        self.scenario = scenario
        self.random = np.random.RandomState()
        self.state = spec.state
        self.info = spec.info

        if self.is_('UNKNOWN'):
            if self.random.rand() < self.scenario.virus.infection_rate:
                self.status = Status.INFECTED
            else:
                self.status = Status.SUSCEPTIBLE

        self.grid = Grid(matrix=self.scenario.sim.masks['VALID'].T)
        self.finder = BiAStarFinder()

        if self.info.start_zone:
            self.pos = self.scenario.get_idx(self.info.start_zone)

    @property
    def status(self) -> Status:
        return self.state.status

    @status.setter
    def status(self, value: Status) -> None:
        self.state.status = value

    @property
    def dt(self) -> AgentTime:
        return self.state.dt

    @property
    def pos(self) -> tuple[int, int]:
        return self.state.x, self.state.y

    @pos.setter
    def pos(self, value: tuple[int, int]) -> None:
        self.state.x, self.state.y = value

    def check_schedule(self):
        """Checks whether a task is scheduled for the current time.
        """
        if self.is_('QUARANTINED') or self.is_('DECEASED'):
            return

        now = self.scenario.dt.strftime('%H:%M')
        action = self.info.schedule.get(now)
        if action and self.dt.last_action_time != now:
            self.dt.last_action_time = now
            self.set_task(action)

    def set_task(self, zone=None, wait=0):
        """Defines a new task / path for the Agent
        """
        if wait > 0:
            self.state.path = [self.pos] * wait
        elif zone is not None:
            if zone == 'WORK':
                zone = self.info.work_zone
            idx = self.scenario.get_idx(zone)
            self.pathfind(idx)
            self.state.path += [self.state.path[-1]] * (120 // self.scenario.sim.t_step) # at least 2 minutes per task

    def pathfind(self, idx):
        """
        Computes the shortest path between two points subject
        to optimization constraints in the a-star search algorithm

        Parameters
        ----------
        idx : (int, int)
            `(x,y)` coordinate tuple to path to from the current Agent position
        """
        start = self.grid.node(*self.pos)
        end = self.grid.node(*idx)

        self.grid.cleanup()
        self.state.path, _ = self.finder.find_path(start, end, self.grid)

    def in_(self, zone):
        """Check whether agent is in `zone`.
        """
        if zone == 'WORK':
            zone = self.info.work_zone
        return self.scenario.sim.masks[zone][self.pos]

    def is_(self, status):
        """Check whether agent status is `status`.
        """
        return self.status is Status[status]

    @abstractmethod
    def move(self):
        pass


class SIRAgent(Agent):
    """Subclassed agent for SIR simulation.
    """
    def __init__(self, scenario: Scenario, spec: AgentSpec):
        super().__init__(scenario, spec)
        self.prevention_index = self._prevention_index()

    def recover(self):
        """Simulates the possibility of a Agent recovering from infection
        """
        if self.contagious():
            if not self.dt.recovery:
                now = self.scenario.dt
                # days before showing symptoms
                if self.random.rand() < 0.17: # TODO: Move this to scenario config
                    n_days_q = 100 # shows asymptomatic Agents not quarantining
                else:
                    n_days_q = self.random.lognormal(1.63, 0.50)
                self.dt.quarantine = now + dt.timedelta(days=n_days_q)
                # days before recovery
                if self.random.rand() < 0.02: # TODO: Move this to scenario config
                    n_days_r = -1 # shows Agent dying - find a better way to do this
                    self.status = Status.DECEASED
                    self.set_task('EXIT')
                elif self.random.rand() < 0.16: # TODO: Move this to scenario config
                    n_days_r = self.random.lognormal(2.624, 0.170) # severe infection
                else:
                    n_days_r = self.random.lognormal(2.049, 0.246) # mild/moderate infection
                self.dt.recovery = now + dt.timedelta(days=n_days_r)
            else:
                if self.scenario.dt >= self.dt.quarantine:
                    if not self.is_('QUARANTINED'):
                        self.status = Status.QUARANTINED
                        self.set_task('EXIT')
                if self.scenario.dt >= self.dt.recovery:
                    if not self.is_('DECEASED'):
                        self.status = Status.RECOVERED

    def _prevention_index(self) -> float:
        """Calculates Agent's protection from infection - vaccines and masks
        """
        vax_index = self.scenario.prevention.vax[self.info.vax_type][self.info.vax_doses]
        mask_index = self.scenario.prevention.mask[self.info.mask_type]

        prevention_index = vax_index + ((1 - vax_index) * mask_index)
        return prevention_index

    def infect(self):
        """Set agent status to infected.
        """
        if self.random.rand() > self.prevention_index:
            self.status = Status.INFECTED
        else:
            return

    def contagious(self):
        """Check whether agent status is contagious.
        """
        return self.is_('INFECTED') or self.is_('QUARANTINED')

    def droplet_expose(self):
        """Simulates infection due to residue disease in the air
        """
        if self.is_('SUSCEPTIBLE'):
            atk = self.scenario.virus.attack_rate
            v_scale = self.scenario.virus_level(*self.pos) / VIRUS_SCALE
            t_scale = self.scenario.sim.t_step / 3600 # per hour
            if self.random.rand() < (atk * v_scale * t_scale):
                self.infect()

    def droplet_spread(self):
        """Causes the area currently occupied by the Agent to be at risk of disease
        """
        if self.contagious():
            viral_load = VIRUS_SCALE * (1 - self.prevention_index)
            self.scenario.contaminate(*self.pos, viral_load)

    def move(self, trivial=False):
        """Movement decision making for the Agent
        """
        self.recover()
        self.check_schedule()

        if self.state.path:
            self.pos = self.state.path.pop(0)
        elif self.in_('EXIT'):
            return
        elif self.in_('WORK'):
            pass
        elif self.random.rand() < 0.5:
            self.set_task('WORK')
        else:
            self.set_task(wait=60 // self.scenario.sim.t_step)

        if not trivial:
            self.droplet_expose()
            self.droplet_spread()
