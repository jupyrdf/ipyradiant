import os
import textwrap
from pathlib import Path
from rdflib import URIRef, Literal, Graph
import traitlets as trt
from rdflib.namespace import RDF
from pandas import DataFrame
import ipycytoscape
from .rdf_processor import CytoscapeGraph
import ipywidgets as ipyw


class RDFVisualization(ipyw.GridBox):
    '''
    This is a class that will take an rdflib.graph.Graph object as a parameter
    and output a visualization tab to go along with the ipyradiant widget.
    '''

    cyto_widget = trt.Instance(ipycytoscape.CytoscapeWidget)
    nodes = trt.List()
    node_selector = trt.Instance(ipyw.Dropdown)
    click_output = trt.Instance(ipyw.Output)
    click_output_box = trt.Instance(ipyw.VBox)
    node_selector_box = trt.Instance(ipyw.VBox)
    selected_node = trt.Unicode(allow_none=True)

    @trt.default('node_selector')
    def _make_node_selector(self):
        selector = ipyw.Dropdown(
            options = self.nodes,
        )
        trt.link((selector,'value'),(self,'selected_node'))
        return selector
    @trt.default('click_output')
    def _make_click_output(self):
        return ipyw.Output()

    @trt.default('nodes')
    def _make_default_nodes(self):
        return []

    @trt.default('click_output_box')
    def _make_default_click_output_box(self):
        return ipyw.VBox()

    @trt.default('node_selector_box')
    def _make_node_selector_box(self):
        return ipyw.VBox()

    default_edge={
        'selector': 'edge',
        'css': {
            'line-color': 'blue'
        }
    }

    default_node={
        'selector': 'node',
        'css': {
            'background-color': 'grey'
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rdf_graph = kwargs['rdf_graph']
        post_process_rdf = CytoscapeGraph(rdf_graph)
        self.cyto_widget = post_process_rdf.cytoscapeobj
        self.nodes = list(post_process_rdf.nodes.keys())
        self.output_title = ipyw.HTML('<h1>Outputs from Nodes/Edges</h1>')
        self.node_selector_title = ipyw.HTML('<h1> Select a node to view </h1>')
        self.cyto_widget.on('node', 'click', self.log_node_clicks)
        self.cyto_widget.on('edge', 'click', self.log_edge_clicks)

        #set styles
        self.cyto_widget.set_style([self.default_node,self.default_edge])
        self.layout=ipyw.Layout(grid_template_columns="32% 40% 28%",height='500px',border='solid 2px')

        self.build_ui()

    def build_ui(self):
        self.click_output_box.children = [self.output_title,self.click_output]
        self.node_selector_box.children = [self.node_selector_title,self.node_selector]
        self.children = [self.node_selector_box, self.cyto_widget, self.click_output_box]

    @trt.observe('selected_node')
    def highlight_node(self, *_):

        self.cyto_widget.set_style([{
            'selector': 'node[id = "{}"]'.format(self.selected_node),
            'css': {
                'background-color': 'red'
            }},
            self.default_edge
        ])

        self.build_ui()

    def log_node_clicks(self,node):
        with self.click_output:
            print(f"node clicked: {node['data']}")
            print('-------------------------------')
        self.build_ui()

    def log_edge_clicks(self,edge):
        with self.click_output:
            print(f'edge clicked:')
            print(f'edge source: {edge["data"]["source"]}')
            print(f'edge target: {edge["data"]["target"]}')
            print('-------------------------------')
        self.build_ui()
