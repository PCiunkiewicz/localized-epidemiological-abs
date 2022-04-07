"""
The `model` module contains code for managing the execution of
the simulation. The base class `Model` should be subclassed
when creating new model types, such as an SIR or SEIR model.
A function is required alongside each model class to run
the simulation due to the way that Python objects are passed
between processes and threads.
"""

import json
import time
import datetime as dt
from abc import ABC, abstractmethod

import numpy as np

from simulation.scenario import SIRScenario, Scenario
from simulation.agent import SIRAgent, Agent
from simulation.types.agent import AgentSpec
from simulation.types.scenario import ScenarioSpec


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
            ret.append((*p.pos, p.status.value))
        return np.array(ret)

    @abstractmethod
    def model_step(self):
        pass


class SIRModel(Model):
    """
    Subclassed model for SIR simulation
    """

    def __init__(self, config):
        super().__init__(config, AgentClass=SIRAgent, ScenarioClass=SIRScenario)

    def model_step(self):
        """
        Steps the simulation forward one iteration
        """
        for _ in range(self.sim.save_resolution):
            for p in self.population:
                p.move(trivial=self.trivial)
            if not self.trivial:
                self.scenario.ventilate()

        self.scenario.dt += dt.timedelta(seconds=self.sim.t_step * self.sim.save_resolution)
        if self.scenario.dt.time().hour >= 19:
            self.scenario.dt += dt.timedelta(hours=12)
            self.scenario.virus.matrix[:] = 0


def simulate_sir_model(queue, event, config_file):
    """
    Run SIR Model simulation.

    Simulations must be handled by functions due to
    the way that objects are passed between processes
    when using the multiprocessing library.

    Parameters
    ----------
    queue : multiprocessing.Queue
        Public queue for sending data to zmq publisher.
    event : multiprocessing.Event
        Stop event for terminating simulation.
    config_file : str
        Path to scenario configuration (json).
    """
    model = SIRModel(config_file)

    n_iter = 0
    model_time = 0
    start_time = time.perf_counter()

    if all([p.is_('SUSCEPTIBLE') for p in model.population]):
        model.trivial = True
        print('TRIVIAL')

    while n_iter < model.sim.max_iter:
        if queue.empty():
            n_iter += 1
            start = time.perf_counter()
            model.model_step()
            model_time += time.perf_counter() - start
            queue.put({
                'topic': 'timesteps',
                'data': model.scenario.dt.timestamp()})
            queue.put({'topic': 'agents', 'data': model.get_agents()})
            if not model.trivial and model.sim.save_verbose:
                queue.put({'topic': 'virus', 'data': model.scenario.virus.matrix.copy()})

            sim_dt = model.scenario.dt.strftime('%y-%m-%d %H:%M:%S')
            print(f'Model Step: {n_iter}    Runtime: {model_time:.2f}s    SimDT: {sim_dt}', end='\r')

    event.set()
    if model.trivial and model.sim.save_verbose:
        queue.put({'topic': 'trivial', 'data': {
            'virus_shape': (model.sim.max_iter, *model.sim.shape)
        }})
    else:
        queue.put({'topic': '', 'data': 'stop'})

    print('\n' + '=' * 50)
    print('Performance Statistics')
    print('-' * 50)
    print(f'Total iterations: {n_iter}')
    print(f'Total simulation steps: {n_iter * model.sim.save_resolution}')
    print(f'Total simulation time: {model_time}')

    print('-' * 50)
    try:
        print(f'Avg iter time: {(time.perf_counter()-start_time) / n_iter}')
        print(f'Avg model cycle time: {model_time / n_iter}')
        print(f'Avg simulation step time: {model_time / n_iter / model.sim.save_resolution}')
    except ZeroDivisionError:
        pass
    print('=' * 50)
