# -*- coding: utf-8 -*-
"""
    pyvisa.typing
    ~~~~~~~~~~~~~

    Type aliases allowing to narrow down definition and reduce duplication

    This file is part of PyVISA.

    :copyright: 2020 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import ctypes
from typing import TYPE_CHECKING, Any, Callable, List, NewType, Union

from . import constants

if TYPE_CHECKING:
    from .resources import Resource

#: Type alias used to identify VISA sessions (ResourceManager or Resource)
VISASession = NewType("VISASession", int)

#: Type alias used to identify an event context (created when handling an event)
VISAEventContext = NewType("VISAEventContext", int)

#: Type alias used to identify a job id created during an asynchronous operation
VISAJobID = NewType("VISAJobID", int)

#: Type alias used to identify a memory address in a register based resource after
#: it has been mapped
VISAMemoryAddress = NewType("VISAMemoryAddress", int)

#: Type for event handler passed to the VISA library
VISAHandler = Callable[
    ["Resource", constants.EventType, VISAEventContext, Any], None,
]
