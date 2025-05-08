"""Utilities for generating simulation exports and statistics."""

import datetime as dt
from pathlib import Path

import bs4
import numpy as np

from utilities.paths import STATIC

ANIMATION_HTML = (STATIC / 'animation.html').read_text()
ANIMATION_CSS = (STATIC / 'animation.css').read_text()

STATUS_COLOR = {
    'SUSCEPTIBLE': '#ffffff',
    'INFECTED': '#ff0000',
    'RECOVERED': '#00ff00',
    'QUARANTINED': '#ffa500',
    'DECEASED': '#000000',
    'HOSPITALIZED': '#a020f0',
    'UNKNOWN': '#ff00ff',
}


def reshape(data: np.typing.NDArray, status: int = None, floor: int = 0) -> np.typing.NDArray:
    """Reshape data for convenient plotting in matplotlib.

    Args:
        data: Array of agent positions and statuses.
        status: Status of the agents to filter by.
        floor: Floor number to filter by.
    """
    if data.shape[1] == 4:
        data = data[(data[:, 2] == floor) & (data[:, 3] == status)][:, :2]
    elif data.shape == (0,):
        return data.reshape(2, -1)
    return data.T[::-1]


def str_date(timestamp: float) -> str:
    """Convert a datetime timestamp to string."""
    date = dt.datetime.fromtimestamp(timestamp)
    return date.strftime('%y-%m-%d %H:%M:%S')


def add_playback_controls(html_anim_path: Path) -> None:
    """Add playback controls to an exported HTML animation."""
    soup = bs4.BeautifulSoup(html_anim_path.read_text(), 'html.parser')

    soup.script.decompose()
    soup.insert(1, bs4.BeautifulSoup(ANIMATION_HTML, 'html.parser'))

    soup.style.append(ANIMATION_CSS)

    zoom_img = f'<label><input type="checkbox">{soup.div.img}</label>'
    soup.div.img.decompose()
    soup.div.insert(0, bs4.BeautifulSoup(zoom_img, 'html.parser'))

    soup.div.div.form.decompose()

    with open(html_anim_path, 'w') as file:
        file.write(soup.prettify())
