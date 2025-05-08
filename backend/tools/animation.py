"""Tools for exporting simulation animations in gif or html format."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tables as tb
from matplotlib import animation, image
from matplotlib.colors import ListedColormap
from tqdm import tqdm

from simulation.scenario import VIRUS_SCALE
from utilities.tools import STATUS_COLOR, add_playback_controls, reshape, str_date
from utilities.types.agent import AgentStatus

plt.rcParams['animation.frame_format'] = 'svg'


class SimAnimation:
    """Base Model class for animating completed simulations.

    Attributes:
        imgs: List of loaded mapfile images for each floor.
        exits: List of boolean arrays indicating exit locations.
        im: List of AxesImage objects for each floor.
        tx: List of Text objects for displaying time.
        plot_ref: List of Line2D objects for plotting agent positions.
        labels: List of Text objects for displaying agent IDs.
        fig: Figure object for the animation.
        axes: List of Axes objects for each floor.
        pbar: Progress bar for tracking animation rendering.
        agents: Array of agent positions and statuses.
        virus: Array of virus data for each floor.
        timesteps: Array of simulation timesteps.
    """

    imgs: list[np.typing.NDArray]
    exits: list[np.typing.NDArray[np.bool_]]
    im: list[plt.AxesImage]
    tx: list[plt.Text]
    plot_ref: list[list[plt.Line2D]]
    labels: list[list[plt.Text]]
    fig: plt.Figure
    axes: list[plt.Axes]
    pbar: tqdm
    agents: np.typing.NDArray
    virus: np.typing.NDArray
    timesteps: np.typing.NDArray

    def __init__(self, results: Path, mapfile: Path) -> None:
        """Initialize the animation with simulation and map files.

        Args:
            results: Path to the simulation output .h5 file.
            mapfile: Path to the map image or directory containing map images.
        """
        self.imgs = []
        if mapfile.is_dir():
            for file in sorted(mapfile.iterdir()):
                if file.suffix == '.png' and '.nodes' not in file.suffixes:
                    self.imgs.append(image.imread(file))
        else:
            self.imgs.append(image.imread(mapfile))
        self.exits = [np.all(np.isclose(img, (1, 1, 0, 1)), axis=2) for img in self.imgs]

        with tb.open_file(results, mode='r') as file:
            self.agents = file.root.agents.read()
            self.timesteps = file.root.timesteps.read()
            try:
                self.virus = file.root.virus.read()
            except tb.NoSuchNodeError:
                self.virus = np.zeros((*self.imgs[0].shape[:2], len(self.imgs)))

        ncols = 2
        self.fig, self.axes = plt.subplots(
            nrows=len(self.imgs) // ncols,
            ncols=ncols,
            figsize=[8 * ncols, 4 * len(self.imgs) // ncols],
        )
        self.axes = self.axes.flatten()
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=0.95)

        self.im, self.tx, self.plot_ref, self.labels = [], [], [], []
        for floor in range(len(self.axes)):
            im, tx, plot_ref, labels = self.draw_frame(floor, 0)
            self.im.append(im)
            self.tx.append(tx)
            self.plot_ref.append(plot_ref)
            self.labels.append(labels)

        self.pbar = None

    def draw_frame(self, floor: int, i: int) -> tuple[plt.AxesImage, plt.Text, list[plt.Line2D], list[plt.Text]]:
        """Draw initial or arbitrary frame from simulation results.

        Args:
            floor: Floor number to draw.
            i: Frame index to draw.
        """
        ax: plt.Axes = self.axes[floor]
        ax.set_title(f'Floor {floor}\n', fontweight='bold', fontsize=14)
        ax.axis('off')

        ax.imshow(self.imgs[floor])
        im: plt.AxesImage = ax.imshow(
            self.virus[i, :, :, floor] != 0,
            alpha=(self.virus[i, :, :, floor] / VIRUS_SCALE) ** 0.35,
            cmap=ListedColormap(['white', 'red'], N=2),
            vmin=0,
            vmax=1,
        )

        tx: plt.Text = ax.text(
            x=0.03,
            y=0.05,
            s=f'{str_date(self.timesteps[i])}\n',
            c='black',
            fontsize=8,
            fontweight='bold',
            horizontalalignment='left',
            verticalalignment='bottom',
            transform=ax.transAxes,
        )

        plot_ref: list[plt.Line2D] = []
        for status in AgentStatus:
            ref = ax.plot(
                *reshape(self.agents[i], status.value, floor),
                'o',
                ms=4,
                mew=0.25,
                c=STATUS_COLOR[status.name],
                mec='black',
                label=status.name,
            )
            plot_ref.append(ref[0])

        labels: list[plt.Text] = []
        for agent in range(self.agents.shape[1]):
            labels.append(
                ax.text(
                    *self.agents[i, agent][:2][::-1],
                    agent,
                    fontsize=2,
                    c='black',
                    horizontalalignment='center',
                    verticalalignment='center',
                    visible=False,
                )
            )

        return im, tx, plot_ref, labels

    def update_floor(self, floor: int, i: int) -> None:
        """Update data for a floor of the simulation."""
        self.im[floor].set_data(self.virus[i, :, :, floor] != 0)
        self.im[floor].set_alpha((self.virus[i, :, :, floor] / VIRUS_SCALE) ** 0.35)
        info = [f'{str_date(self.timesteps[i])}\n']
        for status, ref in zip(AgentStatus, self.plot_ref[floor]):
            agents = reshape(self.agents[i], status.value, floor)
            info.append(f'{status.name.capitalize()}: {agents.shape[1]}')
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
                    continue
            label.set_visible(False)

        self.tx[floor].set_text('\n'.join(info))

    def animate(self, i: int) -> tuple:
        """Progress the simulation animation and set frame `i`."""
        self.pbar.update(1)

        artists = [*self.im, *self.tx]
        for floor in range(len(self.axes)):
            self.update_floor(floor, i)
            artists += self.plot_ref[floor] + self.labels[floor]
        return tuple(artists)

    def export(self, outfile: Path, html: bool = False) -> None:
        """Export animation to output file.

        Args:
            outfile: Path to the output file.
            html: Whether to save as HTML or gif.
        """
        self.pbar = tqdm(total=self.timesteps.size, desc='Animating', unit='frames')

        anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            frames=self.timesteps.size,
            blit=True,
            cache_frame_data=False,
        )

        if html:
            outfile = outfile.with_suffix('.html')
            writer = animation.HTMLWriter(fps=5, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(outfile, writer=writer)
            add_playback_controls(outfile)
        else:
            outfile = outfile.with_suffix('.gif')  # TODO: Explore ffmpeg for better quality / speed
            writer = animation.PillowWriter(fps=5, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(outfile, writer=writer)

        self.pbar.close()
        print(f'Animation saved to {outfile}')
