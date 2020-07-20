""" doit tasks for ipyradiant

    Generally, you'll just want to `doit`. See `doit list` for more options.
"""
import sys
from pathlib import Path

DOIT_CONFIG = {"backend": "sqlite3", "verbosity": 2}


def task_setup():
    """ perform all setup activities
    """
    yield dict(
        name="js",
        file_dep=[P.YARN_LOCK, P.PACKAGE],
        actions=[[*P.JLPM, "--prefer-offline", "--ignore-optional"]],
        targets=[P.YARN_INTEGRITY],
    )


def task_lint():
    """ format all source files
    """
    yield dict(name="isort", file_dep=P.ALL_PY, actions=[["isort", "-rc", *P.ALL_PY]])
    yield dict(name="black", file_dep=P.ALL_PY, actions=[["black", *P.ALL_PY]])
    yield dict(name="flake8", file_dep=P.ALL_PY, actions=[["flake8", *P.ALL_PY]])
    yield dict(name="pylint", file_dep=P.ALL_PY, actions=[["pylint", *P.ALL_PY]])
    yield dict(
        name="prettier",
        file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER],
        actions=[[*P.JLPM, "lint:prettier"]],
    )


# pylint: disable=invalid-name,too-few-public-methods
class P:
    """ important paths
    """

    DODO = Path(__file__)
    HERE = DODO.parent
    POSTBUILD = HERE / "postBuild"

    # tools
    PY = Path(sys.executable)
    JLPM = ["jlpm"]

    NODE_MODULES = HERE / "node_modules"
    PACKAGE = HERE / "package.json"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    YARN_LOCK = HERE / "yarn.lock"

    ALL_PY = [DODO, POSTBUILD]
    ALL_YML = [*HERE.glob("*.yml")]
    ALL_JSON = [*HERE.glob("*.json")]
    ALL_PRETTIER = [*ALL_YML, *ALL_JSON]
