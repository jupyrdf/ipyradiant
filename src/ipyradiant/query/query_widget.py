""" the main query widget
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import re

import IPython
import ipywidgets as W
import traitlets as T
from pandas import DataFrame
from rdflib import Graph, URIRef

from .namespace_manager import collapse_namespace
from .query_constructor import QueryConstructor
from .utils import service_patch_rdflib


class QueryWidget(W.VBox):
    """
    TODO
      - use SPARQLQueryFramer?
      - link select and limit/offset (only needs to be visible for SELECT queries)
      - store namespace info intelligently
      - process longer (via path edges) namespaces first (most reductive to least reductive)
      - error displays or output panel
    """

    # namespace pattern
    NS_PATTERN = re.compile(r"PREFIX ([\w]*): <(.+)>")

    graph = T.Instance(Graph)
    run_button = T.Instance(W.Button)
    log = W.Output(layout={"border": "1px solid black"})
    grid = T.Instance(W.Output)
    current_dataframe = T.Instance(DataFrame)

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if graph is not None:
            self.graph = graph
        self.query_constructor = QueryConstructor()
        self.children = [self.query_constructor, self.run_button, self.grid]

    @log.capture(clear_output=True)
    def run_query(self, button):
        # Get all namespaces from the widget string
        namespaces = self.NS_PATTERN.findall(self.query_constructor.namespaces)

        # RDFlib SERVICE patch -> to be removed in release>5.0.0
        query_str = service_patch_rdflib(self.query_constructor.query)
        self.query_constructor.query = query_str

        res = self.graph.query(self.query_constructor.query, initNs=dict(namespaces))
        self.current_dataframe = DataFrame(list(res))
        collapsed_data = DataFrame(list(res))
        for ii, row in collapsed_data.iterrows():
            for jj, cell in enumerate(row):
                if isinstance(cell, URIRef):
                    collapsed_data.iat[ii, jj] = collapse_namespace(namespaces, cell)
        self.grid.clear_output()
        with self.grid:
            IPython.display.display(
                IPython.display.HTML(collapsed_data.to_html(escape=False))
            )

    @T.default("graph")
    def make_default_graph(self):
        return Graph()

    @T.default("grid")
    def make_default_grid(self):
        return W.Output(layout=dict(max_height="60vh"))

    @T.default("run_button")
    def make_default_run_button(self):
        button = W.Button(
            description="Run Query",
            icon="search",
            tooltip="Click to execute query with current configuration.",
        )
        button.on_click(self.run_query)
        return button
