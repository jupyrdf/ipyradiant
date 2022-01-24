""" Utility Helper Functions
"""
# Copyright (c) 2022 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import re


def collapse_namespace(namespaces, cell):
    """Collapse namespaces and use hyperlink structure."""

    uf_link = """<a href=\"{}" target=\"_blank\">{}</a>"""

    if isinstance(namespaces, dict):
        namespaces = list(namespaces.items())
        # sort based on namespace length (ensure longer ns are processed first)
        namespaces.sort(key=lambda entry: len(entry[1]), reverse=True)

    or_statement = "|".join([uri for _, uri in namespaces])
    pattern = f"({or_statement}).*"
    quick_check = re.match(pattern, str(cell))
    if quick_check:
        for term, uri in namespaces:
            if cell.startswith(uri):
                shorthand = str(cell).replace(uri, term + ":")
                if "/" in shorthand:
                    # break because we don't want to collapse to a partial match
                    # TODO remove if want an irregular shorthand representation
                    break
                return uf_link.format(cell, shorthand)

    return uf_link.format(cell, cell)
