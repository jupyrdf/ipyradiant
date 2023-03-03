""" file uploader widget
"""
# Copyright (c) 2022 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import ipywidgets as W
import traitlets as T
from rdflib.util import SUFFIX_FORMAT_MAP

from .base import BaseLoader


class UpLoader(W.HBox, BaseLoader):
    """Loader that wraps a FileUpload"""

    label = T.Instance(W.Label)
    file_upload = T.Instance(W.FileUpload)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = tuple([self.label, self.file_upload])
        T.link((self, "description"), (self.label, "value"))
        T.dlink((self.file_upload, "value"), (self, "file_upload_value"), lambda x:x[0] if len(x) else {})

    @T.default("label")
    def make_default_label(self):
        return W.Label()

    @property
    def formats(self):
        return ",".join(["." + ext for ext in SUFFIX_FORMAT_MAP.keys()])

    @T.default("file_upload")
    def make_default_file_upload(self):
        # TODO support multiple files
        file_upload = W.FileUpload(accept=self.formats, multiple=False)
        return file_upload
