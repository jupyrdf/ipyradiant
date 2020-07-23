""" ensure the development environment is sane

    this should run in the outermost environment, e.g. `base`
"""
import os
import re
import sys
from pathlib import Path

from ruamel_yaml import safe_dump

from . import project as P

BAD_PATH_RE = r"[^a-zA-Z\d_\-\.\\/]"
ROOT_RECOMMEND = (
    "c:\\git\\ipyradiant" if P.WIN else os.path.expanduser("~/git/ipyradiant")
)
MC3_RECOMMEND = "c:\\mc3" if P.WIN else os.path.expanduser("~/mc3")
ARBITRARY_PATH_LENGTH = 32 if P.WIN else 64
NOT_DEFINED = "!NOT DEFINED!"


def check_path(path, name=None, message=None, check_len=False):
    print(f"Checking sanity of {name or path}...", flush=True)
    errors = {}

    if path == NOT_DEFINED:
        errors["not defined"] = path
    else:
        drive, rest = os.path.splitdrive(str(Path(path).resolve()))

        path_len = len(str(path))

        if not path_len:
            errors["not_defined"] = True
        elif check_len and path_len > ARBITRARY_PATH_LENGTH:
            errors["length"] = path_len

        bad_path_matches = re.findall(BAD_PATH_RE, rest)

        if bad_path_matches:
            errors["bad_characters"] = bad_path_matches

    if errors:
        print(f"... {len(errors)} problems with {name or path}")
        return [{"path": str(path), "message": str(message), "errors": errors}]

    return []


def check_drives(path_a, path_b, message):
    print(f"Checking drives of '{path_a}' and '{path_b}'...")
    a_drive, a_rest = os.path.splitdrive(str(path_a))
    b_drive, b_rest = os.path.splitdrive(str(path_a))

    if a_drive != b_drive:
        print("...drives are no good")
        return [{"paths": [path_a, path_b]}]
    return []


def preflight():
    conda_prefix = os.environ.get("CONDA_PREFIX", NOT_DEFINED)
    errors = [
        *check_path(
            path=P.ROOT,
            name="repo location",
            message=f"please check out to a sane location, e.g {ROOT_RECOMMEND}",
            check_len=True,
        ),
        *check_path(
            path=os.environ.get("CONDA_PREFIX", NOT_DEFINED),
            message=(
                "please install and activate miniconda3 in a sane location"
                f" e.g. {MC3_RECOMMEND}"
            ),
            check_len=True,
        ),
        *check_drives(
            P.ROOT,
            conda_prefix,
            "please ensure miniconda3 and this repo are on the same"
            " physical drive/volume",
        ),
    ]

    if errors:
        print(safe_dump(errors, default_flow_style=False))

    return len(errors)


if __name__ == "__main__":
    sys.exit(preflight())
