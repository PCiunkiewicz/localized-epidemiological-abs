"""Import entrypoint for the agent module."""

from simulation.agent.base import BaseAgent
from simulation.agent.sir import SIRAgent

__all__ = ['BaseAgent', 'SIRAgent']
