# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import IPython
import ipywidgets as W
import traitlets as T
from pandas import DataFrame
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers.rdf import SparqlLexer
from pygments.styles import STYLE_MAP
from rdflib import URIRef
from rdflib.plugins.sparql.processor import SPARQLResult

from .utils import collapse_namespace


class QueryColorizer(W.VBox):
    """Takes sparql query and runs it through pygments lexer and html formatter"""

    query = T.Unicode()
    formatter_style = T.Enum(values=list(STYLE_MAP.keys()), default_value="colorful")
    style_picker = T.Instance(W.Dropdown)
    html_output = T.Instance(W.HTML)

    _style_defs = T.Unicode(default_value="")
    formatter: HtmlFormatter = None
    _sqrl_lexer: SparqlLexer = None

    @T.default("style_picker")
    def make_default_style_picker(self) -> W.Dropdown:
        widget = W.Dropdown(
            description="Style",
            options=list(STYLE_MAP.keys()),
            layout=W.Layout(min_height="30px"),
        )
        T.link((self, "formatter_style"), (widget, "value"))
        return widget

    @T.default("html_output")
    def make_default_html_output(self) -> W.HTML:
        widget = W.HTML()
        widget.layout = {"width": "50%"}
        return widget

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (self.style_picker, self.html_output)
        return children

    @T.observe("formatter_style")
    def _update_style(self, change=None) -> HtmlFormatter:
        """update the css style from the formatter"""
        self.formatter = HtmlFormatter(style=self.formatter_style)
        self._sqrl_lexer = SparqlLexer()
        self._style_defs = f"<style>{self.formatter.get_style_defs()}</style>"

    @T.observe(
        "query",
        "_style_defs",
    )
    def update_formatted_query(self, change):
        """Update the html output widget with the highlighted query"""
        if not self.formatter or not self._sqrl_lexer:
            self._update_style()
        self.html_output.value = self._style_defs + highlight(
            self.query, self._sqrl_lexer, self.formatter
        )


class QueryPreview(W.HBox):
    """A widget for writing and previewing (with syntax highlighting) a SPARQL query."""

    query = T.Instance(str, ("",))
    query_input = T.Instance(W.Textarea)
    query_view = T.Instance(QueryColorizer)
    styler = T.Bool(default_value=False)

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            if self.styler:
                children = (self.query_input, self.query_view)
            else:
                # if self.styler is False, don't include in the children
                children = (self.query_input, self.query_view.children[1])
        return children

    @T.default("query_input")
    def make_default_query_input(self) -> W.Textarea:
        widget = W.Textarea()
        widget.layout = {"width": "50%", "resize": "none"}
        T.link((widget, "value"), (self, "query"))
        widget.observe(self.scale_query_input, "value")
        return widget

    @T.default("query_view")
    def make_default_query_view(self) -> QueryColorizer:
        widget = QueryColorizer()
        T.link((widget, "query"), (self, "query"))
        return widget

    def scale_query_input(self, change):
        """Change the number of rows based on the query input.

        Note: this breaks if the user manually scales the query input Textarea
        TODO: update when Textarea resize can be disabled via css
          tracking issue: https://github.com/jupyter-widgets/ipywidgets/issues/2586
        """
        self.query_input.rows = change.new.count("\n") + 1


class QueryResultsGrid(W.Box):
    """A widget for viewing the result of SPARQL queries as a DataFrame grid."""

    grid = T.Instance(W.Output)
    log = W.Output(layout={"border": "1px solid black"})
    current_dataframe = T.Instance(DataFrame)
    namespaces = T.Instance(dict, kw={})
    query_result = T.Any()

    @T.default("grid")
    def make_default_grid(self):
        # TODO should this max_height be more intelligent?
        return W.Output(
            layout=dict(
                max_height="50vh",
                width="100%",
            )
        )

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (self.grid,)
        return children

    @T.validate("query_result")
    def validate_query_result(self, proposal):
        """Validate query results and update the HTML output."""
        query_result = proposal.value
        if query_result:
            if isinstance(query_result, DataFrame):
                pass
            elif isinstance(query_result, (list, tuple)):
                item_len = len(query_result[0])
                assert (
                    item_len == 3
                ), f"Unexpected number of items in query_result, {item_len}!=3"
                query_result = DataFrame(query_result)
            elif isinstance(query_result, SPARQLResult):
                query_result = DataFrame(query_result)
        else:
            query_result = DataFrame()

        self.observe(self.process_query, "query_result")
        return query_result

    @log.capture(clear_output=True)
    def process_query(self, change):
        """Update HTML output with latest query results."""
        self.current_dataframe = DataFrame(self.query_result)
        collapsed_data = DataFrame(self.query_result)
        for ii, row in collapsed_data.iterrows():
            for jj, cell in enumerate(row):
                if isinstance(cell, URIRef):
                    collapsed_data.iat[ii, jj] = collapse_namespace(
                        self.namespaces, cell
                    )
        self.grid.clear_output()
        with self.grid:
            IPython.display.display(
                IPython.display.HTML(collapsed_data.to_html(escape=False))
            )
