# -*- coding: utf-8 -*-
"""
    pyvisa.ctwrapper
    ~~~~~~~~~~~~~~~~

    ctypes wrapper for IVI-VISA library.

    This file is part of PyVISA.

    :copyright: 2014-2019 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .highlevel import IVIVisaLibrary

WRAPPER_CLASS = IVIVisaLibrary

