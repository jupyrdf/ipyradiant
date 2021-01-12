# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import re

import rdflib


def URItoID(uri: rdflib.term.URIRef) -> str:
    """Returns the URI fragment that follows the last '#' or '/' separator."""
    parts = re.split("/|#", uri)
    return parts[-1]


def URItoShortID(uri: rdflib.term.URIRef, ns: dict = None):
    """Convert URIs to shorthand IDs using namespace information.

    TODO rename to_pithy_uri
    TODO support other namespace objects (e.g. NamespaceManager)?
    """
    prefix = None
    id_ = URItoID(uri)

    if ns is None:
        return id_
    else:
        for term, namespace in ns.items():
            if uri.startswith(namespace):
                prefix = term
                break

    if prefix is None:
        return id_
    else:
        return f"{prefix}:{id_}"
