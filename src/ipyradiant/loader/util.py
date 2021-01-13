# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

from rdflib import Graph, util
from rdflib.plugin import Parser, Serializer, register

# maybe not needed, but better to be sure...
register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")
register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

SUFFIX_FORMAT_MAP = dict(**util.SUFFIX_FORMAT_MAP, jsonld="json-ld", json="json-ld")


def guess_format(path):
    """wrap guess_format with custom files"""
    return util.guess_format(path, SUFFIX_FORMAT_MAP)


def get_n_subjects(graph: Graph):
    """count the unique subjects"""
    return len(set(graph.subjects(None, None)))


def get_n_predicates(graph: Graph):
    """count the unique predicates"""
    return len(set(graph.predicates(None, None)))
