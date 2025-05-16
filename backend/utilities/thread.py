"""Threading utilities for the simulation backend."""

from threading import Thread
from typing import override


class PropagatingThread(Thread):
    """Thread that propagates exceptions to the calling thread."""

    @override
    def run(self) -> None:
        self.exc = None
        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    @override
    def join(self, timeout: float | None = None) -> None:
        super().join(timeout)
        if self.exc:
            raise self.exc


class PublisherThread(PropagatingThread):
    """Thread for publishing simulation data. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='PublisherThread')


class SimulationThread(PropagatingThread):
    """Thread for running the simulation. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='SimulationThread')


class WriterThread(PropagatingThread):
    """Thread for writing simulation data to disk. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='WriterThread')
