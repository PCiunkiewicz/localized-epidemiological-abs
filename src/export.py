"""
This Python script generates exported snapshots
and gif animations.
"""

import time

from argh import arg, ArghParser

from tools.animation import AnimateSim
from tools.snapshot import SnapshotSim
from tools.stats import StatsSim, StatsSimComplete


@arg('simfile', help='Path to the simulation output; example `data/outputs/simulation_0.hdf5`')
@arg('mapfile', help='Path to the mapfile image; example `data/mapfiles/eng301.png`')
def animation(simfile, mapfile, outfile='data/exports/animation.gif'):
    """
    Export simulation animation as gif.
    """
    print(f'Exporting {simfile} as animation...')
    start = time.perf_counter()
    AnimateSim(simfile, mapfile).export(outfile)
    print(f'Time elapsed: {time.perf_counter() - start}')


@arg('simfile', help='Path to the simulation output; example `data/outputs/simulation_0.hdf5`')
@arg('mapfile', help='Path to the mapfile image; example `data/mapfiles/eng301.png`')
def snapshot(simfile, mapfile, frame=0, outfile='data/exports/snapshot.png'):
    """
    Export simulation frame as image.
    """
    print(f'Exporting {simfile} frame {frame}...')
    start = time.perf_counter()
    SnapshotSim(simfile, mapfile).export(frame, outfile)
    print(f'Time elapsed: {time.perf_counter() - start}')


@arg('config', help='Path to the simulation config; example `data/run_configs/eng301.json`')
@arg('runs', help='Number of simulation runs in outputs directory')
def stats(config, runs, outfile='data/exports/stats.png'):
    """
    Export simulation stats as image.
    """
    print(f'Exporting {config} stats...')
    start = time.perf_counter()
    StatsSim(config, int(runs)).export(outfile)
    print(f'Time elapsed: {time.perf_counter() - start}')


@arg('config', help='Path to the simulation config; example `data/run_configs/eng301.json`')
@arg('output_path', help='Simulation outputs path; example `data/outputs-nomask-novax`')
def stats2(config, output_path, flat=0):
    """
    Export simulation stats as image.
    """
    print(f'Exporting {config} stats for {output_path}...')
    start = time.perf_counter()
    StatsSimComplete(config, output_path, int(flat)).export()
    print(f'Time elapsed: {time.perf_counter() - start}')


parser = ArghParser()
parser.add_commands([animation, snapshot, stats, stats2])


if __name__ == '__main__':
    parser.dispatch()
