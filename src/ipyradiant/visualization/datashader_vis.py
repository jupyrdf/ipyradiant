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

    @T.default("output")
    def _make_default_output(self):
        return W.Output()

    edge_tooltips = [
        ("Source", "@start"),
        ("Target", "@end"),
    ]
    edge_hover = HoverTool(tooltips=edge_tooltips)

    node_tooltips = [
        ("ID", "@index"),
    ]
    node_hover = HoverTool(tooltips=node_tooltips)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tooltip = kwargs.get("tooltip", "nodes")
        tooltip_dict = {"nodes": self.node_hover, "edges": self.edge_hover}
        output_graph = self.strip_and_produce_rdf_graph(self.graph)
        p = output_graph.options(
            frame_width=1000,
            frame_height=1000,
            xaxis=None,
            yaxis=None,
            tools=[tooltip_dict[tooltip]],
            inspection_policy=tooltip,
            node_color=self.node_color,
            edge_color=self.edge_color,
        )
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
