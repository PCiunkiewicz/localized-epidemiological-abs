"""
The `utils` module contains utilities for generating
simulation exports.
"""

import contextlib
import datetime as dt
import os
from pathlib import Path

import bs4

with open(Path(__file__).parent / 'animation.html') as file:
    ANIMATION_HTML = file.read()

with open(Path(__file__).parent / 'animation.css') as file:
    ANIMATION_CSS = file.read()

STATUS_COLOR = {
    'SUSCEPTIBLE': '#ffffff',
    'INFECTED': '#ff0000',
    'RECOVERED': '#00ff00',
    'QUARANTINED': '#ffa500',
    'DECEASED': '#000000',
    'HOSPITALIZED': '#a020f0',
    'UNKNOWN': '#ff00ff',
}


@contextlib.contextmanager
def change_directory(path):
    old_directory = os.getcwd()
    os.chdir(path)
    try:
        yield

    finally:
        os.chdir(old_directory)


def reshape(data, status=None, floor=0):
    """
    Reshape data for convenient plotting.
    """
    if data.shape[1] == 4:
        data = data[(data[:, 2] == floor) & (data[:, 3] == status)][:, :2]
    elif data.shape == (0,):
        return data.reshape(2, -1)
    return data.T[::-1]


def str_date(timestamp):
    """
    Convert a datetime timestamp to string.
    """
    date = dt.datetime.fromtimestamp(timestamp)
    return date.strftime('%y-%m-%d %H:%M:%S')


def update_html_controls(html_path):
    """
    Update the HTML file with zoom controls.
    """
    with open(html_path) as file:
        soup = bs4.BeautifulSoup(file.read(), 'html.parser')

    soup.script.decompose()
    soup.insert(1, bs4.BeautifulSoup(ANIMATION_HTML, 'html.parser'))

    soup.style.append(ANIMATION_CSS)

    zoom_img = f'<label><input type="checkbox">{soup.div.img}</label>'
    soup.div.img.decompose()
    soup.div.insert(0, bs4.BeautifulSoup(zoom_img, 'html.parser'))

    with open(html_path, 'w') as file:
        file.write(soup.prettify())
