# -*- coding: utf-8 -*-
"""
    pyvisa.resources.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for a Resource.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import math
import time

from .. import logger
from ..constants import *
from .. import errors
from ..util import warning_context, warn_for_invalid_kwargs


class Resource(object):
    """Base class for resources.

    :param resource_manager: A resource manager instance.
    :param resource_name: the VISA name for the resource (eg. "GPIB::10")
    :param lock: Specifies the mode by which the resource is to be accessed.
                 Valid values: VI_NO_LOCK, VI_EXCLUSIVE_LOCK, VI_SHARED_LOCK
    :param timeout: The timeout in seconds for all resource I/O operations.

    See :class:Instrument for a detailed description.
    """

    DEFAULT_KWARGS = {'lock': VI_NO_LOCK,
                      'timeout': 5}

    def __init__(self, resource_manager, resource_name=None, **kwargs):
        warn_for_invalid_kwargs(kwargs, Resource.DEFAULT_KWARGS.keys())

        self._resource_manager = resource_manager
        self._visalib = self._resource_manager.visalib
        self._resource_name = resource_name

        self._logging_extra = {'library_path': self._visalib.library_path,
                               'resource_manager.session': self._resource_manager.session,
                               'resource_name': self._resource_name,
                               'session': None}

        self.session = None
        self.open(kwargs.get('lock', Resource.DEFAULT_KWARGS['lock']))

        for key, value in Resource.DEFAULT_KWARGS.items():
            setattr(self, key, kwargs.get(key, value))

    def open(self, lock=None):
        """Opens a session to the specified resource.

        :param lock: Specifies the mode by which the resource is to be accessed.
                     Valid values: VI_NO_LOCK, VI_EXCLUSIVE_LOCK, VI_SHARED_LOCK
        """
        lock = self.lock if lock is None else lock

        logger.debug('%s - opening ...', self._resource_name, extra=self._logging_extra)
        with warning_context("ignore", "VI_SUCCESS_DEV_NPRESENT"):
            self.session = self._resource_manager.open_resource(self._resource_name, lock)

            if self._visalib.status == VI_SUCCESS_DEV_NPRESENT:
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

        self._logging_extra['session'] = self.session
        logger.debug('%s - is open with session %s',
                     self._resource_name, self.session,
                     extra=self._logging_extra)

    def close(self):
        """Closes the VISA session and marks the handle as invalid.
        """
        if self._resource_manager.session is None or self.session is None:
            return

        logger.debug('%s - closing', self._resource_name,
                     extra=self._logging_extra)
        self._visalib.close(self.session)
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
        return self._visalib.get_attribute(self.session, name)

    def set_visa_attribute(self, name, status):
        self._visalib.set_attribute(self.session, name, status)

    def clear(self):
        self._visalib.clear(self.session)

    @property
    def timeout(self):
        """The timeout in seconds for all resource I/O operations.

        Note that the VISA library may round up this value heavily.
        I experienced that my NI VISA implementation had only the
        values 0, 1, 3 and 10 seconds.

        """
        timeout = self.get_visa_attribute(VI_ATTR_TMO_VALUE)
        if timeout == VI_TMO_INFINITE:
            return float('+nan')
        return timeout / 1000.0

    @timeout.setter
    def timeout(self, timeout):
        if timeout < 0 or math.isnan(timeout):
            timeout = VI_TMO_INFINITE
        elif not (0 <= timeout <= 4294967):
            raise ValueError("timeout value is invalid")
        else:
            timeout = int(timeout * 1000)
        self.set_visa_attribute(VI_ATTR_TMO_VALUE, timeout)

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
        return self._visalib.parse_resource(self._resource_manager.session,
                                            self.resource_name).interface_type

