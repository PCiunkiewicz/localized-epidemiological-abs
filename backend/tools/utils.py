"""
The `utils` module contains utilities for generating
simulation exports.
"""

import datetime as dt

STATUS_COLOR = {
    'SUSCEPTIBLE': '#ffffff',
    'INFECTED': '#ff0000',
    'RECOVERED': '#00ff00',
    'QUARANTINED': '#ffa500',
    'DECEASED': '#000000',
    'HOSPITALIZED': '#a020f0',
    'UNKNOWN': '#ff00ff',
}


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
