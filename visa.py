# -*- coding: utf-8 -*-
"""
    pyvisa.visa
    ~~~~~~~~~~~

    Module to provide an import shortcut for the most common VISA operations.

    This is a legacy module for backwards compatibility with PyVISA < 1.5

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from pyvisa import logger, __version__
from pyvisa.highlevel import VisaLibrary, ResourceManager, get_instruments_list, instrument
from pyvisa.errors import (Error, VisaIOError, VisaIOWarning, VisaTypeError,
                           UnknownHandler, OSNotSupported, InvalidBinaryFormat)
