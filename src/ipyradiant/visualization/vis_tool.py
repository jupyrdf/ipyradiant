import os
import textwrap
from pathlib import Path
from rdflib import URIRef, Literal, Graph
import traitlets as T
from rdflib.namespace import RDF
from pandas import DataFrame
from .rdf_processer import CytoscapeGraph
import ipywidgets as W
from ipycytoscape import MutableDict, CytoscapeWidget

default_edge={
    'selector': 'edge',
    'css': {
        'line-color': 'blue'
    }
}

default_node={
    'selector': 'node',
    'css': {
        'background-color': 'grey'
    }
}

class RDFVisualization(W.GridBox):
    graph = T.Instance(Graph, allow_none=True)
    cyto_widget = T.Instance(CytoscapeWidget, allow_none=True)
    nodes = T.List()
    click_output = T.Instance(W.Output)
    click_output_box = T.Instance(W.VBox)
    selected_node = T.Unicode(allow_none=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output_title = W.HTML('<h3>Output from Clicks</h3>')
        self.layout=W.Layout(grid_template_columns="60% 40%",height='500px',border='solid 2px')

        self.click_output_box.children = [self.output_title,self.click_output]
        self.children = [self.cyto_widget, self.click_output_box]

    @T.default('click_output')
    def _make_click_output(self):
        return W.Output()

    @T.default('nodes')
    def _make_default_nodes(self):
        return []

    @T.default('click_output_box')
    def _make_default_click_output_box(self):
        return W.VBox()

    @T.default('node_selector_box')
    def _make_node_selector_box(self):
        return W.VBox()

    @T.default('cyto_widget')
    def _make_default_cyto_widget(self):
        cyto_widget = CytoscapeWidget()
        cyto_widget.on('node', 'click', self.log_node_clicks)
        cyto_widget.on('edge', 'click', self.log_edge_clicks)
        cyto_widget.set_style([default_node, default_edge])
        return cyto_widget

    def log_node_clicks(self,node):
        with self.click_output:
            print(f"node clicked: {node['data']}")
            print('-------------------------------')

    def log_edge_clicks(self,edge):
        with self.click_output:
            print(f'edge clicked:')
            print(f'edge source: {edge["data"]["source"]}')
            print(f'edge target: {edge["data"]["target"]}')
            print('-------------------------------')

    @T.observe("graph")
    def update_cyto_widget_graph(self, change):
        # TODO configure vis tool with replace=True/False
        # remove old nodes (which removed other links, e.g. edges)
        # TODO why does this have to be called twice???
        ii = 0
        while len(self.cyto_widget.graph.nodes) > 0:
            [self.cyto_widget.graph.remove_node(node) for node in
             self.cyto_widget.graph.nodes]
            ii += 1
            if ii > 100:
                break
        assert len(self.cyto_widget.graph.nodes) == 0, "OHNO"
        new_json = build_cytoscape_json(change.new)
        self.cyto_widget.graph.add_graph_from_json(new_json, directed=True)





# # TODO:
# Why are there missing edges, etc in the graph and why does it look wrong

def build_cytoscape_json(graph: Graph):
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
                edges.append(
                    {"source": s, "target": o, "label": f"{Path(p).name}",}
                )

    # create nodes
    nodes = {}
    for uri in element_set:
        pathed_node = Path(uri)
        nodes[uri] = {
            "id": uri,
            "name": f"{pathed_node.parent.name} {pathed_node.name}",
        }

    return {
        "nodes": [{"data":v} for v in nodes.values()],
        "edges": [{"data":v} for v in edges]
    }
