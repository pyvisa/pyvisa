#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43.py - VISA VPP-4.3.2 functions implementation
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


VI_SPEC_VERSION = 0x00300000

from vpp43_types import *
from vpp43_constants import *
from visa_messages import completion_and_error_messages \
    as _completion_and_error_messages
import os


class Error(EnvironmentError):
    """Exception class for VISA errors.

    Please note that all values for "errno" are negative according to the
    specification (VPP-4.3.2, observation 3.3.2) and the NI implementation.
    """
    def __init__(self, status):
	(abbreviation, description) = \
	    _completion_and_error_messages[self.errno]
	EnvironmentError.__init__(self, status, abbreviation + ": "
				  + description)

def check_status(status):
    """Check return values for errors."""
    if status < 0:
        raise Error(status)
    else:
        return status


# load VISA library

if os.name == 'nt':
    visa = windll.visa32
elif os.name == 'posix':
    visa = cdll.LoadLibrary("/usr/local/vxipnp/linux/bin/libvisa.so.7")
else:
    raise "No implementation for your platform available."

