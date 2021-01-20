# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

from typing import Union

import ipycytoscape
import ipywidgets as W
import pandas
import rdflib
import traitlets as trt
from ipycytoscape import Edge, Node

from ipyradiant.query.api import SPARQLQueryFramer
from ipyradiant.rdf2nx.uri_converter import URItoID

DEFAULT_CYTO_STYLE = [
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
            "background-color": "grey",
        },
    },
    {
        "selector": "edge[classes='temp-edge']",
        "css": {
            "label": "data(_label)",
            "line-color": "#a8eae5",
        },
    },
    {
        "selector": "node.clicked",
        "css": {
            "background-color": "grey",
            "line-color": "black",
            "target-arrow-color": "black",
            "source-arrow-color": "black",
        },
    },
    {
        "selector": "node.temp",
        "css": {
            "background-color": "#FFB6C1",
            "line-color": "black",
            "target-arrow-color": "black",
            "source-arrow-color": "black",
        },
    },
    {
        "selector": "edge.directed",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "grey",
            # "label": "data(iri)",
            "font-size": "5",
        },
    },
    {
        "selector": "edge.temp",
        "style": {
            "curve-style": "bezier",
            "line-color": "#a8eae5",
            # "label": "data(iri)",
            "font-size": "5",
        },
    },
    {"selector": "edge.multiple_edges", "style": {"curve-style": "bezier"}},
]


