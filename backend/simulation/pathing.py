import gzip
import pickle
from collections import deque
from pathlib import Path

import igraph as ig
from scipy.spatial import KDTree

DATA_PATH = Path(__file__).resolve().parent.parent / 'data'


class GraphGrid:
    def __init__(self, nodes, r=1, spacing=dict(), weights=None):
        self.n = len(nodes)
        self.nodes = nodes
        self.vertex = {tuple(x): i for i, x in enumerate(nodes)}
        self.coord = {v: k for k, v in self.vertex.items()}
        self.weights = weights
        self._compute_edges(r, spacing)

    def _compute_edges(self, r, spacing):
        spaced_nodes = self.nodes.copy()
        for axis, factor in spacing.items():
            spaced_nodes[:, axis] *= factor
        tree = KDTree(spaced_nodes)
        self.edges = sorted(tree.query_pairs(r=r, p=1))
        self.edge_coords = [(self.coord[a], self.coord[b]) for a, b in self.edges]

    def add_edges(self, edges, transform=False):
        if transform:
            edges = self.transform(edges)
        self.edges += edges

    def set_weights(self, weights):
        self.weights = weights

    def create_graph(self):
        self.graph = ig.Graph(self.n, self.edges)

    def pathfind(self, start, end):
        if isinstance(start, tuple) and isinstance(end, tuple):
            start, end = self.vertex[start], self.vertex[end]
        path = self.graph.get_shortest_paths(start, to=end, weights=self.weights)
        return [self.coord[i] for i in path[0]]

    def convert(self, edge):
        start, end = edge
        if isinstance(start, tuple) and isinstance(end, tuple):
            return (self.vertex[start], self.vertex[end])
        elif isinstance(start, int) and isinstance(end, int):
            return (self.coord[start], self.coord[end])

    def transform(self, other):
        return [self.convert(edge) for edge in other.edge_coords]


class OptimizedPathfinder:
    def __init__(self, paths, transit_paths, nodes):
        self.paths = paths
        self.transit_paths = transit_paths
        self.nearest_transit = nodes

    def pathfind(self, start, end):
        if start == end:
            return deque([start])

        first_transit = self.nearest_transit[start]
        last_transit = self.nearest_transit[end]

        path = []
        if start != first_transit:
            path += self.paths[start][first_transit]
        if first_transit != last_transit:
            transit_path = self.transit_paths[first_transit][last_transit]
            for a, b in zip(transit_path, transit_path[1:]):
                segment = self.paths[a][b]
                path += segment[:-1]
            path += segment[-1:]
        if last_transit != end:
            path += self.paths[last_transit][end]

        return deque(path)

    def save(self, name):
        with gzip.open(f'data/paths/{name}.gz', 'wb', compresslevel=1) as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, name):
        with gzip.open(f'data/paths/{name}.gz', 'rb') as f:
            return pickle.load(f)
