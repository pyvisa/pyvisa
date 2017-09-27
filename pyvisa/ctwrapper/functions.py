# -*- coding: utf-8 -*-
"""
    pyvisa.ctwrapper.functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines VPP 4.3.2 wrapping functions using ctypes, adding signatures to the library.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import warnings

from pyvisa.highlevel import ResourceInfo
from pyvisa import attributes, constants

from . import types
from .types import *
from ctypes import byref, c_void_p, c_double, c_long, POINTER, create_string_buffer

visa_functions = [
    "assert_interrupt_signal", "assert_trigger", "assert_utility_signal",
    "buffer_read", "buffer_write", "clear", "close", "disable_event",
    "discard_events", "enable_event", "find_next", "find_resources", "flush",
    "get_attribute", "gpib_command",
    "gpib_control_atn", "gpib_control_ren", "gpib_pass_control",
    "gpib_send_ifc", "in_16", "in_32", "in_8", "install_handler", "lock",
    "map_address", "map_trigger", "memory_allocation", "memory_free", "move",
    "move_asynchronously", "move_in_16", "move_in_32", "move_in_8",
    "move_out_16", "move_out_32", "move_out_8", "open",
    "open_default_resource_manager", "out_16", "out_32", "out_8",
    "parse_resource", "parse_resource_extended", "peek_16", "peek_32",
    "peek_8", "poke_16", "poke_32", "poke_8", "read",
    "read_asynchronously", "read_to_file", "read_stb",
    "set_attribute", "set_buffer", "status_description",
    "terminate", "uninstall_handler", "unlock", "unmap_address",
    "unmap_trigger", "usb_control_in", "usb_control_out",
    "vxi_command_query", "wait_on_event",
    "write", "write_asynchronously", "write_from_file",
    "in_64", "move_in_64", "out_64", "move_out_64", "poke_64",
    "peek_64"]

__all__ = ["visa_functions", 'set_signatures'] + visa_functions

VI_SPEC_VERSION = 0x00300000


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

    :param library: the visa library wrapped by ctypes.
    :type library: ctypes.WinDLL or ctypes.CDLL
    :param errcheck: error checking callable used for visa functions that return
                     ViStatus.
                     It should be take three areguments (result, func, arguments).
                     See errcheck in ctypes.
    """

    # Somehow hasattr(library, '_functions') segfaults in cygwin (See #131)
    if '_functions' not in dir(library):
        library._functions = []
        library._functions_failed = []

    def _applier(restype, errcheck_):
        def _internal(function_name, argtypes, required=False):
            try:
                set_signature(library, function_name, argtypes, restype, errcheck_)
                # noinspection PyProtectedMember
                library._functions.append(function_name)
            except AttributeError:
                library._functions_failed.append(function_name)
                if required:
                    raise
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

    apply("viOpen", [ViSession, ViRsrc, ViAccessMode, ViUInt32, ViPSession], required=True)

    apply("viOpenDefaultRM", [ViPSession], required=True)

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


def set_signature(library, function_name, argtypes, restype, errcheck):
    """Set the signature of single function in a library.

    :param library: ctypes wrapped library.
    :type library: ctypes.WinDLL or ctypes.CDLL
    :param function_name: name of the function as appears in the header file.
    :type function_name: str
    :param argtypes: a tuple of ctypes types to specify the argument types that the function accepts.
    :param restype: A ctypes type to specify the result type of the foreign function.
                    Use None for void, a function not returning anything.
    :param errcheck: a callabe

    :raises: AttributeError
    """

    func = getattr(library, function_name)
    func.argtypes = argtypes
    if restype is not None:
        func.restype = restype
    if errcheck is not None:
        func.errcheck = errcheck


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

    Corresponds to viAssertIntrSignal function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: How to assert the interrupt. (Constants.ASSERT*)
    :param status_id: This is the status value to be presented during an interrupt acknowledge cycle.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viAssertIntrSignal(session, mode, status_id)


