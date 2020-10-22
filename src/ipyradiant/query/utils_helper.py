import logging

import rdflib


def set_logger_level(level):
    logger = logging.getLogger("ipyradiant")
    logger.setLevel(level)


def service_patch_rdflib(query_str):
    # check for rdflib version, if <=5.0.0 throw warning
    version = rdflib.__version__
    v_split = tuple(map(int, version.split(".")))
    check = v_split <= (5, 0, 0)

    if check:
        if "SERVICE" in query_str:
            query_str = query_str.replace("SERVICE", "service")
            logger = logging.getLogger(__name__)
            logger.warning(
                "SERVICE found in query. RDFlib currently only supports `service`, to be fixed in the next release>5.0.0"
            )
    return query_str
