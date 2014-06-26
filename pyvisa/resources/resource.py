# -*- coding: utf-8 -*-
"""
    pyvisa.highlevel
    ~~~~~~~~~~~~~~~~

    High level Visa library wrapper.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time

from .. import logger
from ..constants import *
from .. import errors
from ..util import warning_context, warn_for_invalid_kwargs


class Resource(object):
    """Base class for resources.

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
        warn_for_invalid_kwargs(kwargs, Resource.DEFAULT_KWARGS.keys())

        self.resource_manager = resource_manager or get_resource_manager()
        self.visalib = self.resource_manager.visalib
        self._resource_name = resource_name

        self._logging_extra = {'library_path': self.visalib.library_path,
                               'resource_manager.session': self.resource_manager.session,
                               'resource_name': self._resource_name,
                               'session': None}

        self.session = None
        self.open(kwargs.get('lock', Resource.DEFAULT_KWARGS['lock']))

        for key, value in Resource.DEFAULT_KWARGS.items():
            setattr(self, key, kwargs.get(key, value))

    def open(self, lock=None, timeout=5):
        """Opens a session to the specified resource.

        :param lock: Specifies the mode by which the resource is to be accessed.
                     Valid values: VI_NO_LOCK, VI_EXCLUSIVE_LOCK, VI_SHARED_LOCK
        :param timeout: Specifies the maximum time period (in milliseconds)
                        that this operation waits before returning an error.
        """
        lock = self.lock if lock is None else lock

        logger.debug('%s - opening ...', self._resource_name, extra=self._logging_extra)
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

        self._logging_extra['session'] = self.session
        logger.debug('%s - is open with session %s',
                     self._resource_name, self.session,
                     extra=self._logging_extra)

    def close(self):
        """Closes the VISA session and marks the handle as invalid.
        """
        if self.resource_manager.session is None or self.session is None:
            return

        logger.debug('%s - closing', self._resource_name,
                     extra=self._logging_extra)
        self.visalib.close(self.session)
        logger.debug('%s - is closed', self._resource_name,
                     extra=self._logging_extra)
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

        Note that the VISA library may round up this value heavily.
        I experienced that my NI VISA implementation had only the
        values 0, 1, 3 and 10 seconds.

        """
        timeout = self.get_visa_attribute(VI_ATTR_TMO_VALUE)
        if timeout == VI_TMO_INFINITE:
            raise NameError("no timeout is specified")
        return timeout / 1000.0

    @timeout.setter
    def timeout(self, timeout):
        if not (0 <= timeout <= 4294967):
            raise ValueError("timeout value is invalid")
        self.set_visa_attribute(VI_ATTR_TMO_VALUE, int(timeout * 1000))

    @timeout.deleter
    def timeout(self):
        _ = self.timeout  # just to test whether it's defined
        self.set_visa_attribute(VI_ATTR_TMO_VALUE, VI_TMO_INFINITE)

    @property
    def resource_class(self):
        """The resource class of the resource as a string.
        """

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

