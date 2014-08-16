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


def get_library_paths(library_class, user_lib=None):
    """Return a tuple of possible library paths.

    :rtype: tuple
    """
    from .. import logger
    from ._ct import find_library

    tmp = [find_library(library_path)
           for library_path in ('visa', 'visa32', 'visa32.dll')]

    tmp = [library_class(library_path)
           for library_path in tmp
           if library_path is not None]

    logger.debug('Automatically found library files: %s' % tmp)

    if user_lib:
        user_lib = library_class(user_lib, 'user')
        try:
            tmp.remove(user_lib)
        except ValueError:
            pass
        tmp.insert(0, user_lib)

    return tuple(tmp)
