# -*- coding: utf-8 -*-
from .util import SQRT2


def manhattan(dx, dy):
    """manhattan heuristics"""
    return dx + dy


def octile(dx, dy):
    f = SQRT2 - 1
    if dx < dy:
        return f * dx + dy
    else:
        return f * dy + dx
