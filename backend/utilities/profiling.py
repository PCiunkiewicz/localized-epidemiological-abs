"""Profiling utilities for performance analysis."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, get_args

import yappi
from loguru import logger

from utilities.logging import Redirector
from utilities.types.system import Filter, SortOrder, Stat


class Profiler:
    """Yappi profiler handler."""

    def __init__(self, logfile: Path, callback: Filter = lambda _: True, **callback_kws: Any) -> None:
        """Initialize the profiler with a logfile and a callback filter.

        Args:
            logfile: The path to the logfile where profiling results will be written.
            callback: A filter function to apply to the profiling stats.
                Can build conveniently with `Profiler.filter`.
            **callback_kws: Keyword arguments to pass to construct callback filter.
                - `module: str | list[str]` The module filepath (contains, e.g. `'/backend/'`, `'/site-packages/'`).
                - `name: str | list[str]` The called function name (contains).
                - `ncall: int` The number of function calls (>).
                - `tavg: float` The average time spent in the function per call (>).
                - `ttot: float` The total time spent calling the function (>).
                - `tsub: float` Time spent calling the function excluding subroutines (>).
        """
        self.logfile = logfile
        self.callback = self.filter(extend=callback, **callback_kws)

    def profile(
        self,
        func: Callable,
        *args: tuple,
        sort_by: Stat = 'ttot',
        sort_order: SortOrder = 'desc',
        **kwargs: dict,
    ) -> None:
        """Profile a function using yappi.

        Args:
            func: The function to profile.
            *args: Positional arguments to pass to the function.
            sort_by: The attribute to sort the stats by.
            sort_order: The order to sort the stats by.
            **kwargs: Keyword arguments to pass to the function.
        """
        logger.warning(f'Profiling enabled for {func.__qualname__}. Expect runtime to be slower.')
        yappi.start()
        func(*args, **kwargs)
        yappi.stop()

        with Redirector(self.logfile):
            for thread in sorted(yappi.get_thread_stats(), key=lambda x: x.id):
                callback = self.filter(extend=self.callback, ctx_id=thread.id)
                stats = yappi.get_func_stats(ctx_id=thread.id, filter_callback=callback)

                if not stats.empty():
                    header = {k: k for k in get_args(Stat)}
                    header['label'] = f'{thread.name} (id={thread.id})'
                    logger.profiler(json.dumps(header))

                    for stat in sorted(stats._as_list, key=lambda x: getattr(x, sort_by), reverse=sort_order == 'desc'):
                        logger.profiler(self.format(stat))

    @staticmethod
    def format(stat: yappi.YFuncStat) -> dict[str, str]:
        """Apply formatting to yappi function stats."""
        return json.dumps(
            {
                'source': f'{stat.module.split("/backend/")[-1].split("/site-packages/")[-1]}:{stat.lineno}',
                'name': stat.name,
                'ncall': str(stat.ncall),
                'tsub': f'{stat.tsub:.6f}'[:8],
                'ttot': f'{stat.ttot:.6f}'[:8],
                'tavg': f'{stat.tavg:.6f}'[:8],
            }
        )

    @staticmethod
    def filter(extend: Filter = lambda _: True, **kwargs: Any) -> Filter:
        """Filter callback builder for yappi stats.

        Args:
            extend: A filter function to extend.
            **kwargs: Keyword arguments to filter the yappi stats.
                - `module: str | list[str]` The module filepath (contains, e.g. `'/backend/'`, `'/site-packages/'`).
                - `name: str | list[str]` The called function name (contains).
                - `ncall: int` The number of function calls (>).
                - `tavg: float` The average time spent in the function per call (>).
                - `ttot: float` The total time spent calling the function (>).
                - `tsub: float` Time spent calling the function excluding subroutines (>).
        """

        def callback(x: yappi.YFuncStat) -> bool:
            if extend(x):
                for key, value in kwargs.items():
                    stat = getattr(x, key)
                    if key == 'ctx_id':
                        return value == stat
                    elif isinstance(stat, str):
                        if isinstance(value, list):
                            if any(x in stat for x in value):
                                return True
                        elif value in stat:
                            return True
                    elif isinstance(stat, int | float):
                        if value <= stat:
                            return True
            return False

        return callback
