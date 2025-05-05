"""Tools for managing simulation scenario data and configuration."""

import datetime as dt
from abc import ABC

import numpy as np

from simulation.pathing import GraphGrid, OptimizedPathfinder
from utilities.types.scenario import ScenarioSpec

VIRUS_SCALE = 2**14


class BaseScenario(ABC):
    """Base Scenario class for simulation.

    Attributes:
        sim: Simulation object.
        virus: Virus object.
        prevention: Prevention index object.
        dt: DateTime object for simulation time.
        now: Current time in HH:MM format.
        check_schedule: Boolean to check schedule.
        graph: Optimized pathfinder object for pathfinding.
    """

    def __init__(self, spec: ScenarioSpec, load_optimized_graph: bool = True) -> None:
        """Initialize the scenario with the given specification.

        Args:
            spec: Specification object containing simulation parameters.
            load_optimized_graph: Boolean to use optimized graph for pathfinding.
        """
        self.sim = spec.sim
        self.virus = spec.virus
        self.prevention = spec.prevention
        self.dt = dt.datetime(2024, 5, 1, 7)
        self.now = self.dt.strftime('%H:%M')
        self.check_schedule = True

        if load_optimized_graph:
            self.graph = OptimizedPathfinder.load('bsf')
        else:
            self.construct_graph()

    def construct_graph(self) -> None:
        """Generate a classic graph for pathfinding."""
        valid_nodes = np.argwhere(self.sim.masks['VALID'])
        stair_nodes = np.argwhere(self.sim.masks['STAIRS'] & self.sim.masks['TRANSIT_NODES'])
        self.graph = GraphGrid(valid_nodes, r=1, spacing={2: 2})
        stairs = GraphGrid(stair_nodes, r=1, spacing={0: 2, 1: 2})
        self.graph.add_edges(stairs, transform=True)
        self.graph.build()

    def get_idx(self, zone: str) -> tuple[int, int, int]:
        """Get random `(x,y,z)` coordinate from terrain mask."""
        idx = self.sim.mask_idxs[zone]
        rand = np.random.randint(0, idx.shape[0])
        return tuple(idx[rand])

    def virus_level(self, x: int, y: int, z: int) -> float:
        """Return viral concentration value at coordinate `(x,y,z)`."""
        return self.virus.matrix[x, y, z]

    def contaminate(self, x: int, y: int, z: int, concentration: float = VIRUS_SCALE) -> None:
        """Set viral concentration at coordinate `(x,y,z)`."""
        self.virus.matrix[x, y, z] += concentration
