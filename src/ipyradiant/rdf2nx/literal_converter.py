# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import logging
from datetime import date
from typing import Any, Callable, Dict

from rdflib import Literal, URIRef
from rdflib.namespace import XSD

logger = logging.getLogger(__name__)


# TODO #63
XSD2PY: Dict[URIRef, Callable] = {
    XSD.boolean: bool,
    # XSD.byte: None,
    XSD.date: lambda x: str(date.fromisoformat(x)),
    # XSD.dateTime: None,
    XSD.decimal: float,
    XSD.double: float,
    XSD.float: float,
    XSD.int: int,
    XSD.integer: int,
    XSD.long: int,
    # XSD.negativeInteger: None,
    # XSD.nonNegativeInteger: None,
    # XSD.nonPositiveInteger: None,
    # XSD.positiveInteger: None,
    # XSD.short: None,
    XSD.string: str,
    # XSD.time: None,
    # XSD.unsignedByte: None,
    # XSD.unsignedInt: None,
    # XSD.unsignedLong: None,
    # XSD.unsignedShort: None,
}


def cast_literal(value: Literal, strict: bool = False) -> Any:
    """Converts a single Literal to a python type.

    :param value: the Literal to convert
    :param strict:
    :return: the Literal cast to a python type
    """
    value_datatype = value.datatype or XSD.string
    if value_datatype not in XSD2PY and strict:
        raise NotImplementedError(f"Data type '{value_datatype}' is not mapped.")
    elif value_datatype not in XSD2PY:
        logger.warning(
            f"Data type '{value_datatype}' is not mapped. Using str to cast value."
        )
        return str(value)
    else:
        return XSD2PY[value_datatype](value)
