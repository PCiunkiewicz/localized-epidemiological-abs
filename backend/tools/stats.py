"""Generate and export simulation result statistics."""

import multiprocessing
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, override

import h5py
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import image
from tqdm import tqdm

from utilities.paths import OUTPUTS
from utilities.types.agent import AgentStatus
from utilities.types.config import ScenarioConfig

sns.set_theme('paper')

Topic = Literal['agents', 'virus', 'timesteps']

# TODO: Check if everything still works


class BaseStatistic(ABC):
    """Base class for rendering simulation statistics.

    Attributes:
        cfg: Configuration object for the simulation scenario.
        data: Loaded simulation data.
    """

    cfg: ScenarioConfig
    data: list[np.typing.NDArray]

    @abstractmethod
    def __init__(self, config: Path, results_path: Path) -> None:
        """Initialize the simulation statistics with simulation file.

        Args:
            config: Path to the simulation config file.
            results_path: Path to the simulation results directory.
        """
        if not results_path.is_relative_to(OUTPUTS):
            raise ValueError(f'`results_path` should be in {OUTPUTS}')

        self.cfg = ScenarioConfig.load(config)

        files = list(results_path.glob('*.hdf5'))
        with multiprocessing.Pool(6) as p:  # TODO: replace with ProcessPoolExecutor
            self.data = list(tqdm(p.imap_unordered(self._load, files), total=len(files)))

    @abstractmethod
    def _load(self, file: Path, topic: Topic = 'agents') -> np.typing.NDArray:
        """Load simulation data from .h5 file."""
        with h5py.File(file, 'r') as file:
            return file[topic].__array__()

    @abstractmethod
    def export(self, outfile: Path) -> None:
        """Export statistics visualization to output file."""
        plt.savefig(outfile, dpi=600, bbox_inches='tight')


class ExcessRiskVsTime(BaseStatistic):
    """Visualization of excess risk of infection as a function of time.

    Attributes:
        prob: Probability of infection for each agent.
        hours: Array of time elapsed in hours.
        min_size: Minimum file size to consider a file valid.
    """

    prob: np.typing.NDArray
    hours: np.typing.NDArray

    @override
    def __init__(self, config: Path, results_path: Path) -> None:
        super().__init__(config, results_path)

        param = self.cfg.scenario.sim

        self.prob = (np.array(self.data) != 1).mean(axis=0)
        self.prob -= self.prob[0, :]  # Relative excess risk of infection
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    @override
    def _load(self, file: Path) -> np.typing.NDArray:
        return super()._load(file)[:, :, 2]

    @override
    def export(self, outfile: Path) -> None:
        _, ax = plt.subplots(figsize=[5, 3.5])

        for i in range(self.prob.shape[-1]):
            ax.plot(self.hours, self.prob[:, i], label=f'Agent {i + 1}')

        ax.set(
            xlabel='Time elapsed (hours)',
            ylabel='Excess Risk of Infection',
            xlim=[0, None],
            # ylim=[0, 0.1]
        )
        ax.legend()
        super().export(outfile)


class EpidemiologicalStatusVsTime(BaseStatistic):
    """Render agent epidemiological status summary over time.

    Attributes:
        pal: Color palette for visualization.
        stats: Array of statistics for each status.
        labels: List of status labels.
        hours: Array of time elapsed in hours.
        order: Order of status labels for visualization.
    """

    pal = sns.color_palette()
    stats: np.typing.NDArray
    labels: list[str]
    hours: np.typing.NDArray
    order = [1, 3, 2, 0]

    @override
    def __init__(self, config: Path, results_path: Path) -> None:
        super().__init__(config, results_path)

        param = self.cfg.scenario.sim

        self.stats = np.array(self.data).mean(axis=0)[self.order]
        self.labels = np.array([status.name for status in AgentStatus])[self.order]
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    @override
    def _load(self, file: Path) -> list[np.typing.NDArray]:
        status = super()._load(file)[:, :, 2]
        return [(status == s.value).mean(axis=1) for s in AgentStatus]

    @override
    def export(self, outfile: Path, fill: bool = True, ylim: float = None) -> None:
        """Export agent status progression to file.

        Args:
            outfile: Path to output file.
            fill: If True, fill the area under the curve.
            ylim: Maximum y-axis limit.
        """
        _, ax = plt.subplots(figsize=[5, 3.5])

        colors = [self.pal[3], self.pal[-2], self.pal[2], (1, 1, 1, 0)]

        if fill:
            ax.stackplot(self.hours, self.stats, labels=self.labels, colors=colors, alpha=0.65)
        else:
            ax.plot(self.hours, self.stats[2], label=self.labels[2], color=colors[2])
            ax.plot(self.hours, self.stats[1], label=self.labels[1], color=colors[1])
            ax.plot(self.hours, self.stats[0], label=self.labels[0], color=colors[0])
        ax.set(
            xlabel='Time elapsed (hours)',
            ylabel='Proportion of Population',
            xlim=[0, self.hours.max()],
            ylim=[0, ylim],
        )
        ax.legend()
        super().export(outfile)


class ViralConcentration(BaseStatistic):
    """Render viral load concentration overlay on mapfile image."""

    img: np.typing.NDArray
    virus: np.typing.NDArray
    hours: np.typing.NDArray

    @override
    def __init__(self, config: Path, results_path: Path) -> None:
        super().__init__(config, results_path)

        param = self.cfg.scenario.sim
        self.img = image.imread(param.mapfile)

        self.virus = np.array(self.data).mean(axis=0)
        self.hours = np.arange(param.max_iter) / 3600 * param.t_step * param.save_resolution

    @override
    def _load(self, file: Path, topic: Topic = 'virus') -> np.typing.NDArray:
        return super()._load(file, topic).mean(axis=0)

    @override
    def export(self, outfile: Path) -> None:
        _, ax = plt.subplots(figsize=[10, 10])

        ax.imshow(self.img)
        alpha = self.virus / self.virus.max()
        ax.imshow(self.virus != 0, alpha=alpha, cmap='bwr_r')

        ax.set(xticks=[], yticks=[])
        super().export(outfile)