def assert_trigger(library, session, protocol):
    """Asserts software or hardware trigger.

    Corresponds to viAssertTrigger function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param protocol: Trigger protocol to use during assertion. (Constants.PROT*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viAssertTrigger(session, protocol)


def assert_utility_signal(library, session, line):
    """Asserts or deasserts the specified utility bus signal.

    Corresponds to viAssertUtilSignal function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param line: specifies the utility bus signal to assert. (Constants.UTIL_ASSERT*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viAssertUtilSignal(session, line)


def buffer_read(library, session, count):
    """Reads data from device or interface through the use of a formatted I/O read buffer.

    Corresponds to viBufRead function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: data read, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    ret = library.viBufRead(session, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value], ret


def buffer_write(library, session, data):
    """Writes data to a formatted I/O write buffer synchronously.

    Corresponds to viBufWrite function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :type data: bytes
    :return: number of written bytes, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """

    return_count = ViUInt32()
    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    ret = library.viBufWrite(session, data, len(data), byref(return_count))
    return return_count.value, ret


def clear(library, session):
    """Clears a device.

    Corresponds to viClear function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viClear(session)


def close(library, session):
    """Closes the specified session, event, or find list.

    Corresponds to viClose function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session, event, or find list.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viClose(session)


def disable_event(library, session, event_type, mechanism):
    """Disables notification of the specified event type(s) via the specified mechanism(s).

    Corresponds to viDisableEvent function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be disabled.
                      (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viDisableEvent(session, event_type, mechanism)


def discard_events(library, session, event_type, mechanism):
    """Discards event occurrences for specified event types and mechanisms in a session.

    Corresponds to viDiscardEvents function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be dicarded.
                      (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viDiscardEvents(session, event_type, mechanism)


def enable_event(library, session, event_type, mechanism, context=None):
    """Enable event occurrences for specified event types and mechanisms in a session.

    Corresponds to viEnableEvent function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param mechanism: Specifies event handling mechanisms to be enabled.
                      (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR)
    :param context:
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if context is None:
        context = constants.VI_NULL
    elif context != constants.VI_NULL:
        warnings.warn('In enable_event, context will be set VI_NULL.')
        context = constants.VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    return library.viEnableEvent(session, event_type, mechanism, context)


def find_next(library, find_list):
    """Returns the next resource from the list of resources found during a previous call to find_resources().

    Corresponds to viFindNext function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param find_list: Describes a find list. This parameter must be created by find_resources().
    :return: Returns a string identifying the location of a device, return value of the library call.
    :rtype: unicode (Py2) or str (Py3), :class:`pyvisa.constants.StatusCode`
    """
    instrument_description = create_string_buffer(constants.VI_FIND_BUFLEN)
    ret = library.viFindNext(find_list, instrument_description)
    return buffer_to_text(instrument_description), ret


def find_resources(library, session, query):
    """Queries a VISA system to locate the resources associated with a specified interface.

    Corresponds to viFindRsrc function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session (unused, just to uniform signatures).
    :param query: A regular expression followed by an optional logical expression. Use '?*' for all.
    :return: find_list, return_counter, instrument_description, return value of the library call.
    :rtype: ViFindList, int, unicode (Py2) or str (Py3), :class:`pyvisa.constants.StatusCode`
    """
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(constants.VI_FIND_BUFLEN)

    # [ViSession, ViString, ViPFindList, ViPUInt32, ViAChar]
    # ViString converts from (str, unicode, bytes) to bytes
    ret = library.viFindRsrc(session, query,
                             byref(find_list), byref(return_counter),
                             instrument_description)
    return find_list, return_counter.value, buffer_to_text(instrument_description), ret


def flush(library, session, mask):
    """Manually flushes the specified buffers associated with formatted I/O operations and/or serial communication.

    Corresponds to viFlush function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mask: Specifies the action to be taken with flushing the buffer.
                 (Constants.READ*, .WRITE*, .IO*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viFlush(session, mask)


def get_attribute(library, session, attribute):
    """Retrieves the state of an attribute.

    Corresponds to viGetAttribute function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session, event, or find list.
    :param attribute: Resource attribute for which the state query is made (see Attributes.*)
    :return: The state of the queried attribute for a specified resource, return value of the library call.
    :rtype: unicode (Py2) or str (Py3), list or other type, :class:`pyvisa.constants.StatusCode`
    """

    # FixMe: How to deal with ViBuf?
    attr = attributes.AttributesByID[attribute]
    datatype = getattr(types, attr.visa_type)
    if datatype == ViString:
        attribute_state = create_string_buffer(256)
        ret = library.viGetAttribute(session, attribute, attribute_state)
        return buffer_to_text(attribute_state), ret
    elif datatype == ViAUInt8:
        length = get_attribute(library, session, constants.VI_ATTR_USB_RECV_INTR_SIZE)
        attribute_state = (ViUInt8 * length)()
        ret = library.viGetAttribute(session, attribute, byref(attribute_state))
        return list(attribute_state), ret
    else:
        attribute_state = datatype()
        ret = library.viGetAttribute(session, attribute, byref(attribute_state))
        return attribute_state.value, ret


def gpib_command(library, session, data):
    """Write GPIB command bytes on the bus.

    Corresponds to viGpibCommand function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data tor write.
    :type data: bytes
    :return: Number of written bytes, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    return_count = ViUInt32()

    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    ret = library.viGpibCommand(session, data, len(data), byref(return_count))
    return return_count.value, ret


def gpib_control_atn(library, session, mode):
    """Specifies the state of the ATN line and the local active controller state.

    Corresponds to viGpibControlATN function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                 (Constants.GPIB_ATN*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viGpibControlATN(session, mode)


def gpib_control_ren(library, session, mode):
    """Controls the state of the GPIB Remote Enable (REN) interface line, and optionally the remote/local
    state of the device.

    Corresponds to viGpibControlREN function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies the state of the REN line and optionally the device remote/local state.
                 (Constants.GPIB_REN*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viGpibControlREN(session, mode)


def gpib_pass_control(library, session, primary_address, secondary_address):
    """Tell the GPIB device at the specified address to become controller in charge (CIC).

    Corresponds to viGpibPassControl function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param primary_address: Primary address of the GPIB device to which you want to pass control.
    :param secondary_address: Secondary address of the targeted GPIB device.
                              If the targeted device does not have a secondary address,
                              this parameter should contain the value Constants.NO_SEC_ADDR.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viGpibPassControl(session, primary_address, secondary_address)


def gpib_send_ifc(library, session):
    """Pulse the interface clear line (IFC) for at least 100 microseconds.

    Corresponds to viGpibSendIFC function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viGpibSendIFC(session)


def read_memory(library, session, space, offset, width, extended=False):
    """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

    Corresponds to viIn* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param width: Number of bits to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viIn8* function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    value_8 = ViUInt8()
    if extended:
        ret = library.viIn8Ex(session, space, offset, byref(value_8))
    else:
        ret = library.viIn8(session, space, offset, byref(value_8))
    return value_8.value, ret


def in_16(library, session, space, offset, extended=False):
    """Reads in an 16-bit value from the specified memory space and offset.

    Corresponds to viIn16* function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    value_16 = ViUInt16()
    if extended:
        ret = library.viIn16Ex(session, space, offset, byref(value_16))
    else:
        ret = library.viIn16(session, space, offset, byref(value_16))
    return value_16.value, ret


def in_32(library, session, space, offset, extended=False):
    """Reads in an 32-bit value from the specified memory space and offset.

    Corresponds to viIn32* function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    value_32 = ViUInt32()
    if extended:
        ret = library.viIn32Ex(session, space, offset, byref(value_32))
    else:
        ret = library.viIn32(session, space, offset, byref(value_32))
    return value_32.value, ret


def in_64(library, session, space, offset, extended=False):
    """Reads in an 64-bit value from the specified memory space and offset.

    Corresponds to viIn64* function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from memory, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    value_64 = ViUInt64()
    if extended:
        ret = library.viIn64Ex(session, space, offset, byref(value_64))
    else:
        ret = library.viIn64(session, space, offset, byref(value_64))
    return value_64.value, ret


def install_handler(library, session, event_type, handler, user_handle):
    """Installs handlers for event callbacks.

    Corresponds to viInstallHandler function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
    :param user_handle: A value specified by an application that can be used for identifying handlers
                        uniquely for an event type. Can be a regular python object (int, float, str, list
                        of floats or ints) or a ctypes object.
    :returns: a handler descriptor which consists of three elements:
             - handler (a python callable)
             - user handle (a ctypes object)
             - ctypes handler (ctypes object wrapping handler)
             and return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
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
            try:
                # check if it is already a ctypes
                byref(user_handle)
                converted_user_handle = user_handle
            except TypeError:
                raise TypeError("Type not allowed as user handle: %s" % type(user_handle))

    set_user_handle_type(library, converted_user_handle)
    converted_handler = ViHndlr(handler)
    if user_handle is None:
        ret = library.viInstallHandler(session, event_type, converted_handler, None)
    else:
        ret = library.viInstallHandler(session, event_type, converted_handler,
                                       byref(converted_user_handle))

    return handler, converted_user_handle, converted_handler, ret


def lock(library, session, lock_type, timeout, requested_key=None):
    """Establishes an access mode to the specified resources.

    Corresponds to viLock function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param lock_type: Specifies the type of lock requested, either constants.AccessModes.exclusive_lock
                      or constants.AccessModes.shared_lock.
    :param timeout: Absolute time period (in milliseconds) that a resource waits to get unlocked by the
                    locking session before returning an error.
    :param requested_key: This parameter is not used and should be set to VI_NULL when lockType is VI_EXCLUSIVE_LOCK.
    :return: access_key that can then be passed to other sessions to share the lock, return value of the library call.
    :rtype: str, :class:`pyvisa.constants.StatusCode`
    """
    if lock_type == constants.AccessModes.exclusive_lock:
        requested_key = None
        access_key = None
    else:
        access_key = create_string_buffer(256)
    ret = library.viLock(session, lock_type, timeout, requested_key, access_key)
    if access_key is None:
        return None, ret
    else:
        return access_key.value, ret


def map_address(library, session, map_space, map_base, map_size,
                access=False, suggested=None):
    """Maps the specified memory space into the process's address space.

    Corresponds to viMapAddress function of the VISA library.

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

    :return: address in your process space where the memory was mapped, return value of the library call.
    :rtype: address, :class:`pyvisa.constants.StatusCode`
    """
    if access is False:
        access = constants.VI_FALSE
    elif access != constants.VI_FALSE:
        warnings.warn('In enable_event, context will be set VI_NULL.')
        access = constants.VI_FALSE
    address = ViAddr()
    ret = library.viMapAddress(session, map_space, map_base, map_size, access,
                               suggested, byref(address))
    return address, ret


def map_trigger(library, session, trigger_source, trigger_destination, mode):
    """Map the specified trigger source line to the specified destination line.

    Corresponds to viMapTrigger function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param trigger_source: Source line from which to map. (Constants.TRIG*)
    :param trigger_destination: Destination line to which to map. (Constants.TRIG*)
    :param mode:
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viMapTrigger(session, trigger_source, trigger_destination, mode)


def memory_allocation(library, session, size, extended=False):
    """Allocates memory from a resource's memory region.

    Corresponds to viMemAlloc* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param size: Specifies the size of the allocation.
    :param extended: Use 64 bits offset independent of the platform.
    :return: offset of the allocated memory, return value of the library call.
    :rtype: offset, :class:`pyvisa.constants.StatusCode`
    """
    offset = ViBusAddress()
    if extended:
        ret = library.viMemAllocEx(session, size, byref(offset))
    else:
        ret = library.viMemAlloc(session, size, byref(offset))
    return offset, ret


def memory_free(library, session, offset, extended=False):
    """Frees memory previously allocated using the memory_allocation() operation.

    Corresponds to viMemFree* function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param offset: Offset of the memory to free.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if extended:
        return library.viMemFreeEx(session, offset)
    else:
        return library.viMemFree(session, offset)


def move(library, session, source_space, source_offset, source_width, destination_space,
         destination_offset, destination_width, length):
    """Moves a block of data.

    Corresponds to viMove function of the VISA library.

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
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viMove(session, source_space, source_offset, source_width,
                          destination_space, destination_offset,
                          destination_width, length)


def move_asynchronously(library, session, source_space, source_offset, source_width,
                        destination_space, destination_offset,
                        destination_width, length):
    """Moves a block of data asynchronously.

    Corresponds to viMoveAsync function of the VISA library.

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
    :return: Job identifier of this asynchronous move operation, return value of the library call.
    :rtype: jobid, :class:`pyvisa.constants.StatusCode`
    """
    job_id = ViJobId()
    ret = library.viMoveAsync(session, source_space, source_offset, source_width,
                              destination_space, destination_offset,
                              destination_width, length, byref(job_id))
    return job_id, ret


def move_in(library, session, space, offset, length, width, extended=False):
    """Moves a block of data to local memory from the specified address space and offset.

    Corresponds to viMoveIn* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param width: Number of bits to read per element.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from the bus, return value of the library call.
    :rtype: list, :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viMoveIn8* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from the bus, return value of the library call.
    :rtype: list, :class:`pyvisa.constants.StatusCode`
    """
    buffer_8 = (ViUInt8 * length)()
    if extended:
        ret = library.viMoveIn8Ex(session, space, offset, length, buffer_8)
    else:
        ret = library.viMoveIn8(session, space, offset, length, buffer_8)
    return list(buffer_8), ret


def move_in_16(library, session, space, offset, length, extended=False):
    """Moves an 16-bit block of data from the specified address space and offset to local memory.

    Corresponds to viMoveIn16* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from the bus, return value of the library call.
    :rtype: list, :class:`pyvisa.constants.StatusCode`
    """
    buffer_16 = (ViUInt16 * length)()
    if extended:
        ret = library.viMoveIn16Ex(session, space, offset, length, buffer_16)
    else:
        ret = library.viMoveIn16(session, space, offset, length, buffer_16)

    return list(buffer_16), ret


def move_in_32(library, session, space, offset, length, extended=False):
    """Moves an 32-bit block of data from the specified address space and offset to local memory.

    Corresponds to viMoveIn32* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from the bus, return value of the library call.
    :rtype: list, :class:`pyvisa.constants.StatusCode`
    """
    buffer_32 = (ViUInt32 * length)()
    if extended:
        ret = library.viMoveIn32Ex(session, space, offset, length, buffer_32)
    else:
        ret = library.viMoveIn32(session, space, offset, length, buffer_32)

    return list(buffer_32), ret


def move_in_64(library, session, space, offset, length, extended=False):
    """Moves an 64-bit block of data from the specified address space and offset to local memory.

    Corresponds to viMoveIn64* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param extended: Use 64 bits offset independent of the platform.
    :return: Data read from the bus, return value of the library call.
    :rtype: list, :class:`pyvisa.constants.StatusCode`
    """
    buffer_64 = (ViUInt64 * length)()
    if extended:
        ret = library.viMoveIn64Ex(session, space, offset, length, buffer_64)
    else:
        ret = library.viMoveIn64(session, space, offset, length, buffer_64)

    return list(buffer_64), ret


def move_out(library, session, space, offset, length, data, width, extended=False):
    """Moves a block of data from local memory to the specified address space and offset.

    Corresponds to viMoveOut* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param width: Number of bits to read per element.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viMoveOut8* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`

    Corresponds to viMoveOut8 function of the VISA library.
    """
    converted_buffer = (ViUInt8 * length)(*tuple(data))
    if extended:
        return library.viMoveOut8Ex(session, space, offset, length, converted_buffer)
    else:
        return library.viMoveOut8(session, space, offset, length, converted_buffer)


def move_out_16(library, session, space, offset, length, data, extended=False):
    """Moves an 16-bit block of data from local memory to the specified address space and offset.

    Corresponds to viMoveOut16* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    converted_buffer = (ViUInt16 * length)(*tuple(data))
    if extended:
        return library.viMoveOut16Ex(session, space, offset, length, converted_buffer)
    else:
        return library.viMoveOut16(session, space, offset, length, converted_buffer)


def move_out_32(library, session, space, offset, length, data, extended=False):
    """Moves an 32-bit block of data from local memory to the specified address space and offset.

    Corresponds to viMoveOut32* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    converted_buffer = (ViUInt32 * length)(*tuple(data))
    if extended:
        return library.viMoveOut32Ex(session, space, offset, length, converted_buffer)
    else:
        return library.viMoveOut32(session, space, offset, length, converted_buffer)


def move_out_64(library, session, space, offset, length, data, extended=False):
    """Moves an 64-bit block of data from local memory to the specified address space and offset.

    Corresponds to viMoveOut64* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param length: Number of elements to transfer, where the data width of the elements to transfer
                   is identical to the source data width.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    converted_buffer = (ViUInt64 * length)(*tuple(data))
    if extended:
        return library.viMoveOut64Ex(session, space, offset, length, converted_buffer)
    else:
        return library.viMoveOut64(session, space, offset, length, converted_buffer)


# noinspection PyShadowingBuiltins
def open(library, session, resource_name,
         access_mode=constants.AccessModes.no_lock, open_timeout=constants.VI_TMO_IMMEDIATE):
    """Opens a session to the specified resource.

    Corresponds to viOpen function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be a session returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :param access_mode: Specifies the mode by which the resource is to be accessed. (constants.AccessModes)
    :param open_timeout: Specifies the maximum time period (in milliseconds) that this operation waits
                         before returning an error.
    :return: Unique logical identifier reference to a session, return value of the library call.
    :rtype: session, :class:`pyvisa.constants.StatusCode`
    """
    try:
        open_timeout = int(open_timeout)
    except ValueError:
        raise ValueError('open_timeout (%r) must be an integer (or compatible type)' % open_timeout)
    out_session = ViSession()

    # [ViSession, ViRsrc, ViAccessMode, ViUInt32, ViPSession]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    ret = library.viOpen(session, resource_name, access_mode, open_timeout, byref(out_session))
    return out_session.value, ret


def open_default_resource_manager(library):
    """This function returns a session to the Default Resource Manager resource.

    Corresponds to viOpenDefaultRM function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :return: Unique logical identifier to a Default Resource Manager session, return value of the library call.
    :rtype: session, :class:`pyvisa.constants.StatusCode`
    """
    session = ViSession()
    ret = library.viOpenDefaultRM(byref(session))
    return session.value, ret


def write_memory(library, session, space, offset, data, width, extended=False):
    """Write in an 8-bit, 16-bit, 32-bit, value to the specified memory space and offset.

    Corresponds to viOut* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param width: Number of bits to read.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viOut8* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if extended:
        return library.viOut8Ex(session, space, offset, data)
    else:
        return library.viOut8(session, space, offset, data)


def out_16(library, session, space, offset, data, extended=False):
    """Write in an 16-bit value from the specified memory space and offset.

    Corresponds to viOut16* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if extended:
        return library.viOut16Ex(session, space, offset, data, extended=False)
    else:
        return library.viOut16(session, space, offset, data, extended=False)


def out_32(library, session, space, offset, data, extended=False):
    """Write in an 32-bit value from the specified memory space and offset.

    Corresponds to viOut32* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if extended:
        return library.viOut32Ex(session, space, offset, data)
    else:
        return library.viOut32(session, space, offset, data)


def out_64(library, session, space, offset, data, extended=False):
    """Write in an 64-bit value from the specified memory space and offset.

    Corresponds to viOut64* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param space: Specifies the address space. (Constants.*SPACE*)
    :param offset: Offset (in bytes) of the address or register from which to read.
    :param data: Data to write to bus.
    :param extended: Use 64 bits offset independent of the platform.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    if extended:
        return library.viOut64Ex(session, space, offset, data)
    else:
        return library.viOut64(session, space, offset, data)


def parse_resource(library, session, resource_name):
    """Parse a resource string to get the interface information.

    Corresponds to viParseRsrc function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                    returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :return: Resource information with interface type and board number, return value of the library call.
    :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
    """
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()

    # [ViSession, ViRsrc, ViPUInt16, ViPUInt16]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    ret = library.viParseRsrc(session, resource_name, byref(interface_type),
                              byref(interface_board_number))
    return ResourceInfo(constants.InterfaceType(interface_type.value),
                        interface_board_number.value,
                        None, None, None), ret


def parse_resource_extended(library, session, resource_name):
    """Parse a resource string to get extended interface information.

    Corresponds to viParseRsrcEx function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                    returned from open_default_resource_manager()).
    :param resource_name: Unique symbolic name of a resource.
    :return: Resource information, return value of the library call.
    :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
    """
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    resource_class = create_string_buffer(constants.VI_FIND_BUFLEN)
    unaliased_expanded_resource_name = create_string_buffer(constants.VI_FIND_BUFLEN)
    alias_if_exists = create_string_buffer(constants.VI_FIND_BUFLEN)

    # [ViSession, ViRsrc, ViPUInt16, ViPUInt16, ViAChar, ViAChar, ViAChar]
    # ViRsrc converts from (str, unicode, bytes) to bytes
    ret = library.viParseRsrcEx(session, resource_name, byref(interface_type),
                                byref(interface_board_number), resource_class,
                                unaliased_expanded_resource_name,
                                alias_if_exists)

    res = [buffer_to_text(val)
           for val in (resource_class,
                       unaliased_expanded_resource_name,
                       alias_if_exists)]

    if res[-1] == '':
        res[-1] = None

    return ResourceInfo(constants.InterfaceType(interface_type.value),
                        interface_board_number.value, *res), ret


def peek(library, session, address, width):
    """Read an 8, 16 or 32-bit value from the specified address.

    Corresponds to viPeek* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param width: Number of bits to read.
    :return: Data read from bus, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viPeek8 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    value_8 = ViUInt8()
    ret = library.viPeek8(session, address, byref(value_8))
    return value_8.value, ret


def peek_16(library, session, address):
    """Read an 16-bit value from the specified address.

    Corresponds to viPeek16 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    value_16 = ViUInt16()
    ret = library.viPeek16(session, address, byref(value_16))
    return value_16.value, ret


def peek_32(library, session, address):
    """Read an 32-bit value from the specified address.

    Corresponds to viPeek32 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    value_32 = ViUInt32()
    ret = library.viPeek32(session, address, byref(value_32))
    return value_32.value, ret


def peek_64(library, session, address):
    """Read an 64-bit value from the specified address.

    Corresponds to viPeek64 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :return: Data read from bus, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    value_64 = ViUInt64()
    ret = library.viPeek64(session, address, byref(value_64))
    return value_64.value, ret


def poke(library, session, address, width, data):
    """Writes an 8, 16 or 32-bit value from the specified address.

    Corresponds to viPoke* functions of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param width: Number of bits to read.
    :param data: Data to be written to the bus.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
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

    Corresponds to viPoke8 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: Data read from bus.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viPoke8(session, address, data)


def poke_16(library, session, address, data):
    """Write an 16-bit value from the specified address.

    Corresponds to viPoke16 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viPoke16(session, address, data)


def poke_32(library, session, address, data):
    """Write an 32-bit value from the specified address.

    Corresponds to viPoke32 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viPoke32(session, address, data)


def poke_64(library, session, address, data):
    """Write an 64-bit value from the specified address.

    Corresponds to viPoke64 function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param address: Source address to read the value.
    :param data: value to be written to the bus.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viPoke64(session, address, data)


def read(library, session, count):
    """Reads data from device or interface synchronously.

    Corresponds to viRead function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: data read, return value of the library call.
    :rtype: bytes, :class:`pyvisa.constants.StatusCode`
    """
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    ret = library.viRead(session, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value], ret


def read_asynchronously(library, session, count):
    """Reads data from device or interface asynchronously.

    Corresponds to viReadAsync function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param count: Number of bytes to be read.
    :return: result, jobid, return value of the library call.
    :rtype: ctypes buffer, jobid, :class:`pyvisa.constants.StatusCode`
    """
    buffer = create_string_buffer(count)
    job_id = ViJobId()
    ret = library.viReadAsync(session, buffer, count, byref(job_id))
    return buffer, job_id, ret


def read_stb(library, session):
    """Reads a status byte of the service request.

    Corresponds to viReadSTB function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: Service request status byte, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    status = ViUInt16()
    ret = library.viReadSTB(session, byref(status))
    return status.value, ret


def read_to_file(library, session, filename, count):
    """Read data synchronously, and store the transferred data in a file.

    Corresponds to viReadToFile function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param filename: Name of file to which data will be written.
    :param count: Number of bytes to be read.
    :return: Number of bytes actually transferred, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    return_count = ViUInt32()
    ret = library.viReadToFile(session, filename, count, return_count)
    return return_count, ret


def set_attribute(library, session, attribute, attribute_state):
    """Sets the state of an attribute.

    Corresponds to viSetAttribute function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param attribute: Attribute for which the state is to be modified. (Attributes.*)
    :param attribute_state: The state of the attribute to be set for the specified object.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viSetAttribute(session, attribute, attribute_state)


def set_buffer(library, session, mask, size):
    """Sets the size for the formatted I/O and/or low-level I/O communication buffer(s).

    Corresponds to viSetBuf function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mask: Specifies the type of buffer. (Constants.READ_BUF, .WRITE_BUF, .IO_IN_BUF, .IO_OUT_BUF)
    :param size: The size to be set for the specified buffer(s).
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viSetBuf(session, mask, size)


def status_description(library, session, status):
    """Returns a user-readable description of the status code passed to the operation.

    Corresponds to viStatusDesc function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param status: Status code to interpret.
    :return: - The user-readable string interpretation of the status code passed to the operation,
             - return value of the library call.
    :rtype: - unicode (Py2) or str (Py3)
            - :class:`pyvisa.constants.StatusCode`
    """
    description = create_string_buffer(256)
    ret = library.viStatusDesc(session, status, description)
    return buffer_to_text(description), ret


def terminate(library, session, degree, job_id):
    """Requests a VISA session to terminate normal execution of an operation.

    Corresponds to viTerminate function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param degree: Constants.NULL
    :param job_id: Specifies an operation identifier.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viTerminate(session, degree, job_id)


def uninstall_handler(library, session, event_type, handler, user_handle=None):
    """Uninstalls handlers for events.

    Corresponds to viUninstallHandler function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param event_type: Logical event identifier.
    :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
    :param user_handle: The user_handle (a ctypes object) in the returned value from install_handler.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    set_user_handle_type(library, user_handle)
    if user_handle != None:
         user_handle = byref(user_handle)
    return library.viUninstallHandler(session, event_type, handler, user_handle)


def unlock(library, session):
    """Relinquishes a lock for the specified resource.

    Corresponds to viUnlock function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viUnlock(session)


def unmap_address(library, session):
    """Unmaps memory space previously mapped by map_address().

    Corresponds to viUnmapAddress function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viUnmapAddress(session)


def unmap_trigger(library, session, trigger_source, trigger_destination):
    """Undo a previous map from the specified trigger source line to the specified destination line.

    Corresponds to viUnmapTrigger function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param trigger_source: Source line used in previous map. (Constants.TRIG*)
    :param trigger_destination: Destination line used in previous map. (Constants.TRIG*)
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    return library.viUnmapTrigger(session, trigger_source, trigger_destination)


def usb_control_in(library, session, request_type_bitmap_field, request_id, request_value,
                   index, length=0):
    """Performs a USB control pipe transfer from the device.

    Corresponds to viUsbControlIn function of the VISA library.

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
    :return: - The data buffer that receives the data from the optional data stage of the control transfer
             - return value of the library call.
    :rtype: - bytes
            - :class:`pyvisa.constants.StatusCode`
    """
    buffer = create_string_buffer(length)
    return_count = ViUInt16()
    ret = library.viUsbControlIn(session, request_type_bitmap_field, request_id,
                                 request_value, index, length, buffer,
                                 byref(return_count))
    return buffer.raw[:return_count.value], ret


def usb_control_out(library, session, request_type_bitmap_field, request_id, request_value,
                    index, data=""):
    """Performs a USB control pipe transfer to the device.

    Corresponds to viUsbControlOut function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
    :param request_id: bRequest parameter of the setup stage of a USB control transfer.
    :param request_value: wValue parameter of the setup stage of a USB control transfer.
    :param index: wIndex parameter of the setup stage of a USB control transfer.
                  This is usually the index of the interface or endpoint.
    :param data: The data buffer that sends the data in the optional data stage of the control transfer.
    :return: return value of the library call.
    :rtype: :class:`pyvisa.constants.StatusCode`
    """
    length = len(data)
    return library.viUsbControlOut(session, request_type_bitmap_field, request_id,
                                   request_value, index, length, data)


def vxi_command_query(library, session, mode, command):
    """Sends the device a miscellaneous command or query and/or retrieves the response to a previous query.

    Corresponds to viVxiCommandQuery function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param mode: Specifies whether to issue a command and/or retrieve a response. (Constants.VXI_CMD*, .VXI_RESP*)
    :param command: The miscellaneous command to send.
    :return: The response retrieved from the device, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    response = ViUInt32()
    ret = library.viVxiCommandQuery(session, mode, command, byref(response))
    return response.value, ret


def wait_on_event(library, session, in_event_type, timeout):
    """Waits for an occurrence of the specified event for a given session.

    Corresponds to viWaitOnEvent function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param in_event_type: Logical identifier of the event(s) to wait for.
    :param timeout: Absolute time period in time units that the resource shall wait for a specified event to
                    occur before returning the time elapsed error. The time unit is in milliseconds.
    :return: - Logical identifier of the event actually received
             - A handle specifying the unique occurrence of an event
             - return value of the library call.
    :rtype: - eventtype
            - event
            - :class:`pyvisa.constants.StatusCode`
    """
    out_event_type = ViEventType()
    out_context = ViEvent()
    ret = library.viWaitOnEvent(session, in_event_type, timeout,
                                byref(out_event_type), byref(out_context))
    return out_event_type.value, out_context, ret


def write(library, session, data):
    """Writes data to device or interface synchronously.

    Corresponds to viWrite function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :type data: str
    :return: Number of bytes actually transferred, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    return_count = ViUInt32()
    # [ViSession, ViBuf, ViUInt32, ViPUInt32]
    ret = library.viWrite(session, data, len(data), byref(return_count))
    return return_count.value, ret


def write_asynchronously(library, session, data):
    """Writes data to device or interface asynchronously.

    Corresponds to viWriteAsync function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param data: data to be written.
    :return: Job ID of this asynchronous write operation, return value of the library call.
    :rtype: jobid, :class:`pyvisa.constants.StatusCode`
    """
    job_id = ViJobId()
    # [ViSession, ViBuf, ViUInt32, ViPJobId]
    ret = library.viWriteAsync(session, data, len(data), byref(job_id))
    return job_id, ret


def write_from_file(library, session, filename, count):
    """Take data from a file and write it out synchronously.

    Corresponds to viWriteFromFile function of the VISA library.

    :param library: the visa library wrapped by ctypes.
    :param session: Unique logical identifier to a session.
    :param filename: Name of file from which data will be read.
    :param count: Number of bytes to be written.
    :return: Number of bytes actually transferred, return value of the library call.
    :rtype: int, :class:`pyvisa.constants.StatusCode`
    """
    return_count = ViUInt32()
    ret = library.viWriteFromFile(session, filename, count, return_count)
    return return_count, ret
