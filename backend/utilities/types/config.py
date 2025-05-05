"""Type definitions for the simulation configuration format."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self, override

import dacite

from utilities.types.agent import AgentSpec, AgentStatus
from utilities.types.scenario import ScenarioSpec, SimSetup


@dataclass
class SimplifiedAgentState:
    """Simplified agent state information."""

    x: int = 0
    y: int = 0
    status: str = 'UNKNOWN'

    @override
    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            self.status = AgentStatus[self.status]


class SimplifiedAgentSpec(AgentSpec):
    """Simplified agent specification."""

    state: SimplifiedAgentState


@dataclass
class FullAgentSpec:
    """Full specification for all agents in the scenario."""

    default: SimplifiedAgentSpec
    random_agents: int = 0
    random_infected: int = 0
    custom: list[SimplifiedAgentSpec] = None


@dataclass
class SimplifiedSimSetup(SimSetup):
    """Simplified simulation setup information."""

    @override
    def __post_init__(self) -> None:
        pass


@dataclass
class SimplifiedScenarioSpec(ScenarioSpec):
    """Simplified simulation scenario specification."""

    sim: SimplifiedSimSetup

    @override
    def __post_init__(self) -> None:
        pass


@dataclass
class ScenarioConfig:
    """Configuration for the simulation scenario."""

    scenario: SimplifiedScenarioSpec
    agents: FullAgentSpec

    @classmethod
    def from_dict(cls, data: dict) -> AgentSpec:
        """Create a ScenarioConfig instance from a dictionary."""
        return dacite.from_dict(data_class=cls, data=data)

    @classmethod
    def load(cls, config_path: Path) -> Self:
        """Load a ScenarioConfig instance from a JSON file."""
        data = json.loads(config_path.read_text())
        return cls.from_dict(data)
