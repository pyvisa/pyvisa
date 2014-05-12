# -*- coding: utf-8 -*-
"""
    pyvisa.highlevel
    ~~~~~~~~~~~~~~~~

    High level Visa library wrapper.

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

import time
import atexit
import warnings
import contextlib
from collections import defaultdict

from . import logger
from .constants import *
from . import ctwrapper
from . import errors
from .util import (warning_context, split_kwargs, warn_for_invalid_kwargs,
                   parse_ascii, parse_binary, get_library_paths)


def add_visa_methods(wrapper_module):
    """Decorator factory to add methods in `wrapper_module.visa_functions`
    iterable to a class.

    :param wrapper_module: the python module/package that wraps the visa library.
    """
    def _internal(aclass):
        aclass._wrapper_module = wrapper_module
        methods = wrapper_module.visa_functions
        for method in methods:
            if hasattr(aclass, method):
                setattr(aclass, '_' + method, getattr(wrapper_module, method))
            else:
                setattr(aclass, method, getattr(wrapper_module, method))
        return aclass
    return _internal


@add_visa_methods(ctwrapper)
class VisaLibrary(object):
    """High level VISA Library wrapper.

    The easiest way to instantiate the library is to let `pyvisa` find the
    right one for you. This looks first in your configuration file (~/.pyvisarc).
    If it fails, it uses `ctypes.util.find_library` to try to locate a library
    in a way similar to what the compiler does:

       >>> visa_library = VisaLibrary()

    But you can also specify the path:

        >>> visa_library = VisaLibrary('/my/path/visa.so')

    Or use the `from_paths` constructor if you want to try multiple paths:

        >>> visa_library = VisaLibrary.from_paths(['/my/path/visa.so', '/maybe/this/visa.so'])

    :param library_path: path of the VISA library.
    """

    #: Maps library path to VisaLibrary object
    _registry = dict()

    @classmethod
    def from_paths(cls, *paths):
        """Helper constructor that tries to instantiate VisaLibrary from an
        iterable of possible library paths.
        """
        errs = []
        for path in paths:
            try:
                return cls(path)
            except OSError as e:
                logger.debug('Could not open VISA library %s: %s', path, str(e))
                errs.append(str(e))
        else:
            raise OSError('Could not open VISA library:\n' + '\n'.join(errs))

    def __new__(cls, library_path=None):
        if library_path is None:
            paths = get_library_paths(cls._wrapper_module)
            if not paths:
                raise OSError('Could not found VISA library. '
                              'Please install VISA or pass its location as an argument.')
            return cls.from_paths(*paths)
        else:
            if library_path in cls._registry:
                return cls._registry[library_path]

            cls._registry[library_path] = obj = super(VisaLibrary, cls).__new__(cls)

        try:
            obj.lib = cls._wrapper_module.Library(library_path)
        except OSError as exc:
            raise errors.LibraryError.from_exception(exc, library_path)

        obj.library_path = library_path

        logger.debug('Created library wrapper for %s', library_path)

        # Set the argtypes, restype and errcheck for each function
        # of the visa library. Additionally store in `_functions` the
        # name of the functions.
        cls._wrapper_module.set_signatures(obj.lib, errcheck=obj._return_handler)

        # Set the library functions as attributes of the object.
        for method_name in getattr(obj.lib, '_functions', []):
            setattr(obj, method_name, getattr(obj.lib, method_name))

        #: Error codes on which to issue a warning.
        obj.issue_warning_on = set([VI_SUCCESS_MAX_CNT, VI_SUCCESS_DEV_NPRESENT,
                                    VI_SUCCESS_SYNC, VI_WARN_QUEUE_OVERFLOW,
                                    VI_WARN_CONFIG_NLOADED, VI_WARN_NULL_OBJECT,
                                    VI_WARN_NSUP_ATTR_STATE, VI_WARN_UNKNOWN_STATUS,
                                    VI_WARN_NSUP_BUF, VI_WARN_EXT_FUNC_NIMPL])

        #: Contains all installed event handlers.
        #: Its elements are tuples with three elements: The handler itself (a Python
        #: callable), the user handle (as a ct object) and the handler again, this
        #: time as a ct object created with CFUNCTYPE.
        obj.handlers = defaultdict(list)

        #: Last return value of the library.
        obj._status = 0

        #: Default ResourceManager instance for this library.
        obj._resource_manager = None
        return obj

    def __str__(self):
        return 'Visa Library at %s' % self.library_path

    def __repr__(self):
        return '<VisaLibrary(%r)>' % self.library_path

    @property
    def status(self):
        """Last return value of the library.
        """
        return self._status

    @property
    def resource_manager(self):
        """Default resource manager object for this library.
        """
        if self._resource_manager is None:
            self._resource_manager = ResourceManager(self)
        return self._resource_manager

    def _return_handler(self, ret_value, func, arguments):
        """Check return values for errors and warnings.
        """

        logger.debug('%s: %s%s -> %s',
                     self, func.__name__, arguments, ret_value)

        self._status = ret_value

        if ret_value < 0:
            raise errors.VisaIOError(ret_value)

        if ret_value in self.issue_warning_on:
            warnings.warn(errors.VisaIOWarning(ret_value), stacklevel=2)

        return ret_value

    def install_handler(self, session, event_type, handler, user_handle=None):
        """Installs handlers for event callbacks.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: user handle (a ctypes object)
        """
        try:
            new_handler = self._install_handler(self.lib, session, event_type, handler, user_handle)
        except TypeError as e:
            raise errors.VisaTypeError(str(e))

        self.handlers[session].append(new_handler)
        return new_handler[1]

    def uninstall_handler(self, session, event_type, handler, user_handle=None):
        """Uninstalls handlers for events.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely in a session for an event.
        """
        for ndx, element in enumerate(self.handlers[session]):
            if element[0] is handler and element[1] is user_handle:
                del self.handlers[session][ndx]
                break
        else:
            raise errors.UnknownHandler(event_type, handler, user_handle)
        self._uninstall_handler(self.lib, session, event_type, handler, user_handle)


class ResourceManager(object):
    """VISA Resource Manager

    :param visa_library: VisaLibrary Instance or path of the VISA library
                         (if not given, the default for the platform will be used).
    """

    #: Maps VisaLibrary instance to ResourceManager
    _registry = dict()

    def __new__(cls, visa_library=None):
        if visa_library is None or isinstance(visa_library, str):
            visa_library = VisaLibrary(visa_library)

        if visa_library in cls._registry:
            return cls._registry[visa_library]

        cls._registry[visa_library] = obj = super(ResourceManager, cls).__new__(cls)

        obj.visalib = visa_library

        obj.session = obj.visalib.open_default_resource_manager()
        logger.debug('Created ResourceManager (session: %s) for %s',  obj.session, obj.visalib)
        return obj

    def __str__(self):
        return 'Resource Manager of %s' % self.visalib

    def __repr__(self):
        return '<ResourceManager(%r)>' % self.visalib

    def __del__(self):
        self.close()

    def close(self):
        if self.session is not None:
            logger.debug('Closing ResourceManager (session: %s) for %s', self.session, self.visalib)
            self.visalib.close(self.session)
            self.session = None

    def list_resources(self, query='?*::INSTR'):
        """Returns a tuple of all connected devices matching query.

        :param query: regular expression used to match devices.
        """

        lib = self.visalib

        resources = []
        find_list, return_counter, instrument_description = lib.find_resources(self.session, query)
        resources.append(instrument_description)
        for i in range(return_counter - 1):
            resources.append(lib.find_next(find_list))

        return tuple(resource for resource in resources)

    def list_resources_info(self, query='?*::INSTR'):
        """Returns a dictionary mapping resource names to resource extended
        information of all connected devices matching query.

        :param query: regular expression used to match devices.
        :return: Mapping of resource name to ResourceInfo
        :rtype: dict
        """

        return dict((resource, self.resource_info(resource))
                    for resource in self.list_resources(query))

    def resource_info(self, resource_name):
        """Get the extended information of a particular resource

        :param resource_name: Unique symbolic name of a resource.

        :rtype: ResourceInfo
        """
        return self.visalib.parse_resource_extended(self.session, resource_name)

    def open_resource(self, resource_name, access_mode=VI_NO_LOCK, open_timeout=VI_TMO_IMMEDIATE):
        """Open the specified resources.

        :param resource_name: name or alias of the resource to open.
        :param access_mode: access mode.
        :param open_timeout: time out to open.

        :return: Unique logical identifier reference to a session.
        """
        return self.visalib.open(self.session, resource_name, access_mode, open_timeout)

    def get_instrument(self, resource_name, **kwargs):
        """Return an instrument for the resource name.

        :param resource_name: name or alias of the resource to open.
        :param kwargs: keyword arguments to be passed to the instrument constructor.
        """
        interface_type = self.resource_info(resource_name).interface_type

        if interface_type == VI_INTF_GPIB:
            return GpibInstrument(resource_name, resource_manager=self, **kwargs)
        elif interface_type == VI_INTF_ASRL:
            return SerialInstrument(resource_name, resource_manager=self, **kwargs)
        else:
            return Instrument(resource_name, resource_manager=self, **kwargs)


class _BaseInstrument(object):
    """Base class for instruments.

    :param resource_name: the VISA name for the resource (eg. "GPIB::10")
                          If None, it's assumed that the resource manager
                          is to be constructed.
    :param resource_manager: A resource manager instance.
                             If None, the default resource manager will be used.
    :param lock:
    :param timeout:

    See :class:Instrument for a detailed description.
    """

    DEFAULT_KWARGS = {'lock': VI_NO_LOCK,
                      'timeout': 5}

    def __init__(self, resource_name=None, resource_manager=None, **kwargs):
        warn_for_invalid_kwargs(kwargs, _BaseInstrument.DEFAULT_KWARGS.keys())

        self.resource_manager = resource_manager or get_resource_manager()
        self.visalib = self.resource_manager.visalib
        self._resource_name = resource_name

        self.open()

        for key, value in _BaseInstrument.DEFAULT_KWARGS.items():
            setattr(self, key, kwargs.get(key, value))

    def open(self, lock=VI_NO_LOCK, timeout=5):
        with warning_context("ignore", "VI_SUCCESS_DEV_NPRESENT"):
            self.session = self.resource_manager.open_resource(self._resource_name, lock)

            if self.visalib.status == VI_SUCCESS_DEV_NPRESENT:
                # okay, the device was not ready when we opened the session.
                # Now it gets five seconds more to become ready.
                # Every 0.1 seconds we probe it with viClear.
                start_time = time.time()
                sleep_time = 0.1
                try_time = 5
                while time.time() - start_time < try_time:
                    time.sleep(sleep_time)
                    try:
                        self.clear()
                        break
                    except errors.VisaIOError as error:
                        if error.error_code != VI_ERROR_NLISTENERS:
                            raise

        if timeout is None:
            self.set_visa_attribute(VI_ATTR_TMO_VALUE, VI_TMO_INFINITE)
        else:
            self.timeout = timeout

    def close(self):
        """Closes the VISA session and marks the handle as invalid.
        """
        if self.resource_manager.session is None or self.session is None:
            return

        logger.debug('Closing Instrument (session: %s) for %s', self.session, self.visalib)
        self.visalib.close(self.session)
        self.session = None

    def __del__(self):
        self.close()

    def __str__(self):
        return "%s at %s" % (self.__class__.__name__, self.resource_name)

    def __repr__(self):
        return "<%r(%r)>" % (self.__class__.__name__, self.resource_name)

    def get_visa_attribute(self, name):
        return self.visalib.get_attribute(self.session, name)

    def set_visa_attribute(self, name, status):
        self.visalib.set_attribute(self.session, name, status)

    def clear(self):
        self.visalib.clear(self.session)

    @property
    def timeout(self):
        """The timeout in seconds for all resource I/O operations.

        Note that the VISA library may round up this value heavily.  I
        experienced that my NI VISA implementation had only the values 0, 1, 3
        and 10 seconds.

        """
        timeout = self.get_visa_attribute(VI_ATTR_TMO_VALUE)
        if timeout == VI_TMO_INFINITE:
            raise NameError("no timeout is specified")
        return timeout / 1000.0

    @timeout.setter
    def timeout(self, timeout):
        if not(0 <= timeout <= 4294967):
            raise ValueError("timeout value is invalid")
        self.set_visa_attribute(VI_ATTR_TMO_VALUE, int(timeout * 1000))

    @timeout.deleter
    def timeout(self):
        timeout = self.timeout  # just to test whether it's defined
        self.set_visa_attribute(VI_ATTR_TMO_VALUE, VI_TMO_INFINITE)

    @property
    def resource_class(self):
        """The resource class of the resource as a string.
        """

        # TODO: Check possible outputs.
        try:
            return self.get_visa_attribute(VI_ATTR_RSRC_CLASS).upper()
        except errors.VisaIOError as error:
            if error.error_code != VI_ERROR_NSUP_ATTR:
                raise
        return 'Unknown'

    @property
    def resource_name(self):
        """The VISA resource name of the resource as a string.
        """
        return self.get_visa_attribute(VI_ATTR_RSRC_NAME)

    @property
    def interface_type(self):
        """The interface type of the resource as a number.
        """
        return self.visalib.parse_resource(self.resource_manager.session,
                                           self.resource_name).interface_type

    @contextlib.contextmanager
    def read_termination_context(self, new_termination):
        term = self.get_visa_attribute(VI_ATTR_TERMCHAR)
        self.set_visa_attribute(VI_ATTR_TERMCHAR, ord(new_termination[-1]))
        yield
        self.set_visa_attribute(VI_ATTR_TERMCHAR, term)

# The bits in the bitfield mean the following:
#
# bit number   if set / if not set
#     0          binary/ascii
#     1          double/single (IEEE floating point)
#     2          big-endian/little-endian
#
# This leads to the following constants:

ascii      = 0
single     = 1
double     = 3
big_endian = 4

CR = '\r'
LF = '\n'


class Instrument(_BaseInstrument):
    """Class for all kinds of Instruments.

    It can be instantiated, however, if you want to use special features of a
    certain interface system (GPIB, USB, RS232, etc), you must instantiate one
    of its child classes.

    :param resource_name: the instrument's resource name or an alias,
                          may be taken from the list from
                          `list_resources` method from a ResourceManager.
    :param timeout: the VISA timeout for each low-level operation in
                    milliseconds.
    :param term_chars: the termination characters for this device.
    :param chunk_size: size of data packets in bytes that are read from the
                       device.
    :param lock: whether you want to have exclusive access to the device.
                 Default: VI_NO_LOCK
    :param ask_delay: waiting time in seconds after each write command.
                      Default: 0.0
    :param send_end: whether to assert end line after each write command.
                     Default: True
    :param values_format: floating point data value format. Default: ascii (0)
    """

    #: Termination character sequence.
    __term_chars = None


    DEFAULT_KWARGS = {#: Termination character sequence.
                      'term_chars': None,
                      #: How many bytes are read per low-level call.
                      'chunk_size': 20 * 1024,
                      #: Seconds to wait between write and read operations inside ask.
                      'ask_delay': 0.0,
                      'send_end': True,
                      #: floating point data value format
                      'values_format': ascii}

    ALL_KWARGS = dict(DEFAULT_KWARGS, **_BaseInstrument.DEFAULT_KWARGS)

    def __init__(self, resource_name, resource_manager=None, **kwargs):
        skwargs, pkwargs = split_kwargs(kwargs,
                                        Instrument.DEFAULT_KWARGS.keys(),
                                        _BaseInstrument.DEFAULT_KWARGS.keys())

        self._read_termination = None
        self._write_termination = None

        super(Instrument, self).__init__(resource_name, resource_manager, **pkwargs)

        for key, value in Instrument.DEFAULT_KWARGS.items():
            setattr(self, key, skwargs.get(key, value))

        if not self.resource_class:
            warnings.warn("resource class of instrument could not be determined",
                          stacklevel=2)
        elif self.resource_class not in ("INSTR", "RAW", "SOCKET"):
            warnings.warn("given resource was not an INSTR but %s"
                          % self.resource_class, stacklevel=2)

    @property
    def read_termination(self):
        """Read termination character.
        """
        return self._read_termination

    @read_termination.setter
    def read_termination(self, value):

        if value:
            # termination character, the rest is just used for verification after
            # each read operation.
            last_char = value[-1:]
            # Consequently, it's illogical to have the real termination character
            # twice in the sequence (otherwise reading would stop prematurely).

            if value[:-1].find(last_char) != -1:
                raise ValueError("ambiguous ending in termination characters")

            self.set_visa_attribute(VI_ATTR_TERMCHAR, ord(last_char))
            self.set_visa_attribute(VI_ATTR_TERMCHAR_EN, VI_TRUE)
        else:
            self.set_visa_attribute(VI_ATTR_TERMCHAR_EN, VI_FALSE)

        self._read_termination = value

    @property
    def write_termination(self):
        """Writer termination character.
        """
        return self._write_termination

    @write_termination.setter
    def write_termination(self, value):
        self._write_termination = value

    def write_raw(self, message):
        """Write a string message to the device.

        The term_chars are appended to it, unless they are already.

        :param message: the message to be sent.
        :type message: bytes
        :return: number of bytes written.
        :rtype: int
        """

        return self.visalib.write(self.session, message)

    def write(self, message, termination=None):
        """Write a string message to the device.

        The term_chars are appended to it, unless they are already.

        :param message: the message to be sent.
        :type message: unicode (Py2) or str (Py3)
        :return: number of bytes written.
        :rtype: int
        """

        term = self._write_termination if termination is None else termination

        if term:
            if message.endswith(term):
                warnings.warn("write message already ends with "
                              "termination characters", stacklevel=2)
            message += term

        count = self.write_raw(message.encode('ascii'))

        return count

    def _strip_term_chars(self, message):
        """Strips termination chars from a message

        :type message: str
        """
        if self.__term_chars:
            if message.endswith(self.__term_chars):
                message = message[:-len(self.__term_chars)]
            else:
                warnings.warn("read string doesn't end with "
                              "termination characters", stacklevel=2)

        return message.rstrip(CR + LF)

    def read_raw(self):
        """Read the unmodified string sent from the instrument to the computer.

        In contrast to read(), no termination characters are checked or
        stripped. You get the pristine message.

        :rtype: bytes

        """
        ret = bytes()
        with warning_context("ignore", "VI_SUCCESS_MAX_CNT"):
            try:
                status = VI_SUCCESS_MAX_CNT
                while status == VI_SUCCESS_MAX_CNT:
                    logger.debug('Reading %d bytes from session %s (last status %r)',
                                 self.chunk_size, self.session, status)
                    ret += self.visalib.read(self.session, self.chunk_size)
                    status = self.visalib.status
            except errors.VisaIOError as e:
                logger.debug('Exception while reading: %s', e)
                raise

        return ret

    def read(self, termination=None):
        """Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting
        appropriate bus lines), or the termination characters sequence was
        detected.  Attention: Only the last character of the termination
        characters is really used to stop reading, however, the whole sequence
        is compared to the ending of the read string message.  If they don't
        match, a warning is issued.

        All line-ending characters are stripped from the end of the string.

        :rtype: str
        """

        if termination is not None:
            with self.read_termination_context(termination):
                message = self.read_raw().decode('ascii')
        else:
            termination = self._read_termination
            message = self.read_raw().decode('ascii')

        if not termination:
            return message

        if not message.endswith(termination):
            warnings.warn("read string doesn't end with "
                          "termination characters", stacklevel=2)

        return message[:-len(termination)]

    def read_values(self, fmt=None):
        """Read a list of floating point values from the device.

        :param fmt: the format of the values.  If given, it overrides
            the class attribute "values_format".  Possible values are bitwise
            disjunctions of the above constants ascii, single, double, and
            big_endian.  Default is ascii.

        :return: the list of read values
        :rtype: list
        """
        if not fmt:
            fmt = self.values_format

        if fmt & 0x01 == ascii:
            return parse_ascii(self.read())

        data = self.read_raw()

        try:
            if fmt & 0x03 == single:
                is_single = True
            elif fmt & 0x03 == double:
                is_single = False
            else:
                raise ValueError("unknown data values fmt requested")
            return parse_binary(data, fmt & 0x04 == big_endian, is_single)
        except ValueError as e:
            raise errors.InvalidBinaryFormat(e.args)

    def ask(self, message, delay=None):
        """A combination of write(message) and read()

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.ask_delay
        :returns: the answer from the device.
        :rtype: str
        """

        self.write(message)
        if delay is None:
            delay = self.ask_delay
        if delay > 0.0:
            time.sleep(delay)
        return self.read()

    def ask_for_values(self, message, format=None, delay=None):
        """A combination of write(message) and read_values()

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.ask_delay
        :returns: the answer from the device.
        :rtype: list
        """

        self.write(message)
        if delay is None:
            delay = self.ask_delay
        if delay > 0.0:
            time.sleep(delay)
        return self.read_values(format)

    def trigger(self):
        """Sends a software trigger to the device.
        """

        self.set_visa_attribute(VI_ATTR_TRIG_ID, VI_TRIG_SW)
        self.visalib.assert_trigger(self.session, VI_TRIG_PROT_DEFAULT)

    @property
    def term_chars(self):
        """Set or read a new termination character sequence (property).

        Normally, you just give the new termination sequence, which is appended
        to each write operation (unless it's already there), and expected as
        the ending mark during each read operation.  A typical example is CR+LF
        or just CR.  If you assign "" to this property, the termination
        sequence is deleted.

        The default is None, which means that CR + LF is appended to each write
        operation but not expected after each read operation (but stripped if
        present).
        """

        return self.__term_chars

    @term_chars.setter
    def term_chars(self, term_chars):

        # First, reset termination characters, in case something bad happens.
        self.__term_chars = ""

        if term_chars == "" or term_chars is None:
            self.read_termination = None
            self.write_termination = CR + LF
            self.__term_chars = term_chars
            return
            # Only the last character in term_chars is the real low-level

        self.read_termination = term_chars
        self.write_termination = term_chars

    @term_chars.deleter
    def term_chars(self):
        self.term_chars = None

    @property
    def send_end(self):
        """Whether or not to assert EOI (or something equivalent after each
        write operation.
        """

        return self.get_visa_attribute(VI_ATTR_SEND_END_EN) == VI_TRUE

    @send_end.setter
    def send_end(self, send):
        self.set_visa_attribute(VI_ATTR_SEND_END_EN, VI_TRUE if send else VI_FALSE)


class GpibInstrument(Instrument):
    """Class for GPIB instruments.

    This class extents the Instrument class with special operations and
    properties of GPIB instruments.

    :param gpib_identifier: strings are interpreted as instrument's VISA resource name.
                            Numbers are interpreted as GPIB number.
    :param board_number: the number of the GPIB bus.

    Further keyword arguments are passed to the constructor of class
    Instrument.

    """

    def __init__(self, gpib_identifier, board_number=0, resource_manager=None, **keyw):
        warn_for_invalid_kwargs(keyw, Instrument.ALL_KWARGS.keys())
        if isinstance(gpib_identifier, int):
            resource_name = "GPIB%d::%d" % (board_number, gpib_identifier)
        else:
            resource_name = gpib_identifier

        super(GpibInstrument, self).__init__(resource_name, resource_manager, **keyw)

        # Now check whether the instrument is really valid
        if self.interface_type != VI_INTF_GPIB:
            raise ValueError("device is not a GPIB instrument")

        self.visalib.enable_event(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

    def __del__(self):
        if self.session is not None:
            self.__switch_events_off()
            super(GpibInstrument, self).__del__()

    def __switch_events_off(self):
        self.visalib.disable_event(self.session, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)
        self.visalib.discard_events(self.session, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)

    def wait_for_srq(self, timeout=25):
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        :param timeout: the maximum waiting time in seconds.
                        Defaul: 25 (seconds).
                        None means waiting forever if necessary.
        """
        lib = self.visalib

        lib.enable_event(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

        if timeout and not(0 <= timeout <= 4294967):
            raise ValueError("timeout value is invalid")

        starting_time = time.clock()

        while True:
            if timeout is None:
                adjusted_timeout = VI_TMO_INFINITE
            else:
                adjusted_timeout = int((starting_time + timeout - time.clock()) * 1000)
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            event_type, context = lib.wait_on_event(self.session, VI_EVENT_SERVICE_REQ,
                                                    adjusted_timeout)
            lib.close(context)
            if self.stb & 0x40:
                break

        lib.discard_events(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

    @property
    def stb(self):
        """Service request status register."""

        return self.visalib.read_stb(self.session)

# The following aliases are used for the "end_input" property
no_end_input = VI_ASRL_END_NONE
last_bit_end_input = VI_ASRL_END_LAST_BIT
term_chars_end_input = VI_ASRL_END_TERMCHAR

# The following aliases are used for the "parity" property
no_parity = VI_ASRL_PAR_NONE
odd_parity = VI_ASRL_PAR_ODD
even_parity = VI_ASRL_PAR_EVEN
mark_parity = VI_ASRL_PAR_MARK
space_parity = VI_ASRL_PAR_SPACE


class SerialInstrument(Instrument):
    """Class for serial (RS232 or parallel port) instruments.  Not USB!

    This class extents the Instrument class with special operations and
    properties of serial instruments.

    :param resource_name: the instrument's resource name or an alias, may be
        taken from the list from `list_resources` method from a ResourceManager.

    Further keyword arguments are passed to the constructor of class
    Instrument.
    """

    DEFAULT_KWARGS = {'baud_rate': 9600,
                      'data_bits': 8,
                      'stop_bits': 1,
                      'parity': no_parity,
                      'end_input': term_chars_end_input}

    def __init__(self, resource_name, resource_manager=None, **keyw):
        skwargs, pkwargs = split_kwargs(keyw,
                                        SerialInstrument.DEFAULT_KWARGS.keys(),
                                        Instrument.ALL_KWARGS.keys())

        pkwargs.setdefault("term_chars", CR)

        super(SerialInstrument, self).__init__(resource_name, resource_manager, **pkwargs)
        # Now check whether the instrument is really valid
        if self.interface_type != VI_INTF_ASRL:
            raise ValueError("device is not a serial instrument")

        for key, value in SerialInstrument.DEFAULT_KWARGS.items():
            setattr(self, key, skwargs.get(key, value))

    @property
    def baud_rate(self):
        """The baud rate of the serial instrument.
        """
        return self.get_visa_attribute(VI_ATTR_ASRL_BAUD)

    @baud_rate.setter
    def baud_rate(self, rate):
        self.set_visa_attribute(VI_ATTR_ASRL_BAUD, rate)

    @property
    def data_bits(self):
        """Number of data bits contained in each frame (from 5 to 8).
        """

        return self.get_visa_attribute(VI_ATTR_ASRL_DATA_BITS)

    @data_bits.setter
    def data_bits(self, bits):
        if not 5 <= bits <= 8:
            raise ValueError("number of data bits must be from 5 to 8")

        self.set_visa_attribute(VI_ATTR_ASRL_DATA_BITS, bits)

    @property
    def stop_bits(self):
        """Number of stop bits contained in each frame (1, 1.5, or 2).
        """

        deci_bits = self.get_visa_attribute(VI_ATTR_ASRL_STOP_BITS)
        if deci_bits == 10:
            return 1
        elif deci_bits == 15:
            return 1.5
        elif deci_bits == 20:
            return 2

    @stop_bits.setter
    def stop_bits(self, bits):
        deci_bits = 10 * bits
        if 9 < deci_bits < 11:
            deci_bits = 10
        elif 14 < deci_bits < 16:
            deci_bits = 15
        elif 19 < deci_bits < 21:
            deci_bits = 20
        else:
            raise ValueError("invalid number of stop bits")

        self.set_visa_attribute(VI_ATTR_ASRL_STOP_BITS, deci_bits)

    @property
    def parity(self):
        """The parity used with every frame transmitted and received."""

        return self.get_visa_attribute(VI_ATTR_ASRL_PARITY)

    @parity.setter
    def parity(self, parity):

        self.set_visa_attribute(VI_ATTR_ASRL_PARITY, parity)

    @property
    def end_input(self):
        """indicates the method used to terminate read operations"""

        return self.get_visa_attribute(VI_ATTR_ASRL_END_IN)

    @end_input.setter
    def end_input(self, termination):
        self.set_visa_attribute(VI_ATTR_ASRL_END_IN, termination)


def get_instruments_list(use_aliases=True):
    """Get a list of all connected devices.

    This function is kept for backwards compatibility with PyVISA < 1.5.

    Use::

        >>> rm = ResourceManager()
        >>> rm.list_resources()

    or::

        >>> rm = ResourceManager()
        >>> rm.list_resources_info()

    in the future.

    :param use_aliases: if True (default), return the device alias if it has one.
                        Otherwise, always return the standard resource name
                        like "GPIB::10".

    :return: A list of strings with the names of all connected devices,
             ready for being used to open each of them.

    """

    if use_aliases:
        return [info.alias or resource_name
                for resource_name, info in get_resource_manager().list_resources_info().items()]

    return get_resource_manager().list_resources()


def instrument(resource_name, **kwargs):
    """Factory function for instrument instances.

    :param resource_name: the VISA resource name of the device.
                          It may be an alias.
    :param kwargs: keyword argument for the class constructor of the device instance
                   to be generated.  See the class Instrument for further information.

    :return: The generated instrument instance.

    """

    return get_resource_manager().get_instrument(resource_name, **kwargs)


resource_manager = None

def get_resource_manager():
    global resource_manager
    if resource_manager is None:
        resource_manager = ResourceManager()
        atexit.register(resource_manager.__del__)
    return resource_manager
