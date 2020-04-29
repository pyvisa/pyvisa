# -*- coding: utf-8 -*-
"""Module to provide an import shortcut for the most common VISA operations.

This file is part of PyVISA.

:copyright: 2014-2019 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see COPYING for more details.

"""

import warnings

warnings.warn(
    (
        "The visa module provided by PyVISA is being deprecated. "
        "You can replace `import visa` by `import pyvisa as visa` "
        "to achieve the same effect.\n\n"
        "The reason for the deprecation is the possible conflict with "
        "the visa package provided by the "
        "https://github.com/visa-sdk/visa-python which can result in "
        "hard to debug situations."
    ),
    FutureWarning,
)

from pyvisa import logger, __version__, log_to_screen, constants
from pyvisa.highlevel import ResourceManager
from pyvisa.errors import (
    Error,
    VisaIOError,
    VisaIOWarning,
    VisaTypeError,
    UnknownHandler,
    OSNotSupported,
    InvalidBinaryFormat,
    InvalidSession,
    LibraryError,
)

# This is needed to registry all resources.
from pyvisa.resources import Resource
from pyvisa.cmd_line_tools import visa_main

__all__ = [
    "ResourceManager",
    "constants",
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
]

if __name__ == "__main__":
    visa_main()
