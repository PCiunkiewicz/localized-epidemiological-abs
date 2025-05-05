"""Miscellaneous utility functions for simulation."""

import numpy as np
from matplotlib import colors


def mask_color(img: np.typing.NDArray, hex_value: str) -> np.typing.NDArray:
    """Generate pixel mask for matching hex color.

    Args:
        img: Image array to search for the color.
        hex_value: Hexadecimal color value to match (e.g., '#AAAAAA').

    Returns:
        pixel_mask: Boolean mask array where `img ~= color`.
    """
    rgb = colors.to_rgb(hex_value)
    pixel_mask = np.all(np.isclose(img, rgb), axis=-1)
    return pixel_mask
