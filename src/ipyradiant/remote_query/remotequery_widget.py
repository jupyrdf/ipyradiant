""" remote query query widget
"""
# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import re

import traitlets as T

import ipywidgets as W
import qgrid
from pandas import DataFrame
from rdflib import Graph
from SPARQLWrapper import JSON, SPARQLWrapper

# from .namespace_manager import collapse_namespace
from .query_constructor import QueryConstructor

# DIGEST, N3, POST, RDFXML, XML,


class RemoteQueryWidget(W.VBox):
    # namespace pattern
    NS_PATTERN = re.compile(r"PREFIX ([\w]*): <(.+)>")

    graph = T.Instance(Graph)
    run_button = T.Instance(W.Button)
    log = W.Output(layout={"border": "1px solid black"})
    qgridw = T.Instance(qgrid.QgridWidget)
    current_dataframe = T.Instance(DataFrame)

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if graph is not None:
            self.graph = graph
        self.query_constructor = QueryConstructor()
        self.children = [
            self.query_constructor,
            self.run_button,
            self.qgridw,
        ]

    # @log.capture(clear_output=True)
    def run_query(self, button):
        # Get Graph IRI
        graphIRI = self.query_constructor.namespaces
        query = self.query_constructor.formatted_query.value
        sparql = SPARQLWrapper(graphIRI)
        body = query.replace(graphIRI, "")
        sparql.setQuery(body)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        #         print(results)
        for result in results["results"]["bindings"]:
            print(result["label"]["value"])

        # res = self.graph.query(
        #     self.query_constructor.formatted_query.value, initNs=dict({'graphIRI': graphIRI})
        # )
        # print(res)

        # self.current_dataframe = DataFrame(list(res))
        # collapsed_data = DataFrame(list(res))
        # for ii, row in collapsed_data.iterrows():
        #     for jj, cell in enumerate(row):
        #         if isinstance(cell, URIRef):
        #             collapsed_data.iat[ii, jj] = collapse_namespace(namespaces, cell)
        # self.qgridw.df = collapsed_data

    @T.default("graph")
    def make_default_graph(self):
        return Graph()

    @T.default("qgridw")
    def make_default_qgridw(self):
        qgridw = qgrid.show_grid(
            DataFrame(),
            grid_options={"editable": False},
            column_options={"editable": False},
            column_definitions={"index": {"width": "20"}},
        )
        return qgridw

    @T.default("run_button")
    def make_default_run_button(self):
        button = W.Button(
            description="Run Query",
            icon="search",
            tooltip="Click to execute query with current configuration.",
        )
        button.on_click(self.run_query)
        return button
