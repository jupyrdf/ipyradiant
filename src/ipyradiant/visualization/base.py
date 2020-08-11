import types

import traitlets as T

import ipywidgets as W
import networkx as nx
from rdflib import Graph, URIRef


class VisBase(W.VBox):
    graph = T.Instance(Graph, allow_none=True)
    _vis = T.Instance(W.Box, allow_none=True)
    edge_color = T.Unicode(default_value="pink")
    node_color = T.Unicode(default_value="grey")
    selected_nodes = W.trait_types.TypedTuple(trait=T.Instance(URIRef))
    selected_edges = T.List()
    hovered_nodes = W.trait_types.TypedTuple(trait=T.Instance(URIRef))
    hovered_edges = T.List()
    graph_layout = T.Unicode()
    graph_layout_options = W.trait_types.TypedTuple(trait=T.Unicode())
    graph_layout_params = T.Dict()

    @T.default("graph_layout_params")
    def make_params(self):
        return {}


class NXBase(VisBase):
    _layouts = {
        "Kamada Kawai": nx.kamada_kawai_layout,
        "Circular": nx.circular_layout,
        "Planar": nx.planar_layout,
        "Random": nx.random_layout,
        "Shell": nx.shell_layout,
        "Spectral": nx.spectral_layout,
        "Spiral": nx.spiral_layout,
        "Spring": nx.spring_layout,
        # "Bipartite": nx.bipartite_layout,
        # "Rescale": nx.rescale_layout,
    }

    _nx_layout = T.Instance(types.FunctionType)

    @T.default("graph_layout_options")
    def _make_default_options(self):
        return tuple(self._layouts.keys())

    @T.default("graph_layout")
    def _make_default_layout(self):
        return self.graph_layout_options[0]

    @T.observe("graph_layout")
    def _update_graph_layout(self, change):
        self._nx_layout = self._layouts[self.graph_layout]

    @T.default("_nx_layout")
    def set_default_nx_layout(self):
        return self._layouts[self.graph_layout]
