""" Utility Helper Functions
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import logging
import re

import rdflib


def service_patch_rdflib(query_str):
    # check for rdflib version, if <=5.0.0 throw warning
    version = rdflib.__version__
    v_split = tuple(map(int, version.split(".")))
    major_minor_version = (v_split[0], v_split[1])

    # if version > 5, warn users ipyradiant needs to be updated
    if major_minor_version <= (5, 0) and "SERVICE" in query_str:
        query_str = query_str.replace("SERVICE", "service")
        logging.info(
            "SERVICE found in query. RDFlib currently only supports `service`, to be fixed in the next release>5.0.0"
        )
    elif major_minor_version > (5, 0):
        logging.info("Service patch for ipyradiant should be removed.")

    return query_str


def collapse_namespace(namespaces, cell):
    """Collapse namespaces and use hyperlink structure."""

    uf_link = """<a href=\"{}" target=\"_blank\">{}</a>"""

    if isinstance(namespaces, dict):
        namespaces = list(namespaces.items())
        # sort based on namespace length (ensure longer ns are processed first)
        namespaces.sort(key=lambda entry: len(entry[1]), reverse=True)

    or_statement = "|".join([uri for _, uri in namespaces])
    pattern = f"({or_statement}).*"
    quick_check = re.match(pattern, str(cell))
    if quick_check:
        for term, uri in namespaces:
            if cell.startswith(uri):
                shorthand = str(cell).replace(uri, term + ":")
                if "/" in shorthand:
                    # break because we don't want to collapse to a partial match
                    # TODO remove if want an irregular shorthand representation
                    break
                return uf_link.format(cell, shorthand)

    return uf_link.format(cell, cell)
