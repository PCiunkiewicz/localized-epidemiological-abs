"""System logging utilities."""

from __future__ import annotations

import json
import sys
from functools import partialmethod
from pathlib import Path
from typing import Literal, get_args

import loguru
from loguru import logger

LogLevel = Literal['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL', 'PROFILE']

LOGGER_FORMAT = (
    '<level><bold>{level: >8}</bold></level> | '
    '<black>{path: >36}</black> | : '
    '<level>{message: <62}</level> | '
    '<light-black>{time:HH:mm:ss.SSS}</light-black>\n'
)

PROFILE_FORMAT = (
    '<level><bold>{level: >8}</bold></level> | '
    '<black>{source: >36}</black> | '
    '<black>{name: >32}</black> | '
    '<black>{ncall: >8}</black> | '
    '<cyan>{tavg: ^8}</cyan> | '
    '<green>{ttot: ^8}</green> | '
    '<light-black>{tsub: ^8}</light-black>\n'
)

HEADER_FORMAT = (
    '\n<cyan><bold>{label: <36}</bold></cyan>   '
    '<black><bold>{source: >8}</bold></black>   '
    '<black><bold>{name: >32}</bold></black>   '
    '<bold><black>{ncall: >8}</black></bold>   '
    '<cyan><bold>{tavg: >8}</bold></cyan>   '
    '<green><bold>{ttot: >8}</bold></green>   '
    '<light-black><bold>{tsub: >8}</bold></light-black>\n'
)

LEVEL_COLOR: dict[LogLevel, str] = {
    'TRACE': '<magenta>',
    'DEBUG': '<cyan>',
    'INFO': '<black>',
    'PROFILE': '<magenta>',
    'SUCCESS': '<green><bold>',
    'WARNING': '<yellow>',
    'ERROR': '<red><bold>',
    'CRITICAL': '<RED><bold>',
}


def configure_logger(level: LogLevel = 'SUCCESS', file: loguru.Writable | None = None) -> None:
    """Configure the logger with a specific level."""
    logger.remove()
    logger.add(sys.stderr, level=level, format=formatter)
    if file:
        logger.add(file, level=level, format=formatter)

    try:
        logger.level('PROFILE', no=20, color=LEVEL_COLOR['PROFILE'])
        logger.__class__.profile = partialmethod(logger.__class__.log, 'PROFILE')
    except ValueError:
        # If the level already exists, we can just use it
        pass

    for level in get_args(LogLevel):
        logger.level(level, color=LEVEL_COLOR[level])


def formatter(record: loguru.Record) -> str:
    """Format the log message based on the level."""
    if record['level'].name == 'PROFILE':
        record.update(json.loads(record['message']))
        return HEADER_FORMAT if record['source'] == 'source' else PROFILE_FORMAT
    else:
        record['path'] = f'{Path(*Path(record["file"].path).parts[-2:])}:{record["line"]}'
        return LOGGER_FORMAT
