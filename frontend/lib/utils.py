"""
Utility functions for streamlit demos
"""
from lib.api import get_obj


def options(model, label='name'):
    """
    Get ids and names for a given model
    """
    try:
        return [''] + [f'{x["id"]} - {x[label]}' for x in get_obj(model).json()]
    except TypeError:
        return ['']


def id_(option):
    """
    Get id from an option
    """
    return option.split(' - ')[0]


def name_(option):
    """
    Get name from an option
    """
    return option.split(' - ')[1]
