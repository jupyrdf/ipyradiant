# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import traitlets as T

import ipywidgets as W
from rdflib import Graph

from ...basic_tools.custom_uri_ref import CustomURI
from ...basic_tools.uri_widgets import SelectMultipleURI
from ...query.api import SPARQLQueryFramer, build_values


class AllTypes(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?o
    WHERE {
        ?s a ?o .
    }
    """


class CustomItem:
    """Class used to build list items with custom repr"""

    def __init__(self, _repr: callable, **kwargs):
        self._repr = _repr
        for attr, value in kwargs.items():
            self.__setattr__(attr, value)

    def __repr__(self):
        return self._repr(self)


class MetaSubjectsOfType(type):
    """Metaclass to query for type and label for specific VALUES."""

    _sparql = """
        SELECT DISTINCT ?s ?label
        WHERE {{
            ?s a ?type .
            OPTIONAL {{ ?s rdfs:label ?label . }}

            VALUES ({}) {{
                {}
            }}
        }}
    """
    values = None

    @property
    def sparql(cls):
        return build_values(cls._sparql, cls.values)


class RDFTypeSelectMultiple(W.VBox):
    """TODO improve docs, and rename attrs and methods?
    Used to build a selection for available types in the graph.
    Uses a library query. Uses graph object's namespace.
    """

    graph = T.Instance(Graph, allow_none=True)
    label = T.Instance(W.HTML)
    select_widget = T.Instance(SelectMultipleURI)

    def __init__(self, label: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = label or "Available types:"
        self.label.value = f"<b>{label}</b>"
        self.children = tuple([self.label, self.select_widget])

    def make_available_types(self):
        if self.graph is not None:
            ns = dict(self.graph.namespaces())
            types = AllTypes.run_query(self.graph)
            # TODO how to allow user specification of custom CustomURI class
            self.select_widget.pithy_uris = tuple(
                map(lambda x: CustomURI(x, namespaces=ns), types["o"].to_list())
            )

    @T.default("label")
    def make_default_label(self):
        return W.HTML("<b>Available types:</b>")

    @T.default("select_widget")
    def make_default_select_widget(self):
        return SelectMultipleURI(rows=10)

    @T.observe("graph")
    def update_graph(self, change):
        self.make_available_types()


class RDFSubjectSelectMultiple(W.VBox):
    # Define the query class
    class SubjectsOfType(SPARQLQueryFramer, metaclass=MetaSubjectsOfType):
        values = None  # note: query will not run without values

    graph = T.Instance(Graph, allow_none=True).tag(default=None)
    query = SubjectsOfType
    _values = T.Instance(dict, allow_none=True).tag(default=None)
    #
    label = T.Instance(W.HTML)
    select_widget = T.Instance(SelectMultipleURI)

    def __init__(self, label: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = label or "Available subjects:"
        self.label.value = f"<b>{label}</b>"
        self.children = tuple([self.label, self.select_widget])

    @T.default("label")
    def make_default_label(self):
        # TODO update_label(label_str: str):
        #  label should be a property that is based on label_text
        return W.HTML("<b>Available subjects:</b>")

    @T.default("select_widget")
    def make_default_select_widget(self):
        return SelectMultipleURI(rows=10)

    def update_select(self):
        if self.graph is not None and self._values is not None:
            qres = self.run_query()
            sw_uris = []
            for uri, label in qres.values:
                sw_uris.append(
                    CustomItem(
                        _repr=lambda x: f"{x.label}:   ->   {x.uri}",
                        uri=uri,
                        label=label,
                    )
                )
            self.select_widget.pithy_uris = tuple(sw_uris)

    @T.observe("graph")
    def update_graph(self, change):
        self.update_select()

    @T.observe("_values")
    def update_values(self, change):
        if change.old != change.new:
            self.query.values = change.new
            self.update_select()

    def run_query(self):
        assert self.query.values is not None
        return self.query.run_query(self.graph)


class GraphExploreNodeSelection(W.VBox):
    graph = T.Instance(Graph, kw={})
    type_select = T.Instance(RDFTypeSelectMultiple)
    subject_select = T.Instance(RDFSubjectSelectMultiple)

    @property
    def selected_types(self):
        return self.type_select.select_widget.value

    @T.validate("children")
    def validate_children(self, proposal):
        children = proposal.value
        if not children:
            children = (self.type_select, self.subject_select)
        return children

    @T.default("type_select")
    def make_default_type_select(self):
        type_selector = RDFTypeSelectMultiple(self.graph)
        type_selector.select_widget.observe(self.update_subject_select_values, "value")
        return type_selector

    @T.default("subject_select")
    def make_default_subject_select(self):
        return RDFSubjectSelectMultiple(self.graph)

    @T.observe("graph")
    def update_subwidget_graphs(self, change):
        # reset the subject select options and value
        self.subject_select.select_widget.options = ()
        self.subject_select.select_widget.value = ()
        self.subject_select._values = None

        self.type_select.graph = self.graph
        self.subject_select.graph = self.graph

    def update_subject_select_values(self, change):
        if change.old != change.new and change.new:
            # Note: change.new == self.type_select.select_widget.value
            self.subject_select._values = {"type": list(change.new)}
