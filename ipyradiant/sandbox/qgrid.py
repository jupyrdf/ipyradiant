import qgrid
import ipywidgets as W
import traitlets as T

from rdflib import Graph
from pandas import DataFrame


class QGRIDGraphWidget(W.Box):
    graph = T.Instance(Graph)
    qgridw = T.Instance(qgrid.QgridWidget)

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if graph is not None:
            self.graph = graph

        self.children = (
            [
                self.qgridw
            ]
        )

    @T.default("qgridw")
    def make_default_qgridw(self):
        qgridw = qgrid.show_grid(
            DataFrame(),
            grid_options={
                'editable': False,
            },
            column_options={
                'editable': False,
            }
        )
        return qgridw
