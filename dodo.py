""" doit tasks for ipyradiant

    Generally, you'll just want to `doit`.

    `doit release` does pretty much everything.

    See `doit list` for more options.
"""
import re
import site
import sys
from pathlib import Path

import jupyterlab.commands

DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "default_tasks": ["binder"],
}


def task_binder():
    """ get to a minimal interactive environment
    """
    return dict(
        file_dep=[P.LAB_INDEX, P.EGG_LINK], actions=[["echo", "ready for binder"]]
    )


def task_release():
    """ everything we'd need to do to release (except release)
    """
    return dict(
        file_dep=[P.LAB_INDEX, P.EGG_LINK, B.LINT, B.WHEEL, B.CONDA_PACKAGE],
        actions=[["echo", "ready to release"]],
    )


def task_setup():
    """ perform all setup activities
    """
    yield dict(
        name="js",
        file_dep=[P.YARN_LOCK, P.PACKAGE],
        actions=[[*P.JLPM, "--prefer-offline", "--ignore-optional"]],
        targets=[P.YARN_INTEGRITY],
    )
    yield dict(
        name="py",
        file_dep=[P.SETUP_PY, P.SETUP_CFG],
        actions=[[*P.PIP, "install", "-e", ".", "--no-deps"], [*P.PIP, "check"]],
        targets=[P.EGG_LINK],
    )


def task_build():
    """ build packages
    """
    yield dict(
        name="py",
        file_dep=[*P.ALL_PY_SRC, P.SETUP_CFG, P.SETUP_PY, B.LINT],
        actions=[[*P.PY, "setup.py", "sdist"], [*P.PY, "setup.py", "bdist_wheel"]],
        targets=[B.WHEEL, B.SDIST],
    )
    yield dict(
        name="conda",
        file_dep=[B.SDIST, P.META_YAML],
        actions=[
            [
                *P.CONDA_BUILD,
                "--output-folder",
                P.DIST_CONDA,
                "-c",
                "conda-forge",
                P.RECIPE,
            ]
        ],
        targets=[B.CONDA_PACKAGE],
    )


def task_test():
    """ testing
    """
    yield dict(
        name="nbsmoke",
        file_dep=[*P.EXAMPLE_IPYNB],
        actions=[
            [
                "jupyter",
                "nbconvert",
                "--output-dir",
                P.DIST,
                "--execute",
                *P.EXAMPLE_IPYNB,
            ]
        ],
        targets=B.EXAMPLE_HTML,
    )


def task_lint():
    """ format all source files
    """

    yield _ok(
        dict(name="isort", file_dep=P.ALL_PY, actions=[["isort", "-rc", *P.ALL_PY]]),
        B.ISORT,
    )
    yield _ok(
        dict(
            name="black", file_dep=[*P.ALL_PY, B.ISORT], actions=[["black", *P.ALL_PY]]
        ),
        B.BLACK,
    )
    yield _ok(
        dict(
            name="flake8",
            file_dep=[*P.ALL_PY, B.BLACK],
            actions=[["flake8", *P.ALL_PY]],
        ),
        B.FLAKE8,
    )
    yield _ok(
        dict(
            name="mypy",
            file_dep=[*P.ALL_PY_SRC, B.BLACK],
            actions=[["mypy", *P.ALL_PY_SRC]],
        ),
        B.MYPY,
    )
    yield _ok(
        dict(
            name="pylint",
            file_dep=[*P.ALL_PYLINT, B.BLACK],
            actions=[["pylint", *P.ALL_PYLINT]],
        ),
        B.PYLINT,
    )
    yield _ok(
        dict(
            name="prettier",
            file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER],
            actions=[[*P.JLPM, "lint:prettier"]],
        ),
        B.PRETTIER,
    )
    yield _ok(
        dict(
            name="nblint",
            file_dep=[*P.EXAMPLE_IPYNB],
            actions=[[*P.PY, "scripts/nblint.py", *P.EXAMPLE_IPYNB]],
            targets=[B.NBLINT_HASHES],
        ),
        B.NBLINT,
    )
    yield _ok(
        dict(
            name="all",
            actions=[["echo", "all ok"]],
            file_dep=[
                B.BLACK,
                B.FLAKE8,
                B.ISORT,
                B.MYPY,
                B.PRETTIER,
                B.PYLINT,
                B.NBLINT,
            ],
        ),
        B.LINT,
    )


def task_lab_build():
    """ get lab up to running
    """
    exts = [
        line.strip()
        for line in P.EXTENSIONS.read_text().strip().splitlines()
        if line and not line.startswith("#")
    ]
    yield dict(
        name="extensions",
        file_dep=[P.EXTENSIONS],
        actions=[
            [*P.LAB_EXT, "install", "--debug", "--no-build", *exts],
            [
                "jupyter",
                "lab",
                "build",
                "--debug",
                "--minimize=True",
                "--dev-build=False",
            ],
        ],
        targets=[P.LAB_INDEX],
    )


