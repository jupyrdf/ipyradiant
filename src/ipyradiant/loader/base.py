# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.


import ipywidgets as W
import traitlets as T
from rdflib import BNode, Graph

from .util import guess_format


class BaseLoader(W.Widget):
    """Base class for loaders.

    Uses the metadata format from FileUpload
    """

    description = T.Unicode()
    graph = T.Instance(Graph)
    graph_id = T.Instance(BNode)
    file_upload_value = T.Dict()
    log = W.Output()

    @T.default("graph")
    def make_default_graph(self):
        return Graph()

    @T.default("graph_id")
    def make_default_graph_id(self):
        return self.graph.identifier

    @T.observe("file_upload_value")
    def process_files(self, change):
        """load a single graph from upload metadata

        TODO: support multiple graphs as a ConjunctiveGraph
        """
        g = Graph()

        for file_name, data in change.new.items():
            file_format = guess_format(file_name)
            g.parse(data=data["content"], format=file_format)

        self.graph = g
        self.graph_id = g.identifier
