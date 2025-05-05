"""Simulation manual run entrypoint."""

import pickle
import tempfile
from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as EventType
from pathlib import Path

from dask.distributed import Client, LocalCluster
from distributed import Future
from loguru import logger

# from utilities.profiling import profile, profiling_filter
from simulation.model.sir import SIRModel
from simulation.publisher import publisher
from simulation.writer import save_agents, save_agents_fast
from utilities.cli import LauncherCLI
from utilities.logging import configure_logger
from utilities.paths import BACKEND, OUTPUTS, TEMP
from utilities.thread import PublisherThread, SimulationThread, WriterThread

PORT_RANGE = 100


class SimController:
    """Simulation threading controller."""

    def __init__(self, config: Path, outfile: Path = None, fast: bool = True) -> None:
        """Initialize the simulation controller.

        Args:
            config: Path to the simulation config file.
            port: Port for the publisher thread.
            outfile: Path to the output file.
            fast: Whether to run the simulation in fast mode.
        """
        super().__init__()
        self.pub_queue = Queue()
        self.stop_pub: EventType = Event()
        self.stop_sim: EventType = Event()

        model = SIRModel(config)

        self.simulation = SimulationThread(
            target=model.simulate_fast if fast else model.simulate,
            args=(self.pub_queue, self.stop_sim),
        )
        self.publisher = PublisherThread(target=publisher, args=(self.pub_queue, self.stop_pub))
        self.writer = WriterThread(target=save_agents_fast if fast else save_agents, args=(outfile))

    def run(self) -> None:
        """Launch the simulation and publisher/writer threads."""
        self.publisher.start()
        self.simulation.start()
        self.writer.start()
        self.stop_sim.wait()

        self.writer.join()
        self.simulation.join()
        self.stop_pub.set()
        self.publisher.join()


def run_sim(config: Path, run_id: int = 0, save_dir: Path = OUTPUTS, fast: bool = False) -> None:
    """Run the simulation.

    Args:
        config: Path to the simulation config file.
        run_id: ID for the simulation run.
        save_dir: Directory to save the simulation output.
        fast: Whether to run the simulation in fast mode.
    """
    save_dir.mkdir(exist_ok=True)
    outfile = save_dir / f'simulation_{run_id}.hdf5'

    SimController(config, outfile=outfile, fast=fast).run()


def _parallel_helper(outfile: Path, model: SIRModel | Path) -> None:
    """Callable for Dask."""
    if isinstance(model, Path):
        model = pickle.loads(model.read_bytes())

    model.simulate_fast(outfile, stop_sim := Event())
    stop_sim.wait()


def run_parallel(
    config: Path | list[Path],
    runs: int = 4,
    save_dir: Path = OUTPUTS,
    n_jobs: int = 8,
    overwrite: bool = False,
) -> None:
    """Parallelize the simulation runs using Dask.

    Args:
        config: Path to the simulation config file.
        runs: Number of simulation runs to perform.
        save_dir: Directory to save the simulation output.
        n_jobs: Number of parallel jobs to run.
        overwrite: Whether to overwrite existing output files.
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(config, Path):
        config = [config]
    logger.info(f'Scheduling {runs * len(config)} runs across {len(config)} config(s)')
    logger.info(f'Saving outputs to >> {save_dir.relative_to(BACKEND)}/')
    logger.debug(f'Starting {n_jobs} workers...')

    with (
        LocalCluster(n_workers=n_jobs, processes=True, threads_per_worker=1) as cluster,
        Client(cluster, direct_to_workers=True) as client,
    ):
        logger.success(f'Dask cluster dashboard live - {client.dashboard_link}')

        res: list[Future] = []
        for cfg in config:
            filenames = [save_dir / f'{cfg.stem}_{run}.hdf5' for run in range(runs)]
            if not overwrite and any(f.exists() for f in filenames):
                raise FileExistsError(f'Output files already exist in {save_dir}. Use overwrite=True to ignore.')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl', prefix='SIRModel', dir=TEMP) as f:
                pickle.dump(SIRModel(cfg), f, protocol=pickle.HIGHEST_PROTOCOL)
                temp_path = Path(f.name)

            res += client.map(_parallel_helper, filenames, model=temp_path, pure=False, key=cfg.stem)

        client.gather(res)


if __name__ == '__main__':
    configure_logger('TRACE')

    # profile(
    #     run_sim,
    #     config='data/run_configs/bsf.json',
    #     fast=False,
    #     run_id='bsf_1',
    #     callback=profiling_filter(module=['/backend/']),
    # )

    launcher, kwargs = LauncherCLI().run()
    locals().get(launcher)(**kwargs)
    # get launcher method by string

    # run_parallel(config=CFG / 'bsf.json', runs=8, overwrite=True)
