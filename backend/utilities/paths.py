"""Defined filepaths used in the simulation and tools."""

import os
from pathlib import Path

_ROOT = Path(__file__).parents[2]

# For mounted docker volumes, ./backend is mapped to /code
if os.environ.get('DOCKERIZED', False):
    BACKEND = Path('/code')
else:
    BACKEND = _ROOT / 'backend'


class RPath(Path):
    """Path with a relative path property."""

    @property
    def rel(self) -> Path:
        """Return the relative path to the BACKEND directory."""
        return self.relative_to(BACKEND)


BACKEND = RPath(BACKEND)
"""Backend directory: `./backend/` or `/code/`"""

DATA = BACKEND / 'data'
"""Data directory: `./backend/data/`"""
EXPORTS = DATA / 'exports'
"""Exports directory: `./backend/data/exports/`"""
MAPFILES = DATA / 'mapfiles'
"""Mapfiles directory: `./backend/data/mapfiles/`"""
OUTPUTS = DATA / 'outputs'
"""Outputs directory: `./backend/data/outputs/`"""
PATHS = DATA / 'paths'
"""Pathfinding directory: `./backend/data/paths/`"""
CFG = DATA / 'run_configs'
"""Run configurations directory: `./backend/data/run_configs/`"""
LOGS = DATA / 'logs'
"""Run configurations directory: `./backend/data/logs/`"""
TMP = DATA / 'tmp'
"""Temporary files directory: `./backend/data/tmp/`"""

for d in [EXPORTS, MAPFILES, OUTPUTS, PATHS, CFG, LOGS, TMP]:
    d.mkdir(parents=True, exist_ok=True)

SIMULATION = BACKEND / 'simulation'
"""Simulation directory: `./backend/simulation/`"""

TOOLS = BACKEND / 'tools'
"""Tools directory: `./backend/tools/`"""
STATIC = TOOLS / 'static'
"""Static files directory: `./backend/tools/static/`"""
