# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import re

import ipywidgets as W
import traitlets as T
from rdflib import Graph

from ipyradiant.query.visualize import QueryPreview, QueryResultsGrid

PREFIX_PATTERN = re.compile(r"PREFIX (\w+): <(.+)>")


class QueryWidget(W.VBox):
    """Widget used to visualize and run SPARQL queries.
    Results are displayed as a DataFrame grid.
    """

    query = T.Instance(str, ("",))
    query_preview = T.Instance(QueryPreview)
    query_result = T.Any()
    query_results_grid = T.Instance(QueryResultsGrid)
    graph = T.Instance(Graph, kw={})
    run_button = T.Instance(W.Button)

    def run_query(self, button):
        """Execute the query and update query_result.

        Note: This collects the namespaces from the query_preview.
        """
        # TODO do we need to throw some error/warning if prefixes clash?
        # TODO should we catch some errors and display info, e.g. ParseException?

        # initialize using namespaces defined in the graph object
        namespaces = dict(self.graph.namespaces())
        # add namespace prefixes defined in the query string
        for term, ns in PREFIX_PATTERN.findall(self.query):
            namespaces[term] = ns

        self.query_results_grid.namespaces = namespaces
        self.query_result = None  # clear the grid
        self.query_result = self.graph.query(self.query)

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (self.query_preview, self.run_button, self.query_results_grid)
        return children

    @T.default("query_results_grid")
    def make_default_query_results_grid(self):
        widget = QueryResultsGrid()
        T.link((widget, "query_result"), (self, "query_result"))
        return widget

    @T.default("query_preview")
    def make_default_query_preview(self):
        widget = QueryPreview()
        T.link((widget, "query"), (self, "query"))
        return widget

    @T.default("run_button")
    def make_default_run_button(self):
        button = W.Button(
            description="Run Query",
            icon="search",
            tooltip="Click to execute query with current configuration.",
        )
        button.on_click(self.run_query)
        return button
