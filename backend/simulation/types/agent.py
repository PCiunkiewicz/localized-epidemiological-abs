"""
The `types` module contains dataclasses used for
various classes throughout the simulation. Explicit
typing is supported.
"""

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from dacite import from_dict


class Status(Enum):
    """
    Infection status of the Agents.
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
    mask_type: str
    vax_type: str
    vax_doses: int
    age: Optional[float]
    start_zone: Optional[str]
    work_zone: Optional[str]
    schedule: dict[str, str] = field(default_factory=dict)
    access_level: int = 0
    urgency: float = 1.0


@dataclass
class AgentTime:
    recovery: Optional[dt.datetime] = None
    quarantine: Optional[dt.datetime] = None
    last_action_time: Optional[str] = None


@dataclass
class AgentState:
    dt: Optional[AgentTime]
    status: Status | str = Status.UNKNOWN
    x: int = 0
    y: int = 0
    z: int = 0
    path: list[tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = Status[self.status]
        if not self.dt:
            self.dt = AgentTime()


@dataclass
class AgentSpec:
    info: AgentInfo
    state: AgentState

    @classmethod
    def from_dict(cls, data: dict) -> 'AgentSpec':
        return from_dict(data_class=cls, data=data)