class GetOutgoingPredicateObjects(SPARQLQueryFramer):
    """
    This is a SPARQLQueryFramer class used in expanding the graph, where it it will
    use a subject and expand the graph to show all the non-literal objects of said subject.
    """

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
    undo_button = trt.Instance(W.Button)  # undo_button
    remove_temp_nodes_button = trt.Instance(W.Button)
    cyto_graph = trt.Instance(ipycytoscape.CytoscapeWidget)
    selected_node = trt.Instance(ipycytoscape.Node, allow_none=True)
    rdf_graph = trt.Instance(rdflib.graph.Graph, allow_none=True)
    cyto_style = trt.List(allow_none=True)

    @trt.default("expand_button")
    def _create_expand_button(self):
        button = W.Button(
            description="Expand Upon Selected Node",
            layout=W.Layout(width="50%", height="40px"),
        )
        button.on_click(self.expand_button_clicked)
        return button

    # update name to undo_button
    @trt.default("undo_button")
    def _create_undo_button(self):
        button = W.Button(
            description="Undo Last Expansion",
            layout=W.Layout(width="25%", height="40px"),
            disabled=True,
        )
        button.on_click(self.undo_expansion)
        return button

    @trt.default("remove_temp_nodes_button")
    def _create_remove_temp_nodes_button(self):
        button = W.Button(
            description="Remove Temporary Nodes",
            layout=W.Layout(width="25%", height="40px"),
            disabled=False,
        )
        button.on_click(self.remove_temp_nodes)
        return button

    @trt.default("selected_node")
    def _create_default_selected_node(self):
        return None

    @trt.default("cyto_style")
    def _create_cyto_style(self):
        return DEFAULT_CYTO_STYLE

    @trt.default("rdf_graph")
    def _create_rdf_graph(self):
        return rdflib.Graph()

    @trt.default("cyto_graph")
    def _create_cyto_graph(self):
        return ipycytoscape.CytoscapeWidget()

    @trt.default("layout")
    def _create_layout(self):
        return W.Layout(width="80%", border="solid 2px")

    @trt.observe("cyto_graph")
    def update_cyto_graph(self, change):
        self.cyto_graph.set_layout(name="cola")
        self.cyto_graph.set_style(self.cyto_style)
        # on is a callback for cyto_graph instance (must be set on each instance)
        self.cyto_graph.on("node", "click", self.log_node_clicks)
        # TODO: Why doesn't this update automatically?? Shouldn't it?
        self.children = (
            self.cyto_graph,
            W.HBox(
                children=[
                    self.expand_button,
                    self.undo_button,
                    self.remove_temp_nodes_button,
                ]
            ),
        )

    @trt.validate("children")
    def validate_children(self, proposal):
        children = proposal.value
        if not children:
            children = (
                self.cyto_graph,
                W.HBox(
                    children=[
                        self.expand_button,
                        self.undo_button,
                        self.remove_temp_nodes_button,
                    ]
                ),
            )
        return children

    def get_node(self, node):
        """
        This function is used to find a node given the id of a node copy. Used in the log_node_clicks
        method to change the color of nodes.
        """

        for node_obj in self.cyto_graph.graph.nodes:
            if node_obj.data["id"] == node["data"]["id"]:
                return node_obj
        # maybe return None and log warning?
        raise ValueError("Node not found in cytoscape.graph.nodes.")

    def log_node_clicks(self, node):
        """
        This function works with registering a click on a node. This will mark the node as selected and change the color of the
        selected node.
        """

        try:
            node_object = self.get_node(node)
        except ValueError:
            #     # logger.warn
            print("Node {} not found in cytoscape graph.".format(node.data["id"]))
            return

        if self.selected_node == node_object:
            node_object.classes = "clicked"
            self.cyto_graph.graph.add_node(Node(data={"id": "random node"}))
            self.cyto_graph.graph.remove_node_by_id("random node")
            # NOTE: Class changes won't propogate to the front end for added nodes until
            # the graph is updated.
            # To fix this we create a random node and then quickly delete it so that the changes propogate.
            # TODO: Add logger.warning to signal this event
        else:
            # TODO lets also change the class for the selected_node to include a
            #  border indicating it has been selected.
            pass

        self.selected_node = node_object

    def expand_button_clicked(self, b):
        """
        This function expands a node by loading in its predicates and subjects when
        a node is selected and the expand button is clicked.
        """
        self.undo_button.disabled = False
        if self.selected_node is None:
            return None
        new_data = GetOutgoingPredicateObjects.run_query(
            graph=self.rdf_graph, subject=self.selected_node.data["iri"]
        )
        objs = new_data["o"].tolist()
        preds = new_data["p"].tolist()
        labels = new_data["label"].tolist()
        # add nodes
        self.existing_node_ids = [
            node.data["id"] for node in self.cyto_graph.graph.nodes
        ]
        self.new_nodes = {}
        self.new_edges = {}
        for ii, x in enumerate(objs):
            if str(x) not in self.existing_node_ids:

                self.new_nodes[ii] = Node(
                    data={
                        "id": str(x),
                        "iri": x,
                        "_label": labels[ii] or str(x),
                    },
                    classes="temp",
                )
                self.cyto_graph.graph.add_node(self.new_nodes[ii])
            self.new_edges[ii] = Edge(
                data={
                    "source": self.selected_node.data["id"],
                    "target": str(x),
                    "iri": URItoID(preds[ii]),
                },
                classes="temp",
            )

            self.cyto_graph.graph.add_edge(self.new_edges[ii])
        self.cyto_graph.set_layout(name="cola")

    def undo_expansion(self, b):
        """
        This is a preliminary function for undoing expansions upon a node.
        As of right now, a user can only undo the most recent expansion. After doing this,
        the button will be disabled until a new expansion is made.
        """
        self.undo_button.disabled = True
        for node in self.new_nodes:
            self.cyto_graph.graph.remove_node_by_id(self.new_nodes[node].data["id"])
        for edge in self.new_edges:
            try:
                self.cyto_graph.graph.remove_edge(self.new_edges[edge])
            except ValueError:
                # edge already removed from graph because the node was removed earlier.
                pass

        self.cyto_graph.set_layout(name="cola")

    def remove_temp_nodes(self, b):
        """
        This is a basic function that cycles through the graph and removes all nodes that
        have the 'temp' style (i.e. nodes that are not starting nodes or have not been clicked on).
        """
        nodes_to_remove = []
        for node in self.cyto_graph.graph.nodes:
            if node.classes == "temp":
                nodes_to_remove.append(node.data["id"])
        for node in nodes_to_remove:
            self.cyto_graph.graph.remove_node_by_id(node)
        # change edge color
        for edge in self.cyto_graph.graph.edges:
            edge.classes = "directed"
        # propogate changes to front end using hack
        self.cyto_graph.graph.add_node(Node(data={"id": "random node"}))
        self.cyto_graph.graph.remove_node_by_id("random node")

        self.cyto_graph.set_layout(name="cola")
        self.undo_button.disabled = True
