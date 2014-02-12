# -*- coding: utf-8 -*-
"""
    pyvisa.legacy.vpp43
    ~~~~~~~~~~~~~~~~~~~

    Defines VPP 4.3.2 routines.

    This is a legacy module for backwards compatibility with PyVISA < 1.5

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

VI_SPEC_VERSION = 0x00300000

import os
import warnings
import functools

from ctypes import cdll, c_void_p, POINTER

from .. import errors
from .. import constants
from ..constants import *
from .. import ctwrapper
from ..ctwrapper import types

if os.name == 'nt':
    from ctypes import windll, WINFUNCTYPE as FUNCTYPE
else:
    from ctypes import CFUNCTYPE as FUNCTYPE


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

__all__.extend((name for name in dir(constants) if not name[0].startswith('_')))
__all__.extend((name for name in dir(errors) if not name[0].startswith('_')))

#: Global status code for the singleton library
visa_status = 0

def get_status():
    return visa_status

#: For these completion codes, warnings are issued.
dodgy_completion_codes = \
    [VI_SUCCESS_MAX_CNT, VI_SUCCESS_DEV_NPRESENT, VI_SUCCESS_SYNC,
    VI_WARN_QUEUE_OVERFLOW, VI_WARN_CONFIG_NLOADED, VI_WARN_NULL_OBJECT,
    VI_WARN_NSUP_ATTR_STATE, VI_WARN_UNKNOWN_STATUS, VI_WARN_NSUP_BUF,
    VI_WARN_EXT_FUNC_NIMPL]


def check_status(status, func=None, arguments=()):
    """Check return values for errors and warnings."""
    global visa_status
    visa_status = status
    if status < 0:
        raise errors.VisaIOError(status)
    if status in dodgy_completion_codes:
        abbreviation, description = errors.completion_and_error_messages[status]
        warnings.warn("%s: %s" % (abbreviation, description),
                      errors.VisaIOWarning, stacklevel=2)
    return status

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
        if os.name == 'nt':
            if path:
                self.__lib       = windll.LoadLibrary(path)
                self.__cdecl_lib = cdll.LoadLibrary(path)
            else:
                self.__lib       = windll.visa32
                self.__cdecl_lib = cdll.visa32
        elif os.name == 'posix':
            if not path:
                path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"
            self.__lib = self.__cdecl_lib = cdll.LoadLibrary(path)
        else:
            self.__lib = self.__cdecl_lib = None
            raise errors.OSNotSupported(os.name)
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
        ViHndlr = FUNCTYPE(types.ViStatus, types.ViSession, types.ViEventType, types.ViEvent,
                           user_handle_p)
        self.__lib.viInstallHandler.argtypes = [types.ViSession, types.ViEventType,
                                                ViHndlr, user_handle_p]
        self.__lib.viUninstallHandler.argtypes = [types.ViSession, types.ViEventType,
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
        ctwrapper.set_signatures(self.__lib, errcheck=check_status)
        ctwrapper.set_cdecl_signatures(self.__cdecl_lib, errcheck=check_status)


# Create a default instance for VisaLibrary
visa_library = VisaLibrary()

from ..util import read_user_library_path
_user_lib = read_user_library_path()

if _user_lib:
    visa_library.load_library(_user_lib)

# Load the functions defined in the wrapper module using the default VisaLibrary
for name in visa_functions:
    func = getattr(ctwrapper, name)
    locals()[name] = functools.partial(func, visa_library())


#: Contains all installed event handlers.
#: Its elements are tuples with three elements:
#: - The handler itself (a Python callable)
#: - the user handle (as a ctypes object)
#: - the handler again, this time as a ctypes object created with CFUNCTYPE.
handlers = []

def install_handler(vi, event_type, handler, user_handle=None):
    try:
        new_handler = ctwrapper.install_handler(visa_library(), vi, event_type, handler, user_handle)
    except TypeError as e:
        raise errors.VisaTypeError(str(e))

    handlers.append(new_handler)
    return new_handler[1]


def uninstall_handler(vi, event_type, handler, user_handle=None):
    for i in range(len(handlers)):
        element = handlers[i]
        if element[0] is handler and element[1] is user_handle:
            del handlers[i]
            break
    else:
        raise errors.UnknownHandler
    ctwrapper.uninstall_handler(visa_library(), vi, event_type, element[2], element[1])
