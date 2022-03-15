"""
The `scenario` module contains code for defining the
simulation scenario. The base class `Scenario` should
be subclassed when creating new scenario types for
different models.
"""

import json
import datetime as dt

import numpy as np
from scipy.ndimage import gaussian_filter
from matplotlib import image, colors

from simulation.utils import AttrDict


class Scenario:
    """Base Scenario class for simulation.
    """

    def __init__(self, config_file):
        self.ScenarioParameters = None
        self.Terrain = None
        self.dt = dt.datetime(2020, 9, 1, 7)

        self.load_config(config_file)
        self.load_map()
        self.virus = np.zeros(self.shape, np.float32)
        self.virus_total = 0

        _steps = 3 * 60 * 60 // self.ScenarioParameters.t_step
        self.decay = 0.15 ** (1 / _steps)

    def load_config(self, config_file):
        """Load config file as instance attributes.

        Parameters
        ----------
        config_file : string
            Path to scenario configuration (json).
        """
        with open(config_file) as json_file:
            cfg = json.load(json_file)

        self.__dict__.update(AttrDict(cfg))

    def load_map(self):
        """Load in mapfile and compute terrain masks.
        """
        # read image
        self.img = image.imread(self.ScenarioParameters.mapfile)
        self.shape = self.img.shape[:2]

        # remove alpha from RGBA
        if self.img.shape[-1] == 4:
            self.img = self.img[:, :, :3]

        self._mask_terrain()

    def get_idx(self, zone):
        """
        Get random (x,y) point from terrain mask.
        """
        mask = self.Terrain.Masks[zone]
        idx = np.argwhere(mask)
        rand = np.random.randint(0, idx.shape[0] - 1)
        return tuple(idx[rand])

    def _mask_terrain(self):
        """Compute boolean masks for all terrain
        types along with `VALID` mask for walkable
        and non-restricted terrain.
        """
        self.Terrain.Masks = AttrDict({})
        self.Terrain.Masks.__setattr__('VALID', np.ones(self.shape, dtype=bool))

        for name, val in self.Terrain.Types.items():
            terrain_spec = self.Terrain.Default.copy()
            terrain_spec.update(val)
            mask = self._is_color(terrain_spec['value'])
            self.Terrain.Masks.__setattr__(name, mask)

            if terrain_spec['restricted'] or not terrain_spec['walkable']:
                self.Terrain.Masks.VALID &= ~mask
            else:
                self.Terrain.Masks.VALID |= mask

    def _is_color(self, hex_value):
        """Generate pixel mask for matching hex color.
        """
        rgb = colors.to_rgb(hex_value)
        pixel_mask = np.all(np.isclose(self.img, rgb), axis=2)
        return pixel_mask


class SIRScenario(Scenario):
    """Subclassed scenario for SIR simulation.
    """

    def virus_level(self, x, y):
        """Return virus value at coordinate `(x,y)`.
        """
        return self.virus[x,y]

    def contaminate(self, x, y, concentration=2**14):
        """Set virus value at coordinate `(x,y)`.
        """
        self.virus_total += concentration - self.virus[x, y]
        self.virus[x, y] += concentration

    def ventilate(self, sigma=0.459, max_=2**14):
        """Simulates the ventilation of the map.
        """
        self.virus = gaussian_filter(self.virus, sigma=sigma)
        self.virus *= self.decay
        self.virus[self.virus > max_] = max_
