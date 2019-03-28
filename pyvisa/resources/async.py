# -*- coding: utf-8 -*-
"""
    pyvisa.resources.async
    ~~~~~~~~~~~~~~~~~~~~~~

    Asynchronous communication for resources. This is kept as a separate module
    because it uses the ``yield from`` syntax, which was only introduced in
    Python 3.3. ``patch_class()`` is used to patch a given class with its async
    methods.

    This file is part of PyVISA.

    :copyright: 2019 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import warnings
from collections import defaultdict

from .. import logger
from .. import constants
from .. import errors
from ..compat import coroutine

method_registry = defaultdict(list)


def patch_class(cls):
    """Patch a class with its async methods."""
    for method in method_registry[cls.__name__]:
        setattr(cls, method.__name__, method)


def method_of(clsname):
    def wrap(func):
        method_registry[clsname].append(func)
    return wrap


@method_of('MessageBasedResource')
def start_async_read(self, size=None):
    """Start an asynchronous read operation and return immediately.

    :param size: The chunk size to use when reading the data.

    Only available for Python 3.3 and above.
    """

    if not self._io_events_enabled:
        self.visalib.enable_event(self.session,
                                  constants.VI_EVENT_IO_COMPLETION,
                                  constants.VI_QUEUE)
        self._io_events_enabled = True
    size = self.chunk_size if size is None else size
    buf, job_id, status = self.visalib.read_asynchronously(self.session, size)
    self._jobs[job_id.value] = buf


@method_of('MessageBasedResource')
def check_async_read(self, timeout=0):
    """Check if an async read is finished and return the message if so.

    Returns None if the read operation has not yet finished. Note that this
    method can raise a VisaIOError if the read operation itself times out. A
    timeout of 0 can be used to poll the operation and return immediately.

    :param timeout: How long (in milliseconds) to wait for the IO completion
        event

    Only available for Python 3.3 and above.
    """
    msg, _ = self._check_async_read(timeout)
    return msg


@method_of('MessageBasedResource')
def _check_async_read(self, timeout=0):
    try:
        ev_type, ctx, status = self.visalib.wait_on_event(
            self.session, constants.VI_EVENT_IO_COMPLETION, timeout)
    except errors.VisaIOError as e:
        if e.error_code == constants.VI_ERROR_TMO:
            return None, None
        raise

    job_status, _ = self.visalib.get_attribute(ctx, constants.VI_ATTR_STATUS)
    if job_status < 0:
        raise errors.VisaIOError(job_status)

    job_id, _ = self.visalib.get_attribute(ctx, constants.VI_ATTR_JOB_ID)
    count, _ = self.visalib.get_attribute(ctx, constants.VI_ATTR_RET_COUNT)
    self.visalib.close(ctx)

    buf = self._jobs.pop(job_id)
    return buf[:count], job_status


@method_of('MessageBasedResource')
@coroutine
def _async_read_chunk(self, size=None):
    with self.ignore_warning(constants.VI_SUCCESS_SYNC):
        self.start_async_read(size)

    while True:
        yield
        msg, job_status = self._check_async_read(timeout=0)
        if msg is not None:
            return msg, job_status


@method_of('MessageBasedResource')
@coroutine
def _async_read_raw(self, size=None):
    ret = bytearray()
    job_status = loop_status = constants.StatusCode.success_max_count_read
    with self.ignore_warning(constants.VI_SUCCESS_DEV_NPRESENT,
                             constants.VI_SUCCESS_MAX_CNT):
        while job_status == loop_status:
            logger.debug('%s - reading %d bytes (last status %r)',
                         self._resource_name, size, job_status)
            msg, job_status = yield from self._async_read_chunk(size)
            ret.extend(msg)
    return bytes(ret)


@method_of('MessageBasedResource')
@coroutine
def async_read_raw(self, size=None):
    """Read the unmodified string asynchronously

    In contrast to async_read(), no termination characters are stripped.

    Use ``yield from`` to get the value from within another coroutine or
    generator::
        msg = yield from resource.async_read_raw()

    :param size: The chunk size to use when reading the data.

    :rtype: bytes

    Only available for Python 3.3 and above.
    """
    return bytes((yield from self._async_read_raw(size)))


@method_of('MessageBasedResource')
@coroutine
def async_read(self, termination=None, encoding=None):
    """Read a string from the device asynchronously.

    Use ``yield from`` to get the value from within another coroutine or
    generator::
        msg = yield from resource.async_read()

    Reading stops when the device stops sending (e.g. by setting
    appropriate bus lines), or the termination characters sequence was
    detected.  Attention: Only the last character of the termination
    characters is really used to stop reading, however, the whole sequence
    is compared to the ending of the read string message.  If they don't
    match, a warning is issued.

    All line-ending characters are stripped from the end of the string.

    :rtype: str

    Only available for Python 3.3 and above.
    """
    enco = self._encoding if encoding is None else encoding

    if termination is None:
        termination = self._read_termination
        message = (yield from self._async_read_raw()).decode(enco)
    else:
        with self.read_termination_context(termination):
            message = (yield from self._async_read_raw()).decode(enco)

    if not termination:
        return message

    if not message.endswith(termination):
        warnings.warn("read string doesn't end with "
                      "termination characters", stacklevel=2)

    return message[:-len(termination)]
