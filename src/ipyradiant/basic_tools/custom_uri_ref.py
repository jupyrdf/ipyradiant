# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from pathlib import Path
from typing import Dict, Union

from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager

from ..rdf2nx.uri_converter import URItoShortID


class CustomURI:
    """
    Class used for storing uri information including the namespace and shorthand ID.

    TODO rename to PithyURI
    TODO extensive testing and demo notebook
    TODO namespaces support NamespaceManager
    TODO how to specify that this must accept a URIRef and namespace str?
    TODO cast namespace to rdflib.namespace.Namespace?
    TODO can we make this a specialization of URIRef?
    """

    uri = None
    ns = None
    id_ = None  # TODO rename pithy_uri

    def __init__(
        self,
        uri: Union[URIRef, str],
        namespaces: Dict[str, Union[str, Namespace, URIRef]] = None,
        converter: callable = URItoShortID,
    ):
        """
        :param uri: the base URI
        :param namespaces: a dictionary of prefix:namespace(s) used to match to the URI
        :param converter: callable that accepts a URI and namespace (ns) and returns id_
        """
        self.uri = uri
        if namespaces is not None:
            for prefix, ns in namespaces.items():
                if self.get_uri_root(self.uri) == str(ns):
                    self.ns = ns
                    if converter is not None:
                        # Convert with namespace
                        self.id_ = converter(self.uri, ns={prefix: ns})
                    break

        if self.id_ is None and converter is not None:
            # Convert without namespace
            self.id_ = converter(self.uri)
        elif self.id_ is None:
            # Use uri as id_
            self.id_ = str(self.uri)

    def __repr__(self):
        return self.id_ if self.id_ is not None else self.uri

    @staticmethod
    def get_uri_root(uri: URIRef) -> str:
        """Gets the root of a URI (everything but the fragmant, or name)

        TODO should this be a universal util?
        """

        pathlike_uri = Path(uri)
        if uri[-1] == "/":
            return uri

        if "#" in pathlike_uri.name:
            return "#".join(uri.split("#")[0:-1]) + "#"
        else:
            return "/".join(uri.split("/")[0:-1]) + "/"


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
