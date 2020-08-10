import traitlets as T

import ipywidgets as W
import networkx as nx
from rdflib import Graph

LAYOUTS = {
    "circular_layout": nx.circular_layout,
    "random_layout": nx.random_layout,
    "shell_layout": nx.shell_layout,
    "spring_layout": nx.spring_layout,
    "spiral_layout": nx.spiral_layout,
}


class VisSelector(W.Dropdown):
    global LAYOUTS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = LAYOUTS.keys()
        self.disabled = False


# visbase layout widgets
# make visbase layouts global, dropdown/select
# better for user experience
class VisBase(W.VBox):
    graph = T.Instance(Graph, allow_none=True)
    _vis = T.Instance(W.Box, allow_none=True)
    edge_color = T.Unicode()
    node_color = T.Unicode()
    selected_nodes = T.List()
    selected_edges = T.List()
    hovered_nodes = T.List()
    hovered_edges = T.List()
    nx_layout = T.Any()
    layout_choice = T.Unicode()

    global LAYOUTS

    @T.observe("layout_choice")
    def _update_layout(self, change):
        self.nx_layout = LAYOUTS[self.layout_choice]

    @T.default("edge_color")
    def _make_default_edge_color(self):
        return "pink"

    @T.default("nx_layout")
    def _make_default_layout(self):
        return nx.circular_layout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edge_color = kwargs.get("edge_color", "pink")
        self.node_color = kwargs.get("node_color", "grey")
        self.graph = kwargs.get("graph", None)
        self.nx_layout = LAYOUTS[kwargs.get("nx_layout", "circular_layout")]
