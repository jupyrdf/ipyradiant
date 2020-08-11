import traitlets as T

import holoviews as hv
import IPython
import ipywidgets as W
from bokeh.models import HoverTool
from holoviews.operation.datashader import bundle_graph
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph

from .base import NXBase


class DatashaderVis(NXBase):
    output = T.Instance(W.Output)
    tooltip = T.Unicode(default_value="nodes")
    tooltip_dict = T.Dict()
    node_tooltips = T.List()
    edge_tooltips = T.List()
    sparql = T.Unicode()

    @T.default("output")
    def _make_default_output(self):
        output = W.Output()
        with output:
            hv.extension("bokeh")
        output.clear_output()
        return output

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
            LIMIT 300
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = [self.output]

    def display_datashader_vis(self, p):
        self.output.clear_output()
        with self.output:
            IPython.display.display(p)

    def strip_and_produce_rdf_graph(self, rdf_graph: Graph):
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
            tools=[self.tooltip_dict[self.tooltip]],
            inspection_policy=self.tooltip,
            node_color=self.node_color,
            edge_color=self.edge_color,
        )

    @T.observe("_nx_layout", "sparql", "graph", "graph_layout_params")
    def changed_layout(self, change):
        output_graph = self.strip_and_produce_rdf_graph(self.graph)
        p = self.set_options(output_graph)
        self.display_datashader_vis(p)
