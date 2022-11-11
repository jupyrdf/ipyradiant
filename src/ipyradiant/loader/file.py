""" file loader widget
"""
# Copyright (c) 2022 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from pathlib import Path

import ipywidgets as W
import traitlets as T
from rdflib.util import SUFFIX_FORMAT_MAP

from .base import BaseLoader


class FileLoader(W.HBox, BaseLoader):
    """Loader that selects from a list of files in a path"""

    label = T.Instance(W.Label)
    file_entry = T.Instance(W.Text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.label, self.file_entry])
        T.link((self, "description"), (self.label, "value"))
        self.file_entry.observe(self._file_path_changed, "value")
        self._file_path_changed()

    @T.default("description")
    def make_default_description(self):
        return "Specify file"

    @T.default("label")
    def make_default_label(self):
        return W.Label()

    @T.default("file_entry")
    def make_default_file_entry(self):
        return W.Text()

    def _file_path_changed(self, change=None):
        value = self.file_entry.value
        path = Path(value)
        if not value or not path.is_file():
            self.file_upload_value = {}
            return

        text = path.read_text(encoding="utf-8")
        self.file_upload_value = {
            path.name: dict(metadata=dict(size=len(text)), content=text)
        }
