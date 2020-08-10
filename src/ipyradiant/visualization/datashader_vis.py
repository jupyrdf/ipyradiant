import traitlets as T

import holoviews as hv
import ipywidgets as W
from bokeh.models import HoverTool
from holoviews.operation.datashader import bundle_graph
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph

from .base import VisBase

hv.extension("bokeh")


class DatashaderVis(VisBase):
    output = T.Instance(W.Output)
    tooltip = T.Unicode()
    tooltip_dict = T.Dict()
    node_tooltips = T.List()
    edge_tooltips = T.List()

    sparql = """
        CONSTRUCT {
            ?s ?p ?o .
        }
        WHERE {
            ?s ?p ?o .
            FILTER (!isLiteral(?o))
            FILTER (!isLiteral(?s))
        }
        LIMIT 300
    """

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltip = kwargs.get("tooltip", "nodes")
        output_graph = self.strip_and_produce_rdf_graph(self.graph)
        p = self.set_options(output_graph)
        self.display_datashader_vis(p)
        self.children = [
            W.HTML("<h1>Visualization With Datashader"),
            self.output,
        ]

    def display_datashader_vis(self, p):
        with self.output:
            display(p)

    def strip_and_produce_rdf_graph(self, rdf_graph: Graph):
        sparql = self.sparql
        qres = rdf_graph.query(sparql)
        uri_graph = Graph()
        for row in qres:
            uri_graph.add(row)

        new_netx = rdflib_to_networkx_graph(uri_graph)
        original = hv.Graph.from_networkx(new_netx, self.nx_layout,)
        output_graph = bundle_graph(original)
        return output_graph

    def set_options(self, output_graph):
        return output_graph.options(
            frame_width=1000,
            frame_height=1000,
            xaxis=None,
            yaxis=None,
            tools=[self.tooltip_dict[self.tooltip]],
            inspection_policy=self.tooltip,
            node_color=self.node_color,
            edge_color=self.edge_color,
        )

    @T.observe("nx_layout")
    def changed_layout(self, change):
        self.output.clear_output()
        output_graph = self.strip_and_produce_rdf_graph(self.graph)
        p = self.set_options(output_graph)
        self.display_datashader_vis(p)
