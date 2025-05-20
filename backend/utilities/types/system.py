"""Type definitions for system-related data structures."""

from collections.abc import Callable
from typing import Literal, Protocol

import yappi

OpenTextMode = Literal['r', 'w', 'a']


class Writable(Protocol):
    """Protocol for writable objects that can accept string messages."""

    def write(self, message: str) -> None:
        """Write a message to the writable object."""
        ...


class ClosableAndWritable(Writable, Protocol):
    """Protocol for writable objects that can also be closed and flushed."""

    def flush(self) -> None:
        """Flush the writable object."""
        ...

    def close(self) -> None:
        """Close the writable object."""
        ...


Stat = Literal['source', 'name', 'ncall', 'tsub', 'ttot', 'tavg']
SortOrder = Literal['asc', 'desc']

Filter = Callable[[yappi.YFuncStat], bool]
