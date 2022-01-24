# Copyright (c) 2022 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import re

RE_TIMESTAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} -\d*"


def strip_timestamps(*paths):
    for path in paths:
        if not path.exists():
            print("Path does not exist.", path)
            continue

        text = path.read_text(encoding="utf-8")
        if not re.findall(RE_TIMESTAMP, text):
            print("Path contains no timestamps.", path)
            continue

        path.write_text(
            re.sub(
                RE_TIMESTAMP,
                "TIMESTAMP",
                text,
            )
        )
