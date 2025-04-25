"""
This Python script runs the simulation. Currently parameters
are just hardcoded in the file but we can set it up to take
command-line arguments for things like simulation time or
file output location.
"""

import time
from multiprocessing import Event, Queue, cpu_count
from pathlib import Path
from threading import Thread

import dask
import yappi
from argh import ArghParser, arg
from dask.distributed import Client, LocalCluster
from simulation.model import SIRModel, simulate_model
from simulation.publisher import publisher
from simulation.writer import save_agents, save_agents_fast

PORT_RANGE = 100


class SimController(object):
    """
    Controller object adapted from code required for frontend
    execution. Can be converted to a set of functions or moved to
    a dedicated Python module or into the `model` module later.
    """

    def __init__(self, config, port=5556, outfile=None, fast=True):
        super().__init__()
        self.pub_queue = Queue()
        self.stop_publisher = Event()
        self.stop_simulation = Event()
        method = save_agents_fast if fast else save_agents

        self.publisher_process = Thread(
            target=publisher,
            args=(
                self.pub_queue,
                self.stop_publisher,
                port,
            ),
        )
        self.simulation_process = Thread(
            target=simulate_model,
            args=(
                SIRModel,
                config,
                self.pub_queue,
                self.stop_simulation,
                fast,
            ),
        )
        self.writer_process = Thread(
            target=method,
            args=(
                port,
                outfile,
            ),
        )

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


@arg('config', help='Path to the config file; example `data/run_configs/eng301.json`')
def run_sim(config, run_id=0, port=5556, save_dir='data/outputs', fast=True):
    Path(save_dir).mkdir(exist_ok=True)
    start = time.perf_counter()

    if fast:
        model = SIRModel(config)
        outfile = Path(f'{save_dir}/simulation_{run_id}.hdf5')
        run_sim_fast(outfile, model)

    else:
        sim = SimController(
            Path(config),
            port=port,
            outfile=Path(f'{save_dir}/simulation_{run_id}.hdf5'),
            fast=fast,
        )

        sim.launch()
        print('\nLoading Resources...')
        while not sim.stop_simulation.is_set():
            time.sleep(0.1)
        print('Terminating...')
        sim.terminate()
        print(f'Final run time: {time.perf_counter() - start}\n')


def run_sim_fast(outfile, model):
    stop_simulation = Event()
    model.simulate_fast(outfile, stop_simulation)

    while not stop_simulation.is_set():
        time.sleep(0.1)


@arg('config', help='Path to the config file; example `data/run_configs/eng301.json`')
def run_parallel(config, runs=4, offset=0, save_dir='data/outputs', n_jobs=8):
    # if not n_jobs:
    #     n_jobs = max(cpu_count() - 1, 1)

    filenames = [Path(f'{save_dir}/simulation_{run}.hdf5') for run in range(offset, runs + offset)]
    # args = [[model, outfile] for outfile in filenames]

    with (
        LocalCluster(
            n_workers=n_jobs,
            processes=True,
            threads_per_worker=1,
            memory_limit='4GB',
        ) as cluster,
        Client(cluster, direct_to_workers=True) as client,
    ):
        print(client.dashboard_link)
        model = client.scatter(
            SIRModel(config),
            direct=True,
            hash=False,
            broadcast=True,
        )
        res = client.map(run_sim_fast, filenames, model=model, actor=True)
        client.gather(res)


parser = ArghParser()
parser.add_commands([run_sim, run_parallel])


if __name__ == '__main__':
    # Uncomment one of these lines if you don't want to use CLI args
    # run_sim('data/run_configs/eng301.json', fast=False)
    yappi.start()
    run_sim('data/run_configs/bsf.json', fast=True, run_id='bsf_1')
    yappi.stop()
    yappi.get_thread_stats().print_all()
    print('=' * 50)
    threads = yappi.get_thread_stats()
    for thread in threads:
        print('Function stats for (%s) (%d)' % (thread.name, thread.id))  # it is the Thread.__class__.__name__
        yappi.get_func_stats(
            ctx_id=thread.id,
            filter_callback=lambda x: '/backend/' in x.full_name,  # or '/site-packages/' in x.full_name,
        ).print_all(
            columns={
                0: ('name', 80),
                1: ('ncall', 8),
                2: ('tsub', 8),
                3: ('ttot', 8),
                4: ('tavg', 8),
            }
        )
    # run_parallel('data/run_configs/bsf.json', 16)
    # parser.dispatch()
