"""
The `agent` module contains code for defining simulation
agents. the base class `Agent` should be subclassed when
creating new agent types for different models.
"""

import datetime as dt
from abc import ABC, abstractmethod
from bisect import bisect_left
from collections import deque
from random import random

import numpy as np
from simulation.scenario import VIRUS_SCALE, Scenario
from simulation.types.agent import AgentSpec, AgentTime, Status

SUSCEPTIBLE, INFECTED, RECOVERED, QUARANTINED, DECEASED, HOSPITALIZED, UNKNOWN = Status

EXCLUDE = (QUARANTINED, HOSPITALIZED, DECEASED)
CONTAGIOUS = (INFECTED, QUARANTINED, HOSPITALIZED)


class Agent(ABC):  # TODO: Set up as abstract base class
    """
    Base agent class for simulation.

        Attributes
        ----------
        scenario : Scenario
            Scenario instance from simulation.scenario module.
        x : integer
            The X coordinate.
        y : integer
            The Y coordinate.
        z : integer
            The Z coordinate.
        status : Status
            The infection state of the person
        access_level : int
            Not implemented.
        urgency : float
            Agent likelihood to progress to objective, domain [0, 1].
    """

    def __init__(self, scenario: Scenario, spec: AgentSpec) -> None:
        self.scenario = scenario
        self.random = np.random.RandomState()
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
        return self.state.dt

    def check_schedule(self):
        """
        Checks whether a task is scheduled for the current time.
        """
        action = self.info.schedule.get(self.scenario.now)
        if action and self.dt.last_action_time != self.scenario.now:
            self.dt.last_action_time = self.scenario.now
            self.set_task(action)

    def set_task(self, zone=None, wait=0):
        """
        Defines a new task / path for the Agent
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

    def pathfind(self, idx):
        """
        Computes the shortest path between two points subject
        to optimization constraints in the a-star search algorithm

        Parameters
        ----------
        idx : (int, int, int)
            `(x,y,z)` coordinate tuple to path to from the current Agent position
        """
        self.state.path = self.scenario.graph.pathfind(self.state.pos, idx)

    def in_(self, zone):
        """
        Check whether agent is in `zone`.
        """
        match zone:
            case 'WORK':
                zone = self.info.work_zone
            case 'HOME':
                zone = self.info.home_zone

        return self.scenario.sim.masks[zone][self.state.pos]

    def is_(self, status):
        """
        Check whether agent status is `status`.
        """
        return self.state.status is status

    @abstractmethod
    def move(self):
        pass


class SIRAgent(Agent):
    """
    Subclassed agent for SIR simulation.
    """

    dist = {
        'severe': (2.624, 0.170),
        'mild': (2.049, 0.246),
        'presymptomatic': (1.63, 0.50),
    }

    def __init__(self, scenario: Scenario, spec: AgentSpec):
        super().__init__(scenario, spec)
        self.prevention_index = self._prevention_index()
        self.age, self.susceptibility, self.severity = self._age_effect()
        self.long_covid = False
        self.infected = False
        self.hospitalized = False
        self.deceased = False

    def _age_effect(self):
        age = int(self.random.normal(41, 15))
        age = min((max((age, 18)), 85))

        age_bins = (19, 29, 39, 49, 59, 69)
        age_idx = bisect_left(age_bins, age)
        susceptibilities = (
            (0.38, 0.06),
            (0.79, 0.09),
            (0.87, 0.08),
            (0.80, 0.09),
            (0.82, 0.09),
            (0.89, 0.09),
            (0.74, 0.09),
        )
        clinical_fractions = (
            (0.20, 0.05),
            (0.26, 0.05),
            (0.33, 0.05),
            (0.40, 0.06),
            (0.49, 0.06),
            (0.63, 0.07),
            (0.69, 0.06),
        )

        susceptibility = self.random.normal(*susceptibilities[age_idx])
        susceptibility = min((max((susceptibility, 0)), 1))
        severity = self.random.normal(*clinical_fractions[age_idx])
        severity = min((max((severity, 0)), 1))

        return age, susceptibility, severity

    def recover(self):
        """
        Simulates the possibility of a Agent recovering from infection
        """
        if not self.dt.recovery:
            now = self.scenario.dt
            # days before showing symptoms
            if random() < 0.17:  # TODO: Move this to scenario config
                n_days_q = 100  # shows asymptomatic Agents not quarantining
            else:
                n_days_q = self.random.lognormal(*self.dist['presymptomatic'])
            # days before recovery
            if random() < 0.02:  # TODO: Move this to scenario config
                n_days_r = -1  # shows Agent dying - find a better way to do this
                n_days_q = self.random.lognormal(*self.dist['presymptomatic'])
                self.deceased = True
            elif random() < 0.30 * self.severity:  # TODO: Move this to scenario config
                n_days_r = self.random.lognormal(*self.dist['severe'])  # severe infection
                n_days_q = self.random.lognormal(*self.dist['presymptomatic'])
                self.hospitalized = True
            else:
                n_days_r = self.random.lognormal(*self.dist['mild'])  # mild/moderate infection
            if random() < 0.16:  # TODO: Move this to scenario config
                n_days_r *= 3  # long-covid
                self.long_covid = True
            self.dt.recovery = now + dt.timedelta(days=n_days_r)
            self.dt.quarantine = now + dt.timedelta(days=n_days_q)
        else:
            if self.scenario.dt >= self.dt.quarantine:
                if self.hospitalized:
                    self.state.status = HOSPITALIZED
                    self.set_task('EXIT')
                elif self.deceased:
                    self.state.status = DECEASED
                    self.set_task('EXIT')
                elif not self.is_(QUARANTINED):
                    self.state.status = QUARANTINED
                    self.set_task('HOME')
            if self.scenario.dt >= self.dt.recovery:
                if not self.deceased:
                    self.state.status = RECOVERED

    def _prevention_index(self) -> float:
        """
        Calculates Agent's protection from infection - vaccines and masks
        """
        vax_index = self.scenario.prevention.vax[self.info.vax_type][self.info.vax_doses]
        mask_index = self.scenario.prevention.mask[self.info.mask_type]

        prevention_index = vax_index + ((1 - vax_index) * mask_index)
        return prevention_index

    def infect(self):
        """
        Set agent status to infected.
        """
        if random() > self.prevention_index:
            self.state.status = INFECTED
            self.infected = True
        else:
            return

    def _droplet_expose(self, virus_level):
        """
        Simulates infection due to residue disease in the air
        """
        atk = self.scenario.virus.attack_rate
        v_scale = virus_level / VIRUS_SCALE
        t_scale = self.scenario.sim.t_step / 3600  # per hour
        if random() < (atk * v_scale * t_scale * self.susceptibility):
            self.infect()

    def _droplet_spread(self):
        """
        Causes the area currently occupied by the Agent to be at risk of disease
        """
        viral_load = VIRUS_SCALE * (1 - self.prevention_index)
        self.scenario.contaminate(*self.state.pos, viral_load)

    def move(self, trivial=False):
        """
        Movement decision making for the Agent
        """
        if self.state.status in CONTAGIOUS:
            self.recover()
        if (self.state.status not in EXCLUDE) and self.scenario.check_schedule:
            self.check_schedule()

        if self.state.path:
            self.state.pos = self.state.path.popleft()
        elif self.in_('EXIT'):
            return
        elif self.in_('HOME'):
            self.set_task(wait=300 // self.scenario.sim.t_step)
        elif random() < 0.5:
            self.set_task('OPEN')
        else:
            self.set_task(wait=300 // self.scenario.sim.t_step)

        if not trivial:
            if self.is_(SUSCEPTIBLE):
                if (virus_level := self.scenario.virus_level(*self.state.pos)) > 1:
                    self._droplet_expose(virus_level)
            elif self.state.status in CONTAGIOUS:
                self._droplet_spread()
