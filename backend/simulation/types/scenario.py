"""
The `types` module contains dataclasses used for
various classes throughout the simulation. Explicit
typing is supported.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from dacite import from_dict
from matplotlib import image
from simulation.utils import mask_color


@dataclass
class VirusInfo:
    attack_rate: float
    infection_rate: float
    matrix: Optional[np.ndarray]
    decay_factor: Optional[float]


@dataclass
class Terrain:
    name: str
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
    terrain: list[Terrain]
    t_step: int = 5
    save_resolution: int = 60
    save_verbose: bool = False
    max_iter: int = 2500
    masks: dict[str, np.ndarray] = field(default_factory=dict)

    def __post_init__(self):
        map_path = Path(self.mapfile).resolve()
        if map_path.is_file():
            img = image.imread(map_path)[:, :, :3]
            img = np.expand_dims(img, axis=2)
        else:
            img = []
            transit_nodes = []
            for file in sorted(map_path.iterdir()):
                if file.suffix == '.png':
                    if '.nodes' not in file.suffixes:
                        img.append(image.imread(file)[:, :, :3])
                    else:
                        transit_nodes.append(image.imread(file)[:, :, :3])
            img = np.stack(img, axis=2)
            if transit_nodes:
                transit_nodes = np.stack(transit_nodes, axis=2)
                self.masks['TRANSIT_NODES'] = mask_color(transit_nodes, '#00ffff')

        self.shape = img.shape[:-1]
        self.masks['VALID'] = np.ones(self.shape, dtype=bool)
        self.masks['BARRIER'] = np.zeros(self.shape, dtype=bool)

        for terrain in self.terrain:
            if terrain.name[-1].isdigit():
                floor = int(terrain.name[-3])
                mask = np.zeros(self.shape, dtype=bool)
                mask[:, :, floor] = mask_color(img[:, :, floor, :], terrain.value)
            else:
                mask = mask_color(img, terrain.value)
            self.masks[terrain.name] = mask

            if terrain.restricted or not terrain.walkable:
                self.masks['VALID'] &= ~mask
            else:
                self.masks['VALID'] |= mask

            if terrain.name in ['WALL', 'DOOR', 'STAIRS', 'EXIT']:
                self.masks['BARRIER'] |= mask

        self.mask_idxs = {k: np.argwhere(v) for k, v in self.masks.items()}


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
