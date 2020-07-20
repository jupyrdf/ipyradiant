""" a small wrapper around qrid for a graph
"""
# pylint: disable=no-self-use
import ipywidgets as W
import traitlets as T
from pandas import DataFrame
from qgrid import QgridWidget, show_grid
from rdflib import Graph


class QGRIDGraphWidget(W.Box):
    """ A box which contains a qgrid
    """

    # pylint: disable=keyword-arg-before-vararg

    graph: Graph = T.Instance(Graph)
    qgridw: QgridWidget = T.Instance(QgridWidget)

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if graph is not None:
            self.graph = graph

        self.children = [self.qgridw]

    @T.default("qgridw")
    def make_default_qgridw(self) -> QgridWidget:
        """ generate a default qgrid if not provided
        """
        qgridw = show_grid(
            DataFrame(),
            grid_options={"editable": False},
            column_options={"editable": False},
        )
        return qgridw
