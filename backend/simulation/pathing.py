"""Pathfinding and graph management for the simulation."""

from __future__ import annotations

import gzip
import pickle
from collections import deque
from pathlib import Path
from typing import Self, overload

import igraph as ig
import numpy as np
from backend.utilities.paths import PATHS
from scipy.spatial import KDTree

from utilities.types.pathing import ComputedPaths, Coordinate, Edge, PathSegment

DATA_PATH = Path(__file__).resolve().parent.parent / 'data'


class GraphGrid:
    """Structure for managing a grid-based graph object.

    Attributes:
        n: Number of nodes in the graph.
        nodes: Coordinates of the nodes.
        vertex: Dictionary mapping coordinates to node indices.
        coord: Dictionary mapping node indices to coordinates.
        weights: Weights for the edges.
        edges: List of edges in the graph.
        edge_coords: List of coordinates for the edges.
        graph: igraph object representing the graph.
    """

    def __init__(
        self,
        nodes: np.typing.NDArray,
        r: float = 1,
        spacing: dict = dict(),
        weights: np.typing.NDArray | None = None,
    ) -> None:
        """Initialize the graph with nodes and parameters.

        Args:
            nodes: Coordinates of the nodes.
            r: Maximum radius for edge-query-pair computation.
            spacing: Spacing factors for each axis (adjacency distance).
            weights: Weights for the edges.
        """
        self.n = len(nodes)
        self.nodes = nodes
        self.vertex: dict[tuple, int] = {tuple(x): i for i, x in enumerate(nodes.tolist())}
        self.coord: dict[int, tuple] = {v: k for k, v in self.vertex.items()}
        self.weights = weights
        self._compute_edges(r, spacing)

    def add_edges(self, edges: list[Edge], transform: bool = False) -> None:
        """Register additional edges to the graph.

        Args:
            edges: List of edges to add.
            transform: Transform edges to graph coordinates.
        """
        if transform:
            edges = self.transform(edges)
        self.edges += edges

    def set_weights(self, weights: list[float]) -> None:
        """Set edge weights for subgraph creation and pruning."""
        self.weights = weights

    def prune(self, threshold: float) -> None:
        """Prune graph edges based on a weight threshold."""
        self.edges = [x for i, x in enumerate(self.edges) if self.weights[i] < threshold]
        self.edge_coords = [x for i, x in enumerate(self.edge_coords) if self.weights[i] < threshold]
        self.weights = [x for x in self.weights if x < threshold]

    def build(self) -> None:
        """Create the graph object from edges."""
        self.graph = ig.Graph(self.n, self.edges)

    def pathfind(self, start: Coordinate | int, end: Coordinate | int) -> PathSegment:
        """Find the shortest path between two nodes in the graph.

        Args:
            start: Starting coordinate or vertex id.
            end: Ending coordinate or vertex id.
        """
        if isinstance(start, Coordinate) and isinstance(end, Coordinate):
            start, end = self.vertex[start], self.vertex[end]
        path = self.graph.get_shortest_paths(start, to=end, weights=self.weights)
        return [self.coord[i] for i in path[0]]

    def transform(self, other: GraphGrid) -> list[Edge]:
        """Transform edges from another graph to this graph's coordinates."""
        return [self.convert(edge) for edge in other.edge_coords]

    @overload
    def convert(self, edge: Edge[int]) -> Edge[Coordinate]: ...
    @overload
    def convert(self, edge: Edge[Coordinate]) -> Edge[int]: ...
    def convert(self, edge: Edge) -> Edge:
        """Convert edge coordinates to graph vertex indices or vice versa."""
        start, end = edge
        if isinstance(edge, Coordinate) and isinstance(end, Coordinate):
            return (self.vertex[start], self.vertex[end])
        elif isinstance(start, int) and isinstance(end, int):
            return (self.coord[start], self.coord[end])
        raise ValueError(f'Invalid edge type: {type(edge)}')

    def _compute_edges(self, r: float, spacing: dict) -> None:
        """Compute edges based on the node coordinates and spacing adjacency."""
        spaced_nodes = self.nodes.copy()
        for axis, factor in spacing.items():
            spaced_nodes[:, axis] *= factor
        tree = KDTree(spaced_nodes)
        self.edges = sorted(tree.query_pairs(r=r, p=1))
        self.edge_coords = [(self.coord[a], self.coord[b]) for a, b in self.edges]


class OptimizedPathfinder:
    """Optimized pathfinding solver for the simulation.

    Attributes:
        paths: Dictionary of paths between nodes.
        transit_paths: Dictionary of transit paths between nodes.
    """

    def __init__(self, paths: ComputedPaths, transit_paths: ComputedPaths) -> None:
        """Initialize the pathfinder with computed paths and transit paths.

        Args:
            paths: Dictionary of paths between nodes.
            transit_paths: Dictionary of paths between transit nodes.
        """
        self.paths = paths
        self.transit_paths = transit_paths

    @classmethod
    def load(cls, name: str) -> Self:
        """Load the pathfinder from a compressed file by name."""
        with gzip.open(PATHS / f'{name}.gz', 'rb') as f:
            return cls(**pickle.load(f))

    def save(self, name: str) -> None:
        """Save the pathfinder to a compressed file with the given name."""
        with gzip.open(PATHS / f'{name}.gz', 'wb', compresslevel=1) as f:
            pickle.dump({'paths': self.paths, 'transit_paths': self.transit_paths}, f)

    def get_segment(self, start: Coordinate, end: Coordinate, transit: bool = False) -> PathSegment:
        """Get the precomputed path segment between two nodes."""
        lookup = self.paths if not transit else self.transit_paths
        try:
            return lookup[start][end]
        except KeyError:
            return lookup[end][start][::-1]

    def pathfind(self, start: Coordinate, end: Coordinate) -> PathSegment:
        """Construct a path between two nodes using precomputed segments and transit node routing."""
        if start == end:
            return deque([start])

        first_transit = self.paths[start]['transit']
        last_transit = self.paths[end]['transit']

        path = []
        if start != first_transit:
            path += self.get_segment(start, first_transit)
        if first_transit != last_transit:
            transit_path = self.get_segment(first_transit, last_transit, transit=True)
            for a, b in zip(transit_path, transit_path[1:]):
                segment = self.get_segment(a, b)
                path += segment[:-1]
            path += segment[-1:]
        if last_transit != end:
            path += self.get_segment(last_transit, end)

        return deque(path)
