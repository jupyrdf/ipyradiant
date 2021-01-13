""" Utility Helper Functions
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import logging

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
