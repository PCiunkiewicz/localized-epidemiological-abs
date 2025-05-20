"""Command line interface for the backend."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, override

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import DummyCompleter, WordCompleter
from prompt_toolkit.validation import DummyValidator, Validator

from utilities.paths import CFG


class BaseCLI(ABC):
    """Base class for command line interface."""

    session: PromptSession[str]

    def __init__(self) -> None:
        """Initialize promptsession."""
        self.session = PromptSession[str](validate_while_typing=False, mouse_support=True)

    @abstractmethod
    def prompt(self) -> None:
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
    def prompt(self) -> dict[str, Any]:
        """Prompt user to select run config."""
        cfg_files = [f.relative_to(CFG) for f in CFG.iterdir() if f.suffix == '.json']

        kwargs = {
            'config': CFG / self.session.prompt(HTML('<b>Config file: </b>'), **self._prompt_kws(cfg_files)),
            'runs': int(self.session.prompt(HTML('<b>Number of runs: </b>'), **self._prompt_kws(dtype=int)) or 1),
        }
        return {k: v for k, v in kwargs.items() if v}


class ExporterCLI(BaseCLI):
    """CLI tool for exporting simulation data."""

    @override
    def prompt(self) -> tuple[str, dict[str, Any]]:
        """Prompt user to select export tool and kwargs."""
        exporter = self.select_exporter()
        kwargs = self.exporter_kwargs(exporter)
        kwargs = {k: v for k, v in kwargs.items() if v}

        return exporter, kwargs
