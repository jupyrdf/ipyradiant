import re

import rdflib


def URItoID(uri: rdflib.term.URIRef) -> str:
    """returns the URI fragment that follows the last '#' or '/' separator

    TODO validate on larger group of URIs to ensure robustness
    """
    parts = re.split("/|#", uri)
    return parts[-1]


# TODO IRI to ShortID for predicates????
def URItoShortID(uri: rdflib.term.URIRef, ns: dict = None):
    """TODO

    :param uri:
    :param ns: namespace
    :return:
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
