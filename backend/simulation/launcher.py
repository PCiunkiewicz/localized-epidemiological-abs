"""Simulation manual run entrypoint."""

from __future__ import annotations

import os
import pickle
import sys
import tempfile
from pathlib import Path
from queue import Queue
from threading import Event

import django
from dask.distributed import Client, LocalCluster
from django.db import connections
from loguru import logger

from api.simulation.models import Run
from simulation.model.sir import SIRModel
from simulation.publisher import Publisher
from simulation.writer import Writer
from utilities.importer import ConfigImporter
from utilities.logging import configure_logger
from utilities.paths import BACKEND, TEMP
from utilities.thread import PublisherThread, SimulationThread, WriterThread

N_JOBS = os.cpu_count() or 1


class SimLauncher:
    """Simulation launcher."""

    def __init__(self, run: Run | int) -> None:
        """Initialize the simulation launcher with a run."""
        if os.environ.get('DOCKERIZED', False):
            sys.stderr = run.logfile.open('w')
            sys.stdout = run.logfile.open('a')
            configure_logger('TRACE', file=None)
        else:
            configure_logger('TRACE', file=run.logfile.open('w'))

        django.setup()
        for conn in connections.all():
            conn.close()

        self.run = Run.objects.get(id=run) if isinstance(run, int) else run

    @classmethod
    def from_config(cls, config: Path, runs: int = 1, exist_ok: bool = True) -> SimLauncher:
        """Create a simulation launcher from a config file."""
        if not config.exists():
            raise FileNotFoundError(f'Config file {config} does not exist.')

        importer = ConfigImporter(config, exist_ok=exist_ok)
        run = importer.import_config()
        run.runs = runs
        run.save()

        return cls(run)

    def start(self) -> None:
        """Start the simulation run."""
        self.set_status(Run.Status.RUNNING)
        try:
            self.run_parallel() if self.run.runs > 1 else self.run_sim()
            self.set_status(Run.Status.SUCCESS)
        except Exception:
            self.set_status(Run.Status.FAILURE)
            raise

    def set_status(self, status: Run.Status) -> None:
        """Set the status of the run."""
        Run.objects.filter(id=self.run.id).update(status=status)

    def run_sim(self) -> None:
        """Launch a single simulation run using threads."""
        model = SIRModel(self.run.config)
        outfile = self.run.save_dir.with_suffix('.hdf5')

        try:
            logger.info('Starting simulation...')
            terminate = Event()
            (publisher := PublisherThread(target=Publisher().publish, args=(pub_queue := Queue(), terminate))).start()
            (simulation := SimulationThread(target=model.simulate, args=(pub_queue,))).start()
            (writer := WriterThread(target=Writer(outfile, model.sim.max_iter).write, args=(terminate,))).start()

            simulation.join()
            publisher.join()
            logger.debug('Simulation finished, waiting for writer...')
            writer.join()
            logger.success(f'Simulation results saved to {outfile}.')
        except Exception:
            logger.error('Simulation failed, sending termination signal to threads...')
            terminate.set()
            raise
        finally:
            for thread in (simulation, publisher, writer):
                thread.join(timeout=1)
                if thread.is_alive():
                    logger.warning(f'Thread {thread.name} is still alive after 1 second.')

    def run_parallel(self) -> None:
        """Parallelize multiple simulation runs using Dask."""
        self.run.save_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f'Scheduling {self.run.runs} runs for {self.run.name}...')
        logger.info(f'Saving outputs to >> {self.run.save_dir.relative_to(BACKEND)}/')
        logger.debug(f'Starting {N_JOBS} workers...')

        with (
            LocalCluster(n_workers=N_JOBS, processes=True, threads_per_worker=1) as cluster,
            Client(cluster, direct_to_workers=True) as client,
        ):
            logger.success(f'Dask cluster dashboard live - {client.dashboard_link}')

            filenames = [self.run.save_dir / f'{run}.hdf5' for run in range(self.run.runs)]
            if any(f.exists() for f in filenames):
                raise FileExistsError(f'Output files already exist in {self.run.save_dir}')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl', prefix='SIRModel', dir=TEMP) as f:
                pickle.dump(SIRModel(self.run.config), f, protocol=pickle.HIGHEST_PROTOCOL)
                temp_path = Path(f.name)

            res = client.map(self._parallel_helper, filenames, model=temp_path, pure=False, key=self.run.name)
            client.gather(res)

    def _parallel_helper(self, outfile: Path, model: SIRModel | Path) -> None:
        """Callable for Dask."""
        if isinstance(model, Path):
            model = pickle.loads(model.read_bytes())

        model.simulate_fast(outfile)
