"""Tools for  exporting simulation snapshots as image files."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tables as tb
from matplotlib import image

from simulation.scenario import VIRUS_SCALE
from utilities.tools import STATUS_COLOR, reshape, str_date
from utilities.types.agent import AgentStatus


class SimSnapshot:
    """Base Model class for rendering frame snapshots from simulations.

    Attributes:
        img: Loaded mapfile image.
        agents: Array of agent positions and statuses.
        virus: Array of virus data for each floor.
        timesteps: Array of simulation timesteps.
    """

    img: np.typing.NDArray
    agents: np.typing.NDArray
    virus: np.typing.NDArray
    timesteps: np.typing.NDArray

    def __init__(self, results: Path, mapfile: Path) -> None:
        """Initialize the snapshot with simulation and map files.

        Args:
            results: Path to the simulation output .h5 file.
            mapfile: Path to the map image or directory containing map images.
        """
        self.img = image.imread(mapfile)

        with tb.open_file(results, mode='r') as file:
            self.agents = file.root.agents.read()
            self.timesteps = file.root.timesteps.read()
            try:
                self.virus = file.root.virus.read()
            except tb.NoSuchNodeError:
                self.virus = np.zeros((*self.imgs[0].shape[:2], len(self.imgs)))

    def export(self, i: int, outfile: Path, cmap: str = 'bwr_r', label: bool = True) -> None:
        """Export snapshot to output file.

        Args:
            i: Index of the snapshot frame to export.
            outfile: Path to the output file.
            cmap: Colormap for the virus overlay.
                https://matplotlib.org/stable/users/explain/colors/colormaps.html
            label: Whether to label agents with their IDs.
        """
        _, ax = plt.subplots(figsize=[10, 10])
        ax.imshow(self.img)
        ax.imshow(self.virus[i] != 0, alpha=self.virus[i] / VIRUS_SCALE, cmap=cmap)
        ax.text(1, 2, str_date(self.timesteps[i]), c='w', fontsize=14)

        plot_ref = []
        for status in AgentStatus:
            ref = ax.plot(
                *reshape(self.agents[i], status.value),
                'o',
                ms=16,
                c=STATUS_COLOR[status.name],
                mec='black',
                label=status.name,
            )
            plot_ref.append(ref[0])

        if label:
            for n in range(self.agents[i].shape[0]):
                x, y, _ = self.agents[i][n]
                ax.annotate(
                    n + 1,
                    (y, x),
                    va='center',
                    ha='center',
                )

        ax.set(xticks=[], yticks=[])
        plt.savefig(outfile, dpi=300, bbox_inches='tight')
