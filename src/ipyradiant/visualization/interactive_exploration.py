# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import ipycytoscape
import ipywidgets as W
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
    Return all triples for non-Literal objects (and the optional object labels).
    """

    sparql = """
    SELECT DISTINCT ?s ?p ?o ?label

    WHERE {
        ?s ?p ?o .
        FILTER (!isLiteral(?o))
        OPTIONAL {?o rdfs:label ?label}
    }

    """


# Throughout this class, we assign the layout to self.cyto_graph_layout multiple times.
# This is so that the graph refreshes the layout every time nodes are added or removed,
# which provides an optimal viewing experience.


class InteractiveViewer(W.VBox):
    expand_button = trt.Instance(W.Button)
    undo_button = trt.Instance(W.Button)
    remove_temp_nodes_button = trt.Instance(W.Button)
    cyto_graph = trt.Instance(ipycytoscape.CytoscapeWidget)
    selected_node = trt.Instance(ipycytoscape.Node, allow_none=True)
    rdf_graph = trt.Instance(rdflib.graph.Graph, allow_none=True)
    cyto_style = trt.List(allow_none=True)
    cyto_graph_layout = trt.Unicode(default_value="cola")

    @trt.default("expand_button")
    def _create_expand_button(self):
        button = W.Button(
            description="Expand Upon Selected Node",
            layout=W.Layout(width="50%", height="40px"),
        )
        button.on_click(self.expand_button_clicked)
        return button

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
        return W.Layout(width="80%")

    @trt.observe("cyto_graph")
    def update_cyto_graph(self, change):
        self.cyto_graph.set_layout(name=self.cyto_graph_layout)
        self.cyto_graph.set_style(self.cyto_style)
        # on is a callback for cyto_graph instance (must be set on each instance)
        self.cyto_graph.on("node", "click", self.log_node_clicks)
        # Here we have to set the children again so that the changes propogate to the front end
        # automatically. Ideally this would be done with traits but did not seem to work. LINK TO GITHUB ISSUE:
        # https://github.com/jupyrdf/ipyradiant/issues/79
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

    def get_node(self, node: Node) -> Node:
        """
        This function is used to find a node given the id of a node copy.
        """

        for node_obj in self.cyto_graph.graph.nodes:
            if node_obj.data["id"] == node["data"]["id"]:
                return node_obj
        # TODO: Make this function return None and log a warning if not node not found.
        raise ValueError("Node not found in cytoscape.graph.nodes.")

    def log_node_clicks(self, node: Node):
        """
        This function works with registering a click on a node. This will mark the node as selected and change the color of the
        selected node.
        """

        node_object = self.get_node(node)

        if self.selected_node == node_object:
            node_object.classes = "clicked"
            # NOTE: Class changes won't propogate to the front end for added nodes until
            # the graph is updated.
            # To fix this we create a random node and then quickly delete it so that the changes propogate.
            self.update_cytoscape_frontend()

        self.selected_node = node_object

    def expand_button_clicked(self, button):
        """
        This function expands a node by loading in its predicates and subjects when
        a node is selected and the expand button is clicked.
        """
        self.undo_button.disabled = False
        if self.selected_node is None:
            return None
        new_data = GetOutgoingPredicateObjects.run_query(
            graph=self.rdf_graph, s=self.selected_node.data["iri"]
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
        self.cyto_graph.set_layout(name=self.cyto_graph_layout)

    def undo_expansion(self, button):
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

        self.cyto_graph.set_layout(name=self.cyto_graph_layout)

    def remove_temp_nodes(self, button):
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
        self.update_cytoscape_frontend()

        self.cyto_graph.set_layout(name=self.cyto_graph_layout)
        self.undo_button.disabled = True

    def update_cytoscape_frontend(self):
        """
        This function quickly adds and deletes a node to update cytoscape front end. Looking to improve
        it for future release.
        """
        self.cyto_graph.graph.add_node(Node(data={"id": "random node"}))
        self.cyto_graph.graph.remove_node_by_id("random node")
