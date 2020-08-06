import ipywidgets as W
import traitlets as T
from ipycytoscape import CytoscapeWidget
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF
import networkx as nx


class VisBase(W.VBox):
    graph = T.Instance(Graph, allow_none=True)
    _vis = T.Instance(W.Box, allow_none=True)
    edge_color = T.Unicode()
    node_color = T.Unicode()
    selected_nodes = T.List()
    selected_edges = T.List()
    hovered_nodes = T.List()
    hovered_edges = T.List()
    layout = T.Any()

    layouts = {
        "circular_layout": nx.layout.circular_layout,
        "random_layout": nx.layout.random_layout,
        "shell_layout": nx.layout.shell_layout,
        "spring_layout": nx.layout.spring_layout,
        "spiral_layout": nx.layout.spiral_layout,
    }

    @T.default("layout")
    def _make_default_layout(self):
        return layouts["circulat_layout"]

    @T.default("edge_color")
    def _make_default_edge_color(self):
        return "pink"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edge_color = kwargs.get("edge_color", "pink")
        self.node_color = kwargs.get("node_color", "grey")
        self.graph = kwargs.get("graph", None)
        self.layout = self.layouts[kwargs.get("layout", "circular_layout")]
