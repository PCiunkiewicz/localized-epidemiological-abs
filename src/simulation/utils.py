"""
The `utils` module contains utility classes
and functions which do not fit in elsewhere.
"""

import numpy as np
from matplotlib import colors


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

        for key, val in self.items():
            if isinstance(val, dict):
                self[key] = AttrDict(val)


def mask_color(img, hex_value):
    """
    Generate pixel mask for matching hex color.
    """
    rgb = colors.to_rgb(hex_value)
    pixel_mask = np.all(np.isclose(img, rgb), axis=2)
    return pixel_mask
