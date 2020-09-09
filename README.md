# ipyradiant

[Jupyter Widgets][widgets] for [RDF][rdf] graph interaction, querying, and visualization
in [JupyterLab][jupyterlab].

|                           Install                           |            Demo             |        Build        |                          Docs                           |
| :---------------------------------------------------------: | :-------------------------: | :-----------------: | :-----------------------------------------------------: |
| [![pypi-badge][]][pypi] <br/> [![conda-badge]][conda-forge] | [![binder-badge][]][binder] | [![ci-badge][]][ci] | [CHANGELOG][] <br/> [CONTRIBUTING][] <br/> [examples][] |

Powered by [ipyctoscape][ipycytoscape], [datashader][datashader], and
[holoviews][holoviews].

## Visualization Widgets

`ipyradiant` includes several widgets for visualizing RDF graphs that can be accessed
through the examples. ![datashader screencast][screencast1]

## Example Tooling Widgets

`ipyradiant` includes examples where visualization and utility widgets are linked into
example tooling. ![TabApp screencast][screencast2]

## Prerequisites

- `python >=3.6`

`ipyradiant`'s python dependencies will install their required `nbextensions` for
Notebook Classic.

For JupyterLab support, ensure you have the following installed:

- `jupyterlab >=1`
- `nodejs >=10`

## Install

### `ipyradiant` with `conda` (recommended)

```bash
conda install -c conda-forge ipyradiant
```

### `ipyradiant` with `pip`

```bash
pip install ipyradiant
```

### JupyterLab Extensions

Install the lab extensions that `ipyradiant` depends on.

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-cytoscape @pyviz/jupyterlab_pyviz qgrid2
```

> For additional information, see [CONTRIBUTING.md][contributing]

## Open Source

This work is licensed under the [BSD-3-Clause License][license].

[license]: https://github.com/jupyrdf/ipyradiant/tree/master/LICENSE
[examples]: https://github.com/jupyrdf/ipyradiant/tree/master/index.ipynb
[contributing]: https://github.com/jupyrdf/ipyradiant/tree/master/CONTRIBUTING.md
[changelog]: https://github.com/jupyrdf/ipyradiant/tree/master/CHANGELOG.md
[ci-badge]: https://github.com/jupyrdf/ipyradiant/workflows/CI/badge.svg
[ci]: https://github.com/jupyrdf/ipyradiant/actions?query=workflow%3ACI+branch%3Amaster
[datashader]: https://datashader.org/
[binder-badge]: https://mybinder.org/badge_logo.svg
[binder]:
  https://mybinder.org/v2/gh/jupyrdf/ipyradiant/master?urlpath=lab/tree/index.ipynb
[holoviews]: http://holoviews.org/
[ipycytoscape]: https://github.com/QuantStack/ipycytoscape
[jupyterlab]: https://github.com/jupyterlab/jupyterlab
[widgets]: https://jupyter.org/widgets
[rdf]: https://www.w3.org/RDF/
[screencast1]:
  https://user-images.githubusercontent.com/32652349/91210101-b6104500-e6da-11ea-9db2-967d2426c630.gif
[screencast2]:
  https://user-images.githubusercontent.com/32652349/90517340-44148a80-e133-11ea-9ee4-add09ee2c0d4.gif
[pypi]: https://pypi.org/project/ipyradiant
[pypi-badge]: https://img.shields.io/pypi/v/ipyradiant
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/ipyradiant
[conda-forge]: https://anaconda.org/conda-forge/ipyradiant/
