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
from simulation.pathing import GraphGrid, OptimizedPathfinder
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
        self.now = self.dt.strftime('%H:%M')
        self.check_schedule = True

        # valid_nodes = np.argwhere(self.sim.masks['VALID'])
        # stair_nodes = np.argwhere(self.sim.masks['STAIRS'] & self.sim.masks['TRANSIT_NODES'])
        # self.graph = GraphGrid(valid_nodes, r=1, spacing={2: 2})
        # stairs = GraphGrid(stair_nodes, r=1, spacing={0: 2, 1: 2})
        # self.graph.add_edges(stairs, transform=True)
        # self.graph.create_graph()
        self.graph = OptimizedPathfinder.load('bsf')

    def get_idx(self, zone: str) -> tuple:
        """
        Get random (x,y,z) point from terrain mask.
        """
        idx = self.sim.mask_idxs[zone]
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
        gaussian_filter(
            self.virus.matrix,
            sigma=(sigma, sigma, 0),
            mode='constant',
            truncate=2.0,
            output=self.virus.matrix,
        )
        self.virus.matrix[self.sim.masks['BARRIER']] = 0
        self.virus.matrix *= self.virus.decay_factor
        np.clip(self.virus.matrix, 0, max_, out=self.virus.matrix)
