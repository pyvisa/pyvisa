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

import warnings
from collections import defaultdict

from . import logger
from . import constants
from . import ctwrapper
from . import errors
from .util import get_library_paths


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

    #: Maps session handle to last status
    _last_status_in_session = dict()

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
        obj.issue_warning_on = set(errors.default_warnings)

        #: Contains all installed event handlers.
        #: Its elements are tuples with three elements: The handler itself (a Python
        #: callable), the user handle (as a ct object) and the handler again, this
        #: time as a ct object created with CFUNCTYPE.
        obj.handlers = defaultdict(list)

        #: Last return value of the library.
        obj._last_status = 0

        #: Default ResourceManager instance for this library.
        obj._resource_manager = None

        obj._logging_extra = {'library_path': obj.library_path}

        return obj

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
            return self._last_resource_status[session]
        except KeyError:
            raise errors.Error('The session %r does not seem to be valid as it does not have any last status' % session)

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

        logger.debug('%s%s -> %s',
                     func.__name__, arguments, ret_value,
                     extra=self._logging_extra)

        self._last_status = ret_value

        # The first argument of all registered visa functions is a session.
        # We store the error code
        try:
            session = arguments[0]
        except KeyError:
            raise Exception('Function %r does not seem to be a valid visa function' % func)

        if not isinstance(session, int):
            raise Exception('Function %r does not seem to be a valid visa function' % func)

        self._last_status_in_session[session] = ret_value

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

    #: Maps (Interface Type, Resource Class) to Python class encapsulating that resource.
    resource_classes = dict()

    def __new__(cls, visa_library=None):
        if visa_library is None or isinstance(visa_library, str):
            visa_library = VisaLibrary(visa_library)

        if visa_library in cls._registry:
            return cls._registry[visa_library]

        cls._registry[visa_library] = obj = super(ResourceManager, cls).__new__(cls)

        obj.visalib = visa_library

        obj.session = obj.visalib.open_default_resource_manager()
        logger.debug('Created ResourceManager with session %s',  obj.session)
        return obj

    def __str__(self):
        return 'Resource Manager of %s' % self.visalib

    def __repr__(self):
        return '<ResourceManager(%r)>' % self.visalib

    def __del__(self):
        self.close()

    @property
    def last_status(self):
        return self.visalib.get_last_status_in_session(self.session)

    def close(self):
        if self.session is not None:
            logger.debug('Closing ResourceManager (session: %s)', self.session)
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

    def open_bare_resource(self, resource_name,
                           access_mode=constants.VI_NO_LOCK, open_timeout=constants.VI_TMO_IMMEDIATE):
        """Open the specified resource without wrapping into a class

        :param resource_name: name or alias of the resource to open.
        :param access_mode: access mode.
        :param open_timeout: time out to open.

        :return: Unique logical identifier reference to a session.
        """
        return self.visalib.open(self.session, resource_name, access_mode, open_timeout)

    def open_resource(self, resource_name,
                      access_mode=constants.VI_NO_LOCK, open_timeout=constants.VI_TMO_IMMEDIATE, **kwargs):
        """Return an instrument for the resource name.

        :param resource_name: name or alias of the resource to open.
        :param access_mode: access mode.
        :param open_timeout: time out to open.
        :param kwargs: keyword arguments to be passed to the instrument constructor.
        """
        info = self.resource_info(resource_name)

        try:
            cls = self.resource_classes[(info.interface_type, info.resource_class)]
        except KeyError:
            raise ValueError('There is no class defined for %r' % ((info.interface_type, info.resource_class),))

        res = cls(self, resource_name)
        for key in kwargs.keys():
            if not hasattr(res, key):
                raise ValueError('%r is not a valid attribute for type %s' % (key, res.__class__.__name__))

        res.open(access_mode, open_timeout)

        for key, value in kwargs.items():
            setattr(res, key, value)

        return res


