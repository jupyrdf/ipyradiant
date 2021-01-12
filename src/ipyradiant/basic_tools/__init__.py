"""basic tooling widgets
"""

# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.


__all__ = [
    "MultiPanelSelect",
    "CustomURIRef",
    "PredicateMultiselectApp",
    "collapse_predicates",
]
from .custom_uri_ref import CustomURIRef
from .object_literal_collapsing import PredicateMultiselectApp, collapse_predicates
from .selection_widget import MultiPanelSelect
