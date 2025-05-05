"""Type definitions for CLI arguments."""

from typing import Literal

Launcher = Literal['run_parallel', 'run_sim']

Export = Literal['animation', 'snapshot', 'excess_risk']
