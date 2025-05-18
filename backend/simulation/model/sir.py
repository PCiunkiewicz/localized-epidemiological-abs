"""SIR model simulation class."""

import os
from datetime import timedelta
from pathlib import Path
from queue import Queue
from typing import override

import numpy as np
import tables as tb
import tqdm
from loguru import logger

from simulation.agent import SIRAgent
from simulation.model.base import BaseModel
from simulation.scenario import SIRScenario
from simulation.writer import AgentInfo
from utilities.types.agent import AgentStatus

SUSCEPTIBLE, *_ = AgentStatus


class SIRModel(BaseModel):
    """Subclassed model for SIR simulation."""

    population: list[SIRAgent]
    scenario: SIRScenario

    @override
    def __init__(self, config: Path) -> None:
        super().__init__(config, agent_cls=SIRAgent, scenario_cls=SIRScenario)

    def summarize_agent_info(self) -> list[dict]:
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
        return ret

    @override
    def model_step(self) -> None:
        for _ in range(self.sim.save_resolution):
            for p in self.population:
                p.move()
            self.scenario.ventilate()

            self.scenario.dt += timedelta(seconds=self.sim.t_step)
            # if self.scenario.dt.time().hour >= sanitation_time:
            #     self.scenario.sanitize() # TODO: Add to config

            now = self.scenario.dt.strftime('%H:%M')
            self.scenario.check_schedule = self.scenario.now != now
            if self.scenario.check_schedule:
                self.scenario.now = now

    @override
    def simulate(self, queue: Queue) -> None:
        step = self.sim.save_resolution
        pbar = tqdm.tqdm(desc='Timesteps', total=self.sim.max_iter * step, file=open(os.devnull, 'w'))
        logger.info(str(pbar), flush=True)

        n_iter = 0
        while n_iter < self.sim.max_iter:
            if queue.empty():
                pbar.update(step)
                logger.info(f'{pbar}\033[F\033[K', flush=True)
                n_iter += 1
                self.model_step()
                queue.put({'topic': 'timesteps', 'data': self.scenario.dt.timestamp()})
                queue.put({'topic': 'agents', 'data': self.get_agents()})
                if self.sim.save_verbose:
                    queue.put({'topic': 'virus', 'data': self.scenario.virus.matrix.copy()})

        logger.info(str(pbar), flush=True)
        queue.put({'topic': 'agent_info', 'data': self.summarize_agent_info()})

    @override
    def simulate_fast(self, outfile: Path) -> None:
        data = {'timesteps': [], 'agents': []}

        step = self.sim.save_resolution
        pbar = tqdm.tqdm(desc=f'Run {int(outfile.stem):03}', total=self.sim.max_iter * step, file=open(os.devnull, 'w'))

        for i in range(self.sim.max_iter):
            pbar.update(step)
            self.model_step()
            data['timesteps'].append(self.scenario.dt.timestamp())
            data['agents'].append(self.get_agents())
            if i % (self.sim.max_iter // 4) == 0:
                logger.info(str(pbar), flush=True)

        logger.debug(f'Writing simulation data to {outfile}')
        self._write_outputs(data, outfile)
        logger.debug(f'Simulation data written to {outfile}')

    def _write_outputs(self, data: dict, outfile: Path) -> None:
        """Write simulation data to HDF5 file directly."""
        with tb.open_file(outfile, mode='w') as f:
            filters = tb.Filters(complevel=9, complib='blosc2')
            f.create_carray(f.root, 'agents', obj=data['agents'], filters=filters)
            f.create_carray(f.root, 'timesteps', obj=data['timesteps'], filters=filters)
            f.create_table(f.root, 'agent_info', AgentInfo, filters=filters)

            agent_info = f.root['agent_info'].row
            for agent in self.summarize_agent_info():
                for key, value in agent.items():
                    agent_info[key] = value
                agent_info.append()
