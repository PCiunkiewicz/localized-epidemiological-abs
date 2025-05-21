"""Scenario dataclasses used throughout the simulation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import override

import dacite
import numpy as np
from matplotlib import image

from utilities.scenario import mask_color


@dataclass
class VirusInfo:
    """Virus epidemiological information.

    Attributes:
        name: Name of the virus.
        attack_rate: Attack rate of the virus.
        infection_rate: Infection rate of the virus.
        matrix: Matrix representing the virus spread.
        decay_factor: Decay factor for the virus.
    """

    name: str
    attack_rate: float
    infection_rate: float
    matrix: np.ndarray | None
    decay_factor: float | None


@dataclass
class Terrain:
    """Simulation terrain / surface information.

    Attributes:
        name: Name of the terrain.
        value: Code for the terrain.
        color: Color representation of the terrain.
        material: Material type of the terrain.
        walkable: Whether the terrain is walkable.
        interactive: Whether the terrain is interactive.
        restricted: Whether the terrain is restricted.
        access_level: Access level for the terrain.
    """

    name: str
    value: str
    color: str
    material: str | None = None
    walkable: bool = True
    interactive: bool = False
    restricted: bool = False
    access_level: int = 0


@dataclass
class SimSetup:
    """Simulation setup information.

    Attributes:
        name: Name of the simulation.
        mapfile: Path to the map file or directory.
        shape: Shape of the simulation area.
        xy_scale: Scale of the simulation area.
        terrain: List of terrain objects.
        t_step: Time step for the simulation in seconds.
        save_resolution: Resolution for saving simulation data.
        save_verbose: Whether to save verbose simulation data.
        max_iter: Maximum number of iterations for the simulation.
        masks: Dictionary of masks for different terrains.
    """

    name: str
    mapfile: str
    shape: tuple[int] | None
    xy_scale: float
    terrain: list[Terrain]
    t_step: int = 5
    save_resolution: int = 60
    save_verbose: bool = False
    max_iter: int = 2500
    masks: dict[str, np.typing.NDArray[np.bool_]] = field(default_factory=dict)

    @override
    def __post_init__(self) -> None:
        img = self._load_mapfile()
        self._mask_terrains(img)

        self.mask_idxs = {k: np.argwhere(v) for k, v in self.masks.items()}

    def _load_mapfile(self) -> np.typing.NDArray:
        """Load the map file and optional transit nodes."""
        map_path = Path(self.mapfile).resolve()
        if map_path.is_file():
            img = image.imread(map_path)[:, :, :3]
            img = np.expand_dims(img, axis=2)
        elif map_path.is_dir():
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
        else:
            raise FileNotFoundError(f'Map file {self.mapfile} not found.')

        self.shape = img.shape[:-1]
        return img

    def _mask_terrains(self, img: np.typing.NDArray) -> None:
        """Generate and apply terrain masks."""
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


@dataclass
class PreventionIndex:
    """Prevention index / intervention measures information.

    Attributes:
        name: Name of the prevention index.
        vax: Dictionary of vaccination measures.
        mask: Dictionary of mask measures.
    """

    name: str
    vax: dict[str, list[float]]
    mask: dict[str, float]

    @classmethod
    def from_dict(cls, data: dict) -> 'ScenarioSpec':
        """Create a ScenarioSpec instance from a dictionary."""
        return dacite.from_dict(data_class=cls, data=data)


@dataclass
class ScenarioSpec:
    """Full simulation scenario specification.

    Attributes:
        name: Name of the scenario.
        sim: Simulation setup information.
        virus: Virus epidemiological information.
        prevention: Prevention index / intervention measures information.
    """

    name: str
    sim: SimSetup
    virus: VirusInfo
    prevention: PreventionIndex

    @override
    def __post_init__(self) -> None:
        _steps = 3 * 60 * 60 // self.sim.t_step
        self.virus.decay_factor = 0.15 ** (1 / _steps)
        self.virus.matrix = np.zeros(self.sim.shape, np.float32)

    @classmethod
    def from_dict(cls, data: dict) -> 'ScenarioSpec':
        """Create a ScenarioSpec instance from a dictionary."""
        return dacite.from_dict(data_class=cls, data=data)
