"""
The `agent` module contains code for defining simulation
agents. the base class `Agent` should be subclassed when
creating new agent types for different models.
"""

import datetime as dt
from enum import Enum

import numpy as np

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Status(Enum):
    """ An enum that represents the infection status of the Agents.
    """
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    QUARANTINED = 4
    DECEASED = 5


class Agent:
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

    def __init__(self, scenario, agent_spec):
        self.scenario = scenario
        self.random = np.random.RandomState()
        self.__dict__.update(agent_spec)
        self.__dict__.update(scenario.ScenarioParameters)
        if self.status == 'RANDOM':
            if self.random.rand() < self.infection_rate:
                self.status = Status.INFECTED
            else:
                self.status = Status.SUSCEPTIBLE
        else:
            self.status = Status[self.status]
        self.path = []
        self.last_action_time = None
        self.dt_recovery = None
        self.dt_quarantine = None

        self.grid = Grid(matrix=self.scenario.Terrain.Masks.VALID.T)
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        if self.start_zone:
            self.x, self.y = self.scenario.get_idx(self.start_zone)

        self.z = 1

    def check_schedule(self):
        """Checks whether a task is scheduled for the current time.
        """
        if self.is_('QUARANTINED') or self.is_('DECEASED'):
            return
        now = self.scenario.dt.strftime('%H:%M')
        action = self.schedule.get(now)
        if action and self.last_action_time != now:
            self.last_action_time = now
            self.set_task(action)

    def set_task(self, zone=None, wait=0):
        """Defines a new task / path for the Agent
        """
        if wait > 0:
            self.path = [(self.x, self.y)] * wait
        elif zone is not None:
            if zone == 'WORK':
                zone = self.work_zone
            idx = self.scenario.get_idx(zone)
            self.pathfind(idx)
            self.path += [self.path[-1]] * (120 // self.t_step) # at least 2 minutes per task

    def pathfind(self, idx):
        """
        Computes the shortest path between two points subject
        to optimization constraints in the a-star search algorithm

        Parameters
        ----------
        idx : (int, int)
            `(x,y)` coordinate tuple to path to from the current Agent position
        """
        start = self.grid.node(self.x, self.y)
        end = self.grid.node(*idx)

        self.grid.cleanup()
        self.path, _ = self.finder.find_path(start, end, self.grid)

    def in_(self, zone):
        """Check whether agent is in `zone`.
        """
        if zone == 'WORK':
            zone = self.work_zone
        return self.scenario.Terrain.Masks[zone][self.x, self.y]

    def is_(self, status):
        """Check whether agent status is `status`.
        """
        return (self.status is Status[status])


class SIRAgent(Agent):
    """Subclassed agent for SIR simulation.
    """

    def recover(self):
        """Simulates the possibility of a Agent recovering from infection
        """
        if self.contagious():
            if not self.dt_recovery:
                now = self.scenario.dt
                # days before showing symptoms
                if self.random.rand() < 0.17:
                    n_days_q = 100 # shows asymptomatic Agents not quarantining
                else:
                    n_days_q = self.random.lognormal(1.63, 0.50)
                self.dt_quarantine = now + dt.timedelta(days=n_days_q)
                # days before recovery
                if self.random.rand() < self.random.uniform(0, 0.02):
                    n_days_r = -1 # shows Agent dying - find a better way to do this
                    self.status = Status.DECEASED
                    self.set_task('EXIT')
                elif self.random.rand() < self.random.uniform(0.02, 0.18):
                    n_days_r = self.random.lognormal(2.624, 0.170) # severe infection
                else:
                    n_days_r = self.random.lognormal(2.049, 0.246) # mild/moderate infection
                self.dt_recovery = now + dt.timedelta(days=n_days_r)
            else:
                if self.scenario.dt >= self.dt_quarantine:
                    if not self.is_('QUARANTINED'):
                        self.status = Status.QUARANTINED
                        self.set_task('EXIT')
                if self.scenario.dt >= self.dt_recovery:
                    if not self.is_('DECEASED'):
                        self.status = Status.RECOVERED

    def calculate_protection_index(self):
        """Calculates Agent's protection from infection - vaccines and masks
        """
        vax_index = self.prevention['vax'][self.vax_type][self.n_doses]
        mask_index = self.prevention['mask'][self.mask_type]

        protection_index = vax_index + ((1 - vax_index) * mask_index)
        return protection_index

    def infect(self):
        """Set agent status to infected.
        """
        if self.random.rand() > self.calculate_protection_index():
            self.status = Status.INFECTED
        else:
            return

    def contagious(self):
        """Check whether agent status is contagious.
        """
        return (self.is_('INFECTED') or self.is_('QUARANTINED'))

    def droplet_expose(self):
        """Simulates infection due to residue disease in the air
        """
        if self.is_('SUSCEPTIBLE'):
            atk = self.attack_rate
            v_scale = self.scenario.virus_level(self.x, self.y) / 2**14
            t_scale = self.t_step / 3600 # per hour
            if self.random.rand() < (atk * v_scale * t_scale):
                self.infect()

    def droplet_spread(self):
        """Causes the area currently occupied by the Agent to be at risk of disease
        """
        if self.contagious():
            self.scenario.contaminate(self.x, self.y)

    def move(self):
        """Movement decision making for the Agent
        """
        self.recover()
        self.check_schedule()

        if self.path:
            self.x, self.y = self.path.pop(0)
        elif self.in_('EXIT'):
            return
        elif self.in_('WORK'):
            pass
        elif self.random.rand() < 0.5:
            self.set_task('WORK')
        else:
            self.set_task(wait=60 // self.t_step)

        self.droplet_expose()
        self.droplet_spread()
