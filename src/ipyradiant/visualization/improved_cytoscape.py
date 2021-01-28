# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import ipycytoscape as cyto
import ipywidgets as W
import networkx as nx
import rdflib
import traitlets as T
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

STYLE = [
    {
        "selector": "node",
        "css": {
            "color": "black",
            "background-color": "CadetBlue",
        },
    },
    {
        "selector": "edge.directed",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "grey",
        },
    },
    {"selector": "edge.multiple_edges", "style": {"curve-style": "bezier"}},
]


class CytoscapeViewer(W.VBox):
    layouts = T.List()
    layout_selector = T.Instance(W.Dropdown)
    cytoscape_widget = T.Instance(cyto.CytoscapeWidget)
    data = T.Union(
        (
            T.Instance(rdflib.Graph),
            T.Instance(nx.MultiDiGraph),
            T.Instance(nx.DiGraph),
            T.Instance(nx.Graph),
        )
    )
    cyto_layout = T.Unicode()
    cyto_style = T.List()

    @T.default("cyto_style")
    def _make_cyto_style(self):
        return STYLE

    @T.default("cyto_layout")
    def _make_default_layout(self):
        return "cola"

    @T.default("data")
    def _make_default_graph(self):
        return None

    @T.observe("data")
    def _update_data(self, change):
        # TODO: Clear Graph so that it isn't duplicated
        if isinstance(self.data, nx.MultiDiGraph) or isinstance(self.data, nx.Graph):
            self.cytoscape_widget.graph.add_graph_from_networkx(self.data)
        if isinstance(self.data, rdflib.Graph):
            nx_graph = rdflib_to_networkx_multidigraph(self.data)
            self.cytoscape_widget.graph.add_graph_from_networkx(nx_graph)

    @T.default("cytoscape_widget")
    def _make_cytoscape_widget(self):
        return cyto.CytoscapeWidget()

    @T.default("layouts")
    def _make_layouts(self):
        return ["cola", "concentric", "grid", "circle"]

    @T.default("layout_selector")
    def _make_layout_selector(self):
        return W.Dropdown(options=self.layouts)

    @T.observe("layouts")
    def _update_layout_selector(self, change):
        self.layout_selector = self._make_layout_selector()

    @T.observe("cyto_layout")
    def _update_layout(self, change):
        self.cytoscape_widget.set_layout(name=self.cyto_layout)

    @T.observe("cyto_style")
    def _update_style(self, change):
        self.cytoscape_widget.set_style(self.cyto_style)

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (
                self.layout_selector,
                self.cytoscape_widget,
            )
        return children

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        T.link((self.layout_selector, "value"), (self, "cyto_layout"))
        self.cytoscape_widget.set_style(self.cyto_style)
