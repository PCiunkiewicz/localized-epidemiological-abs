"""
The `stats` module contains code exporting
simulation stats as image files.
"""

import os
import json
from multiprocessing import Pool

import h5py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import image
from tqdm import tqdm

from simulation.utils import AttrDict
from simulation.types import Status

sns.set('paper')


class StatsSim:
    """
    Base Model class for rendering individual simulation statistics.
    """

    def __init__(self, simfile, runs):
        with open(simfile) as file:
            param = AttrDict(json.load(file)['ScenarioParameters'])

        res = []
        for i in range(runs):
            results = f'data/outputs/simulation_{i}.hdf5'
            with h5py.File(results, 'r') as file:
                try:
                    agents = file['agents'].__array__()
                    act_stat = agents[:,:,2]
                    res.append(act_stat)
                except Exception:
                    print(results)

        self.prob = (np.array(res) != 1).sum(axis=0) / runs
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    def export(self, outfile):
        """
        Export statistics visualization to output file.
        """
        _, ax = plt.subplots(figsize=[5, 3.5])

        for i in range(self.prob.shape[-1]):
            _ = ax.plot(self.hours, self.prob[:,i], label=f'Agent {i+1}')
        _ = ax.set(
            xlabel='Time elapsed (hours)',
            ylabel='Probability of Infection',
            xlim=[0, None],
            # ylim=[0, 0.1]
        )
        _ = ax.legend()
        plt.savefig(outfile, dpi=600, bbox_inches='tight')


class StatsSimComplete:
    """
    Base Model class for rendering aggregate simulation statistics.
    """

    def __init__(self, simfile, path, flat=False):
        assert path.startswith('data/outputs-'), '`path` should start with "outputs-"'
        files = os.listdir(path)
        files = [os.path.join(path, x) for x in files]
        self.label = path.replace('data/outputs-', '')
        self.min_size = os.path.getsize('trivial.hdf5')

        with open(simfile) as file:
            cfg = AttrDict(json.load(file))
            param = cfg.ScenarioParameters
            n_agents = cfg.agents.random.n_agents + len(cfg.agents.custom)
            self.shape = (param.max_iter, n_agents)

        with Pool(6) as p:
            res = list(tqdm(p.imap_unordered(self._load, files), total=len(files)))

        self.prob = (np.array(res) != 1).mean(axis=0)
        if flat:
            self.prob -= self.prob[0,:] # - param.infection_rate
            self.label += '-flat'
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    def _load(self, file):
        size = os.path.getsize(file)
        if size > self.min_size:
            with h5py.File(file, 'r') as file:
                agents = file['agents'].__array__()
                return agents[:,:,2]
        else:
            return np.zeros(self.shape)

    def export(self):
        """
        Export statistics visualization to output file.
        """
        _, ax = plt.subplots(figsize=[5, 3.5])

        for i in range(self.prob.shape[-1]):
            _ = ax.plot(self.hours, self.prob[:,i], label=f'Agent {i+1}')

        if self.label.endswith('-flat'):
            label = 'Excess Risk of Infection'
        else:
            label = 'Probability of Infection'

        _ = ax.set(
            xlabel='Time elapsed (hours)',
            ylabel=label,
            xlim=[0, None],
            # ylim=[0, 0.1]
        )
        _ = ax.legend()
        plt.savefig(f'data/exports/stats-{self.label}.png', dpi=600, bbox_inches='tight')


class StatsSimStatus:
    """
    Base Model class for rendering status simulation statistics.
    """

    pal = sns.color_palette()

    def __init__(self, simfile, path):
        assert path.startswith('data/outputs-'), '`path` should start with "outputs-"'
        files = os.listdir(path)
        files = [os.path.join(path, x) for x in files]
        self.label = path.replace('data/outputs-', '')

        with open(simfile) as file:
            param = AttrDict(json.load(file)['ScenarioParameters'])

        with Pool(6) as p:
            stats = list(tqdm(p.imap_unordered(self._load, files), total=len(files)))

        order = [1, 3, 2, 0]
        self.stats = np.array(stats).mean(axis=0)[order]
        self.labels = np.array([status.name for status in Status])[order]
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    def _load(self, file):
        with h5py.File(file, 'r') as file:
            agents = file['agents'].__array__()
            status = agents[:,:,2]
            return [(status == s.value).mean(axis=1) for s in Status]

    def export(self, fill=True, ylim=None):
        """
        Export statistics visualization to output file.
        """
        _, ax = plt.subplots(figsize=[5, 3.5])

        colors = [self.pal[3], self.pal[-2], self.pal[2], (1, 1, 1, 0)]

        if fill:
            _ = ax.stackplot(self.hours, self.stats, labels=self.labels, colors=colors, alpha=0.65)
        else:
            _ = ax.plot(self.hours, self.stats[2], label=self.labels[2], color=colors[2])
            _ = ax.plot(self.hours, self.stats[1], label=self.labels[1], color=colors[1])
            _ = ax.plot(self.hours, self.stats[0], label=self.labels[0], color=colors[0])
        _ = ax.set(
            xlabel='Time elapsed (hours)',
            ylabel='Proportion of Population',
            xlim=[0, self.hours.max()],
            ylim=[0, ylim]
        )
        _ = ax.legend()
        plt.savefig('data/exports/sir-plot.png', dpi=600, bbox_inches='tight')


class StatsSimVirus:
    """
    Base Model class for rendering virus simulation statistics.
    """

    def __init__(self, simfile, path):
        assert path.startswith('data/outputs-'), '`path` should start with "outputs-"'
        files = os.listdir(path)
        files = [os.path.join(path, x) for x in files]
        self.label = path.replace('data/outputs-', '')
        self.min_size = os.path.getsize('trivial.hdf5')

        with open(simfile) as file:
            param = AttrDict(json.load(file)['ScenarioParameters'])
            self.img = image.imread(param.mapfile)
            self.shape = self.img.shape[:2]

        with Pool(6) as p:
            res = list(tqdm(p.imap_unordered(self._load, files), total=len(files)))

        self.virus = np.array(res).mean(axis=0)
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    def _load(self, file):
        size = os.path.getsize(file)
        if size > self.min_size:
            with h5py.File(file, 'r') as file:
                virus = file['virus'].__array__()
                return virus.mean(axis=0)
        else:
            return np.zeros(self.shape)

    def export(self):
        """
        Export statistics visualization to output file.
        """
        _, ax = plt.subplots(figsize=[10, 10])

        ax.imshow(self.img)
        alpha = self.virus / self.virus.max()
        ax.imshow(self.virus != 0, alpha=alpha, cmap='bwr_r')

        _ = ax.set(xticks=[], yticks=[])
        plt.savefig('data/exports/virus-levels.png', dpi=600, bbox_inches='tight')
