# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import traitlets as T

import ipywidgets as W

from .base import VisualizerBase


class LayoutSelector(W.Dropdown):
    vis = T.Instance(VisualizerBase)

    @T.observe("vis")
    def _update_options(self, change):
        if change.new is None:
            return
        T.link((change.new, "graph_layout_options"), (self, "options"))
        T.link((change.new, "graph_layout"), (self, "value"))
