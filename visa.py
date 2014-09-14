# -*- coding: utf-8 -*-
"""
    pyvisa.visa
    ~~~~~~~~~~~

    Module to provide an import shortcut for the most common VISA operations.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from pyvisa import logger, __version__, log_to_screen
from pyvisa.highlevel import ResourceManager
from pyvisa.errors import (Error, VisaIOError, VisaIOWarning, VisaTypeError,
                           UnknownHandler, OSNotSupported, InvalidBinaryFormat,
                           InvalidSession, LibraryError)
# This is needed to registry all resources.
from pyvisa.resources import Resource
