"""Dask cluster management for parallel simulation runs."""

import os

from dask.distributed import LocalCluster
from loguru import logger

from utilities.paths import BACKEND
from utilities.reloader import Reloader

N_JOBS = os.cpu_count() or 1


if __name__ == '__main__':
    with Reloader(BACKEND) as reloader:
        logger.info(f'Starting Dask cluster with {N_JOBS} workers...')
        cluster = LocalCluster(
            host='0.0.0.0',
            n_workers=N_JOBS,
            processes=True,
            threads_per_worker=1,
            scheduler_port=8786,
        )
        logger.debug(cluster)
        logger.success('Dask cluster started, awaiting jobs.')

        try:
            while reloader.is_alive():
                reloader.join(5)
        finally:
            reloader.stop()
            reloader.join()
            logger.warning('Stopping Dask cluster...')
            cluster.close()
