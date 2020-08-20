# ipyradiant

[![Binder][]][binder-link] [![status][]][status-link]

Jupyter Widgets for RDF graph interaction, querying, and visualization in JupyterLab and
the Jupyter notebook.

[binder]: https://mybinder.org/badge_logo.svg
[binder-link]:
  https://mybinder.org/v2/gh/jupyrdf/ipyradiant/master?urlpath=lab/tree/index.ipynb
[status]:
  https://github.com/jupyrdf/ipyradiant/workflows/.github/workflows/ciV0.yml/badge.svg
[status-link]: https://github.com/jupyrdf/ipyradiant/actions

Powered by [ipyctoscape](https://github.com/QuantStack/ipycytoscape),
[datashader](https://datashader.org/), and [holoviews](http://holoviews.org/).

## Visualization Widgets

`ipyradiant` includes several widgets for visualizing RDF graphs that can be accessed
through the examples.
![datashader screencast](https://user-images.githubusercontent.com/32652349/90517352-470f7b00-e133-11ea-8cb8-8e810198ced0.gif)

## Example Tooling Widgets

`ipyradiant` includes examples where visualization and utility widgets are linked into
example tooling.
![TabApp screencast](https://user-images.githubusercontent.com/32652349/90517340-44148a80-e133-11ea-9ee4-add09ee2c0d4.gif)

## Prerequisites

- `python >=3.6`

`ipyradiant`'s python dependencies will install their required `nbextensions` for
Notebook Classic.

For JupyterLab support, ensure you have the following installed:

- `jupyterlab >=1`
- `nodejs >=10`

## Installation

```bash
pip install ipyradiant
jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-cytoscape @pyviz/jupyterlab_pyviz qgrid2
```

> For additional information, see [CONTRIBUTING.md](./CONTRIBUTING.md)
