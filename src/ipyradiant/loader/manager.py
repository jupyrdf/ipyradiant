""" loading widgets
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import ipywidgets as W
import traitlets as T
from rdflib import BNode, Graph

from .base import BaseLoader
from .upload import UpLoader
from .util import get_n_predicates, get_n_subjects


class FileManager(W.VBox):
    """Wraps a file selector and stats"""

    n_triples = T.Int()
    n_subjects = T.Int()
    n_predicates = T.Int()

    loader = T.Instance(BaseLoader)
    stats = T.Instance(W.HTML)

    graph = T.Instance(Graph)
    graph_id = T.Instance(BNode)

    log = W.Output()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        T.link((self.loader, "graph"), (self, "graph"))
        T.link((self.loader, "graph_id"), (self, "graph_id"))
        self.children = [self.loader, self.stats]

    @T.default("loader")
    def make_default_loader(self):
        return UpLoader()

    @T.default("n_triples")
    def make_default_n_triples(self):
        return len(self.graph), 0

    @T.default("n_subjects")
    def make_default_n_subjects(self):
        return get_n_subjects(self.graph)

    @T.default("n_predicates")
    def make_default_n_predicates(self):
        return get_n_subjects(self.graph)

    def build_html_str(self):
        return f"""
                <b>Stats: </b>
                <ul>
                    <li>n_triples: {self.n_triples}</li>
                    <ul>
                        <li>n_subjects: {self.n_subjects}</li>
                        <li>n_predicates: {self.n_predicates}</li>
                    </ul>
                </ul>
                """

    @T.default("stats")
    def make_default_stats(self):
        html = W.HTML(self.build_html_str())
        return html

    @T.observe("graph_id")
    def update_stats(self, change):
        self.n_triples = len(self.graph)
        self.n_subjects = get_n_subjects(self.graph)
        self.n_predicates = get_n_predicates(self.graph)
        self.stats.value = self.build_html_str()
