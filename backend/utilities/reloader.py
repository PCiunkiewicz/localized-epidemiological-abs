"""Watchdog test script to monitor file system events."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import override

from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from utilities.logging import configure_logger


class EventHandler(FileSystemEventHandler):
    """Custom event handler for file system events."""

    ignore_patterns = [
        '__pycache__/',
        'data/',
    ]

    def __init__(self, reloader: Reloader, path: Path) -> None:
        """Initialize the event handler."""
        configure_logger('TRACE')
        self.root = path
        self.reloader = reloader

    @override
    def on_any_event(self, event: FileSystemEvent) -> None:
        src = Path(event.src_path).relative_to(self.root)
        dst = Path(event.dest_path).relative_to(self.root) if event.dest_path else None

        if event.is_directory or any(x in str(src) for x in self.ignore_patterns):
            return None
        elif event.event_type in ['opened', 'closed', 'closed_no_write']:
            return None
        elif event.event_type == 'created':
            logger.reloader(json.dumps({'message': 'File created', 'path': str(src)}))
        elif event.event_type == 'modified':
            logger.reloader(json.dumps({'message': 'File modified', 'path': str(src)}))
        elif event.event_type == 'deleted':
            logger.reloader(json.dumps({'message': 'File deleted', 'path': str(src)}))
        elif event.event_type == 'moved':
            logger.reloader(json.dumps({'message': f'File moved to {dst}', 'path': str(src)}))
        else:
            raise ValueError(f'Unhandled event type: {event.event_type} for file {src}')

        self.reloader.stop()


class Reloader(Observer, BaseObserver):
    """Custom observer that reloads the script on file changes."""

    @override
    def __init__(self, root: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root = root
        self.handler = EventHandler(self, root)

    def __enter__(self) -> Reloader:
        """Context manager to start the reloader."""
        self.schedule(self.handler, str(self.root), recursive=True)
        self.start()
        logger.reloader(json.dumps({'message': f'Watching for file changes @ {self.root}', 'path': ''}))
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Context manager exit to stop the reloader."""
        self.join()
        if exc_type is None:
            logger.reloader(json.dumps({'message': f'Reloading {sys.argv[0]}...', 'path': ''}))
            os.execl(sys.executable, sys.executable, *sys.argv)
