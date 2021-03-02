# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

from pathlib import Path

import ipywidgets as W
import traitlets as T
from ipycytoscape import CytoscapeWidget
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from ..base import VisualizerBase


class CytoscapeVisualizer(VisualizerBase):
    """
    A visualization class for visualizing an rdflib.graph.Graph object via ipycytoscape.

    :param graph: an rdflib.graph.Graph object
    :param show_outputs: a boolean, decides whether or not to show feedback from clicks on the graph.
    :param cyto_widget: the actual ipycytoscape visualization.
    """

    cyto_widget = T.Instance(CytoscapeWidget, allow_none=True)
    nodes = T.List()
    click_output = T.Instance(W.Output)
    click_output_box = T.Instance(W.VBox)
    show_outputs = T.Bool(False)
    log = W.Output(layout={"border": "1px solid black"})
    node_style = T.Dict()
    edge_style = T.Dict()

    @T.default("click_output")
    def _make_click_output(self):
        return W.Output()

    @T.default("node_style")
    def _make_default_node(self):
        return {
            "selector": "node",
            "css": {"background-color": self.node_color},
        }

    @T.default("edge_style")
    def _make_default_edge(self):
        return {"selector": "edge", "css": {"line-color": self.edge_color}}

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
        cyto_widget = CytoscapeWidget(
            box_select_enabled=True,
        )
        cyto_widget.on("node", "click", self.log_node_clicks)
        cyto_widget.on("edge", "click", self.log_edge_clicks)
        cyto_widget.on("node", "boxselect", self.log_box_select)

        cyto_widget.set_style([self.node_style, self.edge_style])
        return cyto_widget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_title = W.HTML("<h3>Output from Clicks</h3>")
        self.click_output_box.children = [self.output_title, self.click_output]

        T.dlink(
            (self, "show_outputs"),
            (self.click_output_box.layout, "visibility"),
            lambda x: "visible" if x else "hidden",
        )

        if self.show_outputs is True:
            self.children = [
                self.cyto_widget,
                self.click_output_box,
            ]
        else:
            self.children = [
                self.cyto_widget,
            ]

    def log_node_clicks(self, node):
        self.selected_nodes = tuple([URIRef(node["data"]["id"])])
        with self.click_output:
            print(f"node clicked: {node['data']}")
            print("-------------------------------")

    def log_edge_clicks(self, edge):
        self.selected_edges.append(edge["data"])
        with self.click_output:
            print("edge clicked:")
            print(f'edge source: {edge["data"]["source"]}')
            print(f'edge target: {edge["data"]["target"]}')
            print("-------------------------------")

    def log_box_select(self, arg):
        with self.click_output:
            print(arg)

    @T.observe("graph")
    def update_cyto_widget_graph(self, change):
        try:
            self.cyto_widget.headless = True
            for edge in list(self.cyto_widget.graph.edges):
                try:
                    self.cyto_widget.graph.remove_edge(edge)
                except Exception as err:
                    with self.log:
                        print(f"error removing node {edge}:\n{err}")

            for node in list(self.cyto_widget.graph.nodes):
                try:
                    self.cyto_widget.graph.remove_node(node)
                except Exception as err:
                    with self.log:
                        print(f"error removing node {node}:\n{err}")

            if len(self.cyto_widget.graph.nodes) != 0:
                with self.log:
                    print("Unexpected number of nodes remaining after graph cleared.")
        finally:
            self.cyto_widget.headless = False
        new_json = self.build_cytoscape_json(change.new)
        self.cyto_widget.graph.add_graph_from_json(new_json, directed=True)

    def build_cytoscape_json(self, graph: Graph):
        """
        A function to build the specific json format that
        ipycytoscape reads. Takes in an rdflib.graph.Graph object as
        a parameter.
        """
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
