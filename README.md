# ipyradiant

[Jupyter Widgets][widgets] for [RDF][rdf] graph interaction, querying, and visualization
in [JupyterLab][jupyterlab].

|                           Install                           |            Demo             |        Build        |                          Docs                           |
| :---------------------------------------------------------: | :-------------------------: | :-----------------: | :-----------------------------------------------------: |
| [![pypi-badge][]][pypi] <br/> [![conda-badge]][conda-forge] | [![binder-badge][]][binder] | [![ci-badge][]][ci] | [CHANGELOG][] <br/> [CONTRIBUTING][] <br/> [examples][] |

Powered by [ipyctoscape][ipycytoscape], [datashader][datashader], and
[holoviews][holoviews].

## Visualization Widgets

`ipyradiant` includes several widgets for visualizing and interacting with RDF graphs
that can be accessed through the examples. ![InteractiveViewer screencast][screencast1]

## Example Tooling Widgets

`ipyradiant` includes examples where visualization and utility widgets are linked into
example tooling. ![TabApp screencast][screencast2]

## Prerequisites

- `python >=3.6`

`ipyradiant`'s python dependencies will install their required `nbextensions` for
Notebook Classic.

For JupyterLab support, ensure you have the following installed:

- `jupyterlab >=3`
- `nodejs >=10`

## JupyterLab compatibility

While `ipyradiant` doesn't provide any JupyterLab extensions, it depends on a number of
them.

The release of JupyterLab 3 has made some version compatibility unpredictable. Below are
some researched combinations that should work.

| `jupyterlab` | `ipycytoscape` | `pyviz_comms` | `pip install`      |
| ------------ | -------------- | ------------- | ------------------ |
| `>=3,<4`     | `>=1.1.0`      | `>=1.0.3`     | `ipyradiant[lab3]` |

## Install

### `ipyradiant` with `conda` (recommended)

```bash
conda install -c conda-forge ipyradiant
```

### `ipyradiant` with `pip`

```bash
pip install ipyradiant
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
  https://user-images.githubusercontent.com/32652349/113428662-2daafe80-93a5-11eb-9328-f5325c0ab4df.gif
[screencast2]:
  https://user-images.githubusercontent.com/32652349/113429085-f2f59600-93a5-11eb-90de-3dd07d3258f1.gif
[pypi]: https://pypi.org/project/ipyradiant
[pypi-badge]: https://img.shields.io/pypi/v/ipyradiant
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/ipyradiant
[conda-forge]: https://anaconda.org/conda-forge/ipyradiant/
