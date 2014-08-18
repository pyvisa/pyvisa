# -*- coding: utf-8 -*-
"""
    pyvisa.ctwrapper
    ~~~~~~~~~~~~~~~~

    ctypes wrapper for NI-VISA library.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .highlevel import NIVisaLibrary

WRAPPER_CLASS = NIVisaLibrary

