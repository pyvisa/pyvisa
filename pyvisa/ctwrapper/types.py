# -*- coding: utf-8 -*-
"""
    pyvisa.wrapper.types
    ~~~~~~~~~~~~~~~~~~~~

    VISA VPP-4.3 data types (VPP-4.3.2 spec, section 3).

    This file is part of PyVISA.

    All data types that are defined by VPP-4.3.2.

    The module exports all data types including the pointer and array types.  This
    means "ViUInt32" and such.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

# ctypes and os shouldn't be re-exported.
import ctypes as _ctypes
import os as _os
import sys as _sys


# Part One: Type Assignments for VISA and Instrument Drivers, see spec table
# 3.1.1.
#
# Remark: The pointer and probably also the array variants are of no
# significance in Python because there is no native call-by-reference.
# However, as long as I'm not fully sure about this, they won't hurt.

def _type_pair(ctypes_type):
    return ctypes_type, _ctypes.POINTER(ctypes_type)


def _type_triplet(ctypes_type):
    return _type_pair(ctypes_type) + (_ctypes.POINTER(ctypes_type),)

ViUInt64, ViPUInt64, ViAUInt64    = _type_triplet(_ctypes.c_uint64)
ViInt64, ViPInt64, ViAInt64       = _type_triplet(_ctypes.c_long)
ViUInt32, ViPUInt32, ViAUInt32    = _type_triplet(_ctypes.c_ulong)
ViInt32, ViPInt32, ViAInt32       = _type_triplet(_ctypes.c_long)
ViUInt16, ViPUInt16, ViAUInt16    = _type_triplet(_ctypes.c_ushort)
ViInt16, ViPInt16, ViAInt16       = _type_triplet(_ctypes.c_short)
ViUInt8, ViPUInt8, ViAUInt8       = _type_triplet(_ctypes.c_ubyte)
ViInt8, ViPInt8, ViAInt8          = _type_triplet(_ctypes.c_byte)
ViAddr, ViPAddr, ViAAddr          = _type_triplet(_ctypes.c_void_p)
ViChar, ViPChar, ViAChar          = _type_triplet(_ctypes.c_char)
ViByte, ViPByte, ViAByte          = _type_triplet(_ctypes.c_ubyte)
ViBoolean, ViPBoolean, ViABoolean = _type_triplet(ViUInt16)
ViReal32, ViPReal32, ViAReal32    = _type_triplet(_ctypes.c_float)
ViReal64, ViPReal64, ViAReal64    = _type_triplet(_ctypes.c_double)


if _sys.version_info >= (3, 0):
    class ViString(object):

        @classmethod
        def from_param(cls, obj):
            if isinstance(obj, str):
                return bytes(obj, 'ascii')
            return obj

    class ViAString(object):

        @classmethod
        def from_param(cls, obj):
            return _ctypes.POINTER(obj)

    ViPString = ViString

else:

    class ViString(object):

        @classmethod
        def from_param(cls, obj):
            if isinstance(obj, str):
                return obj
            elif isinstance(obj, unicode):
                return obj.encode('ascii')
            return obj

    class ViAString(object):

        @classmethod
        def from_param(cls, obj):
            return _ctypes.POINTER(obj)

    ViPString = ViString

# This follows visa.h definition, but involves a lot of manual conversion.
# ViBuf, ViPBuf, ViABuf = ViPByte, ViPByte, _ctypes.POINTER(ViPByte)

ViBuf, ViPBuf, ViABuf = ViPString, ViPString, ViAString


def buffer_to_text(buf):
    return buf.value.decode('ascii')


ViRsrc = ViString
ViPRsrc = ViString
ViARsrc = ViAString

ViKeyId, ViPKeyId = ViString, ViPString

ViStatus, ViPStatus, ViAStatus    = _type_triplet(ViInt32)
ViVersion, ViPVersion, ViAVersion = _type_triplet(ViUInt32)
ViObject, ViPObject, ViAObject    = _type_triplet(ViUInt32)
ViSession, ViPSession, ViASession = _type_triplet(ViObject)

ViAttr        = ViUInt32
ViConstString = _ctypes.POINTER(ViChar)


# Part Two: Type Assignments for VISA only, see spec table 3.1.2.  The
# difference to the above is of no significance in Python, so I use it here
# only for easier synchronisation with the spec.

ViAccessMode, ViPAccessMode = _type_pair(ViUInt32)
ViBusAddress, ViPBusAddress = _type_pair(ViUInt32)
ViBusAddress64, ViPBusAddress64 = _type_pair(ViUInt64)

ViBusSize     = ViUInt32

ViAttrState, ViPAttrState   = _type_pair(ViUInt32)

# The following is weird, taken from news:zn2ek2w2.fsf@python.net
ViVAList      = _ctypes.POINTER(_ctypes.c_char)

ViEventType, ViPEventType, ViAEventType = _type_triplet(ViUInt32)

ViPAttr       = _ctypes.POINTER(ViAttr)
ViAAttr       = ViPAttr

ViEventFilter = ViUInt32

ViFindList, ViPFindList     = _type_pair(ViObject)
ViEvent, ViPEvent           = _type_pair(ViObject)
ViJobId, ViPJobId           = _type_pair(ViUInt32)

# Class of callback functions for event handling, first type is result type
if _os.name == 'nt':
    ViHndlr = _ctypes.WINFUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent,
                                  ViAddr)
else:
    ViHndlr = _ctypes.CFUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent,
                                ViAddr)
