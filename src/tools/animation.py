"""
The `animation` module contains code exporting
simulation animations as gif files.
"""

import h5py

import matplotlib.pyplot as plt
from matplotlib import animation, image

from tools.utils import reshape, str_date, STATUS_COLOR
from simulation.agent import Status


class AnimateSim:
    """Base Model class for animating completed simulations.
    """

    def __init__(self, simfile, mapfile):
        self.img = image.imread(mapfile)

        with h5py.File(simfile, 'r') as file:
            self.agents = file['agents'].__array__()
            self.virus = file['virus'].__array__()
            self.timesteps = file['timesteps'].__array__()

        self.im, self.tx, self.plot_ref = self.draw_frame(0)

    def draw_frame(self, i, cmap='bwr_r'):
        """Draw initial or arbitrary frame from simulation results.
        """
        _, ax = plt.subplots(figsize=[10, 10])
        ax.imshow(self.img)
        im = ax.imshow(self.virus[i] != 0, alpha=self.virus[i] / 2**14, cmap=cmap)
        tx = ax.text(1, 2, str_date(self.timesteps[i]), c='w', fontsize=14)

        plot_ref = []
        for status in Status:
            ref = ax.plot(
                *reshape(self.agents[i], status.value), 'o', ms=16,
                c=STATUS_COLOR[status.name], mec="black", label=status.name)
            plot_ref.append(ref[0])

        return im, tx, plot_ref

    def animate(self, i):
        """Progress the simulation animation.
        Use with matplotlib `animation.FuncAnimation`.
        """
        self.im.set_data(self.virus[i] != 0)
        self.im.set_alpha(self.virus[i] / 2**14)
        self.tx.set_text(str_date(self.timesteps[i]))
        for status, ref in zip(Status, self.plot_ref):
            ref.set_data(*reshape(self.agents[i], status.value))
        return (self.im,) + tuple(self.plot_ref)

    def export(self, outfile):
        """Export animation to output file.
        """
        anim = animation.FuncAnimation(
            plt.gcf(), self.animate, frames=self.timesteps.size, interval=50, blit=True)

        # writer = FasterFFMpegWriter(fps=30, metadata=dict(artist='Me'), bitrate=1800)
        writer = animation.PillowWriter(fps=30, metadata=dict(artist='Me'), bitrate=1800)
        anim.save(outfile, writer=writer)
