"""SIR scenario simulation class."""

import numpy as np
from scipy.ndimage import gaussian_filter

from simulation.scenario.base import VIRUS_SCALE, BaseScenario


class SIRScenario(BaseScenario):
    """Subclassed scenario for SIR simulation."""

    def ventilate(self, sigma: float = 0.459, max_: float = VIRUS_SCALE) -> None:
        """Simulate the ventilation of the map.

        Args:
            sigma: Standard deviation for Gaussian kernel.
            max_: Maximum virus concentration.
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

    def sanitize(self) -> None:
        """Simulate the sanitization of the map."""
        self.virus.matrix[:] = 0
