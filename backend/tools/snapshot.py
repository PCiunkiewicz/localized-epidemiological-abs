"""
The `snapshot` module contains code exporting
simulation snapshots as image files.
"""

import h5py
import matplotlib.pyplot as plt
from matplotlib import image
from simulation.scenario import VIRUS_SCALE
from simulation.types.agent import Status
from tools.utils import STATUS_COLOR, reshape, str_date


class SnapshotSim:
    """
    Base Model class for rendering frame snapshots
    from completed simulations.
    """

    def __init__(self, simfile, mapfile):
        self.img = image.imread(mapfile)

        with h5py.File(simfile, 'r') as file:
            self.agents = file['agents'].__array__()
            self.virus = file['virus'].__array__()
            self.timesteps = file['timesteps'].__array__()

    def export(self, i, outfile, cmap='bwr_r', label=True):
        """
        Export snapshot to output file.
        """
        _, ax = plt.subplots(figsize=[10, 10])
        ax.imshow(self.img)
        ax.imshow(self.virus[i] != 0, alpha=self.virus[i] / VIRUS_SCALE, cmap=cmap)
        ax.text(1, 2, str_date(self.timesteps[i]), c='w', fontsize=14)

        plot_ref = []
        for status in Status:
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
