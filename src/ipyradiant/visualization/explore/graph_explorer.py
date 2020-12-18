import ipywidgets as W
import traitlets as T

from rdflib import Graph

from ...query.api import SPARQLQueryFramer, build_values
from ...basic_tools.custom_uri_ref import CustomURI


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
    available_types = T.List(allow_none=True)  # TODO how to type
    type_filter = T.Instance(W.SelectMultiple)
    type_filter_value = T.List(allow_none=True)  # TODO how to type List[CustomURI]
    selections = T.List(allow_none=True).tag(
        default=None)  # TODO how to type List[URIRef]

    def __init__(self, label: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = label or "Available types:"
        self.label.value = f"<b>{label}</b>"
        self.children = tuple([self.label, self.type_filter])

    def make_available_types(self):
        if self.graph is not None:
            ns = dict(self.graph.namespaces())
            types = AllTypes.run_query(self.graph)
            # TODO how to allow user specification of custom CustomURI class
            return list(
                map(lambda x: CustomURI(x, namespaces=ns), types["o"].to_list()))
        else:
            return []

    @T.default("available_types")
    def make_default_available_types(self):
        return self.make_available_types()

    @T.default("label")
    def make_default_label(self):
        return W.HTML("<b>Available types:</b>")

    @T.default("type_filter")
    def make_default_type_filter(self):
        type_filter = W.SelectMultiple(
            rows=10,
            disabled=False,
        )
        T.link((self, "available_types"), (type_filter, "options"))
        T.link((type_filter, "value"), (self, "type_filter_value"))
        return type_filter

    @T.observe("type_filter_value")
    def update_selections(self, change):
        if change.new != change.old:
            self.selections = [type_.uri for type_ in change.new]

    @T.observe("graph")
    def update_graph(self, change):
        if change.old != change.new:
            self.available_types = self.make_available_types()


class RDFSubjectSelectMultiple(W.VBox):
    # Define the query class
    class SubjectsOfType(SPARQLQueryFramer, metaclass=MetaSubjectsOfType):
        values = None  # note: query will not run without values

    graph = T.Instance(Graph, allow_none=True).tag(default=None)
    query = SubjectsOfType
    _values = T.Instance(dict, allow_none=True).tag(default=None)
    #
    label = T.Instance(W.HTML)
    available_subjects = T.List(allow_none=True).tag(default=None)  # TODO how to type
    subject_select = T.Instance(W.SelectMultiple)
    subject_select_value = T.List(allow_none=True)  # TODO how to type
    selections = T.List(allow_none=True).tag(default=None)  # TODO how to type

    def __init__(self, label: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = label or "Available subjects:"
        self.label.value = f"<b>{label}</b>"
        self.children = tuple([self.label, self.subject_select])

    @T.default("label")
    def make_default_label(self):
        return W.HTML("<b>Available subjects:</b>")

    @T.default("subject_select")
    def make_default_subject_select(self):
        subject_select = W.SelectMultiple(
            rows=10,
            disabled=False,
        )
        T.link((self, "available_subjects"), (subject_select, "options"))
        T.link((subject_select, "value"), (self, "subject_select_value"))
        return subject_select

    @T.observe("subject_select_value")
    def update_selections(self, change):
        if change.new != change.old:
            # TODO custom repr
            self.selections = [klass.uri for klass in change.new]

    def update_select(self):
        if self.graph is not None and self._values is not None:
            qres = self.run_query()
            subject_select_options = []
            for uri, label in qres.values:
                subject_select_options.append(
                    CustomItem(
                        _repr=lambda x: f"{x.label}:   ->   {x.uri}",
                        uri=uri,
                        label=label
                    )
                )
            self.available_subjects = subject_select_options

    @T.observe("graph")
    def update_graph(self, change):
        self.update_select()

    @T.observe("_values")
    def update_values(self, change):
        self.query.values = change.new
        self.update_select()

    def run_query(self):
        assert self.query.values is not None
        return self.query.run_query(self.graph)


class GraphExploreNodeSelection(W.VBox):
    graph = T.Instance(Graph, allow_none=True)
    type_filter = T.Instance(RDFTypeSelectMultiple)
    type_filter_selections = T.List(allow_none=True).tag(default=None)
    subject_filter = T.Instance(RDFSubjectSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.type_filter, self.subject_filter])
        T.link((self, "graph"), (self.type_filter, "graph"))
        T.link((self, "graph"), (self.subject_filter, "graph"))
        T.link((self.type_filter, "selections"), (self, "type_filter_selections"))

    @T.default("type_filter")
    def make_default_type_filter(self):
        return RDFTypeSelectMultiple(Graph())

    @T.default("subject_filter")
    def make_default_subject_filter(self):
        return RDFSubjectSelectMultiple(Graph())

    @T.observe("type_filter_selections")
    def update_type_filter_selections(self, change):
        if change.old != change.new and change.new:
            self.subject_filter._values = {"type": change.new}
