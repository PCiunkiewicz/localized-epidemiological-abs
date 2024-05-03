"""
The `animation` module contains code exporting
simulation animations as gif files.
"""

from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, image
from matplotlib.colors import ListedColormap
from simulation.scenario import VIRUS_SCALE
from simulation.types.agent import Status
from tools.utils import STATUS_COLOR, reshape, str_date


class AnimateSim:
    """
    Base Model class for animating completed simulations.
    """

    def __init__(self, simfile, mapfile, floor=0):
        if Path(mapfile).is_dir():
            mapfile = f'{mapfile}/{floor}.png'

        self.img = image.imread(mapfile)
        self.exits = np.all(np.isclose(self.img, (1, 1, 0, 1)), axis=2)
        self.floor = floor

        with h5py.File(simfile, 'r') as file:
            self.agents = file['agents'].__array__()
            self.virus = file['virus'].__array__()[:, :, :, floor]
            self.timesteps = file['timesteps'].__array__()

        self.im, self.tx, self.plot_ref, self.labels = self.draw_frame(0)

    def draw_frame(self, i):
        """
        Draw initial or arbitrary frame from simulation results.
        """
        _, ax = plt.subplots(figsize=[12, 12])
        ax.imshow(self.img)
        im = ax.imshow(
            self.virus[i] != 0,
            alpha=self.virus[i] / VIRUS_SCALE,
            cmap=ListedColormap(['white', 'red'], N=2),
            vmin=0,
            vmax=1,
        )
        tx = ax.text(
            x=0.03,
            y=0.05,
            s=str_date(self.timesteps[i]),
            c='black',
            fontsize=10,
            horizontalalignment='left',
            verticalalignment='bottom',
            transform=ax.transAxes,
        )

        plot_ref = []
        for status in Status:
            ref = ax.plot(
                *reshape(self.agents[i], status.value, self.floor),
                'o',
                ms=12,
                c=STATUS_COLOR[status.name],
                mec='black',
                label=status.name,
            )
            plot_ref.append(ref[0])

        labels = []
        for agent in range(self.agents.shape[1]):
            labels.append(
                ax.text(
                    *self.agents[i, agent][:2][::-1],
                    agent,
                    fontsize=8,
                    c='black',
                    horizontalalignment='center',
                    verticalalignment='center',
                )
            )

        return im, tx, plot_ref, labels

    def animate(self, i):
        """
        Progress the simulation animation.
        Use with matplotlib `animation.FuncAnimation`.
        """
        self.im.set_data(self.virus[i] != 0)
        self.im.set_alpha(self.virus[i] / VIRUS_SCALE)
        info = [str_date(self.timesteps[i])]
        for status, ref in zip(Status, self.plot_ref):
            agents = reshape(self.agents[i], status.value, self.floor)
            info.append(f'{status.name}: {agents.shape[1]}')
            if agents.size > 0:
                exit = self.exits[agents[1], agents[0]]
                ref.set_data(*agents[:, ~exit])
            else:
                ref.set_data([], [])

        for (x, y, z, *_), label in zip(self.agents[i], self.labels):
            if not self.exits[x, y] and z == self.floor:
                label.set_visible(True)
                label.set_position((y, x))
            else:
                label.set_visible(False)

        self.tx.set_text('\n'.join(info))
        return (self.im,) + tuple(self.plot_ref)

    def export(self, outfile):
        """
        Export animation to output file.
        """
        anim = animation.FuncAnimation(
            plt.gcf(),
            self.animate,
            frames=self.timesteps.size,
            interval=50,
            blit=True,
        )

        # writer = FasterFFMpegWriter(fps=30, metadata=dict(artist='Me'), bitrate=1800)
        writer = animation.PillowWriter(
            fps=20,
            metadata=dict(artist='Me'),
            bitrate=1800,
        )
        anim.save(outfile, writer=writer)
        print(f'Animation saved to {outfile}')
