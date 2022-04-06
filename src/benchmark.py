# %%
from export import animation
from launch import run_parallel

# %%
%%time
config = 'data/scenarios/benchmark.json'
run_parallel(config, runs=24, offset=0, base_port=5556, n_jobs=1)

# %%
%%time
simfile = 'data/outputs/simulation_0.hdf5'
mapfile = 'data/mapfiles/eng301.png'
animation(simfile, mapfile, outfile='data/exports/animation.gif')

# %%
"""
Ryzen:
    Single-core: 18:29
    Multi-core:   8:35
    Animation:    3:48
M1 Max
    Single-core: 13:48
    Multi-core:   3:34
    Animation:    2:20
Intel
    Single-core: 25:56
    Multi-core:  12:23
    Animation:    6:44
"""
