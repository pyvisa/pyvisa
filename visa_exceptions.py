#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    visa_exceptions.py - Exceptions for the whole VISA package
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#                     Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of pyvisa.
#
#    pyvisa is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    pyvisa is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with pyvisa; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
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

class TypeError(Error):
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
	Error.__init__(self, os + " is not yet supported by pyvisa")
