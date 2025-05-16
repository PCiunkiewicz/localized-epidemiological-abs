"""Simulation manual run entrypoint."""

# from utilities.profiling import profile, profiling_filter
from simulation.launcher import SimLauncher
from utilities.logging import configure_logger
from utilities.paths import CFG

PORT_RANGE = 100


if __name__ == '__main__':
    configure_logger('TRACE')

    # launcher, kwargs = LauncherCLI().run()
    # locals().get(launcher)(**kwargs)

    launcher = SimLauncher.from_config(CFG / 'bsf.json', runs=8)
    launcher.start()

    # profile(
    #     launcher.start,
    #     callback=profiling_filter(module=['/backend/']),
    # )
