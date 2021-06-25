# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

from typing import List

import ipywidgets as ipyw
import rdflib
import traitlets as trt
from IPython.display import JSON, display

from .viewer import CytoscapeViewer


class ConjunctiveGraphViewer(ipyw.GridspecLayout):
    conjunctive_graph = trt.Instance(rdflib.graph.ConjunctiveGraph, kw={})
    context_selector = trt.Instance(ipyw.SelectMultiple)
    context_value = trt.Tuple(allow_none=True)
    json_output = trt.Instance(ipyw.Output)
    viewer = trt.Instance(CytoscapeViewer)
    visual_graph = trt.Instance(rdflib.graph.Graph, kw={})

    context_selector_label = ipyw.Label("Select Context:")
    _simple_context_ids = False

    def __init__(self, n_rows=4, n_columns=5, **kwargs):
        super().__init__(n_rows=n_rows, n_columns=n_columns, **kwargs)

    def _ipython_display_(self, **kwargs):
        super()._ipython_display_(**kwargs)
        self._set_layout()

    def _set_layout(self):
        layout = self.layout
        layout.height = "80vh"
        layout.width = "auto"

        self[:3, :1] = ipyw.VBox(
            [
                self.context_selector_label,
                self.context_selector,
            ]
        )
        self[:3, 1:] = self.viewer
        self[3, 1:] = self.json_output

        for widget in (
            self.context_selector,
            self.viewer,
            self.json_output,
        ):
            widget.layout.height = "auto"
            widget.layout.width = "auto"
            widget.layout.min_height = None
            widget.layout.max_height = None
            widget.layout.max_width = None
            widget.layout.min_width = None

        self.layout = layout

    def add_graphs(self, graphs=List[rdflib.graph.Graph]):
        """Add a set of basic rdflib.graph.Graphs to the conjunctive graph viewer in order to visualize multiple graphs."""
        # TODO support other graph types? (definitely not ConjunctiveGraph)
        assert all(
            [isinstance(graph, rdflib.graph.Graph) for graph in graphs]
        ), "All graphs must be rdflib Graph."
        for context in graphs:
            # context is a sub-graph
            for triple in context:
                self.conjunctive_graph.add([*triple, context])

        # manually call trait function
        self.update_context_selector(None)

    def load_json(self, node):
        data = node["data"]
        data.pop("_label", None)
        data.pop("_attrs", None)
        with self.json_output:
            self.json_output.clear_output()
            display(JSON(data))

    @trt.default("viewer")
    def _make_default_viewer(self):
        widget = CytoscapeViewer()
        widget.cytoscape_widget.on("node", "click", self.load_json)
        trt.link((self, "visual_graph"), (widget, "graph"))
        return widget

    @trt.default("context_selector")
    def _make_default_context_selector(self):
        widget = ipyw.SelectMultiple()
        trt.link((widget, "value"), (self, "context_value"))
        return widget

    @trt.default("json_output")
    def _make_default_json_output(self):
        widget = ipyw.Output()
        # Prevent resizing the JSON output from changing other widgets
        widget.layout.overflow_y = "auto"
        return widget

    @trt.observe("conjunctive_graph")
    def update_context_selector(self, change):
        self.context_selector.options = [
            (f"{graph.identifier} [{len(graph)}]", graph.identifier)
            if not self._simple_context_ids
            else (f"Graph-{ii+1} [{len(graph)}]", graph.identifier)
            for ii, graph in enumerate(self.conjunctive_graph.contexts())
        ]
        self.context_selector.rows = len(self.context_selector.options) + 1

    @trt.observe("context_value")
    def update_visual_graph(self, change):
        """Creates an aggregated graph for visualization by combining all selected contexts."""
        base_graph = rdflib.graph.Graph()
        for context_id in change.new:
            # basic aggregate graph for visualization
            base_graph += self.conjunctive_graph.get_context(context_id)
        self.visual_graph = base_graph

    @trt.validate("children")
    def validate_children(self, proposal):
        """
        Validate method for default children.
        This is necessary because @trt.default does not work on children.
        """
        children = proposal.value
        if not children:
            children = (
                ipyw.VBox(
                    [
                        self.context_selector_label,
                        self.context_selector,
                    ]
                ),
                self.viewer,
                self.json_output,
            )

        return children
