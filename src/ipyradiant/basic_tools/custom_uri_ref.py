# Copyright (c) 2020 ipyradiant contributors.
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
    :namespaces: either a dict or NamespaceManager, this corresponds to the set of namespaces the URI should be
    truncated according to.
    """

    def __hash__(self):
        return id(self)

    def __init__(self, uri: URIRef, namespaces: Union[dict, NamespaceManager]):

        self.uri = URIRef(uri)
        self.namespaces = namespaces

    def __repr__(self):
        if type(self.namespaces) == dict:
            g = Graph()
            for key, value in self.namespaces.items():
                g.namespace_manager.bind(key, value)
            return URIRef(self.uri).n3(g.namespace_manager)
        return URIRef(self.uri).n3(self.namespaces)

    # todo: can we support other = URIRef?
    def __eq__(self, other):
        if type(other) == URIRef:
            return self.uri == other
        return self.uri == other.uri
