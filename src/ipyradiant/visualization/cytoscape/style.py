NODE = {
    "selector": "node",
    "style": {
        "color": "black",
        "background-color": "CadetBlue",
    },
}

LABELLED_NODE = {
    "selector": "node",
    "style": {
        "color": "black",
        "background-color": "CadetBlue",
        "label": "data(_label)",
    },
}

EDGE = {
    "selector": "edge",
    "style": {
        "line-color": "grey",
        "line-opacity": "0.5",
    },
}

LABELLED_EDGE = {
    "selector": "edge",
    "style": {
        "font-size": "12",
        "font-style": "italic",
        "line-color": "grey",
        "line-opacity": "0.5",
        "label": "data(_label)",
    },
}


DIRECTED_EDGE = {
    "selector": "edge.directed",
    "style": {"curve-style": "bezier", "target-arrow-shape": "triangle"},
}

MULTIPLE_EDGES = {
    "selector": "edge.multiple_edges",
    "style": {"curve-style": "bezier"},
}

DIRECTED_GRAPH = [
    NODE,
    EDGE,
    DIRECTED_EDGE,
    MULTIPLE_EDGES,
]

LABELLED_DIRECTED_GRAPH = [
    LABELLED_NODE,
    LABELLED_EDGE,
    DIRECTED_EDGE,
    MULTIPLE_EDGES,
]
