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

VI_SPEC_VERSION = 0x00300000

import sys

import warnings

from ctypes import (byref, cdll, c_void_p, c_double, c_long,
                    create_string_buffer, POINTER)

if sys.platform == 'win32':
    from ctypes import windll, WINFUNCTYPE as FUNCTYPE
else:
    from ctypes import CFUNCTYPE as FUNCTYPE

from .visa_exceptions import *
from .visa_messages import completion_and_error_messages

from .vpp43_constants import *
from .vpp43_types import *
from .vpp43_attributes import attributes

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


# Add all symbols from #visa_exceptions# and #vpp43_constants# to the list of
# exported symbols
import visa_exceptions
import vpp43_constants
__all__.extend([name for name in vpp43_constants.__dict__.keys() +
                visa_exceptions.__dict__.keys() if name[0] != '_'])


# load VISA library

class Singleton(object):
    """Base class for singleton classes.

    Taken from <http://www.python.org/2.2.3/descrintro.html>.  I added the
    definition of __init__.

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

    def __init__(self, *args, **kwds):
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
        self.__lib = self.__cdecl_lib = None

    def load_library(self, path=None):
        """(Re-)loads the VISA library.

        The optional parameter "path" holds the full path to the VISA library.
        It is called implicitly by __call__ if not called successfully before.

        It may raise an OSNotSupported exception, or an OSError if the library
        file was not found.

        """
        if sys.platform.startswith('win32'):
            if path:
                self.__lib       = windll.LoadLibrary(path)
                self.__cdecl_lib = cdll.LoadLibrary(path)
            else:
                self.__lib       = windll.visa32
                self.__cdecl_lib = cdll.visa32
        elif sys.platform.startswith('linux2'):
            if not path:
                path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"
            self.__lib = self.__cdecl_lib = cdll.LoadLibrary(path)
        elif sys.platform.startswith('darwin'):
            if not path:
                path = "/Library/Frameworks/VISA.framework/VISA"
            self.__lib = self.__cdecl_lib = cdll.LoadLibrary(path)
        else:
            self.__lib = self.__cdecl_lib = None
            raise visa_exceptions.OSNotSupported(os.name)
        self.__initialize_library_functions()

    def set_user_handle_type(self, user_handle):
        # Actually, it's not necessary to change ViHndlr *globally*.  However,
        # I don't want to break symmetry too much with all the other VPP43
        # routines.
        global ViHndlr
        if user_handle is None:
            user_handle_p = c_void_p
        else:
            user_handle_p = POINTER(type(user_handle))
        ViHndlr = FUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent,
                           user_handle_p)
        self.__lib.viInstallHandler.argtypes = [ViSession, ViEventType,
                                                ViHndlr, user_handle_p]
        self.__lib.viUninstallHandler.argtypes = [ViSession, ViEventType,
                                                  ViHndlr, user_handle_p]

    def __call__(self, force_cdecl=False):
        """Returns the ctypes object to the VISA library.

        If "force_cdecl" is True, use the cdecl calling convention even under
        Windows, where the stdcall convension is the default.  For Linux, this
        has no effect.

        """
        if self.__lib is None or self.__cdecl_lib is None:
            self.load_library()
        if force_cdecl:
            return self.__cdecl_lib
        return self.__lib

    def __initialize_library_functions(self):
        # Consistency remark: here all VPP-4.3.2 routines must be listed (unless, of
        # course, they don't return a status value, like "peek" and "poke").
        for visa_function in ["viAssertIntrSignal", "viAssertTrigger",
            "viAssertUtilSignal", "viBufRead", "viBufWrite", "viClear",
            "viClose", "viDisableEvent", "viDiscardEvents", "viEnableEvent",
            "viFindNext", "viFindRsrc", "viFlush", "viGetAttribute",
            "viGpibCommand", "viGpibControlATN", "viGpibControlREN",
            "viGpibPassControl", "viGpibSendIFC", "viIn16", "viIn32", "viIn8",
            "viInstallHandler", "viLock", "viMapAddress", "viMapTrigger",
            "viMemAlloc", "viMemFree", "viMove", "viMoveAsync", "viMoveIn16",
            "viMoveIn32", "viMoveIn8", "viMoveOut16", "viMoveOut32",
            "viMoveOut8", "viOpen", "viOpenDefaultRM", "viOut16", "viOut32",
            "viOut8", "viParseRsrc", "viParseRsrcEx", "viRead", "viReadAsync",
            "viReadSTB", "viReadToFile", "viSetAttribute", "viSetBuf",
            "viStatusDesc", "viTerminate", "viUninstallHandler", "viUnlock",
            "viUnmapAddress", "viUnmapTrigger", "viUsbControlIn",
            "viUsbControlOut", "viVPrintf", "viVQueryf", "viVSPrintf",
            "viVSScanf", "viVScanf", "viVxiCommandQuery", "viWaitOnEvent",
            "viWrite", "viWriteAsync", "viWriteFromFile"]:
            try:
                getattr(self.__lib, visa_function).restype = check_status
            except AttributeError:
                # Mostly, viParseRsrcEx was not found
                pass
        for visa_function in ["viPrintf", "viScanf", "viSPrintf", "viSScanf",
                              "viQueryf"]:
            try:
                getattr(self.__cdecl_lib, visa_function).restype = check_status
            except AttributeError:
                pass
        for visa_function in ["viPeek8", "viPeek16", "viPeek32", "viPoke8",
                              "viPoke16", "viPoke32"]:
            try:
                getattr(self.__lib, visa_function).restype = None
            except AttributeError:
                pass
        # Here too, we silently ignore missing functions.  If the user accesses
        # it nevertheless, an AttributeError is raised which is clear enough
        self.__set_argument_types("viAssertIntrSignal", [ViSession,
                                                         ViInt16, ViUInt32])
        self.__set_argument_types("viAssertTrigger", [ViSession, ViUInt16])
        self.__set_argument_types("viAssertUtilSignal", [ViSession, ViUInt16])
        self.__set_argument_types("viBufRead", [ViSession, ViPBuf, ViUInt32,
                                                ViPUInt32])
        self.__set_argument_types("viBufWrite", [ViSession, ViBuf, ViUInt32,
                                                 ViPUInt32])
        self.__set_argument_types("viClear", [ViSession])
        self.__set_argument_types("viClose", [ViObject])
        self.__set_argument_types("viDisableEvent", [ViSession, ViEventType,
                                                     ViUInt16])
        self.__set_argument_types("viDiscardEvents", [ViSession, ViEventType,
                                               ViUInt16])
        self.__set_argument_types("viEnableEvent", [ViSession, ViEventType,
                                                    ViUInt16, ViEventFilter])
        self.__set_argument_types("viFindNext", [ViSession, ViAChar])
        self.__set_argument_types("viFindRsrc", [ViSession, ViString,
                                                 ViPFindList, ViPUInt32,
                                                 ViAChar])
        self.__set_argument_types("viFlush", [ViSession, ViUInt16])
        self.__set_argument_types("viGetAttribute", [ViObject, ViAttr,
                                                     c_void_p])
        self.__set_argument_types("viGpibCommand", [ViSession, ViBuf, ViUInt32,
                                                    ViPUInt32])
        self.__set_argument_types("viGpibControlATN", [ViSession, ViUInt16])
        self.__set_argument_types("viGpibControlREN", [ViSession, ViUInt16])
        self.__set_argument_types("viGpibPassControl", [ViSession, ViUInt16,
                                                        ViUInt16])
        self.__set_argument_types("viGpibSendIFC", [ViSession])
        self.__set_argument_types("viIn8", [ViSession, ViUInt16, ViBusAddress,
                                            ViPUInt8])
        self.__set_argument_types("viIn16", [ViSession, ViUInt16, ViBusAddress,
                                             ViPUInt16])
        self.__set_argument_types("viIn32", [ViSession, ViUInt16, ViBusAddress,
                                             ViPUInt32])
        self.__set_argument_types("viInstallHandler", [ViSession, ViEventType,
                                                       ViHndlr, ViAddr])
        self.__set_argument_types("viLock", [ViSession, ViAccessMode, ViUInt32,
                                             ViKeyId, ViAChar])
        self.__set_argument_types("viMapAddress", [ViSession, ViUInt16,
                                                   ViBusAddress, ViBusSize,
                                                   ViBoolean, ViAddr, ViPAddr])
        self.__set_argument_types("viMapTrigger", [ViSession, ViInt16, ViInt16,
                                                   ViUInt16])
        self.__set_argument_types("viMemAlloc", [ViSession, ViBusSize,
                                                 ViPBusAddress])
        self.__set_argument_types("viMemFree", [ViSession, ViBusAddress])
        self.__set_argument_types("viMove", [ViSession, ViUInt16, ViBusAddress,
                                             ViUInt16, ViUInt16, ViBusAddress,
                                             ViUInt16, ViBusSize])
        self.__set_argument_types("viMoveAsync", [ViSession, ViUInt16,
                                                  ViBusAddress, ViUInt16,
                                                  ViUInt16, ViBusAddress,
                                                  ViUInt16, ViBusSize,
                                                  ViPJobId])
        self.__set_argument_types("viMoveIn8", [ViSession, ViUInt16,
                                                ViBusAddress, ViBusSize,
                                                ViAUInt8])
        self.__set_argument_types("viMoveIn16", [ViSession, ViUInt16,
                                                 ViBusAddress, ViBusSize,
                                                 ViAUInt16])
        self.__set_argument_types("viMoveIn32", [ViSession, ViUInt16,
                                                 ViBusAddress, ViBusSize,
                                                 ViAUInt32])
        self.__set_argument_types("viMoveOut8", [ViSession, ViUInt16,
                                                 ViBusAddress, ViBusSize,
                                                 ViAUInt8])
        self.__set_argument_types("viMoveOut16", [ViSession, ViUInt16,
                                                  ViBusAddress, ViBusSize,
                                                  ViAUInt16])
        self.__set_argument_types("viMoveOut32", [ViSession, ViUInt16,
                                                  ViBusAddress, ViBusSize,
                                                  ViAUInt32])
        # The following function *must* be available in order to assure that we
        # have a VISA library at all (rather than something completely
        # different).  I hope that viOpen is old enough in the VISA
        # specification.
        self.__set_argument_types("viOpen", [ViSession, ViRsrc, ViAccessMode,
                                             ViUInt32, ViPSession],
                                            may_be_missing=False)
        self.__set_argument_types("viOpenDefaultRM", [ViPSession])
        self.__set_argument_types("viOut8", [ViSession, ViUInt16, ViBusAddress,
                                             ViUInt8])
        self.__set_argument_types("viOut16", [ViSession, ViUInt16,
                                              ViBusAddress, ViUInt16])
        self.__set_argument_types("viOut32", [ViSession, ViUInt16,
                                              ViBusAddress, ViUInt32])
        self.__set_argument_types("viParseRsrc", [ViSession, ViRsrc, ViPUInt16,
                                                  ViPUInt16])
        self.__set_argument_types("viParseRsrcEx", [ViSession, ViRsrc,
                                                    ViPUInt16, ViPUInt16,
                                                    ViAChar, ViAChar, ViAChar])
        self.__set_argument_types("viPeek8", [ViSession, ViAddr, ViPUInt8])
        self.__set_argument_types("viPeek16", [ViSession, ViAddr, ViPUInt16])
        self.__set_argument_types("viPeek32", [ViSession, ViAddr, ViPUInt32])
        self.__set_argument_types("viPoke8", [ViSession, ViAddr, ViUInt8])
        self.__set_argument_types("viPoke16", [ViSession, ViAddr, ViUInt16])
        self.__set_argument_types("viPoke32", [ViSession, ViAddr, ViUInt32])
        self.__set_argument_types("viPrintf", [ViSession, ViString],
                                              force_cdecl=True)
        self.__set_argument_types("viQueryf", [ViSession, ViString, ViString],
                                              force_cdecl=True)
        self.__set_argument_types("viRead", [ViSession, ViPBuf, ViUInt32,
                                             ViPUInt32])
        self.__set_argument_types("viReadAsync", [ViSession, ViPBuf, ViUInt32,
                                                  ViPJobId])
        self.__set_argument_types("viReadSTB", [ViSession, ViPUInt16])
        self.__set_argument_types("viReadToFile", [ViSession, ViString,
                                                   ViUInt32, ViPUInt32])
        self.__set_argument_types("viScanf", [ViSession, ViString],
                                             force_cdecl=True)
        self.__set_argument_types("viSetAttribute", [ViObject, ViAttr,
                                                     ViAttrState])
        self.__set_argument_types("viSetBuf", [ViSession, ViUInt16, ViUInt32])
        self.__set_argument_types("viSPrintf", [ViSession, ViPBuf, ViString],
                                               force_cdecl=True)
        self.__set_argument_types("viSScanf", [ViSession, ViBuf, ViString],
                                              force_cdecl=True)
        self.__set_argument_types("viStatusDesc", [ViObject, ViStatus,
                                                   ViAChar])
        self.__set_argument_types("viTerminate", [ViSession, ViUInt16,
                                                  ViJobId])
        self.__set_argument_types("viUninstallHandler", [ViSession,
                                                         ViEventType, ViHndlr,
                                                         ViAddr])
        self.__set_argument_types("viUnlock", [ViSession])
        self.__set_argument_types("viUnmapAddress", [ViSession])
        self.__set_argument_types("viUnmapTrigger", [ViSession, ViInt16,
                                                     ViInt16])
        self.__set_argument_types("viUsbControlIn", [ViSession, ViInt16,
                                                     ViInt16, ViUInt16,
                                                     ViUInt16, ViUInt16,
                                                     ViPBuf, ViPUInt16])
        self.__set_argument_types("viUsbControlOut", [ViSession, ViInt16,
                                                      ViInt16, ViUInt16,
                                                      ViUInt16, ViUInt16,
                                                      ViPBuf])
        # The following "V" routines are *not* implemented in PyVISA, and will
        # never be: viVPrintf, viVQueryf, viVScanf, viVSPrintf, viVSScanf
        self.__set_argument_types("viVxiCommandQuery", [ViSession, ViUInt16,
                                                        ViUInt32, ViPUInt32])
        self.__set_argument_types("viWaitOnEvent", [ViSession, ViEventType,
                                                    ViUInt32, ViPEventType,
                                                    ViPEvent])
        self.__set_argument_types("viWrite", [ViSession, ViBuf, ViUInt32,
                                              ViPUInt32])
        self.__set_argument_types("viWriteAsync", [ViSession, ViBuf, ViUInt32,
                                                   ViPJobId])
        self.__set_argument_types("viWriteFromFile", [ViSession, ViString,
                                                      ViUInt32, ViPUInt32])

    def __set_argument_types(self, visa_function, types, force_cdecl=False,
                             may_be_missing=True):
        if not force_cdecl:
            library = self.__lib
        else:
            library = self.__cdecl_lib
        try:
            getattr(library, visa_function).argtypes = types
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
        raise visa_exceptions.VisaIOError(status)
    if status in dodgy_completion_codes:
        abbreviation, description = completion_and_error_messages[status]
        warnings.warn("%s: %s" % (abbreviation, description),
                      visa_exceptions.VisaIOWarning, stacklevel=2)
    return status


def get_status():
    return visa_status


# convert_argument_list is used for VISA routines with variable argument list,
# which means that also the types are unknown.  Therefore I convert the Python
# types to well-defined ctypes types.
#
# Attention: This means that only C doubles, C long ints, and strings can be
# used in format strings!  No "float"s, no "long doubles", no "int"s etc.
# Further, only floats, integers and strings can be passed to printf and scanf,
# but neither unicode strings nor sequence types.
#
# All of these restrictions may be removed in the future.

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
            converted_arguments.append(c_double(argument))
        elif isinstance(argument, int):
            converted_arguments.append(c_long(argument))
        elif isinstance(argument, str):
            converted_arguments.append(argument)
        else:
            raise visa_exceptions.VisaTypeError("Invalid type in scanf/printf: %s" % type(argument))
    return tuple(converted_arguments)


def convert_to_byref(byvalue_arguments, buffer_length):
    """Converts a list of ctypes objects to a tuple with ctypes references
    (pointers) to them, for use in scanf-like functions.

    Arguments:
    byvalue_arguments -- a list (sic!) with the original arguments.  They must
        be simple ctypes objects or Python strings.  If there are Python
        strings, they are converted in place to ctypes buffers of the same
        length and same contents.
    buffer_length -- minimal length of ctypes buffers generated from Python
        strings.

    Return value: a tuple with the by-references arguments.

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
            raise visa_exceptions.VisaTypeError("Invalid type in scanf: %s" % type(argument))
    return tuple(converted_arguments)


