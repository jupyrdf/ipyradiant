import ipywidgets as W
import traitlets as T


class VisBase(W.VBox):
    renderer = T.Unicode("auto").tag(sync=True)
    graph = T.Instance(Graph, allow_none=True)
    _vis = T.Instance(W.Box, allow_none=True)
    edge_color = T.Unicode()
    node_color = T.Unicode()
    selected_nodes = T.List()
    selected_edges = T.List()
    hovered_nodes = T.List()
    hovered_edges = T.List()
    layout = T.Any()

    @T.observe("graph")
    def _on_graph(self, change):
        if change.old:
            pass
        if change.new is None:
            self.children = []
            self._vis.close()
            self._vis = None
        else:
            pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edge_color = kwargs.get("edge_color", "pink")
        self.node_color = kwargs.get("node_color", "grey")
