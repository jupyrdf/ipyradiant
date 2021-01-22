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

- install [Mambaforge](https://github.com/conda-forge/miniforge/releases)
- install `anaconda-project` and `doit` into the `base` env

```bat
mamba install -c conda-forge anaconda-project=0.8.4 doit=0.32
```

or, use the same base environment as CI:

```bat
:: windows
mamba env update --file .ci\environment.yml
c:\mc3\envs\ipyradiant-base\Scripts\activate
```

```bash
# unix
mamba env update --file .ci/environment.yml
source ~/mc3/envs/ipyradiant-base/bin/activate
```

## See What You Can do(it)

```bash
doit list --all --status
```

## Get To a Running Lab

```bash
doit preflight:lab
doit lab
```

- open the browser with the URL shown
- open `index.ipynb` for a landing page with links to examples

## Get Ready for a Release

```bash
doit release
```

- fix the things that break, keep running until it completes
- this won't actually release anything

## Quick Review a PR

```bash
git clean -dxf
doit all
```

- go get a coffee
- runs `preflight:lab` and `release`

## Releasing

- Start a release issue with version and release name
  - Pick an unused, random radiance unit from [wikipedia][radiance-si-units]
- After merging all PRs to `master`, download the `ipyradiant` dist artifacts after a
  successful CI run
- Tag appropriately through the GitHub release web UI
- Check out `master`
- Extract and inspect the files in `./dist`.
- Ensure you have credentials for `pypi`

```bash
anaconda-project run --env-spec build twine check ipyradiant*
anaconda-project run --env-spec build twine upload ipyradiant*
```

- Check hashes on `pypi`
- Complete `conda-forge` tasks
  - go to [ipyradiant-feedstock](https://github.com/conda-forge/ipyradiant-feedstock) and fork
  - update `recipe/meta.yml` (version and sha for tar)
  - submit PR to conda-forge feedstock (go through checklist). DO NOT PUSH DIRECTLY
  - wait for CI, merge and wait for CI again

[radiance-si-units]: https://en.wikipedia.org/wiki/Radiance#SI_radiometry_units

## Updating environments

After changing any `env_spec` in `anaconda-project.yml` (and/or `environment.yml`), it
is recommended to use `mamba` for the rather hefty re-solve of all the environments.

```bash
# On Unix
export CONDA_EXE=mamba
export CONDARC=.github/.condarc
anaconda-project update -n dev
anaconda-project update -n build
anaconda-project update -n qa
doit lint:prettier
```

Or...

```bat
::on windows
set CONDA_EXE=mamba
set CONDARC=.github\.condarc
anaconda-project update -n dev
anaconda-project update -n build
anaconda-project update -n qa
doit lint:prettier
```
