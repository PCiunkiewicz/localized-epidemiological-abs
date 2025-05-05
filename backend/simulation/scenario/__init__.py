"""Import entrypoint for the scenario module."""

from simulation.scenario.base import VIRUS_SCALE, BaseScenario
from simulation.scenario.sir import SIRScenario

__all__ = ['BaseScenario', 'SIRScenario', 'VIRUS_SCALE']
