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

from visa_exceptions import *
from vpp43_constants import *
from vpp43_types import *
import os
from ctypes import byref, windll, cdll, create_string_buffer



__all__ = ["visa_library", "get_status",

	   # Consistency remark: Here *all* low-level wrappers must be listed
	   "open_default_resource_manager", "get_default_resource_manager",
	   "find_resources", "find_next", "open", "close", "get_attribute",
	   "set_attribute", "status_description", "terminate", "lock",
	   "unlock", "enable_event", "disable_event", "discard_events",
	   "wait_on_event", "install_handler", "uninstall_handler",
	   "mem_allocation", "mem_free", "gpib_control_ren",
	   "vxi_command_query", "parse_resource", "write_from_file",
	   "read_from_file", "parse_resource_extended", "usb_control_out",
	   "read", "read_asynchronously", "write", "write_asynchronously",
	   "assert_trigger", "read_stb", "clear", "set_buffer", "flush",
	   "buffer_write", "buffer_read", "printf", "vprintf", "sprintf",
	   "vsprintf", "scanf", "vscanf", "sscanf", "vsscanf", "queryf",
	   "vqueryf", "gpib_control_atn", "gpib_send_ifc", "gpib_command",
	   "gpib_pass_control", "usb_control_in", "in_8", "out_8", "in_16",
	   "out_16", "in_32", "out_32", "move_in_8", "move_out_8",
	   "move_in_16", "move_out_16", "move_in_32", "move_out_32", "move",
	   "move_asynchronously", "map_address", "unmap_address", "peek_8",
	   "poke_8", "peek_16", "poke_16", "peek_32", "poke_32",
	   "assert_utility_signal", "assert_interrupt_signal", "map_trigger",
	   "unmap_trigger"]

# Add all symbols from visa_exceptions and vpp43_constants to the list of
# exported symbols
import visa_exceptions, vpp43_constants
__all__.extend([name for name in vpp43_constants.__dict__.keys() +
		visa_exceptions.__dict__.keys() if name[0] != "_"])


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
	    raise visa_exceptions.OSNotSupported, os.name
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
        raise visa_exceptions.VisaIOError, status
    else:
        return status

def get_status():
    return visa_status


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
			      instrument_description)
    return (find_list.value, return_counter.value,
	    instrument_description.value)

def find_next(find_list):
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindNext(ViFindList(find_list), instrument_description)
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

def status_description(vi, status):
    description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viStatusDesc(ViSession(vi), ViStatus(status), description)
    return description.value

def terminate(vi, degree, job_id):
    visa_library().viTerminate(ViSession(vi), ViUInt16(degree),
			       ViJobId(job_id))

def lock(vi, lock_type, timeout, requested_key):
    if lock_type == VI_EXCLUSIVE_LOCK:
	requested_key = VI_NULL
	access_key = None
    else:
	access_key = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viLock(ViSession(vi), ViAccessMode(lock_type),
			  ViUInt32(timeout), ViKeyId(requested_key),
			  access_key)
    return access_key.value

def unlock(vi):
    visa_library().viUnlock(ViSession(vi))

def enable_event(vi, event_type, mechanism, context):
    context = VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    visa_library().viEnableEvent(ViSession(vi), ViEventType(event_type),
				 ViUInt16(mechanism), ViEventFilter(context))

def disable_event(vi, event_type, mechanism):
    visa_library().viDisableEvent(ViSession(vi), ViEventType(event_type),
				  ViUInt16(mechanism))

def discard_events(vi, event_type, mechanism):
    visa_library().viDiscardEvents(ViSession(vi), ViEventType(event_type),
				   ViUInt16(mechanism))

def wait_on_event(vi, in_event_type, timeout):
    out_event_type = ViEventType()
    out_context = ViEvent()
    visa_library().viWaitOnEvent(ViSession(vi), ViEventType(in_event_type),
				 ViUInt32(timeout), byref(out_event_type),
				 byref(out_context))
    return (out_event_type, out_context)

def install_handler(vi, event_type, handle, user_handle):
    visa_library().viInstallHandler(ViSession(vi), ViEventType(event_type),
				    ViHndlr(handler), ViAddr(user_handle))

def uninstall_handler(vi, event_type, handle, user_handle):
    visa_library().viUninstallHandler(ViSession(vi), ViEventType(event_type),
				      ViHndlr(handler), ViAddr(user_handle))

def mem_allocation(vi, size):
    offset = ViBusAddress()
    visa_library().viMemAlloc(ViSession(vi), ViBusSize(size), byref(offset))
    return offset.value

def mem_free(vi, offset):
    visa_library().viMemFree(ViSession(vi), ViBusAddress(offset))

def gpib_control_ren(vi, mode):
    visa_library().viGpibControlREN(ViSession(vi), ViUInt16(mode))

def vxi_command_query(vi, mode, command):
    response = ViUInt32()
    visa_library().viVxiCommandQuery(ViSession(vi), ViUInt16(mode),
				     ViUInt32(command), byref(response))
    return response.value

def parse_resource():
    pass

def write_from_file():
    pass

def read_from_file():
    pass

def parse_resource_extended():
    pass

def usb_control_out():
    pass

def read():
    pass

def read_asynchronously():
    pass

def write():
    pass

def write_asynchronously():
    pass

def assert_trigger():
    pass

def read_stb():
    pass

def clear():
    pass

def set_buffer():
    pass

def flush():
    pass

def buffer_write():
    pass

def buffer_read():
    pass

def printf():
    pass

def vprintf():
    pass

def sprintf():
    pass

def vsprintf():
    pass

def scanf():
    pass

def vscanf():
    pass

def sscanf():
    pass

def vsscanf():
    pass

def queryf():
    pass

def vqueryf():
    pass

def gpib_control_atn():
    pass

def gpib_send_ifc():
    pass

def gpib_command():
    pass

def gpib_pass_control():
    pass

def usb_control_in():
    pass

def in_8():
    pass

def out_8():
    pass

def in_16():
    pass

def out_16():
    pass

def in_32():
    pass

def out_32():
    pass

def move_in_8():
    pass

def move_out_8():
    pass

def move_in_16():
    pass

def move_out_16():
    pass

def move_in_32():
    pass

def move_out_32():
    pass

def move():
    pass

def move_asynchronously():
    pass

def map_address():
    pass

def unmap_address():
    pass

def peek_8():
    pass

def poke_8():
    pass

def peek_16():
    pass

def poke_16():
    pass

def peek_32():
    pass

def poke_32():
    pass

def assert_utility_signal():
    pass

def assert_interrupt_signal():
    pass

def map_trigger():
    pass

def unmap_trigger():
    pass
