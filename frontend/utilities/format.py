"""Utility functions for streamlit app options."""

from utilities.api import get_obj


def options(model: str, label: str = 'name') -> list[str]:
    """Get ids and names for a given model."""
    try:
        return [''] + [f'{x["id"]} - {x[label]}' for x in get_obj(model).json()]
    except TypeError:
        return ['']


def id_(option: str) -> str:
    """Get id from an option."""
    return option.split(' - ')[0]


def name_(option: str) -> str:
    """Get name from an option."""
    return option.split(' - ')[1]
