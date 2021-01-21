""" a query form
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import ipywidgets as W
import traitlets as T

from .namespace_manager import NamespaceManager


class QueryHeader(W.HBox):
    dropdown = T.Instance(W.Dropdown)
    dropdown_value = T.Unicode()
    header = T.Instance(W.Box)
    header_value = T.Unicode()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.dropdown, self.header])

    @T.default("dropdown")
    def make_default_dropdown(self):
        dropdown = W.Dropdown(
            options=["SELECT", "SELECT DISTINCT", "ASK", "CONSTRUCT"],
            value="SELECT DISTINCT",
        )
        T.link((dropdown, "value"), (self, "dropdown_value"))
        return dropdown

    def make_default_select_header(self):
        header = W.Text(
            placeholder="*",
            # layout={"width":"80%"},
        )
        T.link((header, "value"), (self, "header_value"))
        return header

    def make_default_construct_header(self):
        header = W.Textarea(placeholder="{\n\t?s ?p ?o .\n}")
        T.link((header, "value"), (self, "header_value"))
        return header

    @T.default("header")
    def make_default_header(self):
        return W.Box([self.make_default_select_header()], layout={"width": "100%"})

    @T.observe("dropdown_value")
    def update_header(self, change):
        if change.new != change.old:
            selects = {"SELECT DISTINCT", "SELECT"}
            if change.new in selects and change.old not in selects:
                self.header.children = tuple([self.make_default_select_header()])
                self.header.layout.visibility = "visible"
            elif change.new == "ASK":
                self.header.children = tuple([W.Text(value="")])
                self.header.layout.visibility = "hidden"
            elif change.new == "CONSTRUCT":
                self.header.children = tuple([self.make_default_construct_header()])
                self.header.layout.visibility = "visible"


class QueryBody(W.HBox):
    label = T.Instance(W.Label)
    body = T.Instance(W.Textarea)
    body_value = T.Unicode()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.label, self.body])

    @T.default("label")
    def make_default_label(self):
        label = W.Label(value="WHERE")
        return label

    @T.default("body")
    def make_default_body(self):
        body = W.Textarea(placeholder="{\n\t?s ?p ?o .\n}")
        T.link((body, "value"), (self, "body_value"))
        return body


class LinkedLimitOffset(W.VBox):
    max_len = T.Int(default_value=10)
    limit = T.Instance(W.IntSlider)
    limit_check = T.Instance(W.Checkbox)
    limit_box = T.Instance(W.HBox)
    limit_enabled = T.Bool()
    offset = T.Instance(W.IntSlider)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_len = kwargs.get("max_len", 10)
        self.children = tuple([self.limit_box, self.offset])

    @T.default("limit")
    def make_default_limit(self):
        limit = W.IntSlider(
            min=0,
            max=self.max_len,
            value=self.max_len,
            continuous_update=True,
            disabled=True,
            layout=W.Layout(visibility="hidden"),
        )
        return limit

    @T.default("limit_check")
    def make_default_limit_check(self):
        limit_check = W.Checkbox(
            value=False,
            indent=False,
            layout=W.Layout(width="20px"),
        )
        T.link((limit_check, "value"), (self, "limit_enabled"))
        return limit_check

    @T.default("limit_box")
    def make_default_limit_box(self):
        return W.HBox(
            [
                W.Label(value="Limit:", layout=W.Layout(width="40px")),
                self.limit_check,
                self.limit,
            ],
            layout=W.Layout(justify_content="flex-start"),
        )

    @T.default("offset")
    def make_default_offset(self):
        offset = W.IntSlider(
            description="Offset:",
            min=0,
            max=self.max_len,
            continuous_update=True,
        )
        return offset

    @T.observe("limit_enabled")
    def update_limit(self, change):
        self.limit.disabled = not change.new
        if not change.new:
            self.limit.layout.visibility = "hidden"
        else:
            self.limit.layout.visibility = "visible"

    @T.observe("max_len")
    def update_limit_max(self, change):
        self.limit.max = change.new
        self.limit.value = change.new


class QueryInput(W.VBox):
    """Aggregates multiple widgets together"""

    namespaces = T.Instance(W.VBox)
    header = T.Instance(W.HBox)
    body = T.Instance(W.HBox)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespaces = NamespaceManager()
        self.header = QueryHeader()
        self.body = QueryBody()
        self.children = tuple([self.namespaces, self.header, self.body])
