"""Type definitions for the simulation configuration format."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, override

import dacite

from utilities.types.agent import AgentSpec, AgentStatus
from utilities.types.scenario import ScenarioSpec, SimSetup


@dataclass
class PartialAgentSpec:
    """Partial specification for all agents in the scenario.

    Attributes:
        name: Name of the total agent configuration.
        default: Default agent specification.
        random_agents: Number of random agents to generate.
        random_infected: Number of random infected agents to generate.
        custom: List of custom agent specifications.
    """

    name: str
    default: dict = field(default_factory=dict)
    random_agents: int = 0
    random_infected: int = 0
    custom: list[dict] = field(default_factory=list)


@dataclass
class TotalAgentSpec(PartialAgentSpec):
    """Total specification for all agents in the scenario with stricter typing."""

    @dataclass
    class SimplifiedAgentSpec(AgentSpec):
        """Simplified agent specification."""

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

        state: SimplifiedAgentState

    default: SimplifiedAgentSpec
    custom: list[SimplifiedAgentSpec] = field(default_factory=list)


@dataclass
class SimplifiedScenarioSpec(ScenarioSpec):
    """Simplified simulation scenario specification."""

    @dataclass
    class SimplifiedSimSetup(SimSetup):
        """Simplified simulation setup information."""

        @override
        def __post_init__(self) -> None:
            pass

    sim: SimplifiedSimSetup

    @override
    def __post_init__(self) -> None:
        pass


@dataclass
class ScenarioConfig:
    """Configuration for the simulation scenario.

    Attributes:
        scenario: The simulation scenario.
        agents: The total agent specification.
    """

    scenario: SimplifiedScenarioSpec
    agents: TotalAgentSpec

    @dataclass
    class PartialScenarioConfig:
        """Configuration for the simulation scenario without agent processing."""

        scenario: SimplifiedScenarioSpec
        agents: PartialAgentSpec

    @classmethod
    def load(cls, config_path: Path, process_agents: bool = True) -> Self:
        """Load a ScenarioConfig instance from a JSON file."""
        data = json.loads(config_path.read_text())
        if process_agents:
            data['agents']['custom'] = cls._process_agents(data)
            return dacite.from_dict(data_class=cls, data=data)
        return dacite.from_dict(data_class=cls.PartialScenarioConfig, data=data)

    @classmethod
    def _process_agents(cls, data: dict) -> None:
        """Apply defaults to custom agents."""
        agents: list[dict] = data['agents']['custom']
        default: dict = data['agents']['default']

        processed = []
        for agent in agents:
            spec = default.copy()
            for key, val in agent.items():
                spec[key].update(val)
            processed.append(spec)

        return processed
