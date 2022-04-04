"""
The `types` module contains dataclasses used for
various classes throughout the simulation. Explicit
typing is supported.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from dacite import from_dict
from matplotlib import image

from simulation.utils import AttrDict, mask_color


@dataclass
class VirusInfo:
    attack_rate: float
    infection_rate: float
    matrix: Optional[np.ndarray]
    decay_factor: Optional[float]


@dataclass
class Terrain:
    value: str
    color: str
    material: Optional[str]
    walkable: bool = True
    interactive: bool = False
    restricted: bool = False
    access_level: int = 0


@dataclass
class SimSetup:
    mapfile: str
    shape: Optional[tuple[int]]
    xy_scale: float
    terrain: dict[str, Terrain]
    t_step: int = 5
    save_resolution: int = 60
    save_verbose: bool = False
    max_iter: int = 2500
    masks: dict[str, np.ndarray] = field(default_factory=dict)

    def __post_init__(self):
        img = image.imread(self.mapfile)[:, :, :3]
        self.shape = img.shape[:2]

        self.masks['VALID'] = np.ones(self.shape, dtype=bool)

        for name, terrain in self.terrain.items():
            mask = mask_color(img, terrain.value)
            self.masks[name] = mask

            if terrain.restricted or not terrain.walkable:
                self.masks['VALID'] &= ~mask
            else:
                self.masks['VALID'] |= mask


@dataclass
class PreventionIndex:
    vax: dict[str, list[float]]
    mask: dict[str, float]


@dataclass
class ScenarioSpec:
    sim: SimSetup
    virus: VirusInfo
    prevention: PreventionIndex

    def __post_init__(self):
        _steps = 3 * 60 * 60 // self.sim.t_step
        self.virus.decay_factor = 0.15 ** (1 / _steps)
        self.virus.matrix = np.zeros(self.sim.shape, np.float32)

    @classmethod
    def from_dict(cls, data: dict) -> 'ScenarioSpec':
        return from_dict(data_class=cls, data=data)
