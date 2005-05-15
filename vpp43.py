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
# TODO:
#
# * Test as many routines as possible, audit the rest
#
# * Create prototypes
#
# * Define a restype for peek and poke functions?
#
# * Sort everything by alphabet
#
# * Test for wrong types for functions without a prototype (e.g. printf)


"""Main module of the implementation of the original VISA routines.

See VPP-4.3.2.

"""

__version__ = "$Revision$"
# \$Source${}$\$


VI_SPEC_VERSION = 0x00300000

from visa_exceptions import *
from vpp43_constants import *
from vpp43_types import *
import os
from ctypes import byref, cdll, create_string_buffer, c_void_p
if os.name == 'nt':
    from ctypes import windll

visa_functions = [
    "open_default_resource_manager", "get_default_resource_manager",
    "find_resources", "find_next", "open", "close", "get_attribute",
    "set_attribute", "status_description", "terminate", "lock", "unlock",
    "enable_event", "disable_event", "discard_events", "wait_on_event",
    "install_handler", "uninstall_handler", "memory_allocation", "memory_free",
    "gpib_control_ren", "vxi_command_query", "parse_resource",
    "write_from_file", "read_from_file", "parse_resource_extended",
    "usb_control_out", "read", "read_asynchronously", "write",
    "write_asynchronously", "assert_trigger", "read_stb", "clear",
    "set_buffer", "flush", "buffer_write", "buffer_read", "printf", "vprintf",
    "sprintf", "vsprintf", "scanf", "vscanf", "sscanf", "vsscanf", "queryf",
    "vqueryf", "gpib_control_atn", "gpib_send_ifc", "gpib_command",
    "gpib_pass_control", "usb_control_in", "in_8", "out_8", "in_16", "out_16",
    "in_32", "out_32", "move_in_8", "move_out_8", "move_in_16", "move_out_16",
    "move_in_32", "move_out_32", "move", "move_asynchronously", "map_address",
    "unmap_address", "peek_8", "poke_8", "peek_16", "poke_16", "peek_32",
    "poke_32", "assert_utility_signal", "assert_interrupt_signal",
    "map_trigger", "unmap_trigger"]

__all__ = ["visa_library", "get_status"] + visa_functions


