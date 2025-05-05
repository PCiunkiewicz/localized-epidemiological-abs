"""Type definitions for pathing related structures."""

from collections import deque

Coordinate = tuple[int, int, int]
type Edge[T: Coordinate | int] = tuple[T, T]
PathSegment = list[Coordinate] | deque[Coordinate]
ComputedPaths = dict[Coordinate, dict[Coordinate, PathSegment]]
