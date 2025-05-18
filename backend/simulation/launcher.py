"""Simulation manual run entrypoint."""

from __future__ import annotations

import os
import pickle
import tempfile
from pathlib import Path
from queue import Queue
from threading import Event

import django
from dask.distributed import Client, wait
from django.db import connections
from loguru import logger

from api.simulation.models import Run
from simulation.model.sir import SIRModel
from simulation.publisher import Publisher
from simulation.writer import Writer
from utilities.importer import ConfigImporter
from utilities.logging import Redirector
from utilities.paths import BACKEND, TMP
from utilities.thread import PublisherThread, SimulationThread, WriterThread

HOST = 'dask' if os.environ.get('DOCKERIZED', False) else 'localhost'


class SimLauncher:
    """Simulation launcher."""

    def __init__(self, run: Run | int) -> None:
        """Initialize the simulation launcher with a run."""
        django.setup()
        for conn in connections.all():
            conn.close()

        self.run = Run.objects.get(id=run) if isinstance(run, int) else run
        (BACKEND / self.run.save_dir).mkdir(parents=True, exist_ok=True)

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
        with Redirector(self.run.logfile):
            try:
                logger.debug(f'Writing outputs to >> {self.run.save_dir}/*.hdf5')
                logger.debug(f'Logging to >> {self.run.logfile}')
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
        logger.debug('Loading model assets...')
        model = SIRModel(BACKEND / self.run.config)
        outfile = self.run.save_dir / '0.hdf5'

        try:
            logger.debug('Starting simulation|publisher|writer threads...')
            terminate = Event()
            (publisher := PublisherThread(target=Publisher().publish, args=(pub_queue := Queue(), terminate))).start()
            (simulation := SimulationThread(target=model.simulate, args=(pub_queue,))).start()
            (writer := WriterThread(target=Writer(outfile, model.sim.max_iter).write, args=(terminate,))).start()

            simulation.join()
            logger.debug('Simulation finished, waiting for publisher|writer threads...')
            publisher.join()
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
        logger.debug(f'Configuring {self.run.runs} runs for {self.run.name} (id={self.run.id})...')

        with Client(f'tcp://{HOST}:8786', direct_to_workers=True) as client:
            logger.success(f'Dask cluster dashboard - {client.dashboard_link}')

            filenames = [self.run.save_dir / f'{run}.hdf5' for run in range(self.run.runs)]
            if any(f.exists() for f in filenames):
                raise FileExistsError(f'Output files already exist in {self.run.save_dir}')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl', prefix='SIRModel', dir=TMP) as f:
                model = SIRModel(self.run.config)
                pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
                model_pkl = Path(f.name).relative_to(TMP)

            job_id = f'{self.run.id:03}-{self.run.name}'
            res = client.map(self._parallel_helper, filenames, model_pkl=model_pkl, pure=False, key=job_id)
            logger.debug('Simulation runs submitted to scheduler, waiting for completion...')
            wait(res)
            logger.success('All simulation runs completed successfully.')

    def _parallel_helper(self, outfile: Path, model_pkl: Path) -> None:
        """Callable for Dask."""
        if isinstance(model_pkl, Path):
            model: SIRModel = pickle.loads((TMP / model_pkl).read_bytes())

        with Redirector(self.run.logfile):
            model.simulate_fast(BACKEND / outfile)
