""" doit tasks for ipyradiant

    Generally, you'll just want to `doit`. See `doit list` for more options.
"""
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


def task_lint():
    """ format all source files
    """
    yield dict(name="isort", file_dep=P.ALL_PY, actions=[["isort", "-rc", *P.ALL_PY]])
    yield dict(name="black", file_dep=P.ALL_PY, actions=[["black", *P.ALL_PY]])
    yield dict(name="flake8", file_dep=P.ALL_PY, actions=[["flake8", *P.ALL_PY]])
    yield dict(name="mypy", file_dep=P.ALL_PY_SRC, actions=[["mypy", *P.ALL_PY_SRC]])
    yield dict(
        name="pylint", file_dep=P.ALL_PYLINT, actions=[["pylint", *P.ALL_PYLINT]]
    )
    yield dict(
        name="prettier",
        file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER],
        actions=[[*P.JLPM, "lint:prettier"]],
    )


def task_lab():
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
            [*P.LAB_EXT, "list"],
            [*P.LAB_EXT, "install", "--debug", "--no-build", *exts],
        ],
        targets=[P.LAB_LOCK],
    )
    yield dict(
        name="build",
        file_dep=[P.LAB_LOCK],
        actions=[
            [
                "jupyter",
                "lab",
                "build",
                "--debug",
                "--minimize=True",
                "--dev-build=False",
            ]
        ],
        targets=[P.LAB_INDEX],
    )


def task_binder():
    """ get to a minimal interactive environment
    """
    return dict(file_dep=[P.LAB_INDEX, P.EGG_LINK], actions=[["echo", "ok"]])


# pylint: disable=invalid-name,too-few-public-methods
class P:
    """ important paths
    """

    DODO = Path(__file__)
    HERE = DODO.parent
    POSTBUILD = HERE / "postBuild"

    # tools
    PY = [Path(sys.executable)]
    SITE_PKGS = Path(site.getsitepackages()[0])
    EGG_LINK = SITE_PKGS / "ipyradiant.egg-link"
    PYM = [*PY, "-m"]
    PIP = [*PYM, "pip"]
    JLPM = ["jlpm"]
    LAB_EXT = ["jupyter", "labextension"]

    NODE_MODULES = HERE / "node_modules"
    PACKAGE = HERE / "package.json"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    YARN_LOCK = HERE / "yarn.lock"

    EXTENSIONS = HERE / "labextensions.txt"

    PY_SRC = HERE / "ipyradiant"
    SETUP_PY = HERE / "setup.py"
    SETUP_CFG = HERE / "setup.cfg"
    ALL_PY_SRC = [*PY_SRC.rglob("*.py")]
    ALL_PY = [DODO, POSTBUILD, *ALL_PY_SRC]
    ALL_PYLINT = [p for p in ALL_PY if p.name != "postBuild"]
    ALL_YML = [*HERE.glob("*.yml")]
    ALL_JSON = [*HERE.glob("*.json")]
    ALL_PRETTIER = [*ALL_YML, *ALL_JSON]

    LAB_APP_DIR = Path(jupyterlab.commands.get_app_dir())
    LAB_STAGING = LAB_APP_DIR / "staging"
    LAB_LOCK = LAB_STAGING / "yarn.lock"
    LAB_STATIC = LAB_APP_DIR / "static"
    LAB_INDEX = LAB_STATIC / "index.html"
