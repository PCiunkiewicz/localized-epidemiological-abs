"""Agent dataclasses used throughout the simulation."""

from __future__ import annotations

import datetime as dt
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import override

import dacite


class AgentStatus(Enum):
    """Infection status of the Agents.

    Attributes:
        SUSCEPTIBLE: The agent is not infected.
        INFECTED: The agent is infected.
        RECOVERED: The agent has recovered from the infection.
        QUARANTINED: The agent is quarantined.
        DECEASED: The agent has died.
        HOSPITALIZED: The agent is hospitalized.
        UNKNOWN: The agent's status is unknown.
    """

    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    QUARANTINED = 4
    DECEASED = 5
    HOSPITALIZED = 6
    UNKNOWN = 7


@dataclass
class AgentInfo:
    """General agent information.

    Attributes:
        mask_type: Type of mask the agent is wearing.
        vax_type: Type of vaccine the agent has received.
        vax_doses: Number of vaccine doses the agent has received.
        age: Age of the agent.
        start_zone: Starting zone of the agent.
        work_zone: Work zone of the agent.
        home_zone: Home zone of the agent.
        schedule: Schedule of tasks for the agent.
        access_level: Access level of the agent.
        urgency: Urgency level of the agent.
    """

    mask_type: str
    vax_type: str
    vax_doses: int
    age: float | None
    start_zone: str | None
    work_zone: str | None
    home_zone: str | None
    schedule: dict[str, str] = field(default_factory=dict)
    access_level: int = 0
    urgency: float = 1.0


@dataclass
class AgentTime:
    """Temporal agent information.

    Attributes:
        recovery: Time of recovery.
        quarantine: Time of quarantine.
        last_action_time: Last action time of the agent.
    """

    recovery: dt.datetime | None = None
    quarantine: dt.datetime | None = None
    last_action_time: str | None = None


@dataclass
class AgentState:
    """Epidemiological state agent information.

    Attributes:
        dt: Temporal information of the agent.
        status: Infected state of the agent.
        pos: Current spatial position of the agent in the environment.
        path: Current agent target path.
    """

    dt: AgentTime | None
    status: AgentStatus | str | int = AgentStatus.UNKNOWN
    pos: tuple[int, int, int] = (0, 0, 0)
    path: deque[tuple[int, int]] = field(default_factory=deque)

    @override
    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            self.status = AgentStatus[self.status]
        if not self.dt:
            self.dt = AgentTime()


@dataclass
class AgentSpec:
    """Individual agent specification.

    Attributes:
        info: General agent information.
        state: Epidemiological state agent information.
    """

    info: AgentInfo
    state: AgentState

    @classmethod
    def from_dict(cls, data: dict) -> AgentSpec:
        """Create an AgentSpec instance from a dictionary."""
        return dacite.from_dict(data_class=cls, data=data)
