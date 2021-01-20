# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from typing import Union

from rdflib import Graph, URIRef
from rdflib.namespace import NamespaceManager


class CustomURIRef:
    """
    This is a class created to represent a URIRef as the truncated form (via the __repr__ method) while
    maintaining access to the full URIRef via the 'uri' object property.

    params:
    :uri: URIRef, the URIRef one wishes to truncate
    :namespaces: either a dict or NamespaceManager or None, this corresponds to the set of namespaces the URI should be
    truncated according to.
    """

    def __init__(self, uri: URIRef, namespaces: Union[dict, NamespaceManager, None]):

        self.uri = URIRef(uri)

        self.namespaces = namespaces

    def __repr__(self):
        if self.namespaces is None or self.namespaces == {}:
            return self.uri
        if type(self.namespaces) == dict:
            g = Graph()
            for key, value in self.namespaces.items():
                g.namespace_manager.bind(key, value)
            return URIRef(self.uri).n3(g.namespace_manager)
        return URIRef(self.uri).n3(self.namespaces)

    # todo: can we support other = URIRef?
    # for example, if we compare an instance of CustomURIRef to a rdflib.term.URIRef instance,
    # can we tell if they are equal? (right now only supports CustomURIRef compares to CustomURIRef)
    def __eq__(self, other):
        if type(other) == URIRef:
            return self.uri == other
        return self.uri == other.uri
