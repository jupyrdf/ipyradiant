""" a Box wrapper around qgrid with a graph
"""
# pylint: disable=R0201,W1113
import ipywidgets as W
import qgrid
import traitlets as T
from pandas import DataFrame
from rdflib import Graph


class QGRIDGraphWidget(W.Box):
    """ A qgrid for a graph
    """

    graph = T.Instance(Graph)
    qgridw = T.Instance(qgrid.QgridWidget)

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if graph is not None:
            self.graph = graph

        self.children = [self.qgridw]

    @T.default("qgridw")
    def make_default_qgridw(self):
        """ create a read-only qgrid
        """
        qgridw = qgrid.show_grid(
            DataFrame(),
            grid_options={"editable": False},
            column_options={"editable": False},
        )
        return qgridw
