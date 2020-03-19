# -*- coding: utf-8 -*-
"""
    pyvisa.events
    ~~~~~~~~~~~~~

    VISA events with convenient access to the available attributes.

    This file is part of PyVISA.

    :copyright: 2020 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from . import constants, typing


# XXX manually implement all attributes


class VisaEvent:
    """

    """

    #:
    event_type: constants.EventType

    #:
    context: typing.VISAEventContext

    @classmethod
    def register(cls,):
        """[summary]
        """

    def get_visa_attribute(self, attribute_id):
        """[summary]

        Parameters
        ----------
        attribute_id : [type]
            [description]
        """
        pass


class VisaExceptionEvent(VisaEvent):
    """[summary]

    """

    #:
    status

    #:
    operation_name


class VisaGPIBCICEvent(VisaEvent):
    """[summary]

    """

    #:
    cic_state


class VisaIOCompletionEvent(VisaEvent):
    """[summary]

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
    """[summary]

    """

    #:
    trigger_id


class VisaUSBInteruptEvent(VisaEvent):
    """
    """

    #:
    status

    #:
    size

    #:
    data


class VisaVXISignalEvent(VisaEvent):
    """
    """

    #:
    status_id


class VisaVXIInterruptEvent(VisaEvent):
    """
    """

    #:
    status_id

    #:
    interrupt_level
