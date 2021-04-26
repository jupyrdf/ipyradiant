# `ipyradiant` CHANGELOG

## 0.2.0 (WIP)

- adds `InteractiveViewer` widget (small RDF graphs as LPG with type coloring)
- adds `CytoscapeViewer` widget (common graph visualization for RDF and LPG i.e.
  networkx)
- removes `InteractiveVisualization` widget
- removes `GraphExplorer` widget and associated code/tests
- improves `QueryWidget` layout and namespace resolution
- improves `RDF2NX` converter by allowing multiple queries to be defined for each
  behavior
- improves reliability of `RDF2NX` converter via improved namespace management
- support for `jupyterlab >= 3`

## 0.1.2 (J_e) (2021-01-21)

- adds `RDF2NX` transformer for converting RDF to a networkx labelled property graph
- adds examples of federated queries
- adds `pygment` for colorizing SPARQL queries in the `QueryWidget`
- adds support and examples for using metaclasses with `SPARQLQueryFramer` to specify
  SPARQL VALUES
- adds `GraphExplorer` widget for simple exploration of RDF graphs
- removes `qgrid` as a dependency

## 0.1.1 (J_e_v) (2020-09-09)

- adds `MultiPanelSelect` widget in preparation for RDF to networkx transformer (#34)
- pins to `networkx >=2`, more lenient loading of layouts (#43)

## 0.1.0 (H_e) (2020-08-24)

- initial release
