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

"""Main module of the implementation of the original VISA routines.

See VPP-4.3.2.

"""

__version__ = "$Revision$"
# $Source$


VI_SPEC_VERSION = 0x00300000

from vpp43_types import *
from visa_exceptions import *
import os
from ctypes import byref, windll, cdll, create_string_buffer


# Consistency remark: Here *all* low-level wrappers must be listed

__all__ = ("visa_library", "visa_status",
	   "open_default_resource_manager", "get_default_resource_manager",
	   "find_resources", "find_next", "open", "close", "get_attribute",
	   "set_attribute")


# load VISA library

class Singleton(object):
    """Base class for singleton classes.

    Taken from <http://www.python.org/2.2.3/descrintro.html>.

    """
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    def init(self, *args, **kwds):
        pass

class VisaLibrary(Singleton):
    """Singleton class for VISA ctypes library handle.

    This class has only one instance called "visa_library".  The purpose of its
    instance is to provide access to the ctypes object that contains the VISA
    library.

    Public methods:
    load_library -- (re-)loads the VISA library
    __call__     -- returns the ctypes object holding the VISA library
    """
    def init(self):
	self.__lib = None
    def load_library(self, path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"):
	"""(Re-)loads the VISA library.

	The optional parameter "path" holds the full path to the VISA library.
	At the moment, it has significance only for Linux.  It is called
	implicitly by __call__ if not called successfully before.

	It may raise an OSNotSupported exception, or an OSError if the library
	file was not found.

	"""
	if os.name == 'nt':
	    self.__lib = _ctypes.windll.visa32
	elif os.name == 'posix':
	    self.__lib = _ctypes.cdll.LoadLibrary(path)
	else:
	    self.__lib = None
	    raise OSNotSupported, os.name
    def __call__(self):
	"""Returns the ctypes object to the VISA library."""
	if self.__lib is None:
	    self.load_library()
	return self.__lib

visa_library = VisaLibrary()

visa_status = 0

def check_status(status):
    """Check return values for errors."""
    global visa_status
    visa_status = status
    if status < 0:
        raise VisaIOError, status
    else:
        return status

# Consistency remark: here all VPP-4.3.2 routines must be listed (unless, of
# course, they don't return a status value).

for visa_function in ["viOpenDefaultRM", "viFindRsrc", "ViFindNext", "viOpen",
		      "viClose", "viGetAttribute", "viSetAttribute"]:
    visa_library().__getattr(visa_function)__.restype = check_status


# The VPP-4.3.2 routines

def open_default_resource_manager():
    resource_manager = ViSession()
    visa_library().viOpenDefaultRM(byref(resource_manager))
    return resource_manager.value

get_default_resource_manager = open_default_resource_manager
"""A deprecated alias.  See VPP-4.3, rule 4.3.5 and observation 4.3.2."""

def find_resources(session, regular_expression):
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindRsrc(ViSession(session), ViString(regular_expression),
			      byref(find_list), byref(return_counter),
			      byref(instrument_description))
    return (find_list.value, return_counter.value, instrument_description.value)

def find_next(find_list):
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindNext(ViFindList(find_list),
			      byref(instrument_description))
    return instrument_description.value

def open(session, resource_name, access_mode, timeout):
    vi = ViSession()
    visa_library().viOpen(ViSession(session), ViRsrc(resource_name),
			  ViAccessMode(access_mode), ViUInt32(timeout),
			  byref(vi))
    return vi.value

def close(vi):
    visa_library().viClose(ViSession(vi))

def get_attribute(vi, attribute):
    attribute_state = ViAttrState()
    visa_library().viGetAttribute(ViSession(vi), ViAttr(attribute),
				  byref(attribute_state))
    return attribute_state.value

def set_attribute(vi, attribute, attribute_state):
    visa_library().viSetAttribute(ViSession(vi), ViAttr(attribute),
				  ViAttrState(attribute_state))
