# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

from typing import Union

import ipycytoscape as cyto


def add_cyto_class(element: Union[cyto.Node, cyto.Edge], class_addition: str) -> str:
    """Update the classes string for a cytoscape element with an addition
    TODO support multiple class additions

    :param element: the cytoscape Node/Edge to update classes for
    :param class_addition: the class string to add
    :return: the class string
    """

    try:
        classes = set(element.classes.split())
    except AttributeError:
        classes = set()
    classes.add(class_addition)
    return " ".join(classes)


def remove_cyto_class(element: Union[cyto.Node, cyto.Edge], class_removal: str) -> str:
    """Update the classes string for a cytoscape element with a removal
    TODO support multiple class subtractions

    :param element: the cytoscape Node/Edge to update classes for
    :param class_removal: the class string to remove
    :return: the class string
    """

    try:
        classes = set(element.classes.split())
        classes.discard(class_removal)
        return " ".join(classes)
    except AttributeError:
        return ""
