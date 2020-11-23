""" doit tasks for ipyradiant

    Generally, you'll just want to `doit`.

    `doit release` does pretty much everything.

    See `doit list` for more options.
"""

# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import os
import shutil
import subprocess

import _scripts.project as P
import _scripts.utils as U
from doit.action import CmdAction
from doit.tools import PythonInteractiveAction, config_changed
from yaml import safe_load

os.environ["PYTHONIOENCODING"] = "utf-8"

DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "default_tasks": ["binder"],
}

COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8")

PROJ = safe_load(P.PROJ.read_text(encoding="utf-8"))


def task_preflight():
    """ensure a sane development environment"""
    file_dep = [P.PROJ_LOCK, P.SCRIPTS / "preflight.py"]

    yield _ok(
        dict(
            uptodate=[config_changed({"commit": COMMIT})],
            name="conda",
            file_dep=file_dep,
            actions=(
                [_echo_ok("skipping preflight, hope you know what you're doing!")]
                if P.SKIP_CONDA_PREFLIGHT
                else [[*P.PREFLIGHT, "conda"]]
            ),
        ),
        P.OK_PREFLIGHT_CONDA,
    )

    yield _ok(
        dict(
            name="kernel",
            file_dep=[*file_dep, P.OK_ENV["dev"]],
            actions=[[*P.APR_DEV, *P.PREFLIGHT, "kernel"]],
        ),
        P.OK_PREFLIGHT_KERNEL,
    )

    yield _ok(
        dict(
            name="lab",
            file_dep=[*file_dep, P.LAB_INDEX, P.OK_ENV["dev"]],
            actions=[[*P.APR_DEV, *P.PREFLIGHT, "lab"]],
        ),
        P.OK_PREFLIGHT_LAB,
    )

    yield _ok(
        dict(
            name="release",
            file_dep=[P.CHANGELOG, P.VERSION_PY, P.SDIST, P.WHEEL, *P.ALL_PY],
            actions=[[*P.APR_DEV, *P.PREFLIGHT, "release"]],
        ),
        P.OK_PREFLIGHT_RELEASE,
    )


def task_binder():
    """get to a minimal interactive environment"""
    return dict(
        file_dep=[
            P.LAB_INDEX,
            P.OK_PIP_INSTALL,
            P.OK_PREFLIGHT_KERNEL,
            P.OK_PREFLIGHT_LAB,
        ],
        actions=[_echo_ok("ready to run JupyterLab with:\n\n\tdoit lab\n")],
    )


def task_env():
    """prepare project envs"""
    envs = ["dev", "build", "qa"]
    for i, env in enumerate(envs):
        file_dep = [P.PROJ_LOCK, P.OK_PREFLIGHT_CONDA]
        if P.FORCE_SERIAL_ENV_PREP and i:
            file_dep += [P.OK_ENV[envs[i - 1]]]
        yield _ok(
            dict(name=env, file_dep=file_dep, actions=[[*P.AP_PREP, env]]),
            P.OK_ENV[env],
        )


def task_release():
    """everything we'd need to do to release (except release)"""
    return _ok(
        dict(
            file_dep=[
                *P.EXAMPLE_HTML,
                P.OK_LINT,
                P.OK_PIP_INSTALL,
                P.OK_PREFLIGHT_RELEASE,
                P.WHEEL,
                P.HTML_COV_INDEX,
            ],
            actions=[_echo_ok("ready to release")],
        ),
        P.OK_RELEASE,
    )


def task_setup():
    """perform all setup activities"""

    _install = ["--no-deps", "--ignore-installed", "-vv"]

    if P.INSTALL_ARTIFACT == "wheel":
        _install += [P.WHEEL]
    elif P.INSTALL_ARTIFACT == "sdist":
        _install += [P.SDIST]
    else:
        _install += ["-e", "."]

    yield _ok(
        dict(
            name="py",
            file_dep=[P.SETUP_PY, P.SETUP_CFG, P.OK_ENV["dev"], P.WHEEL, P.SDIST],
            uptodate=[config_changed({"artifact": P.INSTALL_ARTIFACT})],
            actions=[
                [*P.APR_DEV, *P.PIP, "install", *_install],
                [*P.APR_DEV, *P.PIP, "check"],
            ],
        ),
        P.OK_PIP_INSTALL,
    )

    yield dict(
        name="js",
        file_dep=[P.YARN_LOCK, P.PACKAGE, P.OK_ENV["dev"]],
        actions=[[*P.APR_DEV, *P.JLPM_INSTALL]],
        targets=[P.YARN_INTEGRITY],
    )


def task_build():
    """build packages"""
    yield dict(
        name="py",
        file_dep=[
            *P.ALL_PY_SRC,
            P.SETUP_CFG,
            P.SETUP_PY,
            P.OK_BLACK,
            P.OK_ENV["build"],
        ],
        actions=[
            [*P.APR_BUILD, *P.PY, "setup.py", "sdist"],
            [*P.APR_BUILD, *P.PY, "setup.py", "bdist_wheel"],
        ],
        targets=[P.WHEEL, P.SDIST],
    )


