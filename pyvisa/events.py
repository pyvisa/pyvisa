# -*- coding: utf-8 -*-
"""
    pyvisa.events
    ~~~~~~~~~~~~~

    VISA events with convenient access to the available attributes.

    This file is part of PyVISA.

    :copyright: 2020 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from contextlib import contextmanager
from typing import Optional

from . import constants, highlevel, errors
from .typing import VISAEventContext
from .attributes import AttrVI_ATTR_STATUS, AttrVI_ATTR_OPER_NAME

# XXX manually set all attributes (all attributes should be cached)


class VisaEvent:
    """Event that lead to the call of an event handler.

    Do not instantiate directly use the visa_event context manager of the
    Resource object passed to the handler.

    """

    #: Reference to the visa library
    visalib: highlevel.VisaLibraryBase

    #: Type of the event.
    event_type: constants.EventType

    #: Context use to query the event attributes.
    _context: Optional[VISAEventContext]

    @classmethod
    def register(cls,):
        """[summary]
        """

    def __init__(self, visalib, event_type, context):
        self.visalib = visalib
        self.event_type = event_type
        self._context = context

    @property
    def context(self) -> VISAEventContext:
        c = self._context
        if c is None:
            raise errors.InvalidSession()
        return c

    def get_visa_attribute(self, attribute_id: constants.EventAttribute) -> Any:
        """Get the specified VISA attribute.

        """
        return self.visalib.get_attribute(self.context, attribute_id)


class VisaExceptionEvent(VisaEvent):
    """Event corresponding to an exception

    """

    #: Status code of the opertion that generated the exception
    status = AttrVI_ATTR_STATUS()

    #: Name of the operation that led to the exception
    operation_name = AttrVI_ATTR_OPER_NAME()


class VisaGPIBCICEvent(VisaEvent):
    """GPIB Controller in Charge event.

    The event is emitted if the status is gained or lost.

    """

    #:
    cic_state


class VisaIOCompletionEvent(VisaEvent):
    """Event marking the completion of an IO operation.

    """

    #:
    status

    #:
    job_id

    #:
    buffer

    #:
    return_count

    #:
    operation_name


class VisaTrigEvent(VisaEvent):
    """Trigger event.

    """

    #:
    trigger_id


class VisaUSBInteruptEvent(VisaEvent):
    """USB interruption event.

    """

    #:
    status

    #:
    size

    #:
    data


class VisaVXISignalEvent(VisaEvent):
    """VXI signal event.

    """

    #:
    status


class VisaVXIInterruptEvent(VisaEvent):
    """VXI interrupt event.

    """

    #:
    status

    #:
    interrupt_level
