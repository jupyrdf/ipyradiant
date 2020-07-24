# Contributing to `ipyradiant`

## Pre-requisites

> ### Windows Users
>
> Please try to put your base `conda` and your git checkout in the shortest possible
> paths, and on the same, local drive, e.g. `c:\mc3` and `c:\git\ipyradiant`. Try to
> avoid paths managed by DropBox, OneDrive, etc. and consider turning off search
> indexing and Windows Defender for these paths.
>
> Also, you may wish to ensure you have no existing Jupyter kernels in your user paths:
> basically anything in the output of `jupyter --paths` that quacks like being in your
> HOME/AppData/whatever is fair game, and can safely be deleted. They will be recreated
> as needed with the proper permissions.
>
> `doit` will cowardly refuse to do anything if some of the above are not met

- install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (Python 3, 64-bit)
- install `anaconda-project` and `doit` into the `base` env

```bat
conda install anaconda-project=0.84 doit=0.32
```

or, use the same base environment as CI:

```bat
:: windows
conda env update .ci\environment.yml
c:\mc3\envs\ipyradiant-base\Scripts\activate
```

```bash
# unix
conda env update .ci/environment.yml
source ~/mc3/envs/ipyradiant-base/bin/activate
```

## Get To a Running Lab

```bash
doit lab
```

- open the browser with the URL shown

## Get Ready for a Release

```bash
doit release
```

- fix the things that break, keep running until it completes
- this won't actually release anything
