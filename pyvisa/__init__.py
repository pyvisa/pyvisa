# -*- coding: utf-8 -*-
"""Python wrapper of IVI Virtual Instruments Software Architecture library (VISA).

This file is part of PyVISA.

:copyright: 2014-2020 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
import logging

# Defined here since it is imported in other pyvisa modules
logger = logging.getLogger("pyvisa")
logger.addHandler(logging.NullHandler())

import pkg_resources

from .errors import (
    Error,
    InvalidBinaryFormat,
    InvalidSession,
    LibraryError,
    OSNotSupported,
    UnknownHandler,
    VisaIOError,
    VisaIOWarning,
    VisaTypeError,
)
from .highlevel import ResourceManager
from .resources import Resource  # noqa : F401 This is needed to register all resources.


def log_to_screen(level=logging.DEBUG) -> None:
    log_to_stream(None, level)  # sys.stderr by default


def log_to_stream(stream_output, level=logging.DEBUG) -> None:
    logger.setLevel(level)
    ch = logging.StreamHandler(stream_output)
    ch.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    ch.setFormatter(formatter)

    logger.addHandler(ch)


__version__ = "unknown"
try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("pyvisa").version
except Exception:  # pragma: no cover
    pass
    # we seem to have a local copy without any repository control or installed
    # without setuptools. So the reported version will be __unknown__


__all__ = [
    "ResourceManager",
    "logger",
    "Error",
    "VisaIOError",
    "VisaIOWarning",
    "VisaTypeError",
    "UnknownHandler",
    "OSNotSupported",
    "InvalidBinaryFormat",
    "InvalidSession",
    "LibraryError",
    "log_to_screen",
    "log_to_stream",
]