# pylint: disable=invalid-name,too-few-public-methods
class P:
    """ important paths
    """

    DODO = Path(__file__)
    HERE = DODO.parent
    POSTBUILD = HERE / "postBuild"
    BUILD = HERE / "build"
    DIST = HERE / "dist"
    RECIPE = HERE / "conda.recipe"

    # tools
    PY = [Path(sys.executable)]
    SITE_PKGS = Path(site.getsitepackages()[0])
    EGG_LINK = SITE_PKGS / "ipyradiant.egg-link"
    PYM = [*PY, "-m"]
    PIP = [*PYM, "pip"]
    JLPM = ["jlpm"]
    LAB_EXT = ["jupyter", "labextension"]
    CONDA_BUILD = ["conda", "build"]

    # top-level stuff
    SETUP_PY = HERE / "setup.py"
    SETUP_CFG = HERE / "setup.cfg"
    NODE_MODULES = HERE / "node_modules"
    PACKAGE = HERE / "package.json"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    YARN_LOCK = HERE / "yarn.lock"
    SCRIPTS = HERE / "scripts"
    EXTENSIONS = HERE / "labextensions.txt"
    CI = HERE / ".github"

    PY_SRC = HERE / "src" / "ipyradiant"
    VERSION_PY = PY_SRC / "_version.py"

    LAB_APP_DIR = Path(jupyterlab.commands.get_app_dir())
    LAB_STAGING = LAB_APP_DIR / "staging"
    LAB_LOCK = LAB_STAGING / "yarn.lock"
    LAB_STATIC = LAB_APP_DIR / "static"
    LAB_INDEX = LAB_STATIC / "index.html"

    # tests
    EXAMPLES = HERE / "examples"
    EXAMPLE_IPYNB = [
        p for p in EXAMPLES.rglob("*.ipynb") if ".ipynb_checkpoints" not in str(p)
    ]
    EXAMPLE_PY = [*EXAMPLES.rglob("*.py")]

    ALL_PY_SRC = [*PY_SRC.rglob("*.py")]
    ALL_PY = [DODO, POSTBUILD, *ALL_PY_SRC, *EXAMPLE_PY, *SCRIPTS.rglob("*.py")]
    ALL_PYLINT = [p for p in ALL_PY if p.name != "postBuild"]
    ALL_YML = [*HERE.glob("*.yml"), *CI.rglob("*.yml")]
    ALL_JSON = [*HERE.glob("*.json")]
    ALL_PRETTIER = [*ALL_YML, *ALL_JSON]

    # conda
    META_YAML = RECIPE / "meta.yaml"
    DIST_CONDA = DIST / "conda-bld"


class D:
    """ data loaded from paths
    """

    PY_VERSION = re.findall(r'''__version__ = "(.*)"''', P.VERSION_PY.read_text())[0]
    CONDA_BUILD_NO = re.findall(r'''number: (\d+)''', P.META_YAML.read_text())[0]


class B:
    """ canary files for marking things as ok that don't have predictable outputs
    """

    PYLINT = P.BUILD / "pylint.ok"
    BLACK = P.BUILD / "black.ok"
    MYPY = P.BUILD / "mypy.ok"
    ISORT = P.BUILD / "isort.ok"
    FLAKE8 = P.BUILD / "flake8.ok"
    PRETTIER = P.BUILD / "prettier.ok"
    NBLINT = P.BUILD / "nblint.ok"
    NBLINT_HASHES = P.BUILD / "nblint.hashes"
    LINT = P.BUILD / "lint.ok"
    SDIST = P.DIST / f"ipyradiant-{D.PY_VERSION}.tar.gz"
    WHEEL = P.DIST / f"ipyradiant-{D.PY_VERSION}-py3-none-any.whl"
    EXAMPLE_HTML = [
        P.BUILD / p.name.replace(".ipynb", ".html") for p in P.EXAMPLE_IPYNB
    ]
    CONDA_PACKAGE = P.DIST_CONDA / "noarch" / f"ipyradient-{D.PY_VERSION}-py_{D.CONDA_BUILD_NO}.tar.bz2"


def _ok(task, ok):
    task.setdefault("targets", []).append(ok)
    task["actions"] = [
        lambda: [ok.exists() and ok.unlink(), True][-1],
        *task["actions"],
        lambda: [ok.parent.mkdir(exist_ok=True), ok.write_text("ok"), True][-1],
    ]
    return task
