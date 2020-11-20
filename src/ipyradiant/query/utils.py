""" Utility Helper Functions
"""
# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import logging

import rdflib

logger = logging.getLogger(__name__)


def service_patch_rdflib(query_str):
    # check for rdflib version, if <=5.0.0 throw warning
    version = rdflib.__version__
    v_split = tuple(map(int, version.split(".")))
    check = v_split <= (5, 0, 0)

    # if version > 5, warn users ipyradiant needs to be updated
    if check:
        if "SERVICE" in query_str:
            query_str = query_str.replace("SERVICE", "service")
            logger.info(
                "SERVICE found in query. RDFlib currently only supports `service`, to be fixed in the next release>5.0.0"
            )
    return query_str
