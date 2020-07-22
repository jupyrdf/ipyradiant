""" doit tasks for ipyradiant

    Generally, you'll just want to `doit`.

    `doit release` does pretty much everything.

    See `doit list` for more options.
"""
import re
import subprocess
import sys
from pathlib import Path

import jupyterlab.commands
from doit.tools import PythonInteractiveAction

import _scripts.project as P


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
        file_dep=[P.LAB_INDEX, P.PIP_INSTALL_E],
        actions=[["echo", "ready to run JupyterLab with:\n\n\tdoit lab\n"]],
    )


def task_release():
    """ everything we'd need to do to release (except release)
    """
    return dict(
        file_dep=[
            P.LAB_INDEX,
            P.PIP_INSTALL_E,
            P.OK_LINT,
            P.WHEEL,
            P.CONDA_PACKAGE,
            *P.EXAMPLE_HTML,
        ],
        actions=[["echo", "ready to release"]],
    )


def task_setup():
    """ perform all setup activities
    """
    yield dict(
        name="js",
        file_dep=[P.YARN_LOCK, P.PACKAGE],
        actions=[[*P.APR_DEV, *P.JLPM, "--prefer-offline", "--ignore-optional"]],
        targets=[P.YARN_INTEGRITY],
    )
    yield _ok(
        dict(
            name="py",
            file_dep=[P.SETUP_PY, P.SETUP_CFG],
            actions=[[*P.APR_DEV, *P.PIP, "install", "-e", ".", "--no-deps"], [*P.APR_DEV, *P.PIP, "check"]],
        ),
        P.PIP_INSTALL_E,
    )


def task_build():
    """ build packages
    """
    yield dict(
        name="py",
        file_dep=[*P.ALL_PY_SRC, P.SETUP_CFG, P.SETUP_PY, P.OK_LINT],
        actions=[[*P.APR_BUILD, *P.PY, "setup.py", "sdist"], [*P.PY, "setup.py", "bdist_wheel"]],
        targets=[P.WHEEL, P.SDIST],
    )
    yield dict(
        name="conda",
        file_dep=[P.SDIST, P.META_YAML],
        actions=[
            [
                *P.APR_BUILD,
                *P.CONDA_BUILD,
                "--output-folder",
                P.DIST_CONDA,
                "-c",
                "conda-forge",
                P.RECIPE,
            ]
        ],
        targets=[P.CONDA_PACKAGE],
    )


def task_test():
    """ testing
    """
    yield dict(
        name="nbsmoke",
        file_dep=[*P.EXAMPLE_IPYNB, P.OK_NBLINT],
        actions=[
            [
                *P.APR_DEV,
                "jupyter",
                "nbconvert",
                "--output-dir",
                P.DIST_NBHTML,
                "--execute",
                *P.EXAMPLE_IPYNB,
            ]
        ],
        targets=P.EXAMPLE_HTML,
    )


def task_lint():
    """ format all source files
    """

    yield _ok(
        dict(name="isort", file_dep=P.ALL_PY, actions=[[*P.APR_QA, "isort", "-rc", *P.ALL_PY]]),
        P.OK_ISORT,
    )
    yield _ok(
        dict(
            name="black", file_dep=[*P.ALL_PY, P.OK_ISORT], actions=[[*P.APR_QA, "black", *P.ALL_PY]]
        ),
        P.OK_BLACK,
    )
    yield _ok(
        dict(
            name="flake8",
            file_dep=[*P.ALL_PY, P.OK_BLACK],
            actions=[[*P.APR_QA, "flake8", *P.ALL_PY]],
        ),
        P.OK_FLAKE8,
    )
    yield _ok(
        dict(
            name="pylint",
            file_dep=[*P.ALL_PYLINT, P.OK_BLACK],
            actions=[[*P.APR_QA, "pylint", *P.ALL_PYLINT]],
        ),
        P.OK_PYLINT,
    )
    yield _ok(
        dict(
            name="prettier",
            file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER],
            actions=[[*P.APR_QA, *P.JLPM, "lint:prettier"]],
        ),
        P.OK_PRETTIER,
    )
    yield _ok(
        dict(
            name="nblint",
            file_dep=[*P.EXAMPLE_IPYNB],
            actions=[[*P.APR_QA, *P.PY, "scripts/nblint.py", *P.EXAMPLE_IPYNB]],
            targets=[P.NBLINT_HASHES],
        ),
        P.OK_NBLINT,
    )
    yield _ok(
        dict(
            name="all",
            actions=[["echo", "all ok"]],
            file_dep=[
                P.OK_BLACK,
                P.OK_FLAKE8,
                P.OK_ISORT,
                P.OK_PRETTIER,
                P.OK_PYLINT,
                P.OK_NBLINT,
            ],
        ),
        P.OK_LINT,
    )


def task_lab_build():
    """ do a "production" build of lab
    """
    exts = [
        line.strip()
        for line in P.EXTENSIONS.read_text().strip().splitlines()
        if line and not line.startswith("#")
    ]

    def _build():
        # pylint: disable=broad-except
        build_rc = 1
        try:
            build_rc = subprocess.call(
                [*P.LAB, "build", "--debug", "--minimize=True", "--dev-build=False"]
            )
        except Exception as err:
            print(f"Encountered an error, continuing:\n\t{err}\n", flush=True)

        return build_rc == 0 or P.LAB_INDEX.exists()

    yield dict(
        name="extensions",
        file_dep=[P.EXTENSIONS],
        actions=[
            [*P.LAB, "clean", "--all"],
            [*P.LAB_EXT, "install", "--debug", "--no-build", *exts],
            _build,
            [*P.LAB_EXT, "list"],
        ],
        targets=[P.LAB_INDEX],
    )


def task_lab():
    """ run JupyterLab "normally" (not watching sources)
    """

    def lab():
        proc = subprocess.Popen([*P.LAB, "--no-browser", "--debug"])
        hard_stop = 0
        while hard_stop < 2:
            try:
                proc.wait()
            except KeyboardInterrupt:
                hard_stop += 1

        proc.terminate()
        proc.terminate()
        proc.wait()

    return dict(
        uptodate=[lambda: False],
        file_dep=[P.LAB_INDEX],
        actions=[PythonInteractiveAction(lab)],
    )


def _ok(task, ok):
    task.setdefault("targets", []).append(ok)
    task["actions"] = [
        lambda: [ok.exists() and ok.unlink(), True][-1],
        *task["actions"],
        lambda: [ok.parent.mkdir(exist_ok=True), ok.write_text("ok"), True][-1],
    ]
    return task