def task_test():
    """run all the notebooks"""
    test_deps = [
        P.OK_PYFLAKES,
        P.OK_ENV["dev"],
        P.OK_PIP_INSTALL,
        P.OK_PREFLIGHT_KERNEL,
        *P.ALL_PY_SRC,
    ]

    def _nb_test(nb):
        def _test():
            env = dict(os.environ)
            env.update(IPYRADIANT_TESTING="true")
            args = [
                *P.APR_DEV,
                "jupyter",
                "nbconvert",
                "--output-dir",
                P.DIST_NBHTML,
                "--execute",
                "--ExecutePreprocessor.timeout=1200",
                nb,
            ]
            return CmdAction(args, env=env, shell=False)

        return dict(
            name=f"nb:{nb.name}".replace(" ", "_").replace(".ipynb", ""),
            file_dep=[*P.EXAMPLE_IPYNB, *test_deps],
            actions=[_test()],
            targets=[P.DIST_NBHTML / nb.name.replace(".ipynb", ".html")],
        )

    for nb in P.EXAMPLE_IPYNB:
        yield _nb_test(nb)

    yield dict(
        name="pytest",
        file_dep=[*test_deps],
        actions=[
            lambda: shutil.rmtree(P.HTML_COV_INDEX.parent)
            if P.HTML_COV_INDEX.parent.exists()
            else None,
            [
                *P.APR_DEV,
                "pytest",
                "-vv",
                "--ff",
                "--cov",
                "ipyradiant",
                "--cov-report",
                "html:build/htmlcov",
                "--cov-report",
                "term-missing:skip-covered",
                "--no-cov-on-fail",
                *P.PYTEST_SKIPS,
                P.EXAMPLE_TESTS,
            ],
            lambda: U.strip_timestamps(P.HTML_COV_INDEX),
        ],
        targets=[P.HTML_COV_INDEX],
    )


def task_lint():
    """format all source files"""

    yield _ok(
        dict(
            name="black",
            file_dep=[*P.ALL_PY, P.OK_ENV["qa"]],
            actions=[
                [*P.APR_QA, "isort", "-rc", *P.ALL_PY],
                [*P.APR_QA, "black", "--quiet", *P.ALL_PY],
            ],
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
            name="pyflakes",
            file_dep=[*P.ALL_PY, P.OK_BLACK],
            actions=[[*P.APR_QA, "pyflakes", *P.ALL_PY]],
        ),
        P.OK_PYFLAKES,
    )
    yield _ok(
        dict(
            name="prettier",
            file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER, P.OK_ENV["qa"]],
            actions=[[*P.APR_QA, "jlpm", "lint:prettier"]],
        ),
        P.OK_PRETTIER,
    )
    yield _ok(
        dict(
            name="nblint",
            file_dep=[P.YARN_INTEGRITY, *P.EXAMPLE_IPYNB, P.OK_ENV["qa"]],
            actions=[[*P.APR_QA, *P.PYM, "_scripts.nblint", *P.EXAMPLE_IPYNB]],
            targets=[P.NBLINT_HASHES],
        ),
        P.OK_NBLINT,
    )
    yield _ok(
        dict(
            name="all",
            actions=[_echo_ok("all ok")],
            file_dep=[
                P.OK_BLACK,
                P.OK_FLAKE8,
                P.OK_PRETTIER,
                P.OK_PYFLAKES,
                P.OK_NBLINT,
            ],
        ),
        P.OK_LINT,
    )


def task_lab_build():
    """do a "production" build of lab"""
    exts = [
        line.strip()
        for line in P.EXTENSIONS.read_text().strip().splitlines()
        if line and not line.startswith("#")
    ]

    def _clean():
        _call([*P.APR_DEV, "jlpm", "cache", "clean"])
        _call([*P.APR_DEV, *P.LAB, "clean", "--all"])

        return True

    def _build():
        return _call([*P.APR_DEV, "lab:build"]) == 0

    file_dep = [P.EXTENSIONS, P.OK_ENV["dev"]]

    yield dict(
        name="extensions",
        file_dep=file_dep,
        actions=[
            _clean,
            [
                *P.APR_DEV,
                *P.LAB_EXT,
                "disable",
                "@jupyterlab/extension-manager-extension",
            ],
            [*P.APR_DEV, *P.LAB_EXT, "install", "--debug", "--no-build", *exts],
            _build,
            [*P.APR_DEV, *P.LAB_EXT, "list"],
        ],
        targets=[P.LAB_INDEX],
    )


def task_lab():
    """run JupyterLab "normally" (not watching sources)"""

    def lab():
        proc = subprocess.Popen(
            list(map(str, [*P.APR_DEV, "lab"])), stdin=subprocess.PIPE
        )

        try:
            proc.wait()
        except KeyboardInterrupt:
            print("attempting to stop lab, you may want to check your process monitor")
            proc.terminate()
            proc.communicate(b"y\n")

        proc.wait()
        return True

    return dict(
        uptodate=[lambda: False],
        file_dep=[P.LAB_INDEX, P.OK_PIP_INSTALL, P.OK_PREFLIGHT_LAB],
        actions=[PythonInteractiveAction(lab)],
    )


def task_all():
    """do everything except start lab"""
    return dict(
        file_dep=[P.OK_RELEASE, P.OK_PREFLIGHT_LAB],
        actions=([_echo_ok("ALL GOOD")]),
    )


def _echo_ok(msg):
    def _echo():
        print(msg, flush=True)
        return True

    return _echo


def _ok(task, ok):
    task.setdefault("targets", []).append(ok)
    task["actions"] = [
        lambda: [ok.exists() and ok.unlink(), True][-1],
        *task["actions"],
        lambda: [ok.parent.mkdir(exist_ok=True), ok.write_text("ok"), True][-1],
    ]
    return task


def _call(args, **kwargs):
    if "cwd" in kwargs:
        kwargs["cwd"] = str(kwargs["cwd"])
    if "env" in kwargs:
        kwargs["env"] = {k: str(v) for k, v in kwargs["env"].items()}
    args = list(map(str, args))
    print("\n>>>", " ".join(args), "\n", flush=True)
    return subprocess.call(args, **kwargs)


def _channel_args(env="ipyradiant"):
    return sum([["-c", c] for c in PROJ["env_specs"][env]["channels"]], [])
