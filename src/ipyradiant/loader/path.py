""" path loader widget
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from pathlib import Path

import ipywidgets as W
import traitlets as T

from .base import BaseLoader
from .util import SUFFIX_FORMAT_MAP


class PathLoader(W.HBox, BaseLoader):
    """Loader that selects from a list of files in a path"""

    label = T.Instance(W.Label)
    path = T.Union([T.Unicode(), T.Instance(Path)], allow_none=True)
    file_picker = T.Instance(W.Dropdown)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.label, self.file_picker])
        T.link((self, "description"), (self.label, "value"))
        self.file_picker.observe(self._file_picked, "value")
        self._path_changed()
        self._file_picked

    @T.default("description")
    def make_default_description(self):
        return "Select file"

    @T.default("label")
    def make_default_label(self):
        return W.Label()

    @T.default("file_picker")
    def make_default_file_picker(self):
        """TODO: revisit for multiple files, e.g. checkboxes"""
        return W.Dropdown()

    def _file_picked(self, change=None):
        value = self.file_picker.value
        if not value:
            self.file_upload_value = {}
            return

        text = value.read_text(encoding="utf-8")
        self.file_upload_value = {
            value.name: dict(metadata=dict(size=len(text)), content=text)
        }

    @T.observe("path")
    def _path_changed(self, change=None):
        options = {"Select a file...": ""}

        if not self.path:
            self.file_picker.options = options
            return

        path = Path(self.path)

        if path.is_dir():
            globs = [sorted(path.glob(f"*.{ext}")) for ext in SUFFIX_FORMAT_MAP]
            options.update(**{p.name: p for p in sorted(sum([*globs], []))})

        self.file_picker.options = options
