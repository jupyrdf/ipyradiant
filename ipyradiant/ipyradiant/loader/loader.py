import os
import tempfile

import ipywidgets as W
import traitlets as T

from rdflib import Graph, BNode


def get_n_subjects(graph: Graph):
    return len(set(graph.subjects(None, None)))


def get_n_predicates(graph: Graph):
    return len(set(graph.predicates(None, None)))


class LoadBox(W.HBox):
    graph = T.Instance(Graph)
    graph_id = T.Instance(BNode)
    label = T.Instance(W.Label)
    file_upload = T.Instance(W.FileUpload)
    file_upload_value = T.Dict()
    log = W.Output()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.label, self.file_upload])
        T.link((self.file_upload, "value"), (self, "file_upload_value"))

    @T.default("graph")
    def make_default_graph(self):
        return Graph()

    @T.default("graph_id")
    def make_default_graph_id(self):
        return self.graph.identifier

    @T.default("label")
    def make_default_label(self):
        label = W.Label(
            value="Click to load graph file (.ttl):"
        )
        return label

    @T.default("file_upload")
    def make_default_file_upload(self):
        file_upload = W.FileUpload(
            accept='.ttl',
            multiple=False  # TODO support multiple
        )
        return file_upload

    @T.observe("file_upload_value")
    def process_files(self, change):
        # TODO simplify by using WXYZ HTML File Loader
        # TODO loader for files (not needed until support for >1 file)
        # size is in bytes
        file_graphs = {}
        for file_name, data in change.new.items():
            assert "metadata" and "content" in data
            assert file_name not in file_graphs
            file_graphs[file_name] = {}
            file_graphs[file_name]["metadata"] = data["metadata"]
            # File write/load workaround (replace with WXYZ)
            with tempfile.TemporaryFile(delete=False) as tf:
                # TODO try else to ensure close?
                tf.write(data["content"])
                tf.close()
                g = Graph().parse(tf.name, format="n3")
                file_graphs[file_name]["graph"] = g
                file_graphs[file_name]["metadata"]["length"] = len(g)
                os.unlink(tf.name)

            # TODO combine graphs when multiple=True
            self.graph = g
            self.graph_id = g.identifier


class LoadWidget(W.VBox):
    """
    TODO
     - improve traits and stats
    """
    # Metadata
    n_triples = T.Int()
    n_subjects = T.Int()
    n_predicates = T.Int()

    graph = T.Instance(Graph)
    graph_id = T.Instance(BNode)
    stats = T.Instance(W.HTML)

    log = W.Output()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_box = LoadBox()
        T.link((self.load_box, "graph"), (self, "graph"))
        T.link((self.load_box, "graph_id"), (self, "graph_id"))
        self.children = ([self.load_box, self.stats])

    @T.default("n_triples")
    def make_default_n_triples(self):
        return len(self.graph), 0

    @T.default("n_subjects")
    def make_default_n_triples(self):
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
        html = W.HTML(
            self.build_html_str()
        )
        return html

    @T.observe("graph_id")
    def update_stats(self, change):
        self.n_triples = len(self.graph)
        self.n_subjects = get_n_subjects(self.graph)
        self.n_predicates = get_n_predicates(self.graph)
        self.stats.value = self.build_html_str()