# Add all symbols from #visa_exceptions# and #vpp43_constants# to the list of
# exported symbols
import visa_exceptions, vpp43_constants
__all__.extend([name for name in vpp43_constants.__dict__.keys() +
		visa_exceptions.__dict__.keys() if name[0] != '_'])


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
    def __init__(self):
	self.__lib = self.__cdecl_lib = None
    def load_library(self, path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"):
	"""(Re-)loads the VISA library.

	The optional parameter "path" holds the full path to the VISA library.
	At the moment, it has significance only for Linux.  It is called
	implicitly by __call__ if not called successfully before.

	It may raise an OSNotSupported exception, or an OSError if the library
	file was not found.

	"""
	if os.name == 'nt':
	    self.__lib       = windll.visa32
	    self.__cdecl_lib = cdll.visa32
	elif os.name == 'posix':
	    self.__lib = self.__cdecl_lib = cdll.LoadLibrary(path)
	else:
	    self.__lib = self.__cdecl_lib = None
	    raise visa_exceptions.OSNotSupported, os.name
	self.__set_argument_types()
    def __call__(self, force_cdecl = False):
	"""Returns the ctypes object to the VISA library.

	If "force_cdecl" is True, use the cdecl calling convension even under
	Windows, where the stdcall convension is the default.  For Linux, this
	has no effect.
	
	"""
	if self.__lib is None or self.__cdecl_lib is None:
	    self.load_library()
	if force_cdecl:
	    return self.__cdecl_lib
	return self.__lib
    def __set_argument_types(self):
	# Consistency remark: here all VPP-4.3.2 routines must be listed (unless, of
	# course, they don't return a status value, like "peek" and "poke").
	for visa_function in ["viOpenDefaultRM", "viFindRsrc",
	    "viFindNext", "viParseRsrc", "viParseRsrcEx", "viOpen", "viClose",
	    "viSetAttribute", "viGetAttribute", "viStatusDesc", "viTerminate",
	    "viLock", "viUnlock", "viEnableEvent", "viDisableEvent",
	    "viDiscardEvents", "viWaitOnEvent", "viInstallHandler",
	    "viUninstallHandler", "viRead", "viReadAsync", "viReadToFile",
	    "viWrite", "viWriteAsync", "viWriteFromFile", "viAssertTrigger",
	    "viReadSTB", "viClear", "viSetBuf", "viFlush", "viBufWrite",
	    "viBufRead", "viVPrintf", "viVSPrintf", "viVScanf", "viVSScanf",
	    "viVQueryf", "viIn8", "viOut8", "viIn16", "viOut16", "viIn32",
	    "viOut32", "viMoveIn8", "viMoveOut8", "viMoveIn16", "viMoveOut16",
	    "viMoveIn32", "viMoveOut32", "viMove", "viMoveAsync",
	    "viMapAddress", "viUnmapAddress", "viMemAlloc", "viMemFree",
	    "viGpibControlREN", "viGpibControlATN", "viGpibSendIFC",
	    "viGpibCommand", "viGpibPassControl", "viVxiCommandQuery",
	    "viAssertUtilSignal", "viAssertIntrSignal", "viMapTrigger",
	    "viUnmapTrigger", "viUsbControlOut", "viUsbControlIn"]:
	    self.__lib.__getattr__(visa_function).restype = check_status
	for visa_function in ["viPrintf", "viScanf", "viSPrintf", "viSScanf",
			      "viQueryf"]:
	    self.__cdecl_lib.__getattr__(visa_function).restype = check_status
	for visa_function in ["viPeek8", "viPeek16", "viPeek32", "viPoke8",
			      "viPoke16", "viPoke32"]:
	    self.__lib.__getattr__(visa_function).restype = None
	self.__lib.viAssertIntrSignal.argtypes = [ViSession, ViInt16, ViUInt32]
	self.__lib.viAssertTrigger.argtypes = [ViSession, ViUInt16]
	self.__lib.viAssertUtilSignal.argtypes = [ViSession, ViUInt16]
	self.__lib.viBufRead.argtypes = \
	    [ViSession, ViPBuf, ViUInt32, ViPUInt32]
	self.__lib.viBufWrite.argtypes = \
	    [ViSession, ViBuf, ViUInt32, ViPUInt32]
	self.__lib.viClear.argtypes = [ViSession]
	self.__lib.viClose.argtypes = [ViSession]
	self.__lib.viDisableEvent.argtypes = [ViSession, ViEventType, ViUInt16]
	self.__lib.viDiscardEvents.argtypes = [ViSession, ViEventType,
					       ViUInt16]
	self.__lib.viEnableEvent.argtypes = [ViSession, ViEventType, ViUInt16,
					     ViEventFilter]
	self.__lib.viFindNext.argtypes = [ViSession, ViAChar]
	self.__lib.viFindRsrc.argtypes = [ViSession, ViString, ViPFindList,
					  ViPUInt32, ViAChar]
	self.__lib.viFlush.argtypes = [ViSession, ViUInt16]
	self.__lib.viGetAttribute.argtypes = [ViSession, ViAttr, c_void_p]
	self.__lib.viGpibCommand.argtypes = [ViSession, ViBuf, ViUInt32,
					     ViPUInt32]
	self.__lib.viGpibControlATN.argtypes = [ViSession, ViUInt16]
	self.__lib.viGpibControlREN.argtypes = [ViSession, ViUInt16]
	self.__lib.viGpibPassControl.argtypes = [ViSession, ViUInt16, ViUInt16]
	self.__lib.viGpibSendIFC.argtypes = [ViSession]
	self.__lib.viIn8.argtypes = [ViSession, ViUInt16, ViBusAddress,
				     ViPUInt8]
	self.__lib.viIn16.argtypes = [ViSession, ViUInt16, ViBusAddress,
				      ViPUInt16]
	self.__lib.viIn32.argtypes = [ViSession, ViUInt16, ViBusAddress,
				      ViPUInt32]
	self.__lib.viInstallHandler.argtypes = [ViSession, ViEventType,
						ViHndlr, ViAddr]
	self.__lib.viLock.argtypes = [ViSession, ViAccessMode, ViUInt32,
				      ViKeyId, ViAChar]
	self.__lib.viMapAddress.argtypes = [ViSession, ViUInt16, ViBusAddress,
					    ViBusSize, ViBoolean, ViAddr,
					    ViPAddr]
	self.__lib.viMapTrigger.argtypes = [ViSession, ViInt16, ViInt16,
					    ViUInt16]
	self.__lib.viMemAlloc.argtypes = [ViSession, ViBusSize, ViPBusAddress]
	self.__lib.viMemFree.argtypes = [ViSession, ViBusAddress]
	self.__lib.viMove.argtypes = [ViSession, ViUInt16, ViBusAddress,
				      ViUInt16, ViUInt16, ViBusAddress,
				      ViUInt16, ViBusSize]
	self.__lib.viMoveAsync.argtypes = [ViSession, ViUInt16, ViBusAddress,
					   ViUInt16, ViUInt16, ViBusAddress,
					   ViUInt16, ViBusSize, ViPJobId]
	self.__lib.viMoveIn8.argtypes = [ViSession, ViUInt16, ViBusAddress,
					 ViBusSize, ViAUInt8]
	self.__lib.viMoveIn16.argtypes = [ViSession, ViUInt16, ViBusAddress,
					  ViBusSize, ViAUInt16]
	self.__lib.viMoveIn32.argtypes = [ViSession, ViUInt16, ViBusAddress,
					  ViBusSize, ViAUInt32]
	self.__lib.viMoveOut8.argtypes = [ViSession, ViUInt16, ViBusAddress,
					  ViBusSize, ViAUInt8]
	self.__lib.viMoveOut16.argtypes = [ViSession, ViUInt16, ViBusAddress,
					   ViBusSize, ViAUInt16]
	self.__lib.viMoveOut32.argtypes = [ViSession, ViUInt16, ViBusAddress,
					   ViBusSize, ViAUInt32]
	self.__lib.viOpen.argtypes = [ViSession, ViRsrc, ViAccessMode,
				      ViUInt32, ViPSession]
	self.__lib.viOpenDefaultRM.argtypes = [ViPSession]
	self.__lib.viOut8.argtypes = [ViSession, ViUInt16, ViBusAddress,
				      ViUInt8]
	self.__lib.viOut16.argtypes = [ViSession, ViUInt16, ViBusAddress,
				       ViUInt16]
	self.__lib.viOut32.argtypes = [ViSession, ViUInt16, ViBusAddress,
				       ViUInt32]
	self.__lib.viParseRsrc.argtypes = [ViSession, ViRsrc, ViPUInt16,
					   ViPUInt16]
	self.__lib.viParseRsrcEx.argtypes = [ViSession, ViRsrc, ViPUInt16,
					     ViPUInt16, ViAChar, ViAChar,
					     ViAChar]
	self.__lib.viPeek8.argtypes = [ViSession, ViAddr, ViPUInt8]
	self.__lib.viPeek16.argtypes = [ViSession, ViAddr, ViPUInt16]
	self.__lib.viPeek32.argtypes = [ViSession, ViAddr, ViPUInt32]
	self.__lib.viPoke8.argtypes = [ViSession, ViAddr, ViUInt8]
	self.__lib.viPoke16.argtypes = [ViSession, ViAddr, ViUInt16]
	self.__lib.viPoke32.argtypes = [ViSession, ViAddr, ViUInt32]
	self.__cdecl_lib.viPrintf.argtypes = [ViSession, ViString]
	self.__cdecl_lib.viQueryf.argtypes = [ViSession, ViString, ViString]
	self.__lib.viRead.argtypes = [ViSession, ViPBuf, ViUInt32, ViPUInt32]
	self.__lib.viReadAsync.argtypes = [ViSession, ViPBuf, ViUInt32,
					   ViPJobId]
	self.__lib.viReadSTB.argtypes = [ViSession, ViPUInt16]
	self.__lib.viReadToFile.argtypes = [ViSession, ViString, ViUInt32,
					    ViPUInt32]
	self.__cdecl_lib.viScanf.argtypes = [ViSession, ViString]
	self.__lib.viSetAttribute.argtypes = [ViSession, ViAttr, ViAttrState]
	self.__lib.viSetBuf.argtypes = [ViSession, ViUInt16, ViUInt32]
	self.__cdecl_lib.viSPrintf.argtypes = [ViSession, ViPBuf, ViString]
	self.__cdecl_lib.viSScanf.argtypes = [ViSession, ViBuf, ViString]
	self.__lib.viStatusDesc.argtypes = [ViSession, ViStatus, ViAChar]
	self.__lib.viTerminate.argtypes = [ViSession, ViUInt16, ViJobId]
	self.__lib.viUninstallHandler.argtypes = [ViSession, ViEventType,
						  ViHndlr, ViAddr]
	self.__lib.viUnlock.argtypes = [ViSession]
	self.__lib.viUnmapAddress.argtypes = [ViSession]
	self.__lib.viUnmapTrigger.argtypes = [ViSession, ViInt16, ViInt16]
	self.__lib.viUsbControlIn.argtypes = [ViSession, ViInt16, ViInt16,
					      ViUInt16, ViUInt16, ViUInt16,
					      ViPBuf, ViPUInt16]
	self.__lib.viUsbControlOut.argtypes = [ViSession, ViInt16, ViInt16,
					       ViUInt16, ViUInt16, ViUInt16,
					       ViPBuf]
	# The folloowing "V" routines are *not* implemented in pyvisa, and will
	# never be.  They are listed here to implement a poor man's alert
	# mechanism.
	self.__lib.viVPrintf.argtypes = \
	    self.__cdecl_lib.viVPrintf.argtypes = []
	self.__lib.viVQueryf.argtypes = \
	    self.__cdecl_lib.viVQueryf.argtypes = []
	self.__lib.viVScanf.argtypes = \
	    self.__cdecl_lib.viVScanf.argtypes = []
	self.__lib.viVSPrintf.argtypes = \
	    self.__cdecl_lib.viVSPrintf.argtypes = []
	self.__lib.viVSScanf.argtypes = \
	    self.__cdecl_lib.viVSScanf.argtypes = []
	self.__lib.viVxiCommandQuery.argtypes = [ViSession, ViUInt16, ViUInt32,
						 ViPUInt32]
	self.__lib.viWaitOnEvent.argtypes = [ViSession, ViEventType, ViUInt32,
					     ViPEventType, ViPEvent]
	self.__lib.viWrite.argtypes = [ViSession, ViBuf, ViUInt32, ViPUInt32]
	self.__lib.viWriteAsync.argtypes = [ViSession, ViBuf, ViUInt32,
					    ViPJobId]
	self.__lib.viWriteFromFile.argtypes = [ViSession, ViString, ViUInt32,
					       ViPUInt32]


visa_library = VisaLibrary()

visa_status = 0

def check_status(status):
    """Check return values for errors."""
    global visa_status
    visa_status = status
    if status < 0:
        raise visa_exceptions.VisaIOError, status
    return status

def get_status():
    return visa_status

# convert_argument_list is used for VISA routines with variable argument list,
# which means that also the types are unknown.  While ctypes can deal with
# strings and integer, it is unable to dealt with all other types, in
# particular doubles.  Since I expect doubles to be a rather frequent type in
# the application of VISA, I convert them here.
#
# Attention: This means that only double can be used in format strings!  No
# floats, no long doubles.

def convert_argument_list(original_arguments):
    """Converts a Python arguments list to the equivalent ctypes list.

    Arguments:
    original_arguments -- a sequence type with the arguments that should be
        used with ctypes.

    Return value: a tuple with the ctypes version of the argument list.

    """
    converted_arguments = []
    for argument in original_arguments:
	if isinstance(argument, float):
	    argument_list.append(_ctypes.c_double(argument))
	else:
	    argument_list.append(argument)
    return tuple(converted_arguments)

def ensure_string_type(argument):
    if not isinstance(argument, basestring):
	raise TypeError("string expected instead of " + str(type(argument)))
    


# The VPP-4.3.2 routines

# Usually, there is more than one way to pass parameters to ctypes calls.  The
# ctypes policy used in this code goes as follows:
#
# * Null pointers are passed as "None" rather than "0".  This is a little bit
#   unfortunate, since the VPP specification calls this "VI_NULL", but I can't
#   use "VI_NULL" since it's an integer and may not be compatible with a
#   pointer type (don't know whether this is really dangerous).
#
# * Strings must have been created with "create_string_buffer" and are passed
#   without any further conversion; they stand in the parameter list as is.
#   The same applies to pseudo-string types as ViRsrc or VuBuf.  Their Pythonic
#   counterpats are strings as well.
#
# * All other types are explicitly cast using the types defined in
#   vpp43_types.py.  (This is not really casting but creating, anyway ...)
#
# Further notes:
#
# * The following Python routines take and give handles as ctypes objects.
#   Since the user shouldn't be interested in handle values anyway, I see no
#   point in converting them to Python strings or integers.
#
# * All other parameters are natural Python types, i.e. strings (may contain
#   binary data) and integers.  The same is true for return values.
#
# * The original VPP function signatures cannot be realised in Python, at least
#   not in a sensible way, because a) Python has no real call-by-reference, and
#   b) Python allows for more elegant solutions, e.g. using len(buffer) instead
#   of a separate "count" parameter, or using tuples as return values.
#
#   Therefore, all function signatures have been carefully adjusted.  I think
#   this is okay, since the original standard must be adopted to at least C and
#   Visual Basic anyway, with slight modifications.  I also made the function
#   names and parameters more legible, but in a way that it's perfectly clear
#   which original function is meant.
#
#   The important thing is that the semantics of functions and parameters are
#   totally intact, and the inner order of parameters, too.  There is a 1:1
#   mapping.

def open_default_resource_manager():
    session = ViSession()
    visa_library().viOpenDefaultRM(byref(session))
    return session

get_default_resource_manager = open_default_resource_manager
"""A deprecated alias.  See VPP-4.3, rule 4.3.5 and observation 4.3.2."""

def find_resources(session, regular_expression):
    ensure_string_type(regular_expression)
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindRsrc(session, regular_expression,
			      byref(find_list), byref(return_counter),
			      instrument_description)
    return (find_list.value, return_counter.value,
	    instrument_description.value)

def find_next(find_list):
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindNext(ViFindList(find_list), instrument_description)
    return instrument_description.value

def open(session, resource_name, access_mode, timeout):
    ensure_string_type(resource_name)
    vi = ViSession()
    visa_library().viOpen(session, resource_name, access_mode, timeout,
			  byref(vi))
    return vi

def close(vi):
    visa_library().viClose(vi)

def get_attribute(vi, attribute):
    attribute_state = ViAttrState()
    visa_library().viGetAttribute(vi, attribute, byref(attribute_state))
    return attribute_state.value

def set_attribute(vi, attribute, attribute_state):
    visa_library().viSetAttribute(vi, attribute, attribute_state)

def status_description(vi, status):
    description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viStatusDesc(vi, status, description)
    return description.value

def terminate(vi, degree, job_id):
    visa_library().viTerminate(vi, degree, job_id)

def lock(vi, lock_type, timeout, requested_key):
    if lock_type == VI_EXCLUSIVE_LOCK:
	requested_key = None
	access_key = None
    else:
	access_key = create_string_buffer(256)
    visa_library().viLock(vi, lock_type, timeout, requested_key, access_key)
    return access_key

def unlock(vi):
    visa_library().viUnlock(vi)

def enable_event(vi, event_type, mechanism, context):
    context = VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    visa_library().viEnableEvent(vi, event_type, mechanism, context)

def disable_event(vi, event_type, mechanism):
    visa_library().viDisableEvent(vi, event_type, mechanism)

def discard_events(vi, event_type, mechanism):
    visa_library().viDiscardEvents(vi, event_type, mechanism)

def wait_on_event(vi, in_event_type, timeout):
    out_event_type = ViEventType()
    out_context = ViEvent()
    visa_library().viWaitOnEvent(vi, in_event_type, timeout,
				 byref(out_event_type), byref(out_context))
    return (out_event_type, out_context)

def install_handler(vi, event_type, handler, user_handle):
    visa_library().viInstallHandler(vi, event_type, handler, user_handle)

def uninstall_handler(vi, event_type, handler, user_handle):
    visa_library().viUninstallHandler(vi, event_type, handler, user_handle)

def memory_allocation(vi, size):
    offset = ViBusAddress()
    visa_library().viMemAlloc(vi, size, byref(offset))
    return offset.value

def memory_free(vi, offset):
    visa_library().viMemFree(vi, offset)

def gpib_control_ren(vi, mode):
    visa_library().viGpibControlREN(vi, mode)

def vxi_command_query(vi, mode, command):
    response = ViUInt32()
    visa_library().viVxiCommandQuery(vi, mode, command, byref(response))
    return response.value

def parse_resource(session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16
    visa_library().viParseRsrc(session, resource_name, byref(interface_type),
			       byref(interface_board_number))
    return (interface_type, interface_board_number)

def write_from_file(vi, filename, count):
    return_count = ViUInt32()
    visa_library().viWriteFromFile(vi, filename, count, return_count)
    return return_count

def read_to_file(vi, filename, count):
    return_count = ViUInt32()
    visa_library().viReadToFile(vi, filename, count, return_count)
    return return_count

def parse_resource_extended(session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16
    resource_class = create_string_buffer(VI_FIND_BUFLEN)
    unaliased_expanded_resource_name = create_string_buffer(VI_FIND_BUFLEN)
    alias_if_exists = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viParseRsrc(session, resource_name, byref(interface_type),
			       byref(interface_board_number), resource_class,
			       unaliased_expanded_resource_name,
			       alias_if_exists)
    return (interface_type.value, interface_board_number.value,
	    resource_class.value, unaliased_expanded_resource_name.value,
	    alias_if_exists.value)

def usb_control_out(vi, request_type_bitmap_field, request_id, request_value,
		    index, buffer = ""):
    length = len(buffer)
    visa_library().viUsbControlOut(vi, request_type_bitmap_field, request_id,
				   request_value, index, length, buffer)

def read(vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    visa_library().viRead(vi, buffer, count, byref(return_count))
    return (buffer.raw[:return_count.value], return_count.value)

def read_asynchronously(vi, count):
    buffer = create_string_buffer(count)
    job_id = ViJobId()
    visa_library().viReadAsync(vi, buffer, count, byref(job_id))
    return (buffer.raw[:return_count.value], job_id)

def write(vi, buffer):
    return_count = ViUInt32()
    visa_library().viWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value

def write_asynchronously(vi, buffer):
    job_id = ViJobId()
    visa_library().viWriteAsync(vi, buffer, len(buffer), byref(job_id))
    return job_id

def assert_trigger(vi, protocol):
    visa_library().viAssertTrigger(vi, protocol)

def read_stb(vi):
    status = ViUInt16()
    visa_library().viReadSTB(vi, byref(status))
    return status.value

def clear(vi):
    visa_library().viClear(vi)

def set_buffer(vi, mask, size):
    visa_library().viSetBuf(vi, mask, size)

def flush(vi, mask):
    visa_library().viFlush(vi, mask)

def buffer_write(vi, buffer):
    return_count = ViUInt32()
    visa_library().viBufWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value

def buffer_read(vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    visa_library().viBufRead(vi, buffer, count, byref(return_count))
    return (buffer.raw[:return_count.value], return_count.value)

def printf(vi, write_format, *args):
    visa_library(True).viPrintf(vi, write_format, *convert_argument_list(args))

def sprintf(vi, write_format, *args, **keyw):
    buffer = create_string_buffer(keyw.get("buffer_length", 1024))
    visa_library(True).viSPrintf(vi, buffer, write_format,
				 *convert_argument_list(args))
    return buffer.raw

# FixMe: I have to test whether the results are really written to
# "argument_list" rather than only to a local copy within "viScanf".

def scanf(vi, read_format, *args):
    argument_list = convert_argument_list(args)
    visa_library(True).viScanf(vi, read_format, *argument_list)
    return tuple([argument.value for argument in argument_list])

def sscanf(vi, buffer, read_format, *args):
    argument_list = convert_argument_list(args)
    visa_library(True).viSScanf(vi, buffer, read_format, *argument_list)
    return tuple([argument.value for argument in argument_list])

def queryf(vi, write_format, read_format, write_args, *read_args):
    argument_list = convert_argument_list(read_args)
    if write_args is None: write_args = ()
    visa_library(True).viQueryf(vi, write_format, read_format,
				*(write_args + argument_list))
    return tuple([argument.value for argument in argument_list])


# The following variants make no sense in Python, so I realise them as mere
# aliases.

vprintf  = printf
vsprintf = sprintf
vscanf   = scanf
vsscanf  = sscanf
vqueryf  = queryf

def gpib_control_atn(vi, mode):
    visa_library().viGpibControlATN(vi, ViUInt16(mode))

def gpib_send_ifc(vi):
    visa_library().viGpibSendIFC(vi)

def gpib_command(vi, buffer):
    return_count = ViUInt32()
    visa_library().viGpibCommand(vi, buffer, len(buffer), byref(return_count))
    return return_count.value

def gpib_pass_control(vi, primary_address, secondary_address):
    visa_library().viGpibPassControl(vi, primary_address, secondary_address)

def usb_control_in(vi, bm_request_type, b_request, w_value, w_index, w_length):
    buffer = create_string_buffer(w_length)
    return_count = ViUInt16()
    visa_library().viUsbControlIn(vi, bm_request_type, b_request, w_value,
				  w_index, w_length, buffer,
				  byref(return_count))
    return (buffer.raw[:return_count.value], return_count.value)

def in_8(vi, space, offset):
    value_8 = ViUInt8()
    visa_library().viIn8(vi, space, offset, byref(value_8))
    return value_8.value

def out_8(vi, space, offset, value_8):
    visa_library().viOut8(vi, space, offset, value_8)

def in_16(vi, space, offset):
    value_16 = ViUInt16()
    visa_library().viIn16(vi, space, offset, byref(value_16))
    return value_8.value

def out_16(vi, space, offset, value_16):
    visa_library().viOut16(vi, space, offset, value_16)

def in_32(vi, space, offset):
    value_32 = ViUInt32()
    visa_library().viIn32(vi, space, offset, byref(value_32))
    return value_32.value

def out_32(vi, space, offset, value_32):
    visa_library().viOut32(vi, space, offset, value_32)

def move_in_8(vi, space, offset, length):
    buffer_8 = (ViUInt8 * length)();
    visa_library().viMoveIn8(vi, space, offset, length, byref(buffer_8))
    return list(buffer_8)

def move_out_8(vi, space, offset, length, buffer_8):
    converted_buffer = (ViUInt8 * length)(*tuple(buffer_8))
    visa_library().viMoveOut8(vi, space, offset, length, converted_buffer)

def move_in_16(vi, space, offset, length):
    buffer_16 = (ViUInt16 * length)();
    visa_library().viMoveIn16(vi, space, offset, length, byref(buffer_16))
    return list(buffer_16)

def move_out_16(vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt16 * length)(*tuple(buffer_16))
    visa_library().viMoveOut16(vi, space, offset, length, converted_buffer)

def move_in_32(vi, space, offset, length):
    buffer_32 = (ViUInt32 * length)();
    visa_library().viMoveIn32(vi, space, offset, length, byref(buffer_32))
    return list(buffer_32)

def move_out_32(vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt32 * length)(*tuple(buffer_32))
    visa_library().viMoveOut32(vi, space, offset, length, converted_buffer)

def move(vi, source_space, source_offset, source_width, destination_space,
	 destination_offset, destination_width, length):
    visa_library().viMove(vi, source_space, source_offset, source_width,
			  destination_space, destination_offset,
			  destination_width, length)

def move_asynchronously(vi, source_space, source_offset, source_width,
			destination_space, destination_offset,
			destination_width, length):
    job_id = ViJobId()
    visa_library().viMoveAsync(vi, source_space, source_offset, source_width,
			       destination_space, destination_offset,
			       destination_width, length, byref(job_id))
    return job_id

def map_address(vi, map_space, map_base, map_size, access, suggested):
    address = ViAddr()
    visa_library().viMapAddress(vi, map_space, map_base, map_size, access,
				suggested, byref(address))
    return address.value

def unmap_address(vi):
    visa_library().viUnmapAddress(vi)

def peek_8(vi, address):
    value_8 = ViUInt8()
    visa_library().viPeek8(vi, address, byref(value_8))
    return value_8.value

def poke_8(vi, address, value_8):
    visa_library().viPoke8(vi, address, value_8)

def peek_16(vi, address):
    value_16 = ViUInt16()
    visa_library().viPeek16(vi, address, byref(value_16))
    return value_16.value

def poke_16(vi, address, value_16):
    visa_library().viPoke16(vi, address, value_16)

def peek_32(vi, address):
    value_32 = ViUInt32()
    visa_library().viPeek32(vi, address, byref(value_32))
    return value_32.value

def poke_32(vi, address, value_32):
    visa_library().viPoke32(vi, address, value_32)

def assert_utility_signal(vi, line):
    visa_library().viAssertUtilSignal(vi, line)

def assert_interrupt_signal(vi, mode, status_id):
    visa_library().viAssertIntrSignal(vi, mode, status_id)

def map_trigger(vi, trigger_source, trigger_destination, mode):
    visa_library().viMapTrigger(vi, trigger_source, trigger_destination, mode)

def unmap_trigger(vi, trigger_source, trigger_destination):
    visa_library().viUnmapTrigger(vi, trigger_source, trigger_destination)
