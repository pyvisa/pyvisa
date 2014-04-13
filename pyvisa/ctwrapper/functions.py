# -*- coding: utf-8 -*-
"""
    pyvisa.wrapper.functions
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Defines VPP 4.3.2 wrapping functions, adding signatures to the library.

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import collections

from ctypes import (byref, c_void_p, c_double, c_long, POINTER, CDLL, create_string_buffer)

from . import FUNCTYPE
from ..constants import *
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

__all__ = ["visa_functions", 'set_signatures', 'set_cdecl_signatures'] + visa_functions

VI_SPEC_VERSION = 0x00300000

#: Resource extended information
ResourceInfo = collections.namedtuple('ResourceInfo',
                                      'interface_type interface_board_number '
                                      'resource_class resource_name alias')


def set_user_handle_type(library, user_handle):
    """Set the type of the user handle to install and uninstall handler signature.

    :param library: the visa library wrapped by ctypes.
    :param user_handle: use None for a void_p
    """

    # Actually, it's not necessary to change ViHndlr *globally*.  However,
    # I don't want to break symmetry too much with all the other VPP43
    # routines.
    global ViHndlr

    if user_handle is None:
        user_handle_p = c_void_p
    else:
        user_handle_p = POINTER(type(user_handle))

    ViHndlr = FUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent, user_handle_p)
    library.viInstallHandler.argtypes = [ViSession, ViEventType, ViHndlr, user_handle_p]
    library.viUninstallHandler.argtypes = [ViSession, ViEventType, ViHndlr, user_handle_p]


def set_signatures(library, errcheck=None):
    """Set the signatures of most visa functions in the library.

    All instrumentation related functions are specified here.
    String related functions such as `viPrintf` require a cdecl
    calling convention even in windows and therefore are require
    a CDLL object. See `set_cdecl_signatures`.

    :param library: the visa library wrapped by ctypes.
    :type library: ctypes.WinDLL or ctypes.CDLL
    :param errcheck: error checking callable used for visa functions that return
                     ViStatus.
                     It should be take three areguments (result, func, arguments).
                     See errcheck in ctypes.
    """
    if not hasattr(library, '_functions'):
        library._functions = []

    def _applier(restype, errcheck_):
        def _internal(function_name, argtypes, maybe_missing=False):
            library._functions.append(function_name)
            set_signature(library, function_name, argtypes, restype, errcheck_, maybe_missing)
        return _internal

    # Visa functions with ViStatus return code
    apply = _applier(ViStatus, errcheck)
    apply("viAssertIntrSignal", [ViSession, ViInt16, ViUInt32])
    apply("viAssertTrigger", [ViSession, ViUInt16])
    apply("viAssertUtilSignal", [ViSession, ViUInt16])
    apply("viBufRead", [ViSession, ViPBuf, ViUInt32, ViPUInt32])
    apply("viBufWrite", [ViSession, ViBuf, ViUInt32, ViPUInt32])
    apply("viClear", [ViSession])
    apply("viClose", [ViObject])
    apply("viDisableEvent", [ViSession, ViEventType, ViUInt16])
    apply("viDiscardEvents", [ViSession, ViEventType, ViUInt16])
    apply("viEnableEvent", [ViSession, ViEventType, ViUInt16, ViEventFilter])
    apply("viFindNext", [ViSession, ViAChar])
    apply("viFindRsrc", [ViSession, ViString, ViPFindList, ViPUInt32, ViAChar])
    apply("viFlush", [ViSession, ViUInt16])
    apply("viGetAttribute", [ViObject, ViAttr, c_void_p])
    apply("viGpibCommand", [ViSession, ViBuf, ViUInt32, ViPUInt32])
    apply("viGpibControlATN", [ViSession, ViUInt16])
    apply("viGpibControlREN", [ViSession, ViUInt16])
    apply("viGpibPassControl", [ViSession, ViUInt16, ViUInt16])
    apply("viGpibSendIFC", [ViSession])

    apply("viIn8", [ViSession, ViUInt16, ViBusAddress, ViPUInt8])
    apply("viIn16", [ViSession, ViUInt16, ViBusAddress, ViPUInt16])
    apply("viIn32", [ViSession, ViUInt16, ViBusAddress, ViPUInt32])
    apply("viIn64", [ViSession, ViUInt16, ViBusAddress, ViPUInt64])

    apply("viIn8Ex", [ViSession, ViUInt16, ViBusAddress64, ViPUInt8])
    apply("viIn16Ex", [ViSession, ViUInt16, ViBusAddress64, ViPUInt16])
    apply("viIn32Ex", [ViSession, ViUInt16, ViBusAddress64, ViPUInt32])
    apply("viIn64Ex", [ViSession, ViUInt16, ViBusAddress64, ViPUInt64])

    apply("viInstallHandler", [ViSession, ViEventType, ViHndlr, ViAddr])
    apply("viLock", [ViSession, ViAccessMode, ViUInt32, ViKeyId, ViAChar])
    apply("viMapAddress", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViBoolean, ViAddr, ViPAddr])
    apply("viMapTrigger", [ViSession, ViInt16, ViInt16, ViUInt16])
    apply("viMemAlloc", [ViSession, ViBusSize, ViPBusAddress])
    apply("viMemFree", [ViSession, ViBusAddress])
    apply("viMove", [ViSession, ViUInt16, ViBusAddress, ViUInt16,
                     ViUInt16, ViBusAddress, ViUInt16, ViBusSize])
    apply("viMoveAsync", [ViSession, ViUInt16, ViBusAddress, ViUInt16,
                          ViUInt16, ViBusAddress, ViUInt16, ViBusSize,
                          ViPJobId])

    apply("viMoveIn8", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt8])
    apply("viMoveIn16", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt16])
    apply("viMoveIn32", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt32])
    apply("viMoveIn64", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt64])

    apply("viMoveIn8Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt8])
    apply("viMoveIn16Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt16])
    apply("viMoveIn32Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt32])
    apply("viMoveIn64Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt64])

    apply("viMoveOut8", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt8])
    apply("viMoveOut16", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt16])
    apply("viMoveOut32", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt32])
    apply("viMoveOut64", [ViSession, ViUInt16, ViBusAddress, ViBusSize, ViAUInt64])

    apply("viMoveOut8Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt8])
    apply("viMoveOut16Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt16])
    apply("viMoveOut32Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt32])
    apply("viMoveOut64Ex", [ViSession, ViUInt16, ViBusAddress64, ViBusSize, ViAUInt64])

    apply("viOpen", [ViSession, ViRsrc, ViAccessMode, ViUInt32, ViPSession], maybe_missing=False)

    apply("viOpenDefaultRM", [ViPSession])

    apply("viOut8", [ViSession, ViUInt16, ViBusAddress, ViUInt8])
    apply("viOut16", [ViSession, ViUInt16, ViBusAddress, ViUInt16])
    apply("viOut32", [ViSession, ViUInt16, ViBusAddress, ViUInt32])
    apply("viOut64", [ViSession, ViUInt16, ViBusAddress, ViUInt64])

    apply("viOut8Ex", [ViSession, ViUInt16, ViBusAddress64, ViUInt8])
    apply("viOut16Ex", [ViSession, ViUInt16, ViBusAddress64, ViUInt16])
    apply("viOut32Ex", [ViSession, ViUInt16, ViBusAddress64, ViUInt32])
    apply("viOut64Ex", [ViSession, ViUInt16, ViBusAddress64, ViUInt64])

    apply("viParseRsrc", [ViSession, ViRsrc, ViPUInt16, ViPUInt16])
    apply("viParseRsrcEx", [ViSession, ViRsrc, ViPUInt16, ViPUInt16, ViAChar, ViAChar, ViAChar])

    apply("viRead", [ViSession, ViPBuf, ViUInt32, ViPUInt32])
    apply("viReadAsync", [ViSession, ViPBuf, ViUInt32, ViPJobId])
    apply("viReadSTB", [ViSession, ViPUInt16])
    apply("viReadToFile", [ViSession, ViString, ViUInt32, ViPUInt32])

    apply("viSetAttribute", [ViObject, ViAttr, ViAttrState])
    apply("viSetBuf", [ViSession, ViUInt16, ViUInt32])

    apply("viStatusDesc", [ViObject, ViStatus, ViAChar])
    apply("viTerminate", [ViSession, ViUInt16, ViJobId])
    apply("viUninstallHandler", [ViSession, ViEventType, ViHndlr, ViAddr])
    apply("viUnlock", [ViSession])
    apply("viUnmapAddress", [ViSession])
    apply("viUnmapTrigger", [ViSession, ViInt16, ViInt16])
    apply("viUsbControlIn", [ViSession, ViInt16, ViInt16, ViUInt16,
                             ViUInt16, ViUInt16, ViPBuf, ViPUInt16])
    apply("viUsbControlOut", [ViSession, ViInt16, ViInt16, ViUInt16,
                              ViUInt16, ViUInt16, ViPBuf])

    # The following "V" routines are *not* implemented in PyVISA, and will
    # never be: viVPrintf, viVQueryf, viVScanf, viVSPrintf, viVSScanf

    apply("viVxiCommandQuery", [ViSession, ViUInt16, ViUInt32, ViPUInt32])
    apply("viWaitOnEvent", [ViSession, ViEventType, ViUInt32, ViPEventType, ViPEvent])
    apply("viWrite", [ViSession, ViBuf, ViUInt32, ViPUInt32])
    apply("viWriteAsync", [ViSession, ViBuf, ViUInt32, ViPJobId])
    apply("viWriteFromFile", [ViSession, ViString, ViUInt32, ViPUInt32])

    # Functions that return void.
    apply = _applier(None, None)
    apply("viPeek8", [ViSession, ViAddr, ViPUInt8])
    apply("viPeek16", [ViSession, ViAddr, ViPUInt16])
    apply("viPeek32", [ViSession, ViAddr, ViPUInt32])
    apply("viPeek64", [ViSession, ViAddr, ViPUInt64])

    apply("viPoke8", [ViSession, ViAddr, ViUInt8])
    apply("viPoke16", [ViSession, ViAddr, ViUInt16])
    apply("viPoke32", [ViSession, ViAddr, ViUInt32])
    apply("viPoke64", [ViSession, ViAddr, ViUInt64])


def set_signature(library, function_name, argtypes, restype, errcheck, maybe_missing=True):
    """Set the signature of single function in a library.

    :param library: ctypes wrapped library.
    :type library: ctypes.WinDLL or ctypes.CDLL
    :param function_name: name of the function as appears in the header file.
    :type function_name: str
    :param argtypes: a tuple of ctypes types to specify the argument types that the function accepts.
    :param restype: A ctypes type to specify the result type of the foreign function.
                    Use None for void, a function not returning anything.
    :param errcheck: a callabe
    :param maybe_missing: if False, an Attribute error will be raised if the
                           function_name is not found.

    :raises: AttributeError
    """

    try:
        func = getattr(library, function_name)
        func.argtypes = argtypes
        if restype is not None:
            func.restype = restype
        if errcheck is not None:
            func.errcheck = errcheck
    except AttributeError:
        if not maybe_missing:
            raise


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


def assert_interrupt_signal(library, session, mode, status_id):
    """Asserts the specified interrupt or signal.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: How to assert the interrupt. (Constants.ASSERT*)
    :param status_id: This is the status value to be presented during an interrupt acknowledge cycle.
    """
    library.viAssertIntrSignal(session, mode, status_id)


def assert_trigger(library, session, protocol):
    """Asserts software or hardware trigger.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param protocol: Trigger protocol to use during assertion. (Constants.PROT*)
    """
    library.viAssertTrigger(session, protocol)


def assert_utility_signal(library, session, line):
    """Asserts or deasserts the specified utility bus signal.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param line: specifies the utility bus signal to assert. (Constants.UTIL_ASSERT*)
    """
    library.viAssertUtilSignal(session, line)


def buffer_read(library, session, count):
    """Reads data from device or interface through the use of a formatted I/O read buffer.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: data read.
    :rtype: bytes
    """
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    library.viBufRead(session, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def buffer_write(library, session, data):
    """Writes data to a formatted I/O write buffer synchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :type data: bytes
    :return: number of written bytes.
    """

    return_count = ViUInt32()
    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    library.viBufWrite(session, data, len(data), byref(return_count))
    return return_count.value


def clear(library, session):
    """Clears a device.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    """
    library.viClear(session)


def close(library, session):
    """Closes the specified session, event, or find list.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session, event, or find list.
    """
    library.viClose(session)


def disable_event(library, session, event_type, mechanism):
    """Disables notification of the specified event type(s) via the specified mechanism(s).

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be disabled.
                      (Constants.QUEUE, .Handler, .SUSPEND_HNDLR, .ALL_MECH)
    """
    library.viDisableEvent(session, event_type, mechanism)


def discard_events(library, session, event_type, mechanism):
    """Discards event occurrences for specified event types and mechanisms in a session.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be disabled.
                      (Constants.QUEUE, .Handler, .SUSPEND_HNDLR, .ALL_MECH)
    """
    library.viDiscardEvents(session, event_type, mechanism)


def enable_event(library, session, event_type, mechanism, context=VI_NULL):
    """Enable event occurrences for specified event types and mechanisms in a session.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be disabled.
                      (Constants.QUEUE, .Handler, .SUSPEND_HNDLR)
    :param context:
    """
    context = VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    library.viEnableEvent(session, event_type, mechanism, context)


def find_next(library, find_list):
    """Returns the next resource from the list of resources found during a previous call to find_resources().

    :param library: the visa library wrapped by ctypes.
    :param find_list: Describes a find list. This parameter must be created by find_resources().
    :return: Returns a string identifying the location of a device.
    :rtype: unicode (Py2) or str (Py3)
    """
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    library.viFindNext(find_list, instrument_description)
    return buffer_to_text(instrument_description)


def find_resources(library, session, query):
    """Queries a VISA system to locate the resources associated with a specified interface.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session (unused, just to uniform signatures).
    :param query: A regular expression followed by an optional logical expression. Use '?*' for all.
    :return: find_list, return_counter, instrument_description
    :rtype: ViFindList, int, unicode (Py2) or str (Py3)
    """
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)

    # [ViSession, ViString, ViPFindList, ViPUInt32, ViAChar]
    # ViString converts from (str, unicode, bytes) to bytes
    library.viFindRsrc(session, query,
                       byref(find_list), byref(return_counter),
                       instrument_description)
    return find_list, return_counter.value, buffer_to_text(instrument_description)


def flush(library, session, mask):
    """Manually flushes the specified buffers associated with formatted I/O operations and/or serial communication.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mask: Specifies the action to be taken with flushing the buffer.
                 (Constants.READ*, .WRITE*, .IO*)
    """
    library.viFlush(session, mask)


def get_attribute(library, session, attribute):
    """Retrieves the state of an attribute.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session, event, or find list.
    :param attribute: Resource attribute for which the state query is made (see Attributes.*)
    :return: The state of the queried attribute for a specified resource.
    :rtype: unicode (Py2) or str (Py3), list or other type
    """

    # FixMe: How to deal with ViBuf?
    datatype = attributes[attribute]
    if datatype == ViString:
        attribute_state = create_string_buffer(256)
        library.viGetAttribute(session, attribute, attribute_state)
        return buffer_to_text(attribute_state)
    elif datatype == ViAUInt8:
        length = get_attribute(library, session, VI_ATTR_USB_RECV_INTR_SIZE)
        attribute_state = (ViUInt8 * length)()
        library.viGetAttribute(session, attribute, byref(attribute_state))
        return list(attribute_state)
    else:
        attribute_state = datatype()
        library.viGetAttribute(session, attribute, byref(attribute_state))
        return attribute_state.value


def gpib_command(library, session, data):
    """Write GPIB command bytes on the bus.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data tor write.
    :type data: bytes
    :return: Number of written bytes.
    """
    return_count = ViUInt32()

    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    library.viGpibCommand(session, data, len(data), byref(return_count))
    return return_count.value


def gpib_control_atn(library, session, mode):
    """Specifies the state of the ATN line and the local active controller state.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                 (Constants.GPIB_ATN*)
    """
    library.viGpibControlATN(session, mode)


def gpib_control_ren(library, session, mode):
    """Controls the state of the GPIB Remote Enable (REN) interface line, and optionally the remote/local
    state of the device.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies the state of the REN line and optionally the device remote/local state.
                 (Constants.GPIB_REN*)
    """
    library.viGpibControlREN(session, mode)


def gpib_pass_control(library, session, primary_address, secondary_address):
    """Tell the GPIB device at the specified address to become controller in charge (CIC).

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param primary_address: Primary address of the GPIB device to which you want to pass control.
    :param secondary_address: Secondary address of the targeted GPIB device.
                              If the targeted device does not have a secondary address,
                              this parameter should contain the value Constants.NO_SEC_ADDR.
    """
    library.viGpibPassControl(session, primary_address, secondary_address)


def gpib_send_ifc(library, session):
    """Pulse the interface clear line (IFC) for at least 100 microseconds.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    """
    library.viGpibSendIFC(session)


def read_memory(library, session, space, offset, width, extended=False):
    """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param width: Number of bits to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory.

    Corresponds to viIn* functions of the visa library.
    """
    if width == 8:
        return in_8(library, session, space, offset, extended)
    elif width == 16:
        return in_16(library, session, space, offset, extended)
    elif width == 32:
        return in_32(library, session, space, offset, extended)
    elif width == 64:
        return in_64(library, session, space, offset, extended)

    raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)


def in_8(library, session, space, offset, extended=False):
    """Reads in an 8-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory.
    """
    value_8 = ViUInt8()
    if extended:
        library.viIn8Ex(session, space, offset, byref(value_8))
    else:
        library.viIn8(session, space, offset, byref(value_8))
    return value_8.value


def in_16(library, session, space, offset, extended=False):
    """Reads in an 16-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory.
    """
    value_16 = ViUInt16()
    if extended:
        library.viIn16Ex(session, space, offset, byref(value_16))
    else:
        library.viIn16(session, space, offset, byref(value_16))
    return value_16.value


def in_32(library, session, space, offset, extended=False):
    """Reads in an 32-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory.
    """
    value_32 = ViUInt32()
    if extended:
        library.viIn32Ex(session, space, offset, byref(value_32))
    else:
        library.viIn32(session, space, offset, byref(value_32))
    return value_32.value


def in_64(library, session, space, offset, extended=False):
    """Reads in an 64-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory.
    """
    value_64 = ViUInt64()
    if extended:
        library.viIn64Ex(session, space, offset, byref(value_64))
    else:
        library.viIn64(session, space, offset, byref(value_64))
    return value_64.value


def install_handler(library, session, event_type, handler, user_handle):
    """Installs handlers for event callbacks.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
    :param user_handle: A value specified by an application that can be used for identifying handlers
                        uniquely for an event type.
    :returns: a handler descriptor which consists of three elements:
             - handler (a python callable)
             - user handle (a ctypes object)
             - ctypes handler (ctypes object wrapping handler)
    """
    if user_handle is None:
        converted_user_handle = None
    else:
        if isinstance(user_handle, int):
            converted_user_handle = c_long(user_handle)
        elif isinstance(user_handle, float):
            converted_user_handle = c_double(user_handle)
        elif isinstance(user_handle, str):
            converted_user_handle = create_string_buffer(user_handle)
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
            raise TypeError("Type not allowed as user handle: %s" % type(user_handle))

    set_user_handle_type(library, converted_user_handle)
    converted_handler = ViHndlr(handler)
    if user_handle is None:
        library.viInstallHandler(session, event_type, converted_handler, None)
    else:
        library.viInstallHandler(session, event_type, converted_handler,
                                 byref(converted_user_handle))

    return handler, converted_user_handle, converted_handler


def lock(library, session, lock_type, timeout, requested_key=None):
    """Establishes an access mode to the specified resources.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param lock_type: Specifies the type of lock requested, either Constants.EXCLUSIVE_LOCK or Constants.SHARED_LOCK.
    :param timeout: Absolute time period (in milliseconds) that a resource waits to get unlocked by the
                    locking session before returning an error.
    :param requested_key: This parameter is not used and should be set to VI_NULL when lockType is VI_EXCLUSIVE_LOCK.
    :return: access_key that can then be passed to other sessions to share the lock.
    """
    if lock_type == VI_EXCLUSIVE_LOCK:
        requested_key = None
        access_key = None
    else:
        access_key = create_string_buffer(256)
    library.viLock(session, lock_type, timeout, requested_key, access_key)
    return access_key


def map_address(library, session, map_space, map_base, map_size,
                access=VI_FALSE, suggested=VI_NULL):
    """Maps the specified memory space into the process's address space.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param map_space: Specifies the address space to map. (Constants.*SPACE*)
    :param map_base: Offset (in bytes) of the memory to be mapped.
    :param map_size: Amount of memory to map (in bytes).
    :param access:
    :param suggested: If not Constants.NULL (0), the operating system attempts to map the memory to the address
                      specified in suggested. There is no guarantee, however, that the memory will be mapped to
                      that address. This operation may map the memory into an address region different from
                      suggested.

    :return: Address in your process space where the memory was mapped.
    """
    access = VI_FALSE
    address = ViAddr()
    library.viMapAddress(session, map_space, map_base, map_size, access,
                         suggested, byref(address))
    return address


def map_trigger(library, session, trigger_source, trigger_destination, mode):
    """Map the specified trigger source line to the specified destination line.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param trigger_source: Source line from which to map. (Constants.TRIG*)
    :param trigger_destination: Destination line to which to map. (Constants.TRIG*)
    :param mode:
    """
    library.viMapTrigger(session, trigger_source, trigger_destination, mode)


def memory_allocation(library, session, size, extended=False):
    """Allocates memory from a resource's memory region.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param size: Specifies the size of the allocation.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Returns the offset of the allocated memory.
    """
    offset = ViBusAddress()
    if extended:
        library.viMemAllocEx(session, size, byref(offset))
    else:
        library.viMemAlloc(session, size, byref(offset))
    return offset


def memory_free(library, session, offset, extended=False):
    """Frees memory previously allocated using the memory_allocation() operation.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param offset: Offset of the memory to free.
    :param extended: Use 64 bits offset independent of the platform.
    """
    if extended:
        library.viMemFreeEx(session, offset)
    else:
        library.viMemFree(session, offset)


def move(library, session, source_space, source_offset, source_width, destination_space,
         destination_offset, destination_width, length):
    """Moves a block of data.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param source_space: Specifies the address space of the source.
    :param source_offset: Offset of the starting address or register from which to read.
    :param source_width: Specifies the data width of the source.
    :param destination_space: Specifies the address space of the destination.
    :param destination_offset: Offset of the starting address or register to which to write.
    :param destination_width: Specifies the data width of the destination.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    """
    library.viMove(session, source_space, source_offset, source_width,
                   destination_space, destination_offset,
                   destination_width, length)


def move_asynchronously(library, session, source_space, source_offset, source_width,
                        destination_space, destination_offset,
                        destination_width, length):
    """Moves a block of data asynchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param source_space: Specifies the address space of the source.
    :param source_offset: Offset of the starting address or register from which to read.
    :param source_width: Specifies the data width of the source.
    :param destination_space: Specifies the address space of the destination.
    :param destination_offset: Offset of the starting address or register to which to write.
    :param destination_width: Specifies the data width of the destination.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :return: Job identifier of this asynchronous move operation.
    """
    job_id = ViJobId()
    library.viMoveAsync(session, source_space, source_offset, source_width,
                        destination_space, destination_offset,
                        destination_width, length, byref(job_id))
    return job_id


def move_in(library, session, space, offset, length, width, extended=False):
    """Moves a block of data to local memory from the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param width: Number of bits to read per element.
    :param extended: Use 64 bits offset independent of the platform.
    """
    if width == 8:
        return move_in_8(library, session, space, offset, length, extended)
    elif width == 16:
        return move_in_16(library, session, space, offset, length, extended)
    elif width == 32:
        return move_in_32(library, session, space, offset, length, extended)
    elif width == 64:
        return move_in_64(library, session, space, offset, length, extended)

    raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)


def move_in_8(library, session, space, offset, length, extended=False):
    """Moves an 8-bit block of data from the specified address space and offset to local memory.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from bus.

    Corresponds to viMoveIn8 functions of the visa library.
    """
    buffer_8 = (ViUInt8 * length)()
    if extended:
        library.viMoveIn8Ex(session, space, offset, length, buffer_8)
    else:
        library.viMoveIn8(session, space, offset, length, buffer_8)
    return list(buffer_8)


def move_in_16(library, session, space, offset, length, extended=False):
    """Moves an 16-bit block of data from the specified address space and offset to local memory.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from bus.

    Corresponds to viMoveIn16 functions of the visa library.
    """
    buffer_16 = (ViUInt16 * length)()
    if extended:
        library.viMoveIn16Ex(session, space, offset, length, buffer_16)
    else:
        library.viMoveIn16(session, space, offset, length, buffer_16)

    return list(buffer_16)


def move_in_32(library, session, space, offset, length, extended=False):
    """Moves an 32-bit block of data from the specified address space and offset to local memory.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from bus.

    Corresponds to viMoveIn32 functions of the visa library.
    """
    buffer_32 = (ViUInt32 * length)()
    if extended:
        library.viMoveIn32Ex(session, space, offset, length, buffer_32)
    else:
        library.viMoveIn32(session, space, offset, length, buffer_32)

    return list(buffer_32)


def move_in_64(library, session, space, offset, length, extended=False):
    """Moves an 64-bit block of data from the specified address space and offset to local memory.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from bus.

    Corresponds to viMoveIn32 functions of the visa library.
    """
    buffer_64 = (ViUInt64 * length)()
    if extended:
        library.viMoveIn64Ex(session, space, offset, length, buffer_64)
    else:
        library.viMoveIn64(session, space, offset, length, buffer_64)

    return list(buffer_64)


def move_out(library, session, space, offset, length, data, width, extended=False):
    """Moves a block of data from local memory to the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param width: Number of bits to read per element.
    :param extended: Use 64 bits offset independent of the platform.
    """
    if width == 8:
        return move_out_8(library, session, space, offset, length, data, extended)
    elif width == 16:
        return move_out_16(library, session, space, offset, length, data, extended)
    elif width == 32:
        return move_out_32(library, session, space, offset, length, data, extended)
    elif width == 64:
        return move_out_64(library, session, space, offset, length, data, extended)

    raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)


def move_out_8(library, session, space, offset, length, data, extended=False):
    """Moves an 8-bit block of data from local memory to the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viMoveOut8 functions of the visa library.
    """
    converted_buffer = (ViUInt8 * length)(*tuple(data))
    if extended:
        library.viMoveOut8Ex(session, space, offset, length, converted_buffer)
    else:
        library.viMoveOut8(session, space, offset, length, converted_buffer)


def move_out_16(library, session, space, offset, length, data, extended=False):
    """Moves an 16-bit block of data from local memory to the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viMoveOut16 functions of the visa library.
    """
    converted_buffer = (ViUInt16 * length)(*tuple(data))
    if extended:
        library.viMoveOut16Ex(session, space, offset, length, converted_buffer)
    else:
        library.viMoveOut16(session, space, offset, length, converted_buffer)


def move_out_32(library, session, space, offset, length, data, extended=False):
    """Moves an 32-bit block of data from local memory to the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viMoveOut32 functions of the visa library.
    """
    converted_buffer = (ViUInt32 * length)(*tuple(data))
    if extended:
        library.viMoveOut32Ex(session, space, offset, length, converted_buffer)
    else:
        library.viMoveOut32(session, space, offset, length, converted_buffer)


def move_out_64(library, session, space, offset, length, data, extended=False):
    """Moves an 64-bit block of data from local memory to the specified address space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viMoveOut64 functions of the visa library.
    """
    converted_buffer = (ViUInt64 * length)(*tuple(data))
    if extended:
        library.viMoveOut64Ex(session, space, offset, length, converted_buffer)
    else:
        library.viMoveOut64(session, space, offset, length, converted_buffer)


def open(library, session, resource_name, access_mode=VI_NO_LOCK, open_timeout=VI_TMO_IMMEDIATE):
    """Opens a session to the specified resource.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be a session returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :param access_mode: Specifies the mode by which the resource is to be accessed. (Constants.NULL or Constants.*LOCK*)
    :param open_timeout: Specifies the maximum time period (in milliseconds) that this operation waits
                         before returning an error.
    :return: Unique logical identifier reference to a session.
    """
    out_session = ViSession()

    # [ViSession, ViRsrc, ViAccessMode, ViUInt32, ViPSession]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    library.viOpen(session, resource_name, access_mode, open_timeout, byref(out_session))
    return out_session.value


def open_default_resource_manager(library):
    """This function returns a session to the Default Resource Manager resource.

    :param library: the visa library wrapped by ctypes.
    :return: Unique logical identifier to a Default Resource Manager session.
    """
    session = ViSession()
    library.viOpenDefaultRM(byref(session))
    return session.value


def write_memory(library, session, space, offset, data, width, extended=False):
    """Write in an 8-bit, 16-bit, 32-bit, value to the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param width: Number of bits to read.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viOut* functions of the visa library.
    """
    if width == 8:
        return out_8(library, session, space, offset, data, extended)
    elif width == 16:
        return out_16(library, session, space, offset, data, extended)
    elif width == 32:
        return out_32(library, session, space, offset, data, extended)

    raise ValueError('%s is not a valid size. Valid values are 8, 16 or 32' % width)


def out_8(library, session, space, offset, data, extended=False):
    """Write in an 8-bit value from the specified memory space and offset.
    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viOut8 functions of the visa library.
    """
    if extended:
        library.viOut8Ex(session, space, offset, data)
    else:
        library.viOut8(session, space, offset, data)


def out_16(library, session, space, offset, data, extended=False):
    """Write in an 16-bit value from the specified memory space and offset.
    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viOut16 functions of the visa library.
    """
    if extended:
        library.viOut16Ex(session, space, offset, data, extended=False)
    else:
        library.viOut16(session, space, offset, data, extended=False)


def out_32(library, session, space, offset, data, extended=False):
    """Write in an 32-bit value from the specified memory space and offset.
    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viOut32 functions of the visa library.
    """
    if extended:
        library.viOut32Ex(session, space, offset, data)
    else:
        library.viOut32(session, space, offset, data)


def out_64(library, session, space, offset, data, extended=False):
    """Write in an 64-bit value from the specified memory space and offset.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.

    Corresponds to viOut64 functions of the visa library.
    """
    if extended:
        library.viOut64Ex(session, space, offset, data)
    else:
        library.viOut64(session, space, offset, data)


def parse_resource(library, session, resource_name):
    """Parse a resource string to get the interface information.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                    returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :return: Resource information with interface type and board number.
    :rtype: :class:ResourceInfo
    """
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()

    # [ViSession, ViRsrc, ViPUInt16, ViPUInt16]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    library.viParseRsrc(session, resource_name, byref(interface_type),
                        byref(interface_board_number))
    return ResourceInfo(interface_type.value, interface_board_number.value,
                        None, None, None)


def parse_resource_extended(library, session, resource_name):
    """Parse a resource string to get extended interface information.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                    returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :return: Resource information.
    :rtype: :class:ResourceInfo
    """
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    resource_class = create_string_buffer(VI_FIND_BUFLEN)
    unaliased_expanded_resource_name = create_string_buffer(VI_FIND_BUFLEN)
    alias_if_exists = create_string_buffer(VI_FIND_BUFLEN)

    # [ViSession, ViRsrc, ViPUInt16, ViPUInt16, ViAChar, ViAChar, ViAChar]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    library.viParseRsrcEx(session, resource_name, byref(interface_type),
                          byref(interface_board_number), resource_class,
                          unaliased_expanded_resource_name,
                          alias_if_exists)

    res = [buffer_to_text(val)
           for val in (resource_class,
                       unaliased_expanded_resource_name,
                       alias_if_exists)]

    if res[-1] == '':
        res[-1] = None

    return ResourceInfo(interface_type.value, interface_board_number.value, *res)


def peek(library, session, address, width):
    """Read an 8, 16 or 32-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param width: Number of bits to read.
    :return: Data read from bus.
    :rtype: bytes
    """

    if width == 8:
        return peek_8(library, session, address)
    elif width == 16:
        return peek_16(library, session, address)
    elif width == 32:
        return peek_32(library, session, address)
    elif width == 64:
        return peek_64(library, session, address)

    raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)


def peek_8(library, session, address):
    """Read an 8-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus.
    :rtype: bytes
    """
    value_8 = ViUInt8()
    library.viPeek8(session, address, byref(value_8))
    return value_8.value


def peek_16(library, session, address):
    """Read an 16-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus.
    :rtype: bytes
    """
    value_16 = ViUInt16()
    library.viPeek16(session, address, byref(value_16))
    return value_16.value


def peek_32(library, session, address):
    """Read an 32-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus.
    :rtype: bytes
    """
    value_32 = ViUInt32()
    library.viPeek32(session, address, byref(value_32))
    return value_32.value


def peek_64(library, session, address):
    """Read an 64-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus.
    :rtype: bytes
    """
    value_64 = ViUInt64()
    library.viPeek64(session, address, byref(value_64))
    return value_64.value


def poke(library, session, address, width, data):
    """Writes an 8, 16 or 32-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param width: Number of bits to read.
    :param data: Data to be written to the bus.
    """

    if width == 8:
        return poke_8(library, session, address, data)
    elif width == 16:
        return poke_16(library, session, address, data)
    elif width == 32:
        return poke_32(library, session, address, data)

    raise ValueError('%s is not a valid size. Valid values are 8, 16 or 32' % width)


def poke_8(library, session, address, data):
    """Write an 8-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: Data read from bus.
    """
    library.viPoke8(session, address, data)


def poke_16(library, session, address, data):
    """Write an 16-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: Data read from bus.
    """
    library.viPoke16(session, address, data)


def poke_32(library, session, address, data):
    """Write an 32-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: Data read from bus.
    """
    library.viPoke32(session, address, data)


def poke_64(library, session, address, data):
    """Write an 64-bit value from the specified address.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: Data read from bus.
    """
    library.viPoke64(session, address, data)


def read(library, session, count):
    """Reads data from device or interface synchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: data read.
    :rtype: bytes
    """
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    library.viRead(session, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def read_asynchronously(library, session, count):
    """Reads data from device or interface asynchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: (ctypes buffer with result, jobid)
    """
    buffer = create_string_buffer(count)
    job_id = ViJobId()
    library.viReadAsync(session, buffer, count, byref(job_id))
    return buffer, job_id


def read_stb(library, session):
    """Reads a status byte of the service request.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: Service request status byte.
    """
    status = ViUInt16()
    library.viReadSTB(session, byref(status))
    return status.value


def read_to_file(library, session, filename, count):
    """Read data synchronously, and store the transferred data in a file.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param filename: Name of file to which data will be written.
    :param count: Number of bytes to be read.
    :return: Number of bytes actually transferred.
    """
    return_count = ViUInt32()
    library.viReadToFile(session, filename, count, return_count)
    return return_count


def set_attribute(library, session, attribute, attribute_state):
    """Sets the state of an attribute.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param attribute: Attribute for which the state is to be modified. (Attributes.*)
    :param attribute_state: The state of the attribute to be set for the specified object.
    """
    library.viSetAttribute(session, attribute, attribute_state)


def set_buffer(library, session, mask, size):
    """Sets the size for the formatted I/O and/or low-level I/O communication buffer(s).

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mask: Specifies the type of buffer. (Constants.READ_BUF, .WRITE_BUF, .IO_IN_BUF, .IO_OUT_BUF)
    :param size: The size to be set for the specified buffer(s).
    """
    library.viSetBuf(session, mask, size)


def status_description(library, session, status):
    """Returns a user-readable description of the status code passed to the operation.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param status: Status code to interpret.
    :return: The user-readable string interpretation of the status code passed to the operation.
    :rtype: unicode (Py2) or str (Py3)
    """
    description = create_string_buffer(256)
    library.viStatusDesc(session, status, description)
    return buffer_to_text(description)


def terminate(library, session, degree, job_id):
    """Requests a VISA session to terminate normal execution of an operation.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param degree: Constants.NULL
    :param job_id: Specifies an operation identifier.
    """
    library.viTerminate(session, degree, job_id)


def uninstall_handler(library, session, event_type, handler, user_handle=None):
    """Uninstalls handlers for events.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
    :param user_handle: A value specified by an application that can be used for identifying handlers
                        uniquely in a session for an event.
    """
    library.viUninstallHandler(session, event_type, handler, byref(user_handle))


def unlock(library, session):
    """Relinquishes a lock for the specified resource.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    """
    library.viUnlock(session)


def unmap_address(library, session):
    """Unmaps memory space previously mapped by map_address().

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    """
    library.viUnmapAddress(session)


def unmap_trigger(library, session, trigger_source, trigger_destination):
    """Undo a previous map from the specified trigger source line to the specified destination line.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param trigger_source: Source line used in previous map. (Constants.TRIG*)
    :param trigger_destination: Destination line used in previous map. (Constants.TRIG*)
    """
    library.viUnmapTrigger(session, trigger_source, trigger_destination)


def usb_control_in(library, session, request_type_bitmap_field, request_id, request_value,
                   index, length=0):
    """Performs a USB control pipe transfer from the device.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
    :param request_id: bRequest parameter of the setup stage of a USB control transfer.
    :param request_value: wValue parameter of the setup stage of a USB control transfer.
    :param index: wIndex parameter of the setup stage of a USB control transfer.
                  This is usually the index of the interface or endpoint.
    :param length: wLength parameter of the setup stage of a USB control transfer.
                   This value also specifies the size of the data buffer to receive the data from the
                   optional data stage of the control transfer.
    :return: The data buffer that receives the data from the optional data stage of the control transfer.
    :rtype: bytes
    """
    buffer = create_string_buffer(length)
    return_count = ViUInt16()
    library.viUsbControlIn(session, request_type_bitmap_field, request_id,
                           request_value, index, length, buffer,
                           byref(return_count))
    return buffer.raw[:return_count.value]


def usb_control_out(library, session, request_type_bitmap_field, request_id, request_value,
                    index, data=""):
    """Performs a USB control pipe transfer to the device.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
    :param request_id: bRequest parameter of the setup stage of a USB control transfer.
    :param request_value: wValue parameter of the setup stage of a USB control transfer.
    :param index: wIndex parameter of the setup stage of a USB control transfer.
                  This is usually the index of the interface or endpoint.
    :param data: The data buffer that sends the data in the optional data stage of the control transfer.
    """
    length = len(data)
    library.viUsbControlOut(session, request_type_bitmap_field, request_id,
                            request_value, index, length, data)


def vxi_command_query(library, session, mode, command):
    """Sends the device a miscellaneous command or query and/or retrieves the response to a previous query.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies whether to issue a command and/or retrieve a response. (Constants.VXI_CMD*, .VXI_RESP*)
    :param command: The miscellaneous command to send.
    :return: The response retrieved from the device.
    """
    response = ViUInt32()
    library.viVxiCommandQuery(session, mode, command, byref(response))
    return response.value


def wait_on_event(library, session, in_event_type, timeout):
    """Waits for an occurrence of the specified event for a given session.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param in_event_type: Logical identifier of the event(s) to wait for.
    :param timeout: Absolute time period in time units that the resource shall wait for a specified event to
                    occur before returning the time elapsed error. The time unit is in milliseconds.
    :return: Logical identifier of the event actually received, A handle specifying the unique occurrence of an event.
    """
    out_event_type = ViEventType()
    out_context = ViEvent()
    library.viWaitOnEvent(session, in_event_type, timeout,
                          byref(out_event_type), byref(out_context))
    return out_event_type.value, out_context


def write(library, session, data):
    """Writes data to device or interface synchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :type data: str
    :return: Number of bytes actually transferred.
    """
    return_count = ViUInt32()
    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    library.viWrite(session, data, len(data), byref(return_count))
    return return_count.value


def write_asynchronously(library, session, data):
    """Writes data to device or interface asynchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :return: Job ID of this asynchronous write operation.
    """
    job_id = ViJobId()
    # [ViSession, ViBuf, ViUInt32, ViPJobId]
    library.viWriteAsync(session, data, len(data), byref(job_id))
    return job_id


def write_from_file(library, session, filename, count):
    """Take data from a file and write it out synchronously.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param filename: Name of file from which data will be read.
    :param count: Number of bytes to be written.
    :return: Number of bytes actually transferred.
    """
    return_count = ViUInt32()
    library.viWriteFromFile(session, filename, count, return_count)
    return return_count


# To be deprecated in PyVISA 1.6
# All these functions are easy to replace by Python equivalents.

def set_cdecl_signatures(clibrary, errcheck=None):
    """Set the signatures of visa functions requiring a cdecl calling convention.

    .. note: This function and the support for string formatting operations in the
             VISA library will be removed in PyVISA 1.6. as these functions can be
             easily replaced by Python equivalents.

    :param clibrary: the visa library wrapped by ctypes.
    :type clibrary: ctypes.CDLL
    :param errcheck: error checking callable used for visa functions that return
                     ViStatus.
                     It should be take three areguments (result, func, arguments).
                     See errcheck in ctypes.
    """
    assert isinstance(clibrary, CDLL)

    if not hasattr(clibrary, '_functions'):
        clibrary._functions = []

    def _applier(restype, errcheck_):
        def _internal(function_name, argtypes, maybe_missing=False):
            clibrary._functions.append(function_name)
            set_signature(clibrary, function_name, argtypes, restype, errcheck_, maybe_missing)
        return _internal

    apply = _applier(ViStatus, errcheck)

    apply("viSPrintf", [ViSession, ViPBuf, ViString])
    apply("viSScanf", [ViSession, ViBuf, ViString])
    apply("viScanf", [ViSession, ViString])
    apply("viPrintf", [ViSession, ViString])
    apply("viQueryf", [ViSession, ViString, ViString])


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
            raise TypeError("Invalid type in scanf/printf: %s" % type(argument))
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
            raise TypeError("Invalid type in scanf: %s" % type(byvalue_arguments[i]))
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


def printf(clibrary, session, write_format, *args):
    assert isinstance(clibrary, _ctypes.CDLL)
    clibrary.viPrintf(session, write_format, *convert_argument_list(args))


def queryf(clibrary, session, write_format, read_format, write_args, *read_args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(read_args))
    if write_args is None: write_args = ()
    clibrary.viQueryf(session, write_format, read_format,
                      *(convert_argument_list(write_args) + convert_to_byref(argument_list,  maximal_string_length)))
    return construct_return_tuple(argument_list)

# FixMe: I have to test whether the results are really written to
# "argument_list" rather than only to a local copy within "viScanf".

def scanf(clibrary, session, read_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    clibrary.viScanf(session, read_format, *convert_to_byref(argument_list, maximal_string_length))
    return construct_return_tuple(argument_list)


def sprintf(clibrary, session, write_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    buffer = create_string_buffer(keyw.get("buffer_length", 1024))
    clibrary.viSPrintf(session, buffer, write_format,
                                             *convert_argument_list(args))
    return buffer.raw


def sscanf(clibrary, session, buffer, read_format, *args, **keyw):
    assert isinstance(clibrary, _ctypes.CDLL)
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    clibrary.viSScanf(session, buffer, read_format, *convert_to_byref(argument_list, maximal_string_length))
    return construct_return_tuple(argument_list)

vprintf = printf
vqueryf = queryf
vscanf = scanf
vsprintf = sprintf
vsscanf = sscanf

#: A deprecated alias.  See VPP-4.3, rule 4.3.5 and observation 4.3.2.
get_default_resource_manager = open_default_resource_manager
