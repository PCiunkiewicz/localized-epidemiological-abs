"""Defined filepaths used in the simulation and tools."""

from pathlib import Path

_ROOT = Path(__file__).parents[2]

BACKEND = _ROOT / 'backend'
"""Backend directory: `./backend/`"""

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
TEMP = DATA / 'temp'
"""Temporary files directory: `./backend/data/temp/`"""

SIMULATION = BACKEND / 'simulation'
"""Simulation directory: `./backend/simulation/`"""

TOOLS = BACKEND / 'tools'
"""Tools directory: `./backend/tools/`"""
STATIC = TOOLS / 'static'
"""Static files directory: `./backend/tools/static/`"""
