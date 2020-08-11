import ipywidgets as W
import traitlets as T
from .base import VisBase


class VisSelector(W.Dropdown):
    vis = T.Instance(VisBase)

    @T.observe("vis")
    def _update_options(self, change):
        if change.new is None:
            return
        T.link((change.new, "graph_layout_options"), (self, "options"))
        T.link((change.new, "graph_layout"), (self, "value"))
