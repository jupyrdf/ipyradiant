import datashader as ds
import datashader.transfer_functions as tf
from datashader.layout import random_layout, circular_layout, forceatlas2_layout
from datashader.bundling import connect_edges, hammer_bundle
from rdflib import Graph
import networkx as nx
import ipywidgets as W
import traitlets as T
from pandas import DataFrame
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph


class DatashaderVisualization(W.VBox):
    """
    This is a class that will tentatively take in an RDF graph and return a
    datashader visualization of said file. the process will be rdf.Graph --> networkx --> DatashaderVisualization
    """

    graph = T.Instance(Graph)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = W.HTML("<h1>Datashader Vis</h1>")
        self.children = [self.title]


#     @T.observe("graph")
#     def update_datashader(self,*_):
#         networkx_graph = self.rdf_netx()
#         self.datashader_vis = self.nx_plot(networkx_graph)
#
#     def rdf_netx(self):
#         netx_graph = rdflib_to_networkx_graph(self.graph)
#         return netx_graph
#
#     def ng(self, graph, name):
#         graph.name = name
#         return graph
#
#     def nx_layout(self, graph):
#         layout = nx.circular_layout(graph)
#         data = [[node]+layout[node].tolist() for node in graph.nodes]
#
#         nodes = DataFrame(data, columns=['id', 'x', 'y'])
#         nodes.set_index('id', inplace=True)
#
#         edges = DataFrame(list(graph.edges), columns=['source', 'target'])
#         return nodes, edges
#
#     def nx_plot(self, graph, name=""):
#         print(graph.name, len(graph.edges))
#         nodes, edges = self.nx_layout(graph)
#
#         direct = connect_edges(nodes, edges)
#         bundled_bw005 = hammer_bundle(nodes, edges)
#         bundled_bw030 = hammer_bundle(nodes, edges, initial_bandwidth=0.30)
#
#         return [graphplot(nodes, direct,         graph.name),
#                 graphplot(nodes, bundled_bw005, "Bundled bw=0.05"),
#                 graphplot(nodes, bundled_bw030, "Bundled bw=0.30")]
#
# def nodesplot(nodes, name=None, canvas=None, cat=None):
#     canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
#     aggregator=None if cat is None else ds.count_cat(cat)
#     agg=canvas.points(nodes,'x','y',aggregator)
#     return tf.spread(tf.shade(agg, cmap=["#FF3333"]), px=3, name=name)
#
# def edgesplot(edges, name=None, canvas=None):
#     canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
#     return tf.shade(canvas.line(edges, 'x','y', agg=ds.count()), name=name)
#
# def graphplot(nodes, edges, name="", canvas=None, cat=None):
#     if canvas is None:
#         xr = nodes.x.min(), nodes.x.max()
#         yr = nodes.y.min(), nodes.y.max()
#         canvas = ds.Canvas(x_range=xr, y_range=yr, **cvsopts)
#
#     np = nodesplot(nodes, name + " nodes", canvas, cat)
#     ep = edgesplot(edges, name + " edges", canvas)
#     return tf.stack(ep, np, how="over", name=name)
