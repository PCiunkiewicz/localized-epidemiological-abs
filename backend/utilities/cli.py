"""Command line interface for the backend."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, get_args, override

from loguru import logger
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import DummyCompleter, WordCompleter
from prompt_toolkit.validation import DummyValidator, Validator

from utilities.paths import CFG, OUTPUTS
from utilities.types.cli import Launcher


class BaseCLI(ABC):
    """Base class for command line interface."""

    session: PromptSession[str]

    def __init__(self) -> None:
        """Initialize promptsession."""
        self.session = PromptSession[str](validate_while_typing=False, mouse_support=True)

    @abstractmethod
    def run(self) -> None:
        """Main loop to prompt the user."""
        pass

    def _prompt_kws(self, options: Sequence[str] = [], dtype: type = None) -> dict[str, Any]:
        """Generate prompt keyword arguments."""
        kwargs = {}
        if options := [str(x) for x in options]:
            kwargs = {
                'completer': WordCompleter(options, match_middle=True, sentence=True, ignore_case=True),
                'validator': Validator.from_callable(lambda x: x in options or not x, 'INVALID OPTION'),
                'pre_run': self._prime_autocomplete,
            }
        elif dtype is int:
            kwargs = {'validator': Validator.from_callable(lambda x: x.isdigit() or not x, 'INVALID INTEGER')}
        elif dtype is float:
            kwargs = {
                'validator': Validator.from_callable(
                    lambda x: x.replace('.', '', 1).isdigit() or not x, 'INVALID FLOAT'
                )
            }

        return {'completer': DummyCompleter(), 'validator': DummyValidator(), 'pre_run': None, **kwargs}

    def _prime_autocomplete(self) -> None:
        """Prime the prompt-toolkit autocompleter."""
        b = get_app().current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=False)


class LauncherCLI(BaseCLI):
    """CLI tool for launching simulation runs."""

    @override
    def run(self) -> tuple[Launcher, dict[str, Any]]:
        """Prompt use to select launcher callable and kwargs."""
        launcher = self.select_launcher()
        kwargs = self.launcher_kwargs(launcher)
        kwargs = {k: v for k, v in kwargs.items() if v}

        return launcher, kwargs

    def select_launcher(self) -> str:
        """Prompt the user to select a launcher."""
        launchers = get_args(Launcher)
        if launcher := self.session.prompt(HTML('<b>Launcher: </b>'), **self._prompt_kws(launchers)):
            return launcher
        else:
            logger.error('No launcher selected. Exiting...')
            quit()

    def launcher_kwargs(self, launcher: str) -> dict[str, Any]:
        """Generate keyword arguments for the selected launcher."""
        cfg_files = [f.relative_to(CFG) for f in CFG.iterdir() if f.suffix == '.json']
        config = CFG / self.session.prompt(HTML('<b>Config file: </b>'), **self._prompt_kws(cfg_files))

        dirs = ['New Folder...'] + sorted([f.relative_to(OUTPUTS) for f in OUTPUTS.rglob('*') if f.is_dir()])
        save_dir = OUTPUTS / self.session.prompt(HTML('<b>Output directory: </b>'), **self._prompt_kws(dirs))
        if save_dir.name == 'New Folder...':
            save_dir = OUTPUTS / self.session.prompt(HTML('<b>New folder name: </b>'), **self._prompt_kws())

        if launcher == 'run_parallel':
            return {
                'config': config,
                'save_dir': save_dir,
                'runs': int(self.session.prompt(HTML('<b>Number of runs: </b>'), **self._prompt_kws(dtype=int)) or 0),
                'n_jobs': int(self.session.prompt(HTML('<b>Number of jobs: </b>'), **self._prompt_kws(dtype=int)) or 0),
                'overwrite': self.session.prompt(HTML('<b>Overwrite: </b>'), **self._prompt_kws(['Y', 'N'])) == 'Y',
            }
        elif launcher == 'run_sim':
            return {
                'config': config,
                'save_dir': save_dir,
                'run_id': int(self.session.prompt(HTML('<b>Run ID: </b>'), **self._prompt_kws(dtype=int)) or 0),
                'fast': self.session.prompt(HTML('<b>Fast sim: </b>') ** self._prompt_kws(['Y', 'N'])) == 'Y',
            }
