"""
The `scenario` module contains code for defining the
simulation scenario. The base class `Scenario` should
be subclassed when creating new scenario types for
different models.
"""

import datetime as dt
from abc import ABC

import numpy as np
from scipy.ndimage import gaussian_filter
from simulation.types.scenario import ScenarioSpec

VIRUS_SCALE = 2**14


class Scenario(ABC):
    """
    Base Scenario class for simulation.
    """

    def __init__(self, spec: ScenarioSpec):
        self.sim = spec.sim
        self.virus = spec.virus
        self.prevention = spec.prevention
        self.dt = dt.datetime(2024, 5, 1, 7)

    def get_idx(self, zone: str) -> tuple:
        """
        Get random (x,y,z) point from terrain mask.
        """
        mask = self.sim.masks[zone]
        idx = np.argwhere(mask)
        rand = np.random.randint(0, idx.shape[0])
        return tuple(idx[rand])

    def virus_level(self, x: int, y: int, z: int) -> float:
        """
        Return virus value at coordinate `(x,y,z)`.
        """
        return self.virus.matrix[x, y, z]

    def contaminate(self, x: int, y: int, z: int, concentration: float = VIRUS_SCALE):
        """
        Set virus value at coordinate `(x,y,z)`.
        """
        self.virus.matrix[x, y, z] += concentration


class SIRScenario(Scenario):
    """
    Subclassed scenario for SIR simulation.
    """

    def ventilate(self, sigma: float = 0.459, max_: float = VIRUS_SCALE):
        """
        Simulates the ventilation of the map.
        """
        self.virus.matrix = gaussian_filter(self.virus.matrix, sigma=(sigma, sigma, 0))
        self.virus.matrix *= self.virus.decay_factor
        self.virus.matrix[self.virus.matrix > max_] = max_