def construct_return_tuple(original_ctypes_sequence):
    """Generate a return value for queryf(), scanf(), and sscanf() out of the
    list of ctypes objects.

    Arguments:
    original_ctypes_sequence -- a sequence of ctypes objects, i.e. c_long,
        c_double, and ctypes strings.

    Return value: The pythonic variants of the ctypes objects, in a form
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


def assert_interrupt_signal(vi, mode, status_id):
    visa_library().viAssertIntrSignal(vi, mode, status_id)


def assert_trigger(vi, protocol):
    visa_library().viAssertTrigger(vi, protocol)


def assert_utility_signal(vi, line):
    visa_library().viAssertUtilSignal(vi, line)


def buffer_read(vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    visa_library().viBufRead(vi, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def buffer_write(vi, buffer):
    return_count = ViUInt32()
    visa_library().viBufWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def clear(vi):
    visa_library().viClear(vi)


def close(vi):
    visa_library().viClose(vi)


def disable_event(vi, event_type, mechanism):
    visa_library().viDisableEvent(vi, event_type, mechanism)


def discard_events(vi, event_type, mechanism):
    visa_library().viDiscardEvents(vi, event_type, mechanism)


def enable_event(vi, event_type, mechanism, context=VI_NULL):
    context = VI_NULL  # according to spec VPP-4.3, section 3.7.3.1
    visa_library().viEnableEvent(vi, event_type, mechanism, context)


def find_next(find_list):
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindNext(find_list, instrument_description)
    return instrument_description.value


def find_resources(session, regular_expression):
    find_list = ViFindList()
    return_counter = ViUInt32()
    instrument_description = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viFindRsrc(session, regular_expression,
                              byref(find_list), byref(return_counter),
                              instrument_description)
    return find_list, return_counter.value, instrument_description.value


def flush(vi, mask):
    visa_library().viFlush(vi, mask)


def get_attribute(vi, attribute):
    # FixMe: How to deal with ViBuf?
    datatype = attributes[attribute]
    if datatype == ViString:
        attribute_state = create_string_buffer(256)
        visa_library().viGetAttribute(vi, attribute, attribute_state)
    elif datatype == ViAUInt8:
        length = get_attribute(vi, VI_ATTR_USB_RECV_INTR_SIZE)
        attribute_state = (ViUInt8 * length)()
        visa_library().viGetAttribute(vi, attribute, byref(attribute_state))
        return list(attribute_state)
    else:
        attribute_state = datatype()
        visa_library().viGetAttribute(vi, attribute, byref(attribute_state))
    return attribute_state.value


def gpib_command(vi, buffer):
    return_count = ViUInt32()
    visa_library().viGpibCommand(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def gpib_control_atn(vi, mode):
    visa_library().viGpibControlATN(vi, mode)


def gpib_control_ren(vi, mode):
    visa_library().viGpibControlREN(vi, mode)


def gpib_pass_control(vi, primary_address, secondary_address):
    visa_library().viGpibPassControl(vi, primary_address, secondary_address)


def gpib_send_ifc(vi):
    visa_library().viGpibSendIFC(vi)


def in_8(vi, space, offset):
    value_8 = ViUInt8()
    visa_library().viIn8(vi, space, offset, byref(value_8))
    return value_8.value


def in_16(vi, space, offset):
    value_16 = ViUInt16()
    visa_library().viIn16(vi, space, offset, byref(value_16))
    return value_16.value


def in_32(vi, space, offset):
    value_32 = ViUInt32()
    visa_library().viIn32(vi, space, offset, byref(value_32))
    return value_32.value

handlers = []
"""Contains all installed event handlers.

