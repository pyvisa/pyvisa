# -*- coding: utf-8 -*-
"""
    pyvisa.highlevel
    ~~~~~~~~~~~~~~~~

    High level Visa library wrapper.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import contextlib
import collections
import pkgutil
import os
from collections import defaultdict
from weakref import WeakSet

from . import logger
from . import constants
from . import errors
from . import rname

#: Resource extended information
#:
#: Named tuple with information about a resource. Returned by some :class:`ResourceManager` methods.
#:
#: :interface_type: Interface type of the given resource string. :class:`pyvisa.constants.InterfaceType`
#: :interface_board_number: Board number of the interface of the given resource string.
#: :resource_class: Specifies the resource class (for example, "INSTR") of the given resource string.
#: :resource_name: This is the expanded version of the given resource string.
#:                       The format should be similar to the VISA-defined canonical resource name.
#: :alias: Specifies the user-defined alias for the given resource string.
ResourceInfo = collections.namedtuple('ResourceInfo',
                                      'interface_type interface_board_number '
                                      'resource_class resource_name alias')


class VisaLibraryBase(object):
    """Base for VISA library classes.

    A class derived from `VisaLibraryBase` library provides the low-level communication
    to the underlying devices providing Pythonic wrappers to VISA functions. But not all
    derived class must/will implement all methods.

    The default VisaLibrary class is :class:`pyvisa.ctwrapper.highlevel.NIVisaLibrary`,
    which implements a ctypes wrapper around the NI-VISA library.

    In general, you should not instantiate it directly. The object exposed to the user
    is the :class:`pyvisa.highlevel.ResourceManager`. If needed, you can access the
    VISA library from it::

        >>> import visa
        >>> rm = visa.ResourceManager("/path/to/my/libvisa.so.7")
        >>> lib = rm.visalib
    """

    #: Default ResourceManager instance for this library.
    resource_manager = None

    #: Maps library path to VisaLibrary object
    _registry = dict()

    #: Last return value of the library.
    _last_status = 0

    #: Maps session handle to last status. dict()
    _last_status_in_session = None

    #: Maps session handle to warnings to ignore. defaultdict(set)
    _ignore_warning_in_session = None

    #: Contains all installed event handlers.
    #: Its elements are tuples with three elements: The handler itself (a Python
    #: callable), the user handle (as a ct object) and the handler again, this
    #: time as a ct object created with CFUNCTYPE.
    handlers = None

    #: Set error codes on which to issue a warning. set
    issue_warning_on = None

    def __new__(cls, library_path=''):
        if library_path == '':
            errs = []
            for path in cls.get_library_paths():
                try:
                    return cls(path)
                except OSError as e:
                    logger.debug('Could not open VISA library %s: %s', path, str(e))
                    errs.append(str(e))
                except Exception as e:
                    errs.append(str(e))
            else:
                raise OSError('Could not open VISA library:\n' + '\n'.join(errs))

        if (cls, library_path) in cls._registry:
            return cls._registry[(cls, library_path)]

        obj = super(VisaLibraryBase, cls).__new__(cls)

        obj.library_path = library_path

        obj._logging_extra = {'library_path': obj.library_path}

        obj._init()

        # Create instance specific registries.
        #: Error codes on which to issue a warning.
        obj.issue_warning_on = set(errors.default_warnings)
        obj._last_status_in_session = dict()
        obj._ignore_warning_in_session = defaultdict(set)
        obj.handlers = defaultdict(list)

        logger.debug('Created library wrapper for %s', library_path)

        cls._registry[(cls, library_path)] = obj

        return obj

    @staticmethod
    def get_library_paths():
        """Override this method to return an iterable of possible library_paths
        to try in case that no argument is given.
        """
        return 'unset',

    @staticmethod
    def get_debug_info():
        """Override this method to return an iterable of lines with the backend debug details.
        """
        return ['Does not provide debug info']

    def _init(self):
        """Override this method to customize VisaLibrary initialization.
        """
        pass

    def __str__(self):
        return 'Visa Library at %s' % self.library_path

    def __repr__(self):
        return '<VisaLibrary(%r)>' % self.library_path

    @property
    def last_status(self):
        """Last return value of the library.
        """
        return self._last_status

    def get_last_status_in_session(self, session):
        """Last status in session.

        Helper function to be called by resources properties.
        """
        try:
            return self._last_status_in_session[session]
        except KeyError:
            raise errors.Error('The session %r does not seem to be valid as it does not have any last status' % session)

    @contextlib.contextmanager
    def ignore_warning(self, session, *warnings_constants):
        """A session dependent context for ignoring warnings

        :param session: Unique logical identifier to a session.
        :param warnings_constants: constants identifying the warnings to ignore.
        """
        self._ignore_warning_in_session[session].update(warnings_constants)
        yield
        self._ignore_warning_in_session[session].difference_update(warnings_constants)

    def install_visa_handler(self, session, event_type, handler, user_handle=None):
        """Installs handlers for event callbacks.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: user handle (a ctypes object)
        """
        try:
            new_handler = self.install_handler(session, event_type, handler, user_handle)
        except TypeError as e:
            raise errors.VisaTypeError(str(e))

        self.handlers[session].append(new_handler + (event_type,))
        return new_handler[1]

    def uninstall_visa_handler(self, session, event_type, handler, user_handle=None):
        """Uninstalls handlers for events.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: The user handle (ctypes object or None) returned by install_visa_handler.
        """
        for ndx, element in enumerate(self.handlers[session]):
            if element[0] is handler and element[1] is user_handle and element[4] == event_type:
                del self.handlers[session][ndx]
                break
        else:
            raise errors.UnknownHandler(event_type, handler, user_handle)
        self.uninstall_handler(session, event_type,  element[2], user_handle)

    def __uninstall_all_handlers_helper(self, session):
        for element in self.handlers[session]:
            self.uninstall_handler(session, element[4],  element[2], element[1])
        del self.handlers[session]

    def uninstall_all_visa_handlers(self, session):
        """Uninstalls all previously installed handlers for a particular session.

        :param session: Unique logical identifier to a session. If None, operates on all sessions.
        """

        if session is not None:
            self.__uninstall_all_handlers_helper(session)
        else:
            for session in list(self.handlers):
                self.__uninstall_all_handlers_helper(session)

    def read_memory(self, session, space, offset, width, extended=False):
        """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

        Corresponds to viIn* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        if width == 8:
            return self.in_8(session, space, offset, extended)
        elif width == 16:
            return self.in_16(session, space, offset, extended)
        elif width == 32:
            return self.in_32(session, space, offset, extended)
        elif width == 64:
            return self.in_64(session, space, offset, extended)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)

    def write_memory(self, session, space, offset, data, width, extended=False):
        """Write in an 8-bit, 16-bit, 32-bit, 64-bit value to the specified memory space and offset.

        Corresponds to viOut* functions of the VISA library.

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
            return self.out_8(session, space, offset, data, extended)
        elif width == 16:
            return self.out_16(session, space, offset, data, extended)
        elif width == 32:
            return self.out_32(session, space, offset, data, extended)
        elif width == 64:
            return self.out_64(session, space, offset, data, extended)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32, or 64' % width)

    def move_in(self, session, space, offset, length, width, extended=False):
        """Moves a block of data to local memory from the specified address space and offset.

        Corresponds to viMoveIn* functions of the VISA library.

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
            return self.move_in_8(session, space, offset, length, extended)
        elif width == 16:
            return self.move_in_16(session, space, offset, length, extended)
        elif width == 32:
            return self.move_in_32(session, space, offset, length, extended)
        elif width == 64:
            return self.move_in_64(session, space, offset, length, extended)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)

    def move_out(self, session, space, offset, length, data, width, extended=False):
        """Moves a block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut* functions of the VISA library.

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
            return self.move_out_8(session, space, offset, length, data, extended)
        elif width == 16:
            return self.move_out_16(session, space, offset, length, data, extended)
        elif width == 32:
            return self.move_out_32(session, space, offset, length, data, extended)
        elif width == 64:
            return self.move_out_64(session, space, offset, length, data, extended)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)

    def peek(self, session, address, width):
        """Read an 8, 16, 32, or 64-bit value from the specified address.

        Corresponds to viPeek* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param width: Number of bits to read.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """

        if width == 8:
            return self.peek_8(session, address)
        elif width == 16:
            return self.peek_16(session, address)
        elif width == 32:
            return self.peek_32(session, address)
        elif width == 64:
            return self.peek_64(session, address)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32 or 64' % width)

    def poke(self, session, address, width, data):
        """Writes an 8, 16, 32, or 64-bit value from the specified address.

        Corresponds to viPoke* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param width: Number of bits to read.
        :param data: Data to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """

        if width == 8:
            return self.poke_8(session, address, data)
        elif width == 16:
            return self.poke_16(session, address, data)
        elif width == 32:
            return self.poke_32(session, address, data)
        elif width == 64:
            return self.poke_64(session, address, data)

        raise ValueError('%s is not a valid size. Valid values are 8, 16, 32, or 64' % width)

    # Methods that VISA Library implementations must implement

    def assert_interrupt_signal(self, session, mode, status_id):
        """Asserts the specified interrupt or signal.

        Corresponds to viAssertIntrSignal function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: How to assert the interrupt. (Constants.ASSERT*)
        :param status_id: This is the status value to be presented during an interrupt acknowledge cycle.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def assert_trigger(self, session, protocol):
        """Asserts software or hardware trigger.

        Corresponds to viAssertTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param protocol: Trigger protocol to use during assertion. (Constants.PROT*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def assert_utility_signal(self, session, line):
        """Asserts or deasserts the specified utility bus signal.

        Corresponds to viAssertUtilSignal function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param line: specifies the utility bus signal to assert. (Constants.VI_UTIL_ASSERT*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def buffer_read(self, session, count):
        """Reads data from device or interface through the use of a formatted I/O read buffer.

        Corresponds to viBufRead function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: data read, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def buffer_write(self, session, data):
        """Writes data to a formatted I/O write buffer synchronously.

        Corresponds to viBufWrite function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :type data: bytes
        :return: number of written bytes, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def clear(self, session):
        """Clears a device.

        Corresponds to viClear function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def close(self, session):
        """Closes the specified session, event, or find list.

        Corresponds to viClose function of the VISA library.

        :param session: Unique logical identifier to a session, event, or find list.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def disable_event(self, session, event_type, mechanism):
        """Disables notification of the specified event type(s) via the specified mechanism(s).

        Corresponds to viDisableEvent function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be disabled.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def discard_events(self, session, event_type, mechanism):
        """Discards event occurrences for specified event types and mechanisms in a session.

        Corresponds to viDiscardEvents function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be discarded.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def enable_event(self, session, event_type, mechanism, context=None):
        """Enable event occurrences for specified event types and mechanisms in a session.

        Corresponds to viEnableEvent function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be enabled.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR)
        :param context:
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def flush(self, session, mask):
        """Manually flushes the specified buffers associated with formatted
        I/O operations and/or serial communication.

        Corresponds to viFlush function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mask: Specifies the action to be taken with flushing the buffer.
            The following values (defined in the constants module can be
            combined using the | operator. However multiple operations on a
            single buffer cannot be combined.
            - VI_READ_BUF: Discard the read buffer contents and if data was
              present in the read buffer and no END-indicator was present,
              read from the device until encountering an END indicator
              (which causes the loss of data).
            - VI_READ_BUF_DISCARD: Discard the read buffer contents (does not
              perform any I/O to the device).
            - VI_WRITE_BUF: Flush the write buffer by writing all buffered
              data to the device.
            - VI_WRITE_BUF_DISCARD: Discard the write buffer contents (does not
              perform any I/O to the device).
            - VI_IO_IN_BUF: Discards the receive buffer contents
              (same as VI_IO_IN_BUF_DISCARD).
            - VI_IO_IN_BUF_DISCARD: Discard the receive buffer contents (does
              not perform any I/O to the device).
            - VI_IO_OUT_BUF: Flush the transmit buffer by writing all buffered
              data to the device.
            - VI_IO_OUT_BUF_DISCARD: Discard the transmit buffer contents (does
              not perform any I/O to the device).
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def get_attribute(self, session, attribute):
        """Retrieves the state of an attribute.

        Corresponds to viGetAttribute function of the VISA library.

        :param session: Unique logical identifier to a session, event, or find list.
        :param attribute: Resource attribute for which the state query is made (see Attributes.*)
        :return: The state of the queried attribute for a specified resource, return value of the library call.
        :rtype: unicode (Py2) or str (Py3), list or other type, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_command(self, session, data):
        """Write GPIB command bytes on the bus.

        Corresponds to viGpibCommand function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data tor write.
        :type data: bytes
        :return: Number of written bytes, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_control_atn(self, session, mode):
        """Specifies the state of the ATN line and the local active controller state.

        Corresponds to viGpibControlATN function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                     (Constants.VI_GPIB_ATN*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_control_ren(self, session, mode):
        """Controls the state of the GPIB Remote Enable (REN) interface line, and optionally the remote/local
        state of the device.

        Corresponds to viGpibControlREN function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies the state of the REN line and optionally the device remote/local state.
                     (Constants.VI_GPIB_REN*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_pass_control(self, session, primary_address, secondary_address):
        """Tell the GPIB device at the specified address to become controller in charge (CIC).

        Corresponds to viGpibPassControl function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param primary_address: Primary address of the GPIB device to which you want to pass control.
        :param secondary_address: Secondary address of the targeted GPIB device.
                                  If the targeted device does not have a secondary address,
                                  this parameter should contain the value Constants.VI_NO_SEC_ADDR.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_send_ifc(self, session):
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        Corresponds to viGpibSendIFC function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_8(self, session, space, offset, extended=False):
        """Reads in an 8-bit value from the specified memory space and offset.

        Corresponds to viIn8* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_16(self, session, space, offset, extended=False):
        """Reads in an 16-bit value from the specified memory space and offset.

        Corresponds to viIn16* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_32(self, session, space, offset, extended=False):
        """Reads in an 32-bit value from the specified memory space and offset.

        Corresponds to viIn32* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_64(self, session, space, offset, extended=False):
        """Reads in an 64-bit value from the specified memory space and offset.

        Corresponds to viIn64* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def install_handler(self, session, event_type, handler, user_handle):
        """Installs handlers for event callbacks.

        Corresponds to viInstallHandler function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: a handler descriptor which consists of three elements:
                 - handler (a python callable)
                 - user handle (a ctypes object)
                 - ctypes handler (ctypes object wrapping handler)
                 and return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def list_resources(self, session, query='?*::INSTR'):
        """Returns a tuple of all connected devices matching query.

        :param query: regular expression used to match devices.
        """
        raise NotImplementedError

    def lock(self, session, lock_type, timeout, requested_key=None):
        """Establishes an access mode to the specified resources.

        Corresponds to viLock function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param lock_type: Specifies the type of lock requested, either Constants.EXCLUSIVE_LOCK or Constants.SHARED_LOCK.
        :param timeout: Absolute time period (in milliseconds) that a resource waits to get unlocked by the
                        locking session before returning an error.
        :param requested_key: This parameter is not used and should be set to VI_NULL when lockType is VI_EXCLUSIVE_LOCK.
        :return: access_key that can then be passed to other sessions to share the lock, return value of the library call.
        :rtype: str, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def map_address(self, session, map_space, map_base, map_size,
                    access=False, suggested=None):
        """Maps the specified memory space into the process's address space.

        Corresponds to viMapAddress function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param map_space: Specifies the address space to map. (Constants.*SPACE*)
        :param map_base: Offset (in bytes) of the memory to be mapped.
        :param map_size: Amount of memory to map (in bytes).
        :param access:
        :param suggested: If not Constants.VI_NULL (0), the operating system attempts to map the memory to the address
                          specified in suggested. There is no guarantee, however, that the memory will be mapped to
                          that address. This operation may map the memory into an address region different from
                          suggested.

        :return: address in your process space where the memory was mapped, return value of the library call.
        :rtype: address, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def map_trigger(self, session, trigger_source, trigger_destination, mode):
        """Map the specified trigger source line to the specified destination line.

        Corresponds to viMapTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param trigger_source: Source line from which to map. (Constants.VI_TRIG*)
        :param trigger_destination: Destination line to which to map. (Constants.VI_TRIG*)
        :param mode:
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def memory_allocation(self, session, size, extended=False):
        """Allocates memory from a resource's memory region.

        Corresponds to viMemAlloc* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param size: Specifies the size of the allocation.
        :param extended: Use 64 bits offset independent of the platform.
        :return: offset of the allocated memory, return value of the library call.
        :rtype: offset, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def memory_free(self, session, offset, extended=False):
        """Frees memory previously allocated using the memory_allocation() operation.

        Corresponds to viMemFree* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param offset: Offset of the memory to free.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move(self, session, source_space, source_offset, source_width, destination_space,
             destination_offset, destination_width, length):
        """Moves a block of data.

        Corresponds to viMove function of the VISA library.

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
        raise NotImplementedError

    def move_asynchronously(self, session, source_space, source_offset, source_width,
                            destination_space, destination_offset,
                            destination_width, length):
        """Moves a block of data asynchronously.

        Corresponds to viMoveAsync function of the VISA library.

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
        raise NotImplementedError

    def move_in_8(self, session, space, offset, length, extended=False):
        """Moves an 8-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn8* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_16(self, session, space, offset, length, extended=False):
        """Moves an 16-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn16* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_32(self, session, space, offset, length, extended=False):
        """Moves an 32-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn32* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_64(self, session, space, offset, length, extended=False):
        """Moves an 64-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn64* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_out_8(self, session, space, offset, length, data, extended=False):
        """Moves an 8-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut8* functions of the VISA library.

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
        raise NotImplementedError

    def move_out_16(self, session, space, offset, length, data, extended=False):
        """Moves an 16-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut16* functions of the VISA library.

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
        raise NotImplementedError

    def move_out_32(self, session, space, offset, length, data, extended=False):
        """Moves an 32-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut32* functions of the VISA library.

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
        raise NotImplementedError

    def move_out_64(self, session, space, offset, length, data, extended=False):
        """Moves an 64-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut64* functions of the VISA library.

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
        raise NotImplementedError

    def open(self, session, resource_name,
             access_mode=constants.AccessModes.no_lock, open_timeout=constants.VI_TMO_IMMEDIATE):
        """Opens a session to the specified resource.

        Corresponds to viOpen function of the VISA library.

        :param session: Resource Manager session (should always be a session returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int
        :return: Unique logical identifier reference to a session, return value of the library call.
        :rtype: session, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def open_default_resource_manager(self):
        """This function returns a session to the Default Resource Manager resource.

        Corresponds to viOpenDefaultRM function of the VISA library.

        :return: Unique logical identifier to a Default Resource Manager session, return value of the library call.
        :rtype: session, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_8(self, session, space, offset, data, extended=False):
        """Write in an 8-bit value from the specified memory space and offset.

        Corresponds to viOut8* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_16(self, session, space, offset, data, extended=False):
        """Write in an 16-bit value from the specified memory space and offset.

        Corresponds to viOut16* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_32(self, session, space, offset, data, extended=False):
        """Write in an 32-bit value from the specified memory space and offset.

        Corresponds to viOut32* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_64(self, session, space, offset, data, extended=False):
        """Write in an 64-bit value from the specified memory space and offset.

        Corresponds to viOut64* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def parse_resource(self, session, resource_name):
        """Parse a resource string to get the interface information.

        Corresponds to viParseRsrc function of the VISA library.

        :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                        returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :return: Resource information with interface type and board number, return value of the library call.
        :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
        """
        return self.parse_resource_extended(session, resource_name)

    def parse_resource_extended(self, session, resource_name):
        """Parse a resource string to get extended interface information.

        Corresponds to viParseRsrcEx function of the VISA library.

        :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                        returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :return: Resource information, return value of the library call.
        :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
        """
        try:
            parsed = rname.parse_resource_name(resource_name)

            return (ResourceInfo(parsed.interface_type_const,
                                 parsed.board,
                                 parsed.resource_class,
                                 str(parsed), None),
                    constants.StatusCode.success)
        except ValueError:
            return 0, constants.StatusCode.error_invalid_resource_name

    def peek_8(self, session, address):
        """Read an 8-bit value from the specified address.

        Corresponds to viPeek8 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_16(self, session, address):
        """Read an 16-bit value from the specified address.

        Corresponds to viPeek16 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_32(self, session, address):
        """Read an 32-bit value from the specified address.

        Corresponds to viPeek32 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_64(self, session, address):
        """Read an 64-bit value from the specified address.

        Corresponds to viPeek64 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_8(self, session, address, data):
        """Write an 8-bit value from the specified address.

        Corresponds to viPoke8 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: Data read from bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_16(self, session, address, data):
        """Write an 16-bit value from the specified address.

        Corresponds to viPoke16 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_32(self, session, address, data):
        """Write an 32-bit value from the specified address.

        Corresponds to viPoke32 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_64(self, session, address, data):
        """Write an 64-bit value from the specified address.

        Corresponds to viPoke64 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read(self, session, count):
        """Reads data from device or interface synchronously.

        Corresponds to viRead function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: data read, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_asynchronously(self, session, count):
        """Reads data from device or interface asynchronously.

        Corresponds to viReadAsync function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: result, jobid, return value of the library call.
        :rtype: ctypes buffer, jobid, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_stb(self, session):
        """Reads a status byte of the service request.

        Corresponds to viReadSTB function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: Service request status byte, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_to_file(self, session, filename, count):
        """Read data synchronously, and store the transferred data in a file.

        Corresponds to viReadToFile function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param filename: Name of file to which data will be written.
        :param count: Number of bytes to be read.
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def set_attribute(self, session, attribute, attribute_state):
        """Sets the state of an attribute.

        Corresponds to viSetAttribute function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param attribute: Attribute for which the state is to be modified. (Attributes.*)
        :param attribute_state: The state of the attribute to be set for the specified object.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def set_buffer(self, session, mask, size):
        """Sets the size for the formatted I/O and/or low-level I/O communication buffer(s).

        Corresponds to viSetBuf function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mask: Specifies the type of buffer. (Constants.VI_READ_BUF, .VI_WRITE_BUF, .VI_IO_IN_BUF, .VI_IO_OUT_BUF)
        :param size: The size to be set for the specified buffer(s).
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def status_description(self, session, status):
        """Returns a user-readable description of the status code passed to the operation.

        Corresponds to viStatusDesc function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param status: Status code to interpret.
        :return: - The user-readable string interpretation of the status code passed to the operation,
                 - return value of the library call.
        :rtype: - unicode (Py2) or str (Py3)
                - :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def terminate(self, session, degree, job_id):
        """Requests a VISA session to terminate normal execution of an operation.

        Corresponds to viTerminate function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param degree: Constants.NULL
        :param job_id: Specifies an operation identifier.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def uninstall_handler(self, session, event_type, handler, user_handle=None):
        """Uninstalls handlers for events.

        Corresponds to viUninstallHandler function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely in a session for an event.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unlock(self, session):
        """Relinquishes a lock for the specified resource.

        Corresponds to viUnlock function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unmap_address(self, session):
        """Unmaps memory space previously mapped by map_address().

        Corresponds to viUnmapAddress function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unmap_trigger(self, session, trigger_source, trigger_destination):
        """Undo a previous map from the specified trigger source line to the specified destination line.

        Corresponds to viUnmapTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param trigger_source: Source line used in previous map. (Constants.VI_TRIG*)
        :param trigger_destination: Destination line used in previous map. (Constants.VI_TRIG*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def usb_control_in(self, session, request_type_bitmap_field, request_id, request_value,
                       index, length=0):
        """Performs a USB control pipe transfer from the device.

        Corresponds to viUsbControlIn function of the VISA library.

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
        raise NotImplementedError

    def usb_control_out(self, session, request_type_bitmap_field, request_id, request_value,
                        index, data=""):
        """Performs a USB control pipe transfer to the device.

        Corresponds to viUsbControlOut function of the VISA library.

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
        raise NotImplementedError

    def vxi_command_query(self, session, mode, command):
        """Sends the device a miscellaneous command or query and/or retrieves the response to a previous query.

        Corresponds to viVxiCommandQuery function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies whether to issue a command and/or retrieve a response. (Constants.VI_VXI_CMD*, .VI_VXI_RESP*)
        :param command: The miscellaneous command to send.
        :return: The response retrieved from the device, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def wait_on_event(self, session, in_event_type, timeout):
        """Waits for an occurrence of the specified event for a given session.

        Corresponds to viWaitOnEvent function of the VISA library.

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
        raise NotImplementedError

    def write(self, session, data):
        """Writes data to device or interface synchronously.

        Corresponds to viWrite function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :type data: str
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def write_asynchronously(self, session, data):
        """Writes data to device or interface asynchronously.

        Corresponds to viWriteAsync function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :return: Job ID of this asynchronous write operation, return value of the library call.
        :rtype: jobid, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def write_from_file(self, session, filename, count):
        """Take data from a file and write it out synchronously.

        Corresponds to viWriteFromFile function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param filename: Name of file from which data will be read.
        :param count: Number of bytes to be written.
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError


def list_backends():
    """Return installed backends.

    Backends are installed python packages named pyvisa-<something> where <something>
    is the name of the backend.

    :rtype: list
    """
    return ['ni'] + [name for (loader, name, ispkg) in pkgutil.iter_modules()
                     if name.startswith('pyvisa-') and not name.endswith('-script')]


#: Maps backend name to VisaLibraryBase derived class
#: dict[str, :class:`pyvisa.highlevel.VisaLibraryBase`]
_WRAPPERS = {}


def get_wrapper_class(backend_name):
    """Return the WRAPPER_CLASS for a given backend.

    :rtype: pyvisa.highlevel.VisaLibraryBase
    """
    try:
        return _WRAPPERS[backend_name]
    except KeyError:
        if backend_name == 'ni':
            from .ctwrapper import NIVisaLibrary
            _WRAPPERS['ni'] = NIVisaLibrary
            return NIVisaLibrary

    try:
        pkg = __import__('pyvisa-' + backend_name)
        _WRAPPERS[backend_name] = cls = pkg.WRAPPER_CLASS
        return cls
    except ImportError:
        raise ValueError('Wrapper not found: No package named pyvisa-%s' % backend_name)


def _get_default_wrapper():
    """Return an available default VISA wrapper as a string ('ni' or 'py').

    Use NI if the binary is found, else try to use pyvisa-py.
    If neither can be found, raise a ValueError.
    """

    from .ctwrapper import NIVisaLibrary
    ni_binary_found = bool(NIVisaLibrary.get_library_paths())
    if ni_binary_found:
        logger.debug('The NI implementation available')
        return 'ni'
    else:
        logger.debug('Did not find NI binary')

    try:
        get_wrapper_class('py')  # check for pyvisa-py availability
        logger.debug('pyvisa-py is available.')
        return 'py'
    except ValueError:
        logger.debug('Did not find pyvisa-py package')
    raise ValueError('Could not locate a VISA implementation. Install either the NI binary or pyvisa-py.')


def open_visa_library(specification):
    """Helper function to create a VISA library wrapper.

    In general, you should not use the function directly. The VISA library
    wrapper will be created automatically when you create a ResourceManager object.
    """

    if not specification:
        logger.debug('No visa library specified, trying to find alternatives.')
        try:
            specification = os.environ['PYVISA_LIBRARY']
        except KeyError:
            logger.debug('Environment variable PYVISA_LIBRARY is unset.')

    try:
        argument, wrapper = specification.split('@')
    except ValueError:
        argument = specification
        wrapper = None  # Flag that we need a fallback, but avoid nested exceptions
    if wrapper is None:
        if argument: # some filename given
            wrapper = 'ni'
        else:
            wrapper = _get_default_wrapper()

    cls = get_wrapper_class(wrapper)

    try:
        return cls(argument)
    except Exception as e:
        logger.debug('Could not open VISA wrapper %s: %s\n%s', cls, str(argument), e)
        raise


class ResourceManager(object):
    """VISA Resource Manager

    :param visa_library: VisaLibrary Instance, path of the VISA library or VisaLibrary spec string.
                         (if not given, the default for the platform will be used).
    """

    #: Maps (Interface Type, Resource Class) to Python class encapsulating that resource.
    _resource_classes = dict()

    #: Session handler for the resource manager.
    _session = None

    @classmethod
    def register_resource_class(cls, interface_type, resource_class, python_class):
        if (interface_type, resource_class) in cls._resource_classes:
            logger.warning('%s is already registered in the ResourceManager. '
                           'Overwriting with %s' % ((interface_type, resource_class), python_class))
        cls._resource_classes[(interface_type, resource_class)] = python_class

    def __new__(cls, visa_library=''):
        if not isinstance(visa_library, VisaLibraryBase):
            visa_library = open_visa_library(visa_library)

        if visa_library.resource_manager is not None:
            obj = visa_library.resource_manager
            logger.debug('Reusing ResourceManager with session %s',  obj.session)
            return obj

        obj = super(ResourceManager, cls).__new__(cls)

        obj.session, err = visa_library.open_default_resource_manager()

        obj.visalib = visa_library
        obj.visalib.resource_manager = obj
        obj._created_resources = WeakSet()

        logger.debug('Created ResourceManager with session %s',  obj.session)
        return obj

    @property
    def session(self):
        """Resource Manager session handle.

        :raises: :class:`pyvisa.errors.InvalidSession` if session is closed.
        """
        if self._session is None:
            raise errors.InvalidSession()
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def __str__(self):
        return 'Resource Manager of %s' % self.visalib

    def __repr__(self):
        return '<ResourceManager(%r)>' % self.visalib

    def __del__(self):
        if self._session is not None:
            self.close()

    def ignore_warning(self, *warnings_constants):
        """Ignoring warnings context manager for the current resource.

        :param warnings_constants: constants identifying the warnings to ignore.
        """
        return self.visalib.ignore_warning(self.session, *warnings_constants)

    @property
    def last_status(self):
        """Last status code returned for an operation with this Resource Manager

        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        return self.visalib.get_last_status_in_session(self.session)

    def close(self):
        """Close the resource manager session.

        """
        try:
            logger.debug('Closing ResourceManager (session: %s)', self.session)
            # Cleanly close all resources when closing the manager.
            for resource in self._created_resources:
                resource.close()
            self.visalib.close(self.session)
            self.session = None
            self.visalib.resource_manager = None
        except errors.InvalidSession:
            pass

    def list_resources(self, query='?*::INSTR'):
        """Returns a tuple of all connected devices matching query.

        note: The query uses the VISA Resource Regular Expression syntax - which is not the same
              as the Python regular expression syntax. (see below)

            The VISA Resource Regular Expression syntax is defined in the VISA Library specification:
            http://www.ivifoundation.org/docs/vpp43.pdf

            Symbol      Meaning
            ----------  ----------

            ?           Matches any one character.

            \           Makes the character that follows it an ordinary character
                        instead of special character. For example, when a question
                        mark follows a backslash (\?), it matches the ? character
                        instead of any one character.

            [list]      Matches any one character from the enclosed list. You can
                        use a hyphen to match a range of characters.

            [^list]     Matches any character not in the enclosed list. You can use
                        a hyphen to match a range of characters.

            *           Matches 0 or more occurrences of the preceding character or
                        expression.

            +           Matches 1 or more occurrences of the preceding character or
                        expression.

            Exp|exp     Matches either the preceding or following expression. The or
                        operator | matches the entire expression that precedes or
                        follows it and not just the character that precedes or follows
                        it. For example, VXI|GPIB means (VXI)|(GPIB), not VX(I|G)PIB.

            (exp)       Grouping characters or expressions.

            Thus the default query, '?*::INSTR', matches any sequences of characters ending
            ending with '::INSTR'.

        :param query: a VISA Resource Regular Expression used to match devices.

        """

        return self.visalib.list_resources(self.session, query)

    def list_resources_info(self, query='?*::INSTR'):
        """Returns a dictionary mapping resource names to resource extended
        information of all connected devices matching query.

        For details of the VISA Resource Regular Expression syntax used in query,
        refer to list_resources().

        :param query: a VISA Resource Regular Expression used to match devices.
        :return: Mapping of resource name to ResourceInfo
        :rtype: dict[str, :class:`pyvisa.highlevel.ResourceInfo`]
        """

        return dict((resource, self.resource_info(resource))
                    for resource in self.list_resources(query))

    def list_opened_resources(self):
        """Returns a list of all the opened resources.

        :return: List of resources
        :rtype: list[:class:`pyvisa.resources.resource.Resource`]
        """
        return list(self._created_resources)

    def resource_info(self, resource_name, extended=True):
        """Get the (extended) information of a particular resource.

        :param resource_name: Unique symbolic name of a resource.

        :rtype: :class:`pyvisa.highlevel.ResourceInfo`
        """

        if extended:
            ret, err = self.visalib.parse_resource_extended(self.session, resource_name)
        else:
            ret, err = self.visalib.parse_resource(self.session, resource_name)

        return ret

    def open_bare_resource(self, resource_name,
                          access_mode=constants.AccessModes.no_lock,
                          open_timeout=constants.VI_TMO_IMMEDIATE):
        """Open the specified resource without wrapping into a class

        :param resource_name: Name or alias of the resource to open.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int

        :return: Unique logical identifier reference to a session.
        """
        return self.visalib.open(self.session, resource_name, access_mode, open_timeout)

    def open_resource(self, resource_name,
                      access_mode=constants.AccessModes.no_lock,
                      open_timeout=constants.VI_TMO_IMMEDIATE,
                      resource_pyclass=None,
                      **kwargs):
        """Return an instrument for the resource name.

        :param resource_name: Name or alias of the resource to open.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int
        :param resource_pyclass: Resource Python class to use to instantiate the Resource.
                                 Defaults to None: select based on the resource name.
        :param kwargs: Keyword arguments to be used to change instrument attributes
                       after construction.

        :rtype: :class:`pyvisa.resources.Resource`
        """

        if resource_pyclass is None:
            info = self.resource_info(resource_name, extended=True)

            try:
                resource_pyclass = self._resource_classes[(info.interface_type, info.resource_class)]
            except KeyError:
                resource_pyclass = self._resource_classes[(constants.InterfaceType.unknown, '')]
                logger.warning('There is no class defined for %r. Using Resource', (info.interface_type, info.resource_class))

        res = resource_pyclass(self, resource_name)
        for key in kwargs.keys():
            try:
                getattr(res, key)
                present = True
            except AttributeError:
                present = False
            except errors.InvalidSession:
                present = True

            if not present:
                raise ValueError('%r is not a valid attribute for type %s' % (key, res.__class__.__name__))

        res.open(access_mode, open_timeout)

        self._created_resources.add(res)

        for key, value in kwargs.items():
            setattr(res, key, value)

        return res

    #: For backwards compatibility
    get_instrument = open_resource
