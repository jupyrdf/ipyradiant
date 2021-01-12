from typing import Union

import traitlets as trt

import ipycytoscape
import ipywidgets as W
import pandas
import rdflib
from ipycytoscape import Edge, Node
from ipyradiant.query.api import SPARQLQueryFramer


class GetOutgoingPredicateObjects(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?s ?p ?o ?label

    WHERE {
        ?s ?p ?o .
        FILTER (!isLiteral(?o))
        OPTIONAL {?o rdfs:label ?label}
    }

    """

    @classmethod
    def run_query(
        cls,
        graph: rdflib.graph.Graph,
        subject: Union[rdflib.term.URIRef, str],
        initBindings: dict = None,
        **initBindingsKwarg,
    ) -> pandas.DataFrame:
        """Overwrite the super method in order to wrap with validation checks."""

        qres = super().run_query(
            graph,
            s=rdflib.term.URIRef(subject),
            initBindings=initBindings,
            **initBindingsKwarg,
        )
        # Validating with known requirements on query results
        # TODO
        return qres


class InteractiveViewer(W.VBox):
    expand_button = trt.Instance(W.Button)
    remove_button = trt.Instance(W.Button)
    cyto_graph = trt.Instance(ipycytoscape.CytoscapeWidget)
    selected_node = trt.Dict(allow_none=True)
    rdf_graph = trt.Instance(rdflib.graph.Graph, allow_none=True)
    cyto_style = trt.List(allow_none=True)

    @trt.default("expand_button")
    def _create_expand_button(self):
        return W.Button(
            description="Expand Upon Selected Node",
            layout=W.Layout(width="500px", height="40px"),
        )

    @trt.default("remove_button")
    def _create_remove_button(self):
        return W.Button(
            description="Undo Most Recent Node Expansion",
            layout=W.Layout(width="500px", height="40px"),
            disabled=False,
        )

    @trt.default("selected_node")
    def _create_default_selected_node(self):
        return None

    @trt.default("cyto_style")
    def _create_cyto_style(self):
        return [
            {
                "selector": "node",
                "css": {
                    "label": "data(_label)",
                    "text-wrap": "wrap",
                    "text-max-width": "150px",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "10",
                    "font-family": '"Gill Sans", sans-serif',
                    "color": "black",
                },
            },
            {
                "selector": "node[classes='selected-node']",
                "css": {
                    "label": "data(_label)",
                    "text-wrap": "wrap",
                    "text-max-width": "150px",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "10",
                    "font-family": '"Gill Sans", sans-serif',
                    "background-color": "red",
                },
            },
            {
                "selector": "node[classes='temp-node']",
                "css": {
                    "label": "data(_label)",
                    "text-wrap": "wrap",
                    "text-max-width": "150px",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "10",
                    "font-family": '"Gill Sans", sans-serif',
                    "background-color": "#FFB6C1",
                },
            },
            {
                "selector": "edge[classes='temp-edge']",
                "css": {
                    "label": "data(_label)",
                    "text-wrap": "wrap",
                    "text-max-width": "150px",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "10",
                    "font-family": '"Gill Sans", sans-serif',
                    "color": "green",
                    "line-color": "#a8eae5",
                },
            },
            {
                "selector": "edge.directed",
                "style": {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                },
            },
            {"selector": "edge.multiple_edges", "style": {"curve-style": "bezier"}},
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs is not None and "rdf_graph" in kwargs:
            self.rdf_graph = kwargs["rdf_graph"]
        else:
            print("must pass in an rdf_graph")
        if kwargs is not None and "cyto_graph" in kwargs:
            self.cyto_graph = kwargs["cyto_graph"]
            self.cyto_graph.set_layout(name="concentric")
        else:
            print("must pass in a cyto_graph")

        self.cyto_graph.set_style(self.cyto_style)
        self.expand_button.on_click(self.expand_button_clicked)
        self.remove_button.on_click(self.undo_expansion)
        self.cyto_graph.on("node", "click", self.log_node_clicks)
        self.buttons = W.HBox(children=[self.expand_button, self.remove_button])
        self.children = [self.cyto_graph, self.buttons]
        self.layout = W.Layout(width="1000px", border="solid 2px")

    def log_node_clicks(self, node):
        try:
            self.selected_node["data"]["classes"] = None
        except:
            pass
        self.selected_node = node
        self.selected_node["data"]["classes"] = "selected-node"
        data = node["data"]
        # TODO: replace pops with filter for private attributes
        data.pop("_label", None)
        data.pop("_attrs", None)

    def expand_button_clicked(self, b):
        self.remove_button.disabled = False
        if self.selected_node is None:
            return None
        new_data = GetOutgoingPredicateObjects.run_query(
            graph=self.rdf_graph, subject=self.selected_node["data"]["iri"]
        )
        objs = new_data["o"].tolist()
        # preds = new_data["p"].tolist()
        labels = new_data["label"].tolist()
        # add nodes
        self.new_nodes = {}
        self.new_edges = {}
        for ii, x in enumerate(objs):
            self.new_nodes[ii] = Node(
                data={
                    "id": str(x),
                    "iri": x,
                    "classes": "temp-node",
                    "_label": labels[ii],
                }
            )
            self.new_edges[ii] = Edge(
                data={
                    "source": self.selected_node["data"]["id"],
                    "target": str(x),
                    "classes": "temp-edge",
                }
            )
            self.cyto_graph.graph.add_node(self.new_nodes[ii])
            self.cyto_graph.graph.add_edge(self.new_edges[ii])
        self.cyto_graph.set_layout(name="concentric")

    def undo_expansion(self, b):
        self.remove_button.disabled = True
        for node in self.new_nodes:
            try:
                self.cyto_graph.graph.remove_node(self.new_nodes[node])
            except ValueError:
                print("Node already in starting graph.")
                continue
        for edge in self.new_edges:
            try:
                self.cyto_graph.graph.remove_node(self.new_edges[edge])
            except ValueError:
                print("Node already in starting graph.")
                continue
