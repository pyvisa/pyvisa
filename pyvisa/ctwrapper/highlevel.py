# -*- coding: utf-8 -*-
"""
    pyvisa.ctwrapper.highlevel
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Highlevel wrapper of the VISA Library.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import warnings

from .. import constants, errors, highlevel, logger
from ..compat import integer_types

from ._ct import Library
from . import functions


def add_visa_methods(aclass):
    for method in functions.visa_functions:
        setattr(aclass, method, getattr(functions, method))
    return aclass


def _args_to_str(args):
    out = []
    for arg in args:
        try:
            # noinspection PyProtectedMember
            out.append(str(arg._obj))
        except AttributeError:
            out.append(arg)
    return tuple(out)


@add_visa_methods
class NIVisaLibrary(highlevel.VisaLibraryBase):
    """High level NI-VISA Library wrapper using ctypes.

    The easiest way to instantiate the library is to let `pyvisa` find the
    right one for you. This looks first in your configuration file (~/.pyvisarc).
    If it fails, it uses `ctypes.util.find_library` to try to locate a library
    in a way similar to what the compiler does:

       >>> visa_library = NIVisaLibrary()

    But you can also specify the path:

        >>> visa_library = NIVisaLibrary('/my/path/visa.so')

    :param library_path: path of the VISA library.
    """

    def __new__(cls, library_path):
        if library_path in cls._registry:
            return cls._registry[library_path]

        try:
            lib = Library(library_path)
        except OSError as exc:
            raise errors.LibraryError.from_exception(exc, library_path)

        obj = super(highlevel.VisaLibraryBase, cls).__new__(cls, library_path)
        obj.lib = lib

        # Set the argtypes, restype and errcheck for each function
        # of the visa library. Additionally store in `_functions` the
        # name of the functions.
        functions.set_signatures(obj.lib, errcheck=obj._return_handler)

        # Set the library functions as attributes of the object.
        for method_name in getattr(obj.lib, '_functions', []):
            setattr(obj, method_name, getattr(obj.lib, method_name))

        return obj

    def _return_handler(self, ret_value, func, arguments):
        """Check return values for errors and warnings.
        """

        logger.debug('%s%s -> %r',
                     func.__name__, _args_to_str(arguments), ret_value,
                     extra=self._logging_extra)

        try:
            ret_value = constants.StatusCode(ret_value)
        except ValueError:
            pass

        self._last_status = ret_value

        # The first argument of almost all registered visa functions is a session.
        # We store the error code per session
        session = None
        if func.__name__ not in ('viFindNext', ):
            try:
                session = arguments[0]
            except KeyError:
                raise Exception('Function %r does not seem to be a valid '
                                'visa function (len args %d)' % (func, len(arguments)))

            # Functions that use the first parameter to get a session value.
            if func.__name__ in ('viOpenDefaultRM', ):
                # noinspection PyProtectedMember
                session = session._obj.value

            if isinstance(session, integer_types):
                self._last_status_in_session[session] = ret_value
            else:
                # Functions that might or might have a session in the first argument.
                if func.__name__ not in ('viClose', 'viGetAttribute', 'viSetAttribute', 'viStatusDesc'):
                    raise Exception('Function %r does not seem to be a valid '
                                    'visa function (type args[0] %r)' % (func, type(session)))

        if ret_value < 0:
            raise errors.VisaIOError(ret_value)

        if ret_value in self.issue_warning_on:
            if session and ret_value not in self._ignore_warning_in_session[session]:
                warnings.warn(errors.VisaIOWarning(ret_value), stacklevel=2)

        return ret_value
