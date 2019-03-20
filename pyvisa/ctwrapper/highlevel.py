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

import logging
import warnings

from pyvisa import constants, errors, highlevel, logger
from pyvisa.compat import integer_types, OrderedDict

from .cthelper import Library, find_library
from . import functions


logger = logging.LoggerAdapter(logger, {'backend': 'ni'})


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


def unique(seq):
    """Keep unique while preserving order.
    """
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


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

    @staticmethod
    def get_library_paths():
        """Return a tuple of possible library paths.

        :rtype: tuple
        """

        from ..util import LibraryPath, read_user_library_path

        # Try to find NI libraries using known names.
        tmp = [find_library(library_path)
               for library_path in ('visa', 'visa32', 'visa32.dll', 'visa64', 'visa64.dll')]

        logger.debug('Automatically found library files: %s' % tmp)

        # Prepend the path provided by the user in configuration files (if any).
        user_lib = read_user_library_path()
        if user_lib:
            tmp.insert(0, user_lib)

        # Deduplicate and convert string paths to LibraryPath objects
        tmp = [LibraryPath(library_path)
               for library_path in unique(tmp)
               if library_path is not None]

        return tuple(tmp)

    @staticmethod
    def get_debug_info():
        """Return a list of lines with backend info.
        """
        from pyvisa import __version__
        d = OrderedDict()
        d['Version'] = '%s (bundled with PyVISA)' % __version__

        paths = NIVisaLibrary.get_library_paths()

        for ndx, visalib in enumerate(paths, 1):
            nfo = OrderedDict()
            nfo['found by'] = visalib.found_by
            nfo['bitness'] = visalib.bitness
            try:
                lib = NIVisaLibrary(visalib)
                sess, _ = lib.open_default_resource_manager()
                nfo['Vendor'] = str(lib.get_attribute(sess, constants.VI_ATTR_RSRC_MANF_NAME)[0])
                nfo['Impl. Version'] = str(lib.get_attribute(sess, constants.VI_ATTR_RSRC_IMPL_VERSION)[0])
                nfo['Spec. Version'] = str(lib.get_attribute(sess, constants.VI_ATTR_RSRC_SPEC_VERSION)[0])
                lib.close(sess)
            except Exception as e:
                e = str(e)
                if 'No matching architecture' in e:
                    nfo['Could not get more info'] = 'Interpreter and library have different bitness.'
                else:
                    nfo['Could not get more info'] = str(e).split('\n')

            d['#%d: %s' % (ndx, visalib)] = nfo

        if not paths:
            d['Binary library'] = 'Not found'

        return d

    def _init(self):
        try:
            lib = Library(self.library_path)
        except OSError as exc:
            raise errors.LibraryError.from_exception(exc, self.library_path)

        self.lib = lib

        # Set the argtypes, restype and errcheck for each function
        # of the visa library. Additionally store in `_functions` the
        # name of the functions.
        functions.set_signatures(self.lib, errcheck=self._return_handler)

        logger.debug('Library signatures: %d ok, %d failed',
                     len(getattr(self.lib, '_functions', [])),
                     len(getattr(self.lib, '_functions_failed', [])))

        # Set the library functions as attributes of the object.
        for method_name in getattr(self.lib, '_functions', []):
            setattr(self, method_name, getattr(self.lib, method_name))

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

    def list_resources(self, session, query='?*::INSTR'):
        """Returns a tuple of all connected devices matching query.

        note: The query uses the VISA Resource Regular Expression syntax - which is not the same
              as the Python regular expression syntax. (see below)

            The VISA Resource Regular Expression syntax is defined in the VISA Library specification:
            http://www.ivifoundation.org/docs/vpp43.pdf

            Symbol      Meaning
            ----------  ----------

            ?           Matches any one character.

            \           Makes the character that follows it an ordinary character
                        instead of special character. For example, when a question
                        mark follows a backslash (\?), it matches the ? character
                        instead of any one character.

            [list]      Matches any one character from the enclosed list. You can
                        use a hyphen to match a range of characters.

            [^list]     Matches any character not in the enclosed list. You can use
                        a hyphen to match a range of characters.

            *           Matches 0 or more occurrences of the preceding character or
                        expression.

            +           Matches 1 or more occurrences of the preceding character or
                        expression.

            Exp|exp     Matches either the preceding or following expression. The or
                        operator | matches the entire expression that precedes or
                        follows it and not just the character that precedes or follows
                        it. For example, VXI|GPIB means (VXI)|(GPIB), not VX(I|G)PIB.

            (exp)       Grouping characters or expressions.

            Thus the default query, '?*::INSTR', matches any sequences of characters ending
            ending with '::INSTR'.

        :param query: a VISA Resource Regular Expression used to match devices.
        """

        resources = []

        try:
            find_list, return_counter, instrument_description, err = self.find_resources(session, query)
        except errors.VisaIOError as e:
            if e.error_code == constants.StatusCode.error_resource_not_found:
                return tuple()
            raise e

        resources.append(instrument_description)
        for i in range(return_counter - 1):
            resources.append(self.find_next(find_list)[0])

        self.close(find_list)

        return tuple(resource for resource in resources)

