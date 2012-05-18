#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    visa_exceptions.py - Exceptions for the whole VISA package
#
#    Copyright © 2005, 2006, 2007, 2008
#                Torsten Bronger <bronger@physik.rwth-aachen.de>,
#                Gregor Thalhammer <gth@users.sourceforge.net>.
#  
#    This file is part of PyVISA.
#  
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the MIT licence:
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

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
