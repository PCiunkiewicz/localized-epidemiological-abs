"""Profiling utilities for performance analysis."""

import json
from collections.abc import Callable
from typing import Any, Literal, get_args

import yappi
from loguru import logger

Stat = Literal['source', 'name', 'ncall', 'tsub', 'ttot', 'tavg']
SortOrder = Literal['asc', 'desc']

Filter = Callable[[yappi.YFuncStat], bool]


def profiling_filter(extend: Filter = lambda _: True, **kwargs: Any) -> Filter:
    """Filter function for yappi stats.

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

    def filter_callback(x: yappi.YFuncStat) -> bool:
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

    return filter_callback


def profile(
    func: Callable,
    *args: tuple,
    callback: Filter = profiling_filter(module='/backend/'),
    sort_by: Stat = 'ttot',
    sort_order: SortOrder = 'desc',
    **kwargs: dict,
) -> None:
    """Profile a function using yappi.

    Args:
        func: The function to profile.
        *args: Positional arguments to pass to the function.
        callback: A function to filter the yappi stats.
            Can build conveniently with `profiling_filter`.
        sort_by: The attribute to sort the stats by.
        sort_order: The order to sort the stats by.
        **kwargs: Keyword arguments to pass to the function.
    """
    yappi.start()
    func(*args, **kwargs)
    yappi.stop()

    for thread in sorted(yappi.get_thread_stats(), key=lambda x: x.id):
        _callback = profiling_filter(extend=callback, ctx_id=thread.id)
        stats = yappi.get_func_stats(ctx_id=thread.id, filter_callback=_callback)

        if not stats.empty():
            header = {k: k for k in get_args(Stat)}
            header['label'] = f'{thread.name} (id={thread.id})'
            logger.profile(json.dumps(header))

            for stat in sorted(stats._as_list, key=lambda x: getattr(x, sort_by), reverse=sort_order == 'desc'):
                logger.profile(formatted(stat))


def formatted(stat: yappi.YFuncStat) -> dict[str, str]:
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
