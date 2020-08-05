import networkx as nx
import traitlets as T
import ipywidgets as W
from ipyradiant import LoadWidget
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import holoviews as hv
from holoviews.operation.datashader import datashade, bundle_graph, dynspread
import ipycytoscape
from bokeh.models import HoverTool
import bokeh.models.widgets as bk
import jupyter_bokeh as jbk
from bokeh.plotting import figure

hv.extension("bokeh")


class DatashaderVis(VisBase):
    edge_tooltips = [
        ("Source", "@start"),
        ("Target", "@end"),
    ]
    edge_hover = HoverTool(tooltips=edge_tooltips)

    node_tooltips = [
        ("ID", "@index"),
    ]
    node_hover = HoverTool(tooltips=node_tooltips)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        output_graph = strip_and_produce_rdf_graph(self.graph)
        p = hv.render(
            output_graph.options(
                frame_width=1000,
                frame_height=1000,
                xaxis=None,
                yaxis=None,
                tools=[node_hover],
            ),
            backend="bokeh",
        )
        widget_output = jbk.BokehModel(p)

    def strip_and_produce_rdf_graph(self, rdf_graph: Graph):
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
        qres = rdf_graph.query(sparql)
        uri_graph = Graph()
        for row in qres:
            uri_graph.add(row)

        new_netx = rdflib_to_networkx_graph(uri_graph)

        original = hv.Graph.from_networkx(new_netx, nx.layout.circular_layout,)
        output_graph = bundle_graph(original)
        return output_graph
