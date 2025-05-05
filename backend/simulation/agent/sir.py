"""SIR agent class for simulation."""

import datetime as dt
from bisect import bisect_left
from random import random
from typing import override

from simulation.agent.base import BaseAgent
from simulation.scenario import VIRUS_SCALE, BaseScenario
from utilities.types.agent import AgentSpec, AgentStatus

SUSCEPTIBLE, INFECTED, RECOVERED, QUARANTINED, DECEASED, HOSPITALIZED, UNKNOWN = AgentStatus

EXCLUDE = (QUARANTINED, HOSPITALIZED, DECEASED)
CONTAGIOUS = (INFECTED, QUARANTINED, HOSPITALIZED)


class SIRAgent(BaseAgent):
    """Subclassed agent for SIR simulation.

    Attributes:
        spec: AgentSpec instance from simulation.types.agent module.
        prevention_index: Agent's protection from infection - vaccines and masks.
        age: Age of the agent.
        susceptibility: Susceptibility to infection.
        severity: Severity of the disease.
        long_covid: Whether the agent has long COVID.
        infected: Whether the agent is infected.
        hospitalized: Whether the agent is hospitalized.
        deceased: Whether the agent is deceased.
    """

    dist = {
        'severe': (2.624, 0.170),
        'mild': (2.049, 0.246),
        'presymptomatic': (1.63, 0.50),
    }

    @override
    def __init__(self, scenario: BaseScenario, spec: AgentSpec) -> None:
        super().__init__(scenario, spec)
        self.prevention_index = self._prevention_index()
        self.age, self.susceptibility, self.severity = self._age_effect()
        self.long_covid = False
        self.infected = False
        self.hospitalized = False
        self.deceased = False

    def _age_effect(self) -> tuple[int, float, float]:
        """Generates the age of the agent and its effect on susceptibility and severity."""
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

    def recover(self) -> None:
        """Simulates the possibility of a Agent recovering from infection."""
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
        """Calculates Agent's protection from infection - vaccines and masks."""
        vax_index = self.scenario.prevention.vax[self.info.vax_type][self.info.vax_doses]
        mask_index = self.scenario.prevention.mask[self.info.mask_type]

        prevention_index = vax_index + ((1 - vax_index) * mask_index)
        return prevention_index

    def infect(self) -> None:
        """Set agent status to infected."""
        if random() > self.prevention_index:
            self.state.status = INFECTED
            self.infected = True
        else:
            return

    def _droplet_expose(self, virus_level: int) -> None:
        """Simulates infection due to residue disease in the air."""
        atk = self.scenario.virus.attack_rate
        v_scale = virus_level / VIRUS_SCALE
        t_scale = self.scenario.sim.t_step / 3600  # per hour
        if random() < (atk * v_scale * t_scale * self.susceptibility):
            self.infect()

    def _droplet_spread(self) -> None:
        """Causes the area currently occupied by the Agent to be at risk of disease."""
        viral_load = VIRUS_SCALE * (1 - self.prevention_index)
        self.scenario.contaminate(*self.state.pos, viral_load)

    @override
    def move(self) -> None:
        """Movement decision making for the Agent."""
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

        if self.is_(SUSCEPTIBLE):
            if (virus_level := self.scenario.virus_level(*self.state.pos)) > 1:
                self._droplet_expose(virus_level)
        elif self.state.status in CONTAGIOUS:
            self._droplet_spread()
