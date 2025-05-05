"""Simulation manual run entrypoint."""

import pickle
import tempfile
from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as EventType
from pathlib import Path

from argh import arg
from dask.distributed import Client, LocalCluster
from distributed import Future
from loguru import logger

# from utilities.profiling import profile, profiling_filter
from simulation.model.base import simulate_model
from simulation.model.sir import SIRModel
from simulation.publisher import publisher
from simulation.writer import save_agents, save_agents_fast
from utilities.logging import configure_logger
from utilities.paths import CFG, OUTPUTS, TEMP
from utilities.thread import PublisherThread, SimulationThread, WriterThread

PORT_RANGE = 100


class SimController:
    """Simulation threading controller."""

    def __init__(self, config: Path, port: int = 5556, outfile: Path = None, fast: bool = True) -> None:
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
        method = save_agents_fast if fast else save_agents

        self.publisher = PublisherThread(target=publisher, args=(self.pub_queue, self.stop_pub, port))
        self.simulation = SimulationThread(
            target=simulate_model, args=(SIRModel, config, self.pub_queue, self.stop_sim, fast)
        )
        self.writer = WriterThread(target=method, args=(port, outfile))

    def launch(self) -> None:
        """Launch the simulation and publisher/writer threads."""
        self.publisher.start()
        self.simulation.start()
        self.writer.start()

    def terminate(self) -> None:
        """Terminate the simulation and publisher/writer threads."""
        # self.stop_simulation.set()
        self.writer.join()
        self.simulation.join()
        self.stop_pub.set()
        self.publisher.join()


@arg('config', help='Path to the config file; example `data/run_configs/eng301.json`')
def run_sim(config: Path, run_id: int = 0, port: int = 5556, save_dir: Path = OUTPUTS) -> None:
    """Run the simulation.

    Args:
        config: Path to the simulation config file.
        run_id: ID for the simulation run.
        port: Port for the publisher thread.
        save_dir: Directory to save the simulation output.
    """
    Path(save_dir).mkdir(exist_ok=True)

    sim = SimController(
        Path(config),
        port=port,
        outfile=Path(f'{save_dir}/simulation_{run_id}.hdf5'),
        fast=False,
    )

    sim.launch()
    sim.stop_sim.wait()
    sim.terminate()


def run_sim_fast(outfile: Path, model: SIRModel | Path) -> None:
    """Run the simulation in fast mode.

    Args:
        outfile: Path to the output file.
        model: The simulation model or path to tempfile model artifact.
    """
    if isinstance(model, Path):
        with open(model, 'rb') as f:
            model = pickle.load(f)

    stop_simulation = Event()
    model.simulate_fast(outfile, stop_simulation)
    stop_simulation.wait()


@arg('config', help='Path to the config file; example `data/run_configs/eng301.json`')
def run_parallel(
    config: Path | list[Path],
    runs: int = 4,
    offset: int = 0,
    save_dir: Path = OUTPUTS,
    n_jobs: int = 8,
) -> None:
    """Parallelize the simulation runs using Dask.

    Args:
        config: Path to the simulation config file.
        runs: Number of simulation runs to perform.
        offset: Offset for the simulation run IDs.
        save_dir: Directory to save the simulation output.
        n_jobs: Number of parallel jobs to run.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl', prefix='SIRModel', dir=TEMP) as f:
        pickle.dump(SIRModel(config), f, protocol=pickle.HIGHEST_PROTOCOL)
        temp_path = Path(f.name)

    with (
        LocalCluster(n_workers=n_jobs, processes=True, threads_per_worker=1) as cluster,
        Client(cluster, direct_to_workers=True) as client,
    ):
        logger.info(f'Dask cluster dashboard live - {client.dashboard_link}')
        if isinstance(config, Path):
            config = [config]

        res: list[Future] = []
        for cfg in config:
            filenames = [save_dir / f'{cfg.stem}_{run}.hdf5' for run in range(offset, runs + offset)]
            res += client.map(run_sim_fast, filenames, model=temp_path, pure=False, key=cfg.stem)

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

    run_parallel(CFG / 'bsf.json', 16)
