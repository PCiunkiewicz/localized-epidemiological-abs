"""
This Python script runs the simulation. Currently parameters
are just hardcoded in the file but we can set it up to take
command-line arguments for things like simulation time or
file output location.
"""

import time
import socket
from multiprocessing import Queue, Process, Event, cpu_count
from concurrent.futures import ProcessPoolExecutor as Pool

import numpy as np
from argh import arg, ArghParser
from pathlib import Path

from simulation.model import simulate_sir_model
from simulation.publisher import publisher
from simulation.writer import save_agents


PORT_RANGE = 100


class SimController(object):
    """Controller object adapted from code required for frontend
    execution. Can be converted to a set of functions or moved to
    a dedicated Python module or into the `model` module later.
    """

    def __init__(self, config, port=5556, outfile=None):
        super().__init__()
        self.config = config
        self.port = port

        self.pub_queue = Queue()
        self.stop_publisher = Event()
        self.stop_simulation = Event()

        self.publisher_process = Process(
            target=publisher,
            args=(self.pub_queue, self.stop_publisher, port)
        )
        self.simulation_process = Process(
            target=simulate_sir_model,
            args=(self.pub_queue, self.stop_simulation, config),
        )
        self.writer_process = Process(target=save_agents, args=(port, outfile))

    def launch(self):
        self.publisher_process.start()
        self.simulation_process.start()
        self.writer_process.start()

    def terminate(self):
        # self.stop_simulation.set()
        self.writer_process.join()
        self.simulation_process.join()
        self.stop_publisher.set()
        self.publisher_process.join()


@arg('config', help='Path to the config file; example `scenarios/eng301.json`')
def run_sim(config, run_id=0, port=5556, save_dir='outputs'):
    Path(save_dir).mkdir(exist_ok=True)
    start = time.perf_counter()

    sim = SimController(
        Path(config),
        port=port,
        outfile=Path(f'{save_dir}/simulation_{run_id}_{port}.hdf5')
    )

    sim.launch()
    print('\nSimulating...')
    while not sim.stop_simulation.is_set():
        time.sleep(0.1)
    print('Terminating...')
    sim.terminate()
    print(f'Final run time: {time.perf_counter() - start}\n')
    return


def _run_args(args):
    run_sim(*args)


@arg('config', help='Path to the config file; example `scenarios/eng301.json`')
def run_parallel(config, runs=4, offset=0, base_port=5556, n_jobs=None):
    if not n_jobs:
        n_jobs = max(cpu_count() - 1, 1)

    run_ids = range(offset, runs + offset)
    ports = np.arange(runs) % PORT_RANGE + base_port
    args = [(config, run_id, port) for run_id, port in zip(run_ids, ports)]

    with Pool(max_workers=n_jobs) as pool:
        pool.map(_run_args, args)


parser = ArghParser()
parser.add_commands([run_sim, run_parallel])


if __name__ == '__main__':
    # Uncomment one of these lines if you don't want to use CLI args
    # run_sim('scenarios/eng301.json')
    # run_sim_parallel('scenarios/eng301.json', 20)
    parser.dispatch()
