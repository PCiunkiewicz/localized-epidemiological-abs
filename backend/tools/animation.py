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
from tools.utils import STATUS_COLOR, change_directory, reshape, str_date, update_html_controls
from tqdm import tqdm

plt.rcParams['animation.frame_format'] = 'svg'


class AnimateSim:
    """
    Base Model class for animating completed simulations.
    """

    def __init__(self, simfile, mapfile, floor=0):
        self.imgs = []
        if (mapfile := Path(mapfile)).is_dir():
            for file in sorted(mapfile.iterdir()):
                if file.suffix == '.png':
                    self.imgs.append(image.imread(file))
        else:
            self.imgs.append(image.imread(mapfile))
        self.exits = [np.all(np.isclose(img, (1, 1, 0, 1)), axis=2) for img in self.imgs]
        self.floor = floor

        with h5py.File(simfile, 'r') as file:
            self.agents = file['agents'].__array__()
            self.timesteps = file['timesteps'].__array__()
            try:
                self.virus = file['virus'].__array__()
            except KeyError:
                self.virus = np.zeros((*self.imgs[0].shape[:2], len(self.imgs)))

        self.fig, self.axes = plt.subplots(
            nrows=len(self.imgs),
            figsize=[12, 6 * len(self.imgs)],
            sharex=True,
        )
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=0.95)

        self.im, self.tx, self.plot_ref, self.labels = [], [], [], []
        for floor in range(len(self.axes)):
            im, tx, plot_ref, labels = self.draw_frame(floor, 0)
            self.im.append(im)
            self.tx.append(tx)
            self.plot_ref.append(plot_ref)
            self.labels.append(labels)

        self.pbar = None

    def draw_frame(self, floor, i):
        """
        Draw initial or arbitrary frame from simulation results.
        """
        ax = self.axes[floor]
        ax.set(title=f'Floor {floor}', xticks=[], yticks=[])
        ax.grid(False)

        ax.imshow(self.imgs[floor])
        im = ax.imshow(
            self.virus[i, :, :, floor] != 0,
            alpha=(self.virus[i, :, :, floor] / VIRUS_SCALE) ** 0.25,
            cmap=ListedColormap(['white', 'red'], N=2),
            vmin=0,
            vmax=1,
        )
        tx = ax.text(
            x=0.03,
            y=0.05,
            s=str_date(self.timesteps[i]),
            c='black',
            fontsize=8,
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
                    fontsize=6,
                    c='black',
                    horizontalalignment='center',
                    verticalalignment='center',
                    visible=False,
                )
            )

        return im, tx, plot_ref, labels

    def update_floor(self, floor, i):
        """
        Update the floor of the simulation.
        """
        self.im[floor].set_data(self.virus[i, :, :, floor] != 0)
        self.im[floor].set_alpha((self.virus[i, :, :, floor] / VIRUS_SCALE) ** 0.35)
        info = [str_date(self.timesteps[i])]
        for status, ref in zip(Status, self.plot_ref[floor]):
            agents = reshape(self.agents[i], status.value, floor)
            info.append(f'{status.name}: {agents.shape[1]}')
            if agents.size > 0:
                exit = self.exits[floor][agents[1], agents[0]]
                ref.set_data(*agents[:, ~exit])
            else:
                ref.set_data([], [])

        for (x, y, z, *_), label in zip(self.agents[i], self.labels[floor]):
            if z == floor:
                if not self.exits[z][x, y]:
                    label.set_visible(True)
                    label.set_position((y, x))
            else:
                label.set_visible(False)

        self.tx[floor].set_text('\n'.join(info))

    def animate(self, i):
        """
        Progress the simulation animation.
        Use with matplotlib `animation.FuncAnimation`.
        """
        self.pbar.update(1)

        artists = [*self.im, *self.tx]
        for floor in range(len(self.axes)):
            self.update_floor(floor, i)
            artists += self.plot_ref[floor] + self.labels[floor]
        return tuple(artists)

    def export(self, outfile, html=False):
        """
        Export animation to output file.
        """
        self.pbar = tqdm(total=self.timesteps.size, desc='Animating', unit='frames')

        anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            frames=self.timesteps.size,
            interval=50,
            blit=True,
        )

        if html:
            writer = animation.HTMLWriter(fps=20, metadata=dict(artist='Me'), bitrate=1800)
            with change_directory((outfile := Path(outfile).with_suffix('.html')).parent):
                anim.save(outfile.name, writer=writer)
                update_html_controls(outfile.name)
        else:
            writer = animation.PillowWriter(
                fps=20,
                metadata=dict(artist='Me'),
                bitrate=1800,
            )
            anim.save(outfile, writer=writer)

        self.pbar.close()
        print(f'Animation saved to {outfile}')
