# -*- coding: utf-8 -*-
"""
    vpp43
    ~~~~~

    Defines VPP 4.3.2 routines.

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import os
import warnings

from ctypes import (byref, cdll, c_void_p, c_double, c_long,
                    create_string_buffer, POINTER)

if os.name == 'nt':
    from ctypes import windll, WINFUNCTYPE as FUNCTYPE
else:
    from ctypes import CFUNCTYPE as FUNCTYPE

VI_SPEC_VERSION = 0x00300000

from .visa_messages import completion_and_error_messages
from .constants import *
from .types import *
from .attributes import attributes

visa_functions = [
    "assert_interrupt_signal", "assert_trigger", "assert_utility_signal",
    "buffer_read", "buffer_write", "clear", "close", "disable_event",
    "discard_events", "enable_event", "find_next", "find_resources", "flush",
    "get_attribute", "get_default_resource_manager", "gpib_command",
    "gpib_control_atn", "gpib_control_ren", "gpib_pass_control",
    "gpib_send_ifc", "in_16", "in_32", "in_8", "install_handler", "lock",
    "map_address", "map_trigger", "memory_allocation", "memory_free", "move",
    "move_asynchronously", "move_in_16", "move_in_32", "move_in_8",
    "move_out_16", "move_out_32", "move_out_8", "open",
    "open_default_resource_manager", "out_16", "out_32", "out_8",
    "parse_resource", "parse_resource_extended", "peek_16", "peek_32",
    "peek_8", "poke_16", "poke_32", "poke_8", "printf", "queryf", "read",
    "read_asynchronously", "read_to_file", "read_stb", "scanf",
    "set_attribute", "set_buffer", "sprintf", "sscanf", "status_description",
    "terminate", "uninstall_handler", "unlock", "unmap_address",
    "unmap_trigger", "usb_control_in", "usb_control_out", "vprintf", "vqueryf",
    "vscanf", "vsprintf", "vsscanf", "vxi_command_query", "wait_on_event",
    "write", "write_asynchronously", "write_from_file"]

__all__ = ["visa_library", "get_status"] + visa_functions

def set_user_handle_type(library, user_handle):
    # Actually, it's not necessary to change ViHndlr *globally*.  However,
    # I don't want to break symmetry too much with all the other VPP43
    # routines.
    global ViHndlr

    if user_handle is None:
        user_handle_p = c_void_p
    else:
        user_handle_p = POINTER(type(user_handle))

    ViHndlr = FUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent ,user_handle_p)
    library.viInstallHandler.argtypes = [ViSession, ViEventType, ViHndlr, user_handle_p]
    library.viUninstallHandler.argtypes = [ViSession, ViEventType, ViHndlr, user_handle_p]


def set_signatures(library):
    """Set the signatures of most visa functions in the library.

    All instrumentation related functions are specified here.
    String related functions such as `viPrintf` require a cdecl
    calling convention even in windows and therefore are require
    a CDLL object. See `set_cdecl_signatures`.

    :param library: the visa library wrapped by ctypes.
    :type library: ctypes.WinDLL or ctypes.CDLL
    """

    # Here too, we silently ignore missing functions.  If the user accesses
    # it nevertheless, an AttributeError is raised which is clear enough
    set_signature(library, "viAssertIntrSignal",
                  [ViSession, ViInt16, ViUInt32],
                  check_status)
    set_signature(library, "viAssertTrigger",
                  [ViSession, ViUInt16],
                  check_status)
    set_signature(library, "viAssertUtilSignal",
                  [ViSession, ViUInt16],
                  check_status)
    set_signature(library, "viBufRead",
                  [ViSession, ViPBuf, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viBufWrite",
                  [ViSession, ViBuf, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viClear",
                  [ViSession],
                  check_status)
    set_signature(library, "viClose",
                  [ViObject],
                  check_status)
    set_signature(library, "viDisableEvent",
                  [ViSession, ViEventType, ViUInt16],
                  check_status)
    set_signature(library, "viDiscardEvents",
                  [ViSession, ViEventType, ViUInt16],
                  check_status)
    set_signature(library, "viEnableEvent",
                  [ViSession, ViEventType, ViUInt16, ViEventFilter],
                  check_status)
    set_signature(library, "viFindNext",
                  [ViSession, ViAChar],
                  check_status)
    set_signature(library, "viFindRsrc",
                  [ViSession, ViString, ViPFindList, ViPUInt32, ViAChar],
                  check_status)
    set_signature(library, "viFlush",
                  [ViSession, ViUInt16],
                  check_status)
    set_signature(library, "viGetAttribute",
                  [ViObject, ViAttr, c_void_p],
                  check_status)
    set_signature(library, "viGpibCommand",
                  [ViSession, ViBuf, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viGpibControlATN",
                  [ViSession, ViUInt16],
                  check_status)
    set_signature(library, "viGpibControlREN",
                  [ViSession, ViUInt16],
                  check_status)
    set_signature(library, "viGpibPassControl",
                  [ViSession, ViUInt16, ViUInt16],
                  check_status)
    set_signature(library, "viGpibSendIFC",
                  [ViSession],
                  check_status)
    set_signature(library, "viIn8",
                  [ViSession, ViUInt16, ViBusAddress, ViPUInt8],
                  check_status)
    set_signature(library, "viIn16",
                  [ViSession, ViUInt16, ViBusAddress, ViPUInt16],
                  check_status)
    set_signature(library, "viIn32",
                  [ViSession, ViUInt16, ViBusAddress, ViPUInt32],
                  check_status)
    set_signature(library, "viInstallHandler",
                  [ViSession, ViEventType, ViHndlr, ViAddr],
                  check_status)
    set_signature(library, "viLock",
                  [ViSession, ViAccessMode, ViUInt32, ViKeyId, ViAChar],
                  check_status)
    set_signature(library, "viMapAddress",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViBoolean, ViAddr, ViPAddr],
                  check_status)
    set_signature(library, "viMapTrigger",
                  [ViSession, ViInt16, ViInt16, ViUInt16],
                  check_status)
    set_signature(library, "viMemAlloc",
                  [ViSession, ViBusSize, ViPBusAddress],
                  check_status)
    set_signature(library, "viMemFree",
                  [ViSession, ViBusAddress],
                  check_status)
    set_signature(library, "viMove",
                  [ViSession, ViUInt16, ViBusAddress, ViUInt16,
                   ViUInt16, ViBusAddress, ViUInt16, ViBusSize],
                  check_status)
    set_signature(library, "viMoveAsync",
                  [ViSession, ViUInt16, ViBusAddress, ViUInt16,
                   ViUInt16, ViBusAddress, ViUInt16, ViBusSize,
                   ViPJobId],
                  check_status)
    set_signature(library, "viMoveIn8",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt8],
                  check_status)
    set_signature(library, "viMoveIn16",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt16],
                  check_status)
    set_signature(library, "viMoveIn32",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt32],
                  check_status)
    set_signature(library, "viMoveOut8",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt8],
                  check_status)
    set_signature(library, "viMoveOut16",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt16],
                  check_status)
    set_signature(library, "viMoveOut32",
                  [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt32],
                  check_status)

    # The following function *must* be available in order to assure that we
    # have a VISA library at all (rather than something completely
    # different).  I hope that viOpen is old enough in the VISA
    # specification.
    set_signature(library, "viOpen",
                  [ViSession, ViRsrc, ViAccessMode, ViUInt32, ViPSession],
                  check_status,
                  may_be_missing=False)

    set_signature(library, "viOpenDefaultRM",
                  [ViPSession],
                  check_status)
    set_signature(library, "viOut8",
                  [ViSession, ViUInt16, ViBusAddress, ViUInt8],
                  check_status)
    set_signature(library, "viOut16",
                  [ViSession, ViUInt16, ViBusAddress, ViUInt16],
                  check_status)
    set_signature(library, "viOut32",
                  [ViSession, ViUInt16, ViBusAddress, ViUInt32],
                  check_status)
    set_signature(library, "viParseRsrc",
                  [ViSession, ViRsrc, ViPUInt16, ViPUInt16],
                  check_status)
    set_signature(library, "viParseRsrcEx",
                  [ViSession, ViRsrc, ViPUInt16, ViPUInt16, ViAChar, ViAChar, ViAChar],
                  check_status)

    set_signature(library, "viPeek8",
                  [ViSession, ViAddr, ViPUInt8],
                  None)
    set_signature(library, "viPeek16",
                  [ViSession, ViAddr, ViPUInt16],
                  None)
    set_signature(library, "viPeek32",
                  [ViSession, ViAddr, ViPUInt32],
                  None)
    set_signature(library, "viPoke8",
                  [ViSession, ViAddr, ViUInt8],
                  None)
    set_signature(library, "viPoke16",
                  [ViSession, ViAddr, ViUInt16],
                  None)
    set_signature(library, "viPoke32",
                  [ViSession, ViAddr, ViUInt32],
                  None)

    set_signature(library, "viRead",
                  [ViSession, ViPBuf, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viReadAsync",
                  [ViSession, ViPBuf, ViUInt32, ViPJobId],
                  check_status)
    set_signature(library, "viReadSTB",
                  [ViSession, ViPUInt16],
                  check_status)
    set_signature(library, "viReadToFile",
                  [ViSession, ViString, ViUInt32, ViPUInt32],
                  check_status)

    set_signature(library, "viSetAttribute",
                  [ViObject, ViAttr, ViAttrState],
                  check_status)
    set_signature(library, "viSetBuf",
                  [ViSession, ViUInt16, ViUInt32],
                  check_status)

    set_signature(library, "viStatusDesc",
                  [ViObject, ViStatus, ViAChar],
                  check_status)
    set_signature(library, "viTerminate",
                  [ViSession, ViUInt16, ViJobId],
                  check_status)
    set_signature(library, "viUninstallHandler",
                  [ViSession, ViEventType, ViHndlr, ViAddr],
                  check_status)
    set_signature(library, "viUnlock",
                  [ViSession],
                  check_status)
    set_signature(library, "viUnmapAddress",
                  [ViSession],
                  check_status)
    set_signature(library, "viUnmapTrigger",
                  [ViSession, ViInt16, ViInt16],
                  check_status)
    set_signature(library, "viUsbControlIn",
                  [ViSession, ViInt16, ViInt16, ViUInt16,
                   ViUInt16, ViUInt16, ViPBuf, ViPUInt16],
                  check_status)
    set_signature(library, "viUsbControlOut",
                  [ViSession, ViInt16, ViInt16, ViUInt16,
                   ViUInt16, ViUInt16, ViPBuf],
                  check_status)

    # The following "V" routines are *not* implemented in PyVISA, and will
    # never be: viVPrintf, viVQueryf, viVScanf, viVSPrintf, viVSScanf

    set_signature(library, "viVxiCommandQuery",
                  [ViSession, ViUInt16, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viWaitOnEvent",
                  [ViSession, ViEventType, ViUInt32, ViPEventType, ViPEvent],
                  check_status)
    set_signature(library, "viWrite",
                  [ViSession, ViBuf, ViUInt32, ViPUInt32],
                  check_status)
    set_signature(library, "viWriteAsync",
                  [ViSession, ViBuf, ViUInt32, ViPJobId],
                  check_status)
    set_signature(library, "viWriteFromFile",
                  [ViSession, ViString,ViUInt32, ViPUInt32],
                  check_status)


def set_signature(library, function_name, argtypes, restype, may_be_missing=True):
    """Set the signature of single function in a library.

    :param library: ctypes wrapped library.
    :type library: ctypes.WinDLL or ctypes.CDLL
    :param function_name: name of the function as appears in the header file.
    :type function_name: str
    :param argtypes: a tuple of ctypes types to specify the argument types that the function accepts.
    :param restype: A ctypes type to specify the result type of the foreign function.
                    Use None for void, a function not returning anything.
    :param may_be_missing: if False, an Attribute error will be raised if the
                           function_name is not found.

    :raises: AttributeError
    """

    try:
        getattr(library, function_name).argtypes = argtypes
        getattr(library, function_name).restype = restype
    except AttributeError:
        if not may_be_missing:
            raise


visa_library = VisaLibrary()

visa_status = 0

dodgy_completion_codes = \
    [VI_SUCCESS_MAX_CNT, VI_SUCCESS_DEV_NPRESENT, VI_SUCCESS_SYNC,
    VI_WARN_QUEUE_OVERFLOW, VI_WARN_CONFIG_NLOADED, VI_WARN_NULL_OBJECT,
    VI_WARN_NSUP_ATTR_STATE, VI_WARN_UNKNOWN_STATUS, VI_WARN_NSUP_BUF,
    VI_WARN_EXT_FUNC_NIMPL]
"""For these completion codes, warnings are issued."""


def check_status(status):
    """Check return values for errors and warnings."""
    global visa_status
    visa_status = status
    if status < 0:
        raise VisaIOError(status)
    if status in dodgy_completion_codes:
        abbreviation, description = completion_and_error_messages[status]
        warnings.warn("%s: %s" % (abbreviation, description),
                      VisaIOWarning, stacklevel=2)
    return status


def get_status():
    return visa_status


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
# * All other types are explicitly cast using the types defined by ctypes'
#   "restype".
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


def assert_interrupt_signal(library, vi, mode, status_id):
    library.viAssertIntrSignal(vi, mode, status_id)


def assert_trigger(library, vi, protocol):
    library.viAssertTrigger(vi, protocol)


def assert_utility_signal(library, vi, line):
    library.viAssertUtilSignal(vi, line)


def buffer_read(library, vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    library.viBufRead(vi, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def buffer_write(library, vi, buffer):
    return_count = ViUInt32()
    library.viBufWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def clear(library, vi):
    library.viClear(vi)


def close(library, vi):
    library.viClose(vi)


def disable_event(library, vi, event_type, mechanism):
    library.viDisableEvent(vi, event_type, mechanism)


def discard_events(library, vi, event_type, mechanism):
    library.viDiscardEvents(vi, event_type, mechanism)


def enable_event(library, vi, event_type, mechanism, context=VI_NULL):
    context = VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    library.viEnableEvent(vi, event_type, mechanism, context)


def find_next(library, find_list):
    instrument_description = create_string_buffer(library, vi_FIND_BUFLEN)
    library.viFindNext(find_list, instrument_description)
    return instrument_description.value


def find_resources(library, session, regular_expression):
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    library.viFindRsrc(session, regular_expression,
                       byref(find_list), byref(return_counter),
                       instrument_description)
    return find_list, return_counter.value, instrument_description.value


def flush(library, vi, mask):
    library.viFlush(vi, mask)


def get_attribute(library, vi, attribute):
    # FixMe: How to deal with ViBuf?
    datatype = attributes[attribute]
    if datatype == ViString:
        attribute_state = create_string_buffer(256)
        library.viGetAttribute(vi, attribute, attribute_state)
    elif datatype == ViAUInt8:
        length = get_attribute(library, vi, VI_ATTR_USB_RECV_INTR_SIZE)
        attribute_state = (ViUInt8 * length)()
        library.viGetAttribute(vi, attribute, byref(attribute_state))
        return list(attribute_state)
    else:
        attribute_state = datatype()
        library.viGetAttribute(vi, attribute, byref(attribute_state))
    return attribute_state.value


def gpib_command(library, vi, buffer):
    return_count = ViUInt32()
    library.viGpibCommand(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def gpib_control_atn(library, vi, mode):
    library.viGpibControlATN(vi, mode)


def gpib_control_ren(library, vi, mode):
    library.viGpibControlREN(vi, mode)


def gpib_pass_control(library, vi, primary_address, secondary_address):
    library.viGpibPassControl(vi, primary_address, secondary_address)


def gpib_send_ifc(library, vi):
    library.viGpibSendIFC(vi)


def in_8(library, vi, space, offset):
    value_8 = ViUInt8()
    library.viIn8(vi, space, offset, byref(value_8))
    return value_8.value


def in_16(library, vi, space, offset):
    value_16 = ViUInt16()
    library.viIn16(vi, space, offset, byref(value_16))
    return value_16.value


def in_32(library, vi, space, offset):
    value_32 = ViUInt32()
    library.viIn32(vi, space, offset, byref(value_32))
    return value_32.value


#: Contains all installed event handlers as three elements tuple:
#: - handler (a python callable)
#: - user handle (a ctypes object)
#: - ctypes handler (ctypes object wrapping handler)
handlers = []

def install_handler(library, vi, event_type, handler, user_handle=None):
    if user_handle is None:
        converted_user_handle = None
    else:
        if isinstance(user_handle, int):
            converted_user_handle = c_long(user_handle)
        elif isinstance(user_handle, float):
            converted_user_handle = c_double(user_handle)
        elif isinstance(user_handle, str):
            converted_user_handle = c_create_string_buffer(user_handle)
        elif isinstance(user_handle, list):
            for element in user_handle:
                if not isinstance(element, int):
                    converted_user_handle = \
                        (c_double * len(user_handle))(tuple(user_handle))
                    break
            else:
                converted_user_handle = \
                    (c_long * len(user_handle))(*tuple(user_handle))
        else:
            raise VisaTypeError("Type not allowed as user handle: %s" % type(user_handle))
    visa_library.set_user_handle_type(converted_user_handle)
    converted_handler = ViHndlr(handler)
    if user_handle is None:
        library.viInstallHandler(vi, event_type, converted_handler,
                                 None)
    else:
        library.viInstallHandler(vi, event_type, converted_handler,
                                 byref(converted_user_handle))
    handlers.append((handler, converted_user_handle, converted_handler))
    return converted_user_handle


def lock(library, vi, lock_type, timeout, requested_key=None):
    if lock_type == VI_EXCLUSIVE_LOCK:
        requested_key = None
        access_key = None
    else:
        access_key = create_string_buffer(256)
    library.viLock(vi, lock_type, timeout, requested_key, access_key)
    return access_key


def map_address(library, vi, map_space, map_base, map_size,
                access=VI_FALSE, suggested=VI_NULL):
    access = VI_FALSE
    address = ViAddr()
    library.viMapAddress(vi, map_space, map_base, map_size, access,
                         suggested, byref(address))
    return address


def map_trigger(library, vi, trigger_source, trigger_destination, mode):
    library.viMapTrigger(vi, trigger_source, trigger_destination, mode)


def memory_allocation(library, vi, size):
    offset = ViBusAddress()
    library.viMemAlloc(vi, size, byref(offset))
    return offset


def memory_free(library, vi, offset):
    library.viMemFree(vi, offset)


def move(library, vi, source_space, source_offset, source_width, destination_space,
         destination_offset, destination_width, length):
    library.viMove(vi, source_space, source_offset, source_width,
                   destination_space, destination_offset,
                   destination_width, length)


def move_asynchronously(library, vi, source_space, source_offset, source_width,
                        destination_space, destination_offset,
                        destination_width, length):
    job_id = ViJobId()
    library.viMoveAsync(vi, source_space, source_offset, source_width,
                        destination_space, destination_offset,
                        destination_width, length, byref(job_id))
    return job_id


def move_in_8(library, vi, space, offset, length):
    buffer_8 = (ViUInt8 * length)()
    library.viMoveIn8(vi, space, offset, length, buffer_8)
    return list(buffer_8)


def move_in_16(library, vi, space, offset, length):
    buffer_16 = (ViUInt16 * length)()
    library.viMoveIn16(vi, space, offset, length, buffer_16)
    return list(buffer_16)


def move_in_32(library, vi, space, offset, length):
    buffer_32 = (ViUInt32 * length)()
    library.viMoveIn32(vi, space, offset, length, buffer_32)
    return list(buffer_32)


def move_out_8(library, vi, space, offset, length, buffer_8):
    converted_buffer = (ViUInt8 * length)(*tuple(buffer_8))
    library.viMoveOut8(vi, space, offset, length, converted_buffer)


def move_out_16(library, vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt16 * length)(*tuple(buffer_16))
    library.viMoveOut16(vi, space, offset, length, converted_buffer)


def move_out_32(library, vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt32 * length)(*tuple(buffer_32))
    library.viMoveOut32(vi, space, offset, length, converted_buffer)


def open(library, session, resource_name,
         access_mode=VI_NO_LOCK, open_timeout=VI_TMO_IMMEDIATE):
    vi = ViSession()
    library.viOpen(session, resource_name, access_mode, open_timeout,
                   byref(vi))
    return vi.value


def open_default_resource_manager(library):
    session = ViSession()
    library.viOpenDefaultRM(byref(session))
    return session.value

get_default_resource_manager = open_default_resource_manager
"""A deprecated alias.  See VPP-4.3, rule 4.3.5 and observation 4.3.2."""


def out_8(library, vi, space, offset, value_8):
    library.viOut8(vi, space, offset, value_8)


def out_16(library, vi, space, offset, value_16):
    library.viOut16(vi, space, offset, value_16)


def out_32(library, vi, space, offset, value_32):
    library.viOut32(vi, space, offset, value_32)


def parse_resource(library, session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    library.viParseRsrc(session, resource_name, byref(interface_type),
                        byref(interface_board_number))
    return interface_type.value, interface_board_number.value


def parse_resource_extended(library, session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    resource_class = create_string_buffer(VI_FIND_BUFLEN)
    unaliased_expanded_resource_name = create_string_buffer(VI_FIND_BUFLEN)
    alias_if_exists = create_string_buffer(VI_FIND_BUFLEN)
    library.viParseRsrcEx(session, resource_name, byref(interface_type),
                          byref(interface_board_number), resource_class,
                          unaliased_expanded_resource_name,
                          alias_if_exists)
    if alias_if_exists.value == "":
        alias_if_exists = None
    else:
        alias_if_exists = alias_if_exists.value
    return (interface_type.value, interface_board_number.value,
            resource_class.value, unaliased_expanded_resource_name.value,
            alias_if_exists)


def peek_8(library, vi, address):
    value_8 = ViUInt8()
    library.viPeek8(vi, address, byref(value_8))
    return value_8.value


def peek_16(library, vi, address):
    value_16 = ViUInt16()
    library.viPeek16(vi, address, byref(value_16))
    return value_16.value


def peek_32(library, vi, address):
    value_32 = ViUInt32()
    library.viPeek32(vi, address, byref(value_32))
    return value_32.value


def poke_8(library, vi, address, value_8):
    library.viPoke8(vi, address, value_8)


def poke_16(library, vi, address, value_16):
    library.viPoke16(vi, address, value_16)


def poke_32(library, vi, address, value_32):
    library.viPoke32(vi, address, value_32)

def read(library, vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    library.viRead(vi, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def read_asynchronously(library, vi, count):
    buffer = create_string_buffer(count)
    job_id = ViJobId()
    library.viReadAsync(vi, buffer, count, byref(job_id))
    return buffer, job_id


def read_stb(library, vi):
    status = ViUInt16()
    library.viReadSTB(vi, byref(status))
    return status.value


def read_to_file(library, vi, filename, count):
    return_count = ViUInt32()
    library.viReadToFile(vi, filename, count, return_count)
    return return_count


def set_attribute(library, vi, attribute, attribute_state):
    library.viSetAttribute(vi, attribute, attribute_state)


def set_buffer(library, vi, mask, size):
    library.viSetBuf(vi, mask, size)


def status_description(library, vi, status):
    description = create_string_buffer(256)
    library.viStatusDesc(vi, status, description)
    return description.value


def terminate(library, vi, degree, job_id):
    library.viTerminate(vi, degree, job_id)


def uninstall_handler(library, vi, event_type, handler, user_handle=None):
    for i in range(len(handlers)):
        element = handlers[i]
        if element[0] is handler and element[1] is user_handle:
            del handlers[i]
            break
    else:
        raise UnknownHandler
    library.viUninstallHandler(vi, event_type, element[2],
                               byref(element[1]))

def unlock(library, vi):
    library.viUnlock(vi)


def unmap_address(library, vi):
    library.viUnmapAddress(vi)


def unmap_trigger(library, vi, trigger_source, trigger_destination):
    library.viUnmapTrigger(vi, trigger_source, trigger_destination)


def usb_control_in(library, vi, request_type_bitmap_field, request_id, request_value,
                   index, length=0):
    buffer = create_string_buffer(length)
    return_count = ViUInt16()
    library.viUsbControlIn(vi, request_type_bitmap_field, request_id,
                           request_value, index, length, buffer,
                           byref(return_count))
    return buffer.raw[:return_count.value]


def usb_control_out(library, vi, request_type_bitmap_field, request_id, request_value,
                    index, buffer=""):
    length = len(buffer)
    library.viUsbControlOut(vi, request_type_bitmap_field, request_id,
                            request_value, index, length, buffer)


def vxi_command_query(library, vi, mode, command):
    response = ViUInt32()
    library.viVxiCommandQuery(vi, mode, command, byref(response))
    return response.value


def wait_on_event(library, vi, in_event_type, timeout):
    out_event_type = ViEventType()
    out_context = ViEvent()
    library.viWaitOnEvent(vi, in_event_type, timeout,
                          byref(out_event_type), byref(out_context))
    return out_event_type.value, out_context


def write(library, vi, buffer):
    return_count = ViUInt32()
    library.viWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def write_asynchronously(library, vi, buffer):
    job_id = ViJobId()
    library.viWriteAsync(vi, buffer, len(buffer), byref(job_id))
    return job_id


def write_from_file(library, vi, filename, count):
    return_count = ViUInt32()
    library.viWriteFromFile(vi, filename, count, return_count)
    return return_count


# To be deprecated in PyVISA 1.6
# All these functions are easy to replace by Python equivalents.

def set_cdecl_signatures(clibrary):
    """Set the signatures of visa functions requiring a cdecl calling convention.

    .. note: This function and the support for string formatting operations in the
             VISA library will be removed in PyVISA 1.6. as these functions can be
             easily replaced by Python equivalents.

    :param library: the visa library wrapped by ctypes.
    :type library: ctypes.CDLL
    """
    assert isinstance(clibrary, _ctypes.CDLL)

    set_signature(clibrary, "viSPrintf",
                  [ViSession, ViPBuf, ViString],
                  check_status)
    set_signature(clibrary, "viSScanf",
                  [ViSession, ViBuf, ViString],
                  check_status)
    set_signature(clibrary, "viScanf",
                  [ViSession, ViString],
                  check_status)
    set_signature(clibrary, "viPrintf",
                  [ViSession, ViString],
                  check_status)
    set_signature(clibrary, "viQueryf",
                  [ViSession, ViString, ViString],
                  check_status)



# convert_argument_list is used for VISA routines with variable argument list,
# which means that also the types are unknown.  Therefore I convert the Python
# types to well-defined ctypes types.
#
# Attention: This means that only C doubles, C long ints, and strings can be
# used in format strings!  No "float"s, no "long doubles", no "int"s etc.
# Further, only floats, integers and strings can be passed to printf and scanf,
# but neither unicode strings nor sequence types.
def convert_argument_list(original_arguments):
    """Converts a Python arguments list to the equivalent ctypes list.

    :param original_arguments: a sequence type with the arguments that should be
                               used with ctypes.

    :return: a tuple with the ctypes version of the argument list.
    """

    converted_arguments = []
    for argument in original_arguments:
        if isinstance(argument, float):
            converted_arguments.append(c_double(argument))
        elif isinstance(argument, int):
            converted_arguments.append(c_long(argument))
        elif isinstance(argument, str):
            converted_arguments.append(argument)
        else:
            raise VisaTypeError("Invalid type in scanf/printf: %s" % type(argument))
    return tuple(converted_arguments)


def convert_to_byref(byvalue_arguments, buffer_length):
    """Converts a list of ctypes objects to a tuple with ctypes references
    (pointers) to them, for use in scanf-like functions.

    :param byvalue_arguments: a list (sic!) with the original arguments. They must
        be simple ctypes objects or Python strings. If there are Python
        strings, they are converted in place to ctypes buffers of the same
        length and same contents.
    :param buffer_length: minimal length of ctypes buffers generated from Python
        strings.

    :returns: a tuple with the by-references arguments.
    """

    converted_arguments = []
    for i in range(len(byvalue_arguments)):
        if isinstance(byvalue_arguments[i], str):
            byvalue_arguments[i] = \
                create_string_buffer(byvalue_arguments[i],
                                     max(len(byvalue_arguments[i]) + 1,
                                         buffer_length))
            converted_arguments.append(byvalue_arguments[i])
        elif isinstance(byvalue_arguments[i], (c_long, c_double)):
            converted_arguments.append(byref(byvalue_arguments[i]))
        else:
            raise VisaTypeError("Invalid type in scanf: %s" % type(argument))
    return tuple(converted_arguments)


def construct_return_tuple(original_ctypes_sequence):
    """Generate a return value for queryf(), scanf(), and sscanf() out of the
    list of ctypes objects.

    :param original_ctypes_sequence: a sequence of ctypes objects, i.e. c_long,
                                     c_double, and ctypes strings.

    :returns: The pythonic variants of the ctypes objects, in a form
              suitable to be returned by a function: None if empty, single value, or
              tuple of all values.
    """

    length = len(original_ctypes_sequence)
    if length == 0:
        return None
    elif length == 1:
        return original_ctypes_sequence[0].value
    else:
        return tuple([argument.value for argument in original_ctypes_sequence])


def printf(clibrary, vi, write_format, *args):
    assert isinstance(clibrary, _ctypes.CDLL)
    clibrary.viPrintf(vi, write_format, *convert_argument_list(args))


def queryf(clibrary, vi, write_format, read_format, write_args, *read_args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(read_args))
    if write_args is None: write_args = ()
    clibrary.viQueryf(vi, write_format, read_format,
                      *(convert_argument_list(write_args) + convert_to_byref(argument_list,  maximal_string_length)))
    return construct_return_tuple(argument_list)

# FixMe: I have to test whether the results are really written to
# "argument_list" rather than only to a local copy within "viScanf".

def scanf(clibrary, vi, read_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    clibrary.viScanf(vi, read_format, *convert_to_byref(argument_list, maximal_string_length))
    return construct_return_tuple(argument_list)


def sprintf(clibrary, vi, write_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    buffer = create_string_buffer(keyw.get("buffer_length", 1024))
    clibrary.viSPrintf(vi, buffer, write_format,
                                             *convert_argument_list(args))
    return buffer.raw


def sscanf(clibrary, vi, buffer, read_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    clibrary.viSScanf(vi, buffer, read_format, *convert_to_byref(argument_list, maximal_string_length))
    return construct_return_tuple(argument_list)

vprintf = printf
vqueryf = queryf
vscanf = scanf
vsprintf = sprintf
vsscanf = sscanf
