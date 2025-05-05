"""SIR model simulation class."""

import datetime as dt
import time
from multiprocessing import Queue
from multiprocessing.synchronize import Event
from pathlib import Path
from typing import override

import h5py
import numpy as np
from tqdm import tqdm

from simulation.agent import SIRAgent
from simulation.model.base import BaseModel
from simulation.scenario import SIRScenario
from utilities.types.agent import AgentStatus

SUSCEPTIBLE, *_ = AgentStatus


class SIRModel(BaseModel):
    """Subclassed model for SIR simulation."""

    population: list[SIRAgent]
    scenario: SIRScenario

    @override
    def __init__(self, config) -> None:
        super().__init__(config, agent_cls=SIRAgent, scenario_cls=SIRScenario)

    def summarize_agent_info(self) -> list[str]:
        """Summarize agent information for saving."""
        ret = []
        for p in self.population:
            if p.info.vax_doses == 0:
                vax = 'novax'
            elif p.info.vax_doses == 1:
                vax = '1dose'
            elif p.info.vax_doses == 2:
                vax = p.info.vax_type.lower()

            if p.info.mask_type == 'NONE':
                mask = 'nomask'
            else:
                mask = p.info.mask_type.lower()

            ret.append(
                str(
                    {
                        'age': p.age,
                        'sex': np.random.choice(['M', 'F']),
                        'long_covid': p.long_covid,
                        'prevention_index': p.prevention_index,
                        'mask': mask,
                        'vax': vax,
                        'infected': p.infected,
                        'hospitalized': p.hospitalized,
                        'deceased': p.deceased,
                        'capacity': len(self.population),
                    }
                )
            )
        return ret

    @override
    def model_step(self) -> None:
        for _ in range(self.sim.save_resolution):
            for p in self.population:
                p.move(trivial=self.trivial)
            if not self.trivial:
                self.scenario.ventilate()

            self.scenario.dt += dt.timedelta(seconds=self.sim.t_step)
            # if self.scenario.dt.time().hour >= sanitation_time:
            #     self.scenario.sanitize() # TODO: Add to config

            now = self.scenario.dt.strftime('%H:%M')
            self.scenario.check_schedule = self.scenario.now != now
            if self.scenario.check_schedule:
                self.scenario.now = now

    @override
    def simulate(self, queue: Queue, event: Event) -> None:
        print('Simulating...')
        n_iter = 0
        model_time = 0
        start_time = time.perf_counter()

        if all(p.is_(SUSCEPTIBLE) for p in self.population):
            self.trivial = True
            print('TRIVIAL')

        pbar = tqdm(
            desc='Timesteps',
            total=self.sim.max_iter * self.sim.save_resolution,
            unit='step',
        )
        while n_iter < self.sim.max_iter:
            if queue.empty():
                pbar.update(self.sim.save_resolution)
                n_iter += 1
                start = time.perf_counter()
                self.model_step()
                model_time += time.perf_counter() - start
                queue.put({'topic': 'timesteps', 'data': self.scenario.dt.timestamp()})
                queue.put({'topic': 'agents', 'data': self.get_agents()})
                if not self.trivial and self.sim.save_verbose:
                    queue.put({'topic': 'virus', 'data': self.scenario.virus.matrix.copy()})

                # sim_dt = self.scenario.dt.strftime('%y-%m-%d %H:%M:%S')
                # print(f'Model Step: {n_iter}    Runtime: {model_time:.2f}s    SimDT: {sim_dt}', end='\r')

        pbar.close()
        event.set()
        if self.trivial and self.sim.save_verbose:
            queue.put(
                {
                    'topic': 'trivial',
                    'data': {'virus_shape': (self.sim.max_iter, *self.sim.shape)},
                }
            )
        else:
            queue.put({'topic': '', 'data': 'stop'})

        print('\n' + '=' * 50)
        print('Performance Statistics')
        print('-' * 50)
        print(f'Total iterations: {n_iter}')
        print(f'Total simulation steps: {n_iter * self.sim.save_resolution}')
        print(f'Total simulation time: {model_time}')

        print('-' * 50)
        try:
            print(f'Avg iter time: {(time.perf_counter() - start_time) / n_iter}')
            print(f'Avg model cycle time: {model_time / n_iter}')
            print(f'Avg simulation step time: {model_time / n_iter / self.sim.save_resolution}')
        except ZeroDivisionError:
            pass
        print('=' * 50)

    @override
    def simulate_fast(self, outfile: Path, event: Event) -> None:
        n_iter = 0
        model_time = 0

        if all(p.is_(SUSCEPTIBLE) for p in self.population):
            self.trivial = True
            print('TRIVIAL')

        data = {'timesteps': [], 'agents': []}

        pbar = tqdm(
            desc='Timesteps',
            total=self.sim.max_iter * self.sim.save_resolution,
            unit='step',
        )

        while n_iter < self.sim.max_iter:
            pbar.update(self.sim.save_resolution)
            n_iter += 1
            start = time.perf_counter()
            self.model_step()
            model_time += time.perf_counter() - start
            data['timesteps'].append(self.scenario.dt.timestamp())
            data['agents'].append(self.get_agents())

        pbar.close()
        event.set()

        with h5py.File(outfile, 'w') as f:
            f.create_dataset('agents', data=data['agents'], compression='gzip', compression_opts=9)
            f.create_dataset('agent_info', data=self.summarize_agent_info(), compression='gzip', compression_opts=9)
            f.create_dataset('timesteps', data=data['timesteps'], compression='gzip', compression_opts=9)
