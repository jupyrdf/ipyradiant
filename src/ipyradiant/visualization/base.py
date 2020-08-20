# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import types

import traitlets as T

import ipywidgets as W
import networkx as nx
from rdflib import Graph, URIRef


class VisualizerBase(W.VBox):
    """
    The basic Visualization class that takes the shape of an ipywidgets.VBox

    :param graph: an rdflib.graph.Graph object to visualize.
    :param edge_color: a string, the desired color of edges.
    :param node_color: a string, the desired color of nodes.
    :param selected_nodes: a tuple of URIRefs of nodes currently selected either via tap or box select.
    :param selected_edges: a list of edges currently selected, currently only working with ipycytoscape.
    """

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


class NXBase(VisualizerBase):
    """
    The visualization class for the NXLayouts. Used by the datashader visualizations.

    :param _nx_layout: the desired networkx layout to be used.
    :param _layouts: a dictionary mapping all the possible layouts to the corresponding networkx functions.
    """

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
