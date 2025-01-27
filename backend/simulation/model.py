"""
The `model` module contains code for managing the execution of
the simulation. The base class `Model` should be subclassed
when creating new model types, such as an SIR or SEIR model.
A function is required alongside each model class to run
the simulation due to the way that Python objects are passed
between processes and threads.
"""

import datetime as dt
import json
import time
from abc import ABC, abstractmethod

import numpy as np
from simulation.agent import Agent, SIRAgent
from simulation.scenario import Scenario, SIRScenario
from simulation.types.agent import AgentSpec, Status
from simulation.types.scenario import ScenarioSpec
from tqdm import tqdm

SUSCEPTIBLE, INFECTED, RECOVERED, QUARANTINED, DECEASED, HOSPITALIZED, UNKNOWN = Status


class Model(ABC):
    """
    Base Model class for simulation.
    """

    def __init__(self, config: str, AgentClass: type, ScenarioClass: type):
        self.trivial = False

        with open(config) as json_file:
            cfg = json.load(json_file)
            self.scenario: Scenario = ScenarioClass(ScenarioSpec.from_dict(cfg['scenario']))
            self.sim = self.scenario.sim

        self.population: list[Agent] = []
        self.create_agents(cfg['agents'], AgentClass)

    def create_agents(self, config: dict, AgentClass: type):
        """
        Instantiate agents from configuration file.
        """
        for _ in range(config['random_agents']):
            spec = config['default'].copy()
            spec['info']['urgency'] = np.random.uniform(0.75, 0.99)
            agent = AgentClass(self.scenario, AgentSpec.from_dict(spec))
            self.population.append(agent)

        for i in range(config['random_infected']):
            self.population[i].infect()

        for custom_agent in config['custom']:
            spec = config['default'].copy()
            for key, val in custom_agent.items():
                spec[key].update(val)
            agent = AgentClass(self.scenario, AgentSpec.from_dict(spec))
            self.population.append(agent)

    def get_agents(self) -> np.ndarray:
        """
        Get position and status of all agents.
        """
        ret = []
        for p in self.population:
            ret.append((*p.state.pos, p.state.status.value))
        return np.array(ret)

    @abstractmethod
    def model_step(self):
        pass

    @abstractmethod
    def simulate(self):
        pass


class SIRModel(Model):
    """
    Subclassed model for SIR simulation
    """

    def __init__(self, config):
        super().__init__(config, AgentClass=SIRAgent, ScenarioClass=SIRScenario)

    def summarize_agent_info(self):
        """
        Summarize agent information for saving.
        """
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

    def model_step(self):
        """
        Steps the simulation forward one iteration
        """
        for _ in range(self.sim.save_resolution):
            for p in self.population:
                p.move(trivial=self.trivial)
            if not self.trivial:
                self.scenario.ventilate()

            self.scenario.dt += dt.timedelta(seconds=self.sim.t_step)
            # if self.scenario.dt.time().hour >= 19:
            #     self.scenario.dt += dt.timedelta(hours=12)
            #     self.scenario.virus.matrix[:] = 0

            now = self.scenario.dt.strftime('%H:%M')
            self.scenario.check_schedule = self.scenario.now != now
            if self.scenario.check_schedule:
                self.scenario.now = now

    def simulate(self, queue, event):
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

    def simulate_fast(self, queue, event):
        n_iter = 0
        model_time = 0
        start_time = time.perf_counter()

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
        queue.put({'topic': 'timesteps', 'data': np.array(data['timesteps'])})
        queue.put({'topic': 'agents', 'data': np.array(data['agents'])})
        queue.put({'topic': 'agent_info', 'data': self.summarize_agent_info()})
        queue.put({'topic': '', 'data': 'stop'})

        print('\n' + '=' * 50)
        print(f'Total iterations: {n_iter}')
        print(f'Total simulation time: {model_time}')

        try:
            print(f'Avg iter time: {(time.perf_counter() - start_time) / n_iter}')
            print(f'Avg model cycle time: {model_time / n_iter}')
        except ZeroDivisionError:
            pass
        print('=' * 50)


def simulate_model(ModelClass: type, config: str, queue, event, fast=True):
    """
    Run SIR Model simulation.

    Simulations are best handled by functions due to
    the way that objects are passed between processes
    when using multiprocessing.
    """
    if fast:
        ModelClass(config).simulate_fast(queue, event)
    else:
        ModelClass(config).simulate(queue, event)
