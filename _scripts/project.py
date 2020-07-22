""" important project paths
"""
import json
import os
import re
import shutil
from pathlib import Path

SCRIPTS = Path(__file__).parent.resolve()
ROOT = SCRIPTS.parent

# top-level stuff
SETUP_PY = ROOT / "setup.py"
SETUP_CFG = ROOT / "setup.cfg"
NODE_MODULES = ROOT / "node_modules"
PACKAGE = ROOT / "package.json"
YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
YARN_LOCK = ROOT / "yarn.lock"
EXTENSIONS = ROOT / "labextensions.txt"
CI = ROOT / ".github"
DODO = ROOT / "dodo.py"
POSTBUILD = ROOT / "postBuild"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
RECIPE = ROOT / "conda.recipe"
ENVS = ROOT / "envs"
PROJ_LOCK = ROOT / "anaconda-project-lock.yml"

# tools
PY = ["python"]
PYM = [*PY, "-m"]
PIP = [*PYM, "pip"]
NODE = [shutil.which("node") or shutil.which("node.exe") or shutil.which("node.cmd")]

JLPM = ["jlpm"]
LAB_EXT = ["jupyter", "labextension"]
CONDA_BUILD = ["conda-build"]
LAB = ["jupyter", "lab"]
AP = ["anaconda-project"]
AP_PREP = [*AP, "prepare", "--env-spec"]
APR = [*AP, "run", "--env-spec"]
APR_DEV = [*APR, "dev"]
APR_BUILD = [*APR, "build"]
APR_QA = [*APR, "qa"]
PRETTIER = [NODE, str(NODE_MODULES / ".bin" / "prettier")]

# env stuff
OK_ENV = {env: BUILD / f"prep_{env}.ok" for env in ["build", "qa", "dev"]}
FORCE_SERIAL_ENV_PREP = bool(
    json.loads(os.environ.get("FORCE_SERIAL_ENV_PREP", "false"))
)

# python stuff
PY_SRC = ROOT / "src" / "ipyradiant"
VERSION_PY = PY_SRC / "_version.py"

# lab stuff
LAB_APP_DIR = ENVS / "dev/share/jupyter/lab"
LAB_STAGING = LAB_APP_DIR / "staging"
LAB_LOCK = LAB_STAGING / "yarn.lock"
LAB_STATIC = LAB_APP_DIR / "static"
LAB_INDEX = LAB_STATIC / "index.html"

# tests
EXAMPLES = ROOT / "examples"
EXAMPLE_IPYNB = [
    p for p in EXAMPLES.rglob("*.ipynb") if ".ipynb_checkpoints" not in str(p)
]
EXAMPLE_PY = [*EXAMPLES.rglob("*.py")]
DIST_NBHTML = DIST / "nbsmoke"

# mostly linting
ALL_PY_SRC = [*PY_SRC.rglob("*.py")]
ALL_PY = [DODO, POSTBUILD, *ALL_PY_SRC, *EXAMPLE_PY, *SCRIPTS.rglob("*.py")]
ALL_YML = [*ROOT.glob("*.yml"), *CI.rglob("*.yml")]
ALL_JSON = [*ROOT.glob("*.json")]
ALL_MD = [*ROOT.glob("*.md")]
ALL_PRETTIER = [*ALL_YML, *ALL_JSON, *ALL_MD]

# conda
META_YAML = RECIPE / "meta.yaml"
DIST_CONDA = DIST / "conda-bld"

# built files
NBLINT_HASHES = BUILD / "nblint.hashes"
OK_BLACK = BUILD / "black.ok"
OK_FLAKE8 = BUILD / "flake8.ok"
OK_ISORT = BUILD / "isort.ok"
OK_LINT = BUILD / "lint.ok"
OK_PYFLAKES = BUILD / "pyflakes.ok"
OK_NBLINT = BUILD / "nblint.ok"
OK_PIP_INSTALL_E = BUILD / "pip_install_e.ok"
OK_PRETTIER = BUILD / "prettier.ok"

# derived info
PY_VERSION = re.findall(r'''__version__ = "(.*)"''', VERSION_PY.read_text())[0]
CONDA_BUILD_NO = re.findall(r"""number: (\d+)""", META_YAML.read_text())[0]

# built artifacts
SDIST = DIST / f"ipyradiant-{PY_VERSION}.tar.gz"
WHEEL = DIST / f"ipyradiant-{PY_VERSION}-py3-none-any.whl"
EXAMPLE_HTML = [DIST_NBHTML / p.name.replace(".ipynb", ".html") for p in EXAMPLE_IPYNB]
CONDA_PACKAGE = (
    DIST_CONDA / "noarch" / f"ipyradiant-{PY_VERSION}-py_{CONDA_BUILD_NO}.tar.bz2"
)
