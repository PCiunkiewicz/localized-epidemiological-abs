"""Generate export snapshots, statistics, and animations."""

import time
from pathlib import Path

from argh import ArghParser, arg  # TODO: replace with prompt_toolkit for better CLI

from tools.animation import SimAnimation
from tools.snapshot import SimSnapshot
from tools.stats import ExcessRiskVsTime
from utilities.logging import configure_logger
from utilities.paths import EXPORTS


@arg('simfile', help='Path to the simulation output; example `data/outputs/simulation_0.hdf5`')
@arg('mapfile', help='Path to the mapfile image; example `data/mapfiles/eng301.png`')
def animation(
    simfile: Path,
    mapfile: Path,
    outfile: Path = EXPORTS / 'animation.gif',
    html: bool = False,
) -> None:
    """Export simulation animation as gif."""
    print(f'Exporting {simfile} as animation...')
    start = time.perf_counter()
    SimAnimation(simfile, mapfile).export(outfile, html)
    print(f'Time elapsed: {time.perf_counter() - start}')


@arg('simfile', help='Path to the simulation output; example `data/outputs/simulation_0.hdf5`')
@arg('mapfile', help='Path to the mapfile image; example `data/mapfiles/eng301.png`')
def snapshot(simfile: Path, mapfile: Path, frame: int = 0, outfile: Path = EXPORTS / 'snapshot.png') -> None:
    """Export simulation frame as image."""
    print(f'Exporting {simfile} frame {frame}...')
    start = time.perf_counter()
    SimSnapshot(simfile, mapfile).export(frame, outfile)
    print(f'Time elapsed: {time.perf_counter() - start}')


@arg('config', help='Path to the simulation config; example `data/run_configs/eng301.json`')
@arg('results_path', help='Simulation outputs path; example `data/outputs-nomask-novax`')
def excess_risk(config: Path, results_path: Path, outfile: Path = EXPORTS / 'excess_risk.png') -> None:
    """Export simulation stats as image."""
    print(f'Exporting {config} stats for {results_path}...')
    start = time.perf_counter()
    ExcessRiskVsTime(config, results_path).export(outfile)
    print(f'Time elapsed: {time.perf_counter() - start}')


parser = ArghParser()
parser.add_commands([animation, snapshot, excess_risk])


if __name__ == '__main__':
    configure_logger('TRACE')
    parser.dispatch()
