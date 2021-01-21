# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import holoviews as hv
import IPython
import ipywidgets as W
import networkx as nx
import traitlets as T
from bokeh.models import HoverTool
from holoviews import streams
from holoviews.operation.datashader import bundle_graph
from rdflib import Graph, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph

from .base import NXBase

hv.extension("bokeh", logo=False)


class DatashaderVisualizer(NXBase):
    """
    A class for visualization an RDF graph with datashader

    :param graph: an rdflib.graph.Graph object to visualize.
    :param tooltip: takes either 'nodes' or 'edges', and sets the hover tool.
    :param sparql: a query you'd like to perform on the rdflib.graph.Grab object.
    """

    output = T.Instance(W.Output)
    tooltip = T.Unicode(default_value="nodes")
    tooltip_dict = T.Dict()
    node_tooltips = T.List()
    edge_tooltips = T.List()
    sparql = T.Unicode()

    @T.default("output")
    def _make_default_output(self):
        return W.Output()

    @T.default("edge_tooltips")
    def _make_edge_tooltip(self):
        return [
            ("Source", "@start"),
            ("Target", "@end"),
        ]

    @T.default("node_tooltips")
    def _make_node_tooltip(self):
        return [
            ("ID", "@index"),
        ]

    @T.default("tooltip")
    def _make_tooltip(self):
        return "nodes"

    @T.default("tooltip_dict")
    def _make_tooltip_dict(self):
        return {
            "nodes": HoverTool(tooltips=self.node_tooltips),
            "edges": HoverTool(tooltips=self.edge_tooltips),
        }

    @T.default("sparql")
    def _make_sparql(self):
        return """
            CONSTRUCT {
                ?s ?p ?o .
            }
            WHERE {
                ?s ?p ?o .
                FILTER (!isLiteral(?o))
                FILTER (!isLiteral(?s))
            }
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = [self.output]

    def display_datashader_vis(self, p):
        self.output.clear_output()
        with self.output:
            IPython.display.display(p)

    def strip_and_produce_rdf_graph(self, rdf_graph: Graph):
        """
        A function that takes in an rdflib.graph.Graph object
        and transforms it into a datashader holoviews graph.
        Also performs the sparql query on the graph that can be set
        via the 'sparql' parameter
        """

        sparql = self.sparql
        qres = rdf_graph.query(sparql)
        uri_graph = Graph()
        for row in qres:
            uri_graph.add(row)

        new_netx = rdflib_to_networkx_graph(uri_graph)
        original = hv.Graph.from_networkx(
            new_netx, self._nx_layout, **self.graph_layout_params
        )
        output_graph = bundle_graph(original)
        return output_graph

    def set_options(self, output_graph):
        return output_graph.options(
            frame_width=1000,
            frame_height=1000,
            xaxis=None,
            yaxis=None,
            tools=[self.tooltip_dict[self.tooltip], "tap", "box_select"],
            inspection_policy=self.tooltip,
            node_color=self.node_color,
            edge_color=self.edge_color,
        )

    def tap_stream_subscriber(self, x, y):
        nodes_data = self.output_graph.nodes.data
        t = 0.01
        values = nodes_data[nodes_data.x.between(x - t, x + t, True)][
            nodes_data.y.between(y - t, y + t, True)
        ]
        self.selected_nodes = tuple([URIRef(_) for _ in list(values["index"])])

    def box_stream_subscriber(self, **kwargs):
        bounds = kwargs["bounds"]
        nodes_data = self.output_graph.nodes.data
        values = nodes_data[nodes_data.x.between(bounds[0], bounds[2], True)][
            nodes_data.y.between(bounds[1], bounds[3], True)
        ]
        self.selected_nodes = tuple([URIRef(_) for _ in list(values["index"])])

    @T.observe("_nx_layout", "sparql", "graph", "graph_layout_params")
    def changed_layout(self, change):
        self.selected_nodes = []
        if self.graph is None:
            self.output_graph = None
            self.display_datashader_vis(self.output_graph)
        elif len(self.graph) == 0:
            self.output_graph = None
            self.display_datashader_vis("Cannot display blank graph.")
        elif isinstance(self.graph, nx.classes.graph.Graph):
            original = hv.Graph.from_networkx(
                self.graph, self._nx_layout, **self.graph_layout_params
            )
            self.output_graph = bundle_graph(original)
            self.tap_selection_stream = streams.Tap(source=self.output_graph)
            self.tap_selection_stream.add_subscriber(self.tap_stream_subscriber)
            self.box_selection_stream = streams.BoundsXY(source=self.output_graph)
            self.box_selection_stream.add_subscriber(self.box_stream_subscriber)
            self.final_graph = self.set_options(self.output_graph)
            self.display_datashader_vis(self.final_graph)
        else:
            self.output_graph = self.strip_and_produce_rdf_graph(self.graph)
            self.tap_selection_stream = streams.Tap(source=self.output_graph)
            self.tap_selection_stream.add_subscriber(self.tap_stream_subscriber)
            self.box_selection_stream = streams.BoundsXY(source=self.output_graph)
            self.box_selection_stream.add_subscriber(self.box_stream_subscriber)
            self.final_graph = self.set_options(self.output_graph)
            self.display_datashader_vis(self.final_graph)
