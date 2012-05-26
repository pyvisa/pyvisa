# -*- coding: utf-8 -*-
"""
    visa_exceptions
    ~~~~~~~~~~~~~~~

    Defines exceptions hierarchy.

    This file is part of PyVISA.

    :copyright: (c) 2012 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""


__version__ = "$Revision$"
# $Source$

from visa_messages import completion_and_error_messages \
    as _completion_and_error_messages


class Error(Exception):
    """Abstract basic exception class for this module."""
    def __init__(self, description):
        Exception.__init__(self, description)

class VisaIOError(Error):
    """Exception class for VISA I/O errors.

    Please note that all values for "error_code" are negative according to the
    specification (VPP-4.3.2, observation 3.3.2) and the NI implementation.

    """
    def __init__(self, error_code):
        abbreviation, description = _completion_and_error_messages[error_code]
        Error.__init__(self, abbreviation + ": " + description)
        self.error_code = error_code

class VisaIOWarning(Warning):
    """Exception class for VISA I/O warnings.

    According to the specification VPP-4.3.2 and the NI implementation.

    """
    def __init__(self, description):
        Warning.__init__(self, description)

class VisaTypeError(Error):
    """Exception class for wrong types in VISA function argument lists.

    Raised if unsupported types are given to scanf, sscanf, printf, sprintf,
    and queryf.  Because the current implementation doesn't analyse the format
    strings, it can only deal with integers, floats, and strings.

    Additionally, this exception is raised by install_handler if un unsupported
    type is used for the user handle.

    """
    def __init__(self, description):
        Error.__init__(self, description)

class UnknownHandler(Error):
    """Exception class for invalid handler data given to uninstall_handler().

    uninstall_handler() checks whether the handler and user_data parameters
    point to a known handler previously installed with install_handler().  If
    it can't find it, this exception is raised.

    """
    def __init__(self):
        Error.__init__(self, "Handler with this handler function and user data"
                       " not found")

class OSNotSupported(Error):
    def __init__(self, os):
        Error.__init__(self, os + " is not yet supported by PyVISA")

class InvalidBinaryFormat(Error):
    def __init__(self, description = ""):
        if description:
            description = ": " + description
        Error.__init__(self, "unrecognized binary data format" + description)
