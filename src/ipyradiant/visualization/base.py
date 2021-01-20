# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import types

import ipywidgets as W
import networkx as nx
import networkx.drawing.layout as nx_layout
import traitlets as T
from rdflib import Graph, URIRef


class VisualizerBase(W.VBox):
    """
    The basic Visualization class that takes the shape of an ipywidgets.VBox

    :param graph: an rdflib.graph.Graph object or a networkx.classes.graph.Graph object to visualize.
    :param edge_color: a string, the desired color of edges.
    :param node_color: a string, the desired color of nodes.
    :param selected_nodes: a tuple of URIRefs of nodes currently selected either via tap or box select.
    :param selected_edges: a list of edges currently selected, currently only working with ipycytoscape.
    """

    graph = T.Union(
        (T.Instance(Graph), T.Instance(nx.classes.graph.Graph)), allow_none=True
    )
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

    :param _nx_layout: the desired networkx layout function to be used.
    :param _layouts: a dictionary mapping labels of known layouts to networkx functions.

    Notes:
      - not all networkx layouts work without custom node/edge data or graph_layout_params
        and are NOT_HANDLED by default, but can be set explicitly
    """

    NOT_HANDLED = [
        "bipartite_layout",
        "multipartite_layout",
        "rescale_layout",
    ]

    _layouts = T.Dict()

    _nx_layout = T.Instance(types.FunctionType)

    @T.default("graph_layout_options")
    def _make_default_options(self):
        return tuple(self._layouts)

    @T.default("_layouts")
    def _make_default_layouts(self):
        """these are leniently loaded, as the exact set of algorithms depends
        heavily on the version of networkx installed
        """
        layouts = {}
        for layout_key in nx_layout.__all__:
            if layout_key in self.NOT_HANDLED:
                continue
            try:
                layout = getattr(nx_layout, layout_key)
                label = _make_nx_layout_label(layout_key)
                layouts[label] = layout
            except Exception as err:
                self.log.warning(
                    "Expected to be able to load from networkx: %s\n%s", layout_key, err
                )
        return layouts

    @T.default("graph_layout")
    def _make_default_layout(self):
        return self.graph_layout_options[0]

    @T.default("_nx_layout")
    def set_default_nx_layout(self):
        return self._layouts[self.graph_layout]

    @T.observe("graph_layout")
    def _update_graph_layout(self, change):
        if change.new is None:
            self._nx_layout = sorted(self._layouts.items())[0][1]
            return

        if change.new in self._layouts:
            self._nx_layout = self._layouts[self.graph_layout]
            return

        try:
            self._nx_layout = getattr(nx_layout, change.new)
        except Exception as err:
            self.log.warning("Could not load from networkx: %s\n%s", change.new, err)


def _make_nx_layout_label(layout_key):
    words = layout_key.replace("_layout", "").split("_")
    titled = [w[0].upper() + w[1:] for w in words]
    return " ".join(titled)
