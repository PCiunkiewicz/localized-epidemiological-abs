"""Threading utilities for the simulation backend."""

from threading import Thread
from typing import override


class PublisherThread(Thread):
    """Thread for publishing simulation data. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='PublisherThread')


class SimulationThread(Thread):
    """Thread for running the simulation. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='SimulationThread')


class WriterThread(Thread):
    """Thread for writing simulation data to disk. Subclassed for profiling clarity."""

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, name='WriterThread')
