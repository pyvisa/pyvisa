# -*- coding: utf-8 -*-
"""
    pyvisa.resources.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for a Resource.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import math
import time

from .. import constants
from .. import errors
from .. import logger
from .. import highlevel
from .. import attributes


class Resource(object):
    """Base class for resources.

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.

    :param resource_manager: A resource manager instance.
    :param resource_name: the VISA name for the resource (eg. "GPIB::10")
    """

    @classmethod
    def register(cls, interface_type, resource_class):
        def _internal(python_class):
            highlevel.ResourceManager.register_resource_class(interface_type, resource_class, python_class)

            attrs = []
            for attr in attributes.AttributesPerResource[(interface_type, resource_class)]:
                attrs.append(attr)
                if not hasattr(python_class, attr.py_name):
                    setattr(python_class, attr.py_name, attr())
            for attr in attributes.AttributesPerResource[attributes.AllSessionTypes]:
                attrs.append(attr)
                if not hasattr(python_class, attr.py_name):
                    setattr(python_class, attr.py_name, attr())

            setattr(python_class, 'visa_attributes_classes', attrs)
            return python_class
        return _internal

    def __init__(self, resource_manager, resource_name):
        self._resource_manager = resource_manager
        self.visalib = self._resource_manager.visalib
        self._resource_name = resource_name

        self._logging_extra = {'library_path': self.visalib.library_path,
                               'resource_manager.session': self._resource_manager.session,
                               'resource_name': self._resource_name,
                               'session': None}

        #: Session handle.
        self._session = None

    @property
    def session(self):
        """Resource session handle.

        :raises: :class:`pyvisa.errors.InvalidSession` if session is closed.
        """
        if self._session is None:
            raise errors.InvalidSession()
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def __del__(self):
        self.close()

    def __str__(self):
        return "%s at %s" % (self.__class__.__name__, self.resource_name)

    def __repr__(self):
        return "<%r(%r)>" % (self.__class__.__name__, self.resource_name)

    @property
    def last_status(self):
        """Last status code for this session.

        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        return self.visalib.get_last_status_in_session(self.session)

    @property
    def timeout(self):
        """The timeout in milliseconds for all resource I/O operations.

        None is mapped to VI_TMO_INFINITE.
        A value less than 1 is mapped to VI_TMO_IMMEDIATE.
        """
        timeout = self.get_visa_attribute(constants.VI_ATTR_TMO_VALUE)
        if timeout == constants.VI_TMO_INFINITE:
            return float('+inf')
        return timeout

    @timeout.setter
    def timeout(self, timeout):
        if timeout is None or math.isinf(timeout):
            timeout = constants.VI_TMO_INFINITE

        elif timeout < 1:
            timeout = constants.VI_TMO_IMMEDIATE

        elif not (1 <= timeout <= 4294967294):
            raise ValueError("timeout value is invalid")

        else:
            timeout = int(timeout)

        self.set_visa_attribute(constants.VI_ATTR_TMO_VALUE, timeout)

    @timeout.deleter
    def timeout(self):
        self.set_visa_attribute(constants.VI_ATTR_TMO_VALUE, constants.VI_TMO_INFINITE)

    @property
    def resource_info(self):
        """Get the extended information of this resource.

        :param resource_name: Unique symbolic name of a resource.

        :rtype: :class:`pyvisa.highlevel.ResourceInfo`
        """
        return self.visalib.parse_resource_extended(self._resource_manager.session, self.resource_name)

    @property
    def interface_type(self):
        """The interface type of the resource as a number.
        """
        return self.visalib.parse_resource(self._resource_manager.session,
                                           self.resource_name)[0].interface_type

    def ignore_warning(self, *warnings_constants):
        """Ignoring warnings context manager for the current resource.

        :param warnings_constants: constants identifying the warnings to ignore.
        """
        return self.visalib.ignore_warning(self.session, *warnings_constants)

    def open(self, access_mode=constants.AccessModes.no_lock, open_timeout=5000):
        """Opens a session to the specified resource.

        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: Milliseconds before the open operation times out.
        :type open_timeout: int
        """

        logger.debug('%s - opening ...', self._resource_name, extra=self._logging_extra)
        with self._resource_manager.ignore_warning(constants.VI_SUCCESS_DEV_NPRESENT):
            self.session, status = self._resource_manager.open_bare_resource(self._resource_name, access_mode, open_timeout)

            if status == constants.VI_SUCCESS_DEV_NPRESENT:
                # The device was not ready when we opened the session.
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
                        if error.error_code != constants.VI_ERROR_NLISTENERS:
                            raise

        self._logging_extra['session'] = self.session
        logger.debug('%s - is open with session %s',
                     self._resource_name, self.session,
                     extra=self._logging_extra)

    def before_close(self):
        """Called just before closing an instrument.
        """
        pass

    def close(self):
        """Closes the VISA session and marks the handle as invalid.
        """
        try:
            logger.debug('%s - closing', self._resource_name,
                         extra=self._logging_extra)
            self.before_close()
            self.visalib.close(self.session)
            logger.debug('%s - is closed', self._resource_name,
                         extra=self._logging_extra)
            self.session = None
        except errors.InvalidSession:
            pass

    def get_visa_attribute(self, name):
        """Retrieves the state of an attribute in this resource.

        :param name: Resource attribute for which the state query is made (see Attributes.*)
        :return: The state of the queried attribute for a specified resource.
        :rtype: unicode (Py2) or str (Py3), list or other type
        """
        return self.visalib.get_attribute(self.session, name)[0]

    def set_visa_attribute(self, name, state):
        """Sets the state of an attribute.

        :param name: Attribute for which the state is to be modified. (Attributes.*)
        :param state: The state of the attribute to be set for the specified object.
        """
        self.visalib.set_attribute(self.session, name, state)

    def clear(self):
        """Clears this resource
        """
        self.visalib.clear(self.session)

    def install_handler(self, event_type, handler, user_handle=None):
        """Installs handlers for event callbacks in this resource.

        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: user handle (a ctypes object)
        """

        return self.visalib.install_handler(self.session, event_type, handler, user_handle)[:-1]

    def uninstall_handler(self, event_type, handler, user_handle=None):
        """Uninstalls handlers for events in this resource.

        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely in a session for an event.
        """

        self.visalib.uninstall_handler(self.session, event_type, handler, user_handle)

    def lock(self, timeout=None, requested_key=None):
        """Establish a shared lock to the resource.

        :param timeout: Absolute time period (in milliseconds) that a resource
                        waits to get unlocked by the locking session before
                        returning an error. (Defaults to self.timeout)
        :param requested_key: Access key used by another session with which you
                              want your session to share a lock or None to generate
                              a new shared access key.
        :returns: A new shared access key if requested_key is None,
                  otherwise, same value as the requested_key
        """
        timeout = self.timeout if timeout is None else timeout
        return self.visalib.lock(self.session, constants.AccessModes.shared_lock, timeout, requested_key)[0]

    def unlock(self):
        """Relinquishes a lock for the specified resource.
        """
        self.visalib.unlock(self.session)