Its elements are tuples with three elements: The handler itself (a Python
callable), the user handle (as a ctypes object) and the handler again, this
time as a ctypes object created with CFUNCTYPE.

"""


def install_handler(vi, event_type, handler, user_handle=None):
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
            raise visa_exceptions.VisaTypeError("Type not allowed as user handle: %s" % type(user_handle))
    visa_library.set_user_handle_type(converted_user_handle)
    converted_handler = ViHndlr(handler)
    if user_handle is None:
        visa_library().viInstallHandler(vi, event_type, converted_handler,
                                        None)
    else:
        visa_library().viInstallHandler(vi, event_type, converted_handler,
                                        byref(converted_user_handle))
    handlers.append((handler, converted_user_handle, converted_handler))
    return converted_user_handle


def lock(vi, lock_type, timeout, requested_key=None):
    if lock_type == VI_EXCLUSIVE_LOCK:
        requested_key = None
        access_key = None
    else:
        access_key = create_string_buffer(256)
    visa_library().viLock(vi, lock_type, timeout, requested_key, access_key)
    return access_key


def map_address(vi, map_space, map_base, map_size,
                access=VI_FALSE, suggested=VI_NULL):
    access = VI_FALSE
    address = ViAddr()
    visa_library().viMapAddress(vi, map_space, map_base, map_size, access,
                                suggested, byref(address))
    return address


def map_trigger(vi, trigger_source, trigger_destination, mode):
    visa_library().viMapTrigger(vi, trigger_source, trigger_destination, mode)


def memory_allocation(vi, size):
    offset = ViBusAddress()
    visa_library().viMemAlloc(vi, size, byref(offset))
    return offset


def memory_free(vi, offset):
    visa_library().viMemFree(vi, offset)


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


def move_in_8(vi, space, offset, length):
    buffer_8 = (ViUInt8 * length)()
    visa_library().viMoveIn8(vi, space, offset, length, buffer_8)
    return list(buffer_8)


def move_in_16(vi, space, offset, length):
    buffer_16 = (ViUInt16 * length)()
    visa_library().viMoveIn16(vi, space, offset, length, buffer_16)
    return list(buffer_16)


def move_in_32(vi, space, offset, length):
    buffer_32 = (ViUInt32 * length)()
    visa_library().viMoveIn32(vi, space, offset, length, buffer_32)
    return list(buffer_32)


def move_out_8(vi, space, offset, length, buffer_8):
    converted_buffer = (ViUInt8 * length)(*tuple(buffer_8))
    visa_library().viMoveOut8(vi, space, offset, length, converted_buffer)


def move_out_16(vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt16 * length)(*tuple(buffer_16))
    visa_library().viMoveOut16(vi, space, offset, length, converted_buffer)


def move_out_32(vi, space, offset, length, buffer_16):
    converted_buffer = (ViUInt32 * length)(*tuple(buffer_32))
    visa_library().viMoveOut32(vi, space, offset, length, converted_buffer)


def open(session, resource_name,
         access_mode=VI_NO_LOCK, open_timeout=VI_TMO_IMMEDIATE):
    vi = ViSession()
    visa_library().viOpen(session, resource_name, access_mode, open_timeout,
                          byref(vi))
    return vi.value


def open_default_resource_manager():
    session = ViSession()
    visa_library().viOpenDefaultRM(byref(session))
    return session.value

get_default_resource_manager = open_default_resource_manager
"""A deprecated alias.  See VPP-4.3, rule 4.3.5 and observation 4.3.2."""


def out_8(vi, space, offset, value_8):
    visa_library().viOut8(vi, space, offset, value_8)


def out_16(vi, space, offset, value_16):
    visa_library().viOut16(vi, space, offset, value_16)


def out_32(vi, space, offset, value_32):
    visa_library().viOut32(vi, space, offset, value_32)


def parse_resource(session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    visa_library().viParseRsrc(session, resource_name, byref(interface_type),
                               byref(interface_board_number))
    return interface_type.value, interface_board_number.value


def parse_resource_extended(session, resource_name):
    interface_type = ViUInt16()
    interface_board_number = ViUInt16()
    resource_class = create_string_buffer(VI_FIND_BUFLEN)
    unaliased_expanded_resource_name = create_string_buffer(VI_FIND_BUFLEN)
    alias_if_exists = create_string_buffer(VI_FIND_BUFLEN)
    visa_library().viParseRsrcEx(session, resource_name, byref(interface_type),
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


def peek_8(vi, address):
    value_8 = ViUInt8()
    visa_library().viPeek8(vi, address, byref(value_8))
    return value_8.value


def peek_16(vi, address):
    value_16 = ViUInt16()
    visa_library().viPeek16(vi, address, byref(value_16))
    return value_16.value


def peek_32(vi, address):
    value_32 = ViUInt32()
    visa_library().viPeek32(vi, address, byref(value_32))
    return value_32.value


def poke_8(vi, address, value_8):
    visa_library().viPoke8(vi, address, value_8)


def poke_16(vi, address, value_16):
    visa_library().viPoke16(vi, address, value_16)


def poke_32(vi, address, value_32):
    visa_library().viPoke32(vi, address, value_32)


def printf(vi, write_format, *args):
    visa_library(force_cdecl=True).viPrintf(vi, write_format,
                                            *convert_argument_list(args))


def queryf(vi, write_format, read_format, write_args, *read_args, **keyw):
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(read_args))
    if write_args is None: write_args = ()
    visa_library(force_cdecl=True) \
        .viQueryf(vi, write_format, read_format,
                  *(convert_argument_list(write_args) +
                    convert_to_byref(argument_list,
                                     maximal_string_length)))
    return construct_return_tuple(argument_list)


def read(vi, count):
    buffer = create_string_buffer(count)
    return_count = ViUInt32()
    visa_library().viRead(vi, buffer, count, byref(return_count))
    return buffer.raw[:return_count.value]


def read_asynchronously(vi, count):
    buffer = create_string_buffer(count)
    job_id = ViJobId()
    visa_library().viReadAsync(vi, buffer, count, byref(job_id))
    return buffer, job_id


def read_stb(vi):
    status = ViUInt16()
    visa_library().viReadSTB(vi, byref(status))
    return status.value


def read_to_file(vi, filename, count):
    return_count = ViUInt32()
    visa_library().viReadToFile(vi, filename, count, return_count)
    return return_count

# FixMe: I have to test whether the results are really written to
# "argument_list" rather than only to a local copy within "viScanf".

def scanf(vi, read_format, *args, **keyw):
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    visa_library(force_cdecl=True) \
        .viScanf(vi, read_format,
                 *convert_to_byref(argument_list,
                                   maximal_string_length))
    return construct_return_tuple(argument_list)


def set_attribute(vi, attribute, attribute_state):
    visa_library().viSetAttribute(vi, attribute, attribute_state)


def set_buffer(vi, mask, size):
    visa_library().viSetBuf(vi, mask, size)


def sprintf(vi, write_format, *args, **keyw):
    buffer = create_string_buffer(keyw.get("buffer_length", 1024))
    visa_library(force_cdecl=True).viSPrintf(vi, buffer, write_format,
                                             *convert_argument_list(args))
    return buffer.raw


def sscanf(vi, buffer, read_format, *args, **keyw):
    maximal_string_length = keyw.get("maxmial_string_length", 1024)
    argument_list = list(convert_argument_list(args))
    visa_library(force_cdecl=True) \
        .viSScanf(vi, buffer, read_format,
                  *convert_to_byref(argument_list,
                                    maximal_string_length))
    return construct_return_tuple(argument_list)


def status_description(vi, status):
    description = create_string_buffer(256)
    visa_library().viStatusDesc(vi, status, description)
    return description.value


def terminate(vi, degree, job_id):
    visa_library().viTerminate(vi, degree, job_id)


def uninstall_handler(vi, event_type, handler, user_handle=None):
    for i in xrange(len(handlers)):
        element = handlers[i]
        if element[0] is handler and element[1] is user_handle:
            del handlers[i]
            break
    else:
        raise visa_exceptions.UnknownHandler
    visa_library().viUninstallHandler(vi, event_type, element[2],
                                      byref(element[1]))

def unlock(vi):
    visa_library().viUnlock(vi)


def unmap_address(vi):
    visa_library().viUnmapAddress(vi)


def unmap_trigger(vi, trigger_source, trigger_destination):
    visa_library().viUnmapTrigger(vi, trigger_source, trigger_destination)


def usb_control_in(vi, request_type_bitmap_field, request_id, request_value,
                   index, length=0):
    buffer = create_string_buffer(length)
    return_count = ViUInt16()
    visa_library().viUsbControlIn(vi, request_type_bitmap_field, request_id,
                                  request_value, index, length, buffer,
                                  byref(return_count))
    return buffer.raw[:return_count.value]


def usb_control_out(vi, request_type_bitmap_field, request_id, request_value,
                    index, buffer=""):
    length = len(buffer)
    visa_library().viUsbControlOut(vi, request_type_bitmap_field, request_id,
                                   request_value, index, length, buffer)

# The following variants make no sense in Python, so I realise them as mere
# aliases.

vprintf  = printf
vqueryf  = queryf
vscanf   = scanf
vsprintf = sprintf
vsscanf  = sscanf


def vxi_command_query(vi, mode, command):
    response = ViUInt32()
    visa_library().viVxiCommandQuery(vi, mode, command, byref(response))
    return response.value


def wait_on_event(vi, in_event_type, timeout):
    out_event_type = ViEventType()
    out_context = ViEvent()
    visa_library().viWaitOnEvent(vi, in_event_type, timeout,
                                 byref(out_event_type), byref(out_context))
    return out_event_type.value, out_context


def write(vi, buffer):
    return_count = ViUInt32()
    visa_library().viWrite(vi, buffer, len(buffer), byref(return_count))
    return return_count.value


def write_asynchronously(vi, buffer):
    job_id = ViJobId()
    visa_library().viWriteAsync(vi, buffer, len(buffer), byref(job_id))
    return job_id


def write_from_file(vi, filename, count):
    return_count = ViUInt32()
    visa_library().viWriteFromFile(vi, filename, count, return_count)
    return return_count
