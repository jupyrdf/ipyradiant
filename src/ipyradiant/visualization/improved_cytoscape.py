# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import ipycytoscape as cyto
import ipywidgets as W
import networkx as nx
import rdflib
import traitlets as T

from ipycytoscape.cytoscape import Graph as CytoscapeGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from ipyradiant.visualization.cytoscape import style
from ipyradiant.rdf2nx import RDF2NX


class CytoscapeViewer(W.VBox):
    """TODO some docs explaining the attrs"""

    animate = T.Bool(default_value=True)
    # TODO specify node and edge labels separately
    labels = T.Bool(default_value=True)
    layouts = T.List()
    layout_selector = T.Instance(W.Dropdown)
    cytoscape_widget = T.Instance(cyto.CytoscapeWidget)
    graph = T.Union(
        (
            T.Instance(rdflib.Graph),
            T.Instance(nx.Graph),
        ),
        allow_none=True,
        default_value=None,
    )
    cyto_layout = T.Unicode(default_value="random")
    cyto_style = T.List()
    # Can be overwritten prior to assigning `graph` trait
    _rdf_label = "rdfs:label"
    _nx_label = "label"
    # Can be overwritten to change RDF->LPG behavior
    _rdf_converter: RDF2NX = RDF2NX

    @T.default("cyto_style")
    def _make_cyto_style(self):
        if self.labels:
            return style.LABELLED_DIRECTED_GRAPH
        else:
            return style.DIRECTED_GRAPH

    # TODO validate graph and throw warning if # nodes is large?

    @T.observe("graph")
    def _update_graph(self, change):
        # Clear graph so that data isn't duplicated
        self.cytoscape_widget.graph = CytoscapeGraph()
        if isinstance(self.graph, nx.Graph):
            self.cytoscape_widget.graph.add_graph_from_networkx(self.graph)
            # TODO def add_label_from_nx
            for node in self.cytoscape_widget.graph.nodes:
                node.data["_label"] = node.data.get(self._nx_label, None)
        elif isinstance(self.graph, rdflib.Graph):
            # Note: rdflib_to_networkx_multidigraph does not store the predicate AT ALL, 
            #  so it is basically unrecoverable (e.g. for labelling); using _rdf_converter
            nx_graph = self._rdf_converter.convert(self.graph)
            self.cytoscape_widget.graph.add_graph_from_networkx(nx_graph)
            for node in self.cytoscape_widget.graph.nodes:
                node.data["_label"] = node.data.get(self._rdf_label, node.data.get("id", None))

    @T.default("cytoscape_widget")
    def _make_cytoscape_widget(self):
        widget = cyto.CytoscapeWidget()
        widget.set_layout(
            animate=self.animate,
            randomize=True,
            # Fast animation time for initial graph
            maxSimulationTime=1000,
        )
        widget.set_style(self.cyto_style)
        return widget

    @T.observe("labels")
    def _update_labels(self, change):
        if change.old != change.new:
            if self.labels:
                self.cyto_style = style.LABELLED_DIRECTED_GRAPH
            else:
                self.cyto_style = style.DIRECTED_GRAPH

    @T.default("layouts")
    def _make_layouts(self):
        # TODO increase spacing on the layout?
        # https://stackoverflow.com/questions/54015729
        return ["circle", "cola", "concentric", "cose", "dagre", "grid", "random"]

    @T.default("layout_selector")
    def _make_layout_selector(self):
        widget = W.Dropdown(description="Layout:", options=self.layouts)
        T.link((self, "cyto_layout"), (widget, "value"))
        return widget

    @T.observe("layouts")
    def _update_layout_selector(self, change):
        self.layout_selector = self._make_layout_selector()

    @T.observe("cyto_layout")
    def _update_layout(self, change):
        # TODO move to .cytoscape.layout
        # note: animate=False goes through the full simulation to compute layout, which is SLOW
        self.cytoscape_widget.set_layout(
            name=self.cyto_layout,
            animate=self.animate,
            randomize=True,
            maxSimulationTime=2000,
        )

    @T.observe("cyto_style")
    def _update_style(self, change):
        self.cytoscape_widget.set_style(self.cyto_style)

    @T.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (
                self.layout_selector,
                self.cytoscape_widget,
            )
        return children
