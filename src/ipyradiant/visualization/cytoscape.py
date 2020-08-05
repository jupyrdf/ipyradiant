from pathlib import Path

import traitlets as T

import ipywidgets as W
from ipycytoscape import CytoscapeWidget
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

# from .base import VisBase


class CytoscapeVisualization(W.Box):
    graph = T.Instance(Graph, allow_none=True)
    cyto_widget = T.Instance(CytoscapeWidget, allow_none=True)
    nodes = T.List()
    click_output = T.Instance(W.Output)
    click_output_box = T.Instance(W.VBox)
    show_outputs = T.Bool(False)
    log = W.Output(layout={"border": "1px solid black"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edge_color = kwargs.get("edge_color", "pink")
        self.node_color = kwargs.get("node_color", "grey")
        self.output_title = W.HTML("<h3>Output from Clicks</h3>")
        self.click_output_box.children = [self.output_title, self.click_output]

        self.default_edge = {"selector": "edge", "css": {"line-color": self.edge_color}}
        self.default_node = {
            "selector": "node",
            "css": {"background-color": self.node_color},
        }

        T.dlink(
            (self, "show_outputs"),
            (self.click_output_box.layout, "visibility"),
            lambda x: "visible" if x else "hidden",
        )
        self.layout = W.Layout(flex_flow="row wrap")
        self.children = [self.cyto_widget, self.click_output_box]

    @T.default("click_output")
    def _make_click_output(self):
        return W.Output()

    @T.default("nodes")
    def _make_default_nodes(self):
        return []

    @T.default("click_output_box")
    def _make_default_click_output_box(self):
        return W.VBox()

    @T.default("node_selector_box")
    def _make_node_selector_box(self):
        return W.VBox()

    @T.default("cyto_widget")
    def _make_default_cyto_widget(self):
        cyto_widget = CytoscapeWidget()
        cyto_widget.on("node", "click", self.log_node_clicks)
        cyto_widget.on("edge", "click", self.log_edge_clicks)
        cyto_widget.set_style([self.default_node, self.default_edge])
        return cyto_widget

    def log_node_clicks(self, node):
        with self.click_output:
            print(f"node clicked: {node['data']}")
            print("-------------------------------")

    def log_edge_clicks(self, edge):
        with self.click_output:
            print("edge clicked:")
            print(f'edge source: {edge["data"]["source"]}')
            print(f'edge target: {edge["data"]["target"]}')
            print("-------------------------------")

    @T.observe("graph")
    def update_cyto_widget_graph(self, change):
        # TODO configure vis tool with replace=True/False
        # remove old nodes (which removed other links, e.g. edges)
        for node in list(self.cyto_widget.graph.nodes):
            self.cyto_widget.graph.remove_node(node)
        if len(self.cyto_widget.graph.nodes) != 0:
            with self.log:
                print("Unexpected number of nodes remaining after graph cleared.")
        # assert not self.cyto_widget.graph.nodes, "Unexpected number of nodes remaining after graph cleared."
        new_json = self.build_cytoscape_json(change.new)
        self.cyto_widget.graph.add_graph_from_json(new_json, directed=True)

    # # TODO:
    # Why are there missing edges, etc in the graph and why does it look wrong
    # do we want the check for object not being literal ???
    # LINK TO ISSUE: https://github.com/jupyrdf/ipyradiant/issues/16

    def build_cytoscape_json(self, graph: Graph):
        # collect uris & edges
        element_set = set()
        edges = []
        for i, (s, p, o) in enumerate(graph):
            if p != RDF.type:
                if isinstance(s, URIRef):
                    element_set.add(s)
                if isinstance(o, URIRef):
                    element_set.add(o)
                if not isinstance(o, Literal):
                    edges.append({"source": s, "target": o, "label": Path(p).name})
            # edges.append(
            #     {"source":s, "target":o, "label":f"{Path(p).name}",}
            # )
            # above comment also applies to issue #16, link above on line 93

        # create nodes
        nodes = {}
        for uri in element_set:
            pathed_node = Path(uri)
            nodes[uri] = {
                "id": uri,
                "name": f"{pathed_node.parent.name} {pathed_node.name}",
            }

        return {
            "nodes": [{"data": v} for v in nodes.values()],
            "edges": [{"data": v} for v in edges],
        }
