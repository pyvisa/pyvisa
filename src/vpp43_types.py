#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43_types.py - VISA VPP-4.3 data types (VPP-4.3.2 spec, section 3)
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#                     Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of PyVISA.
#
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    PyVISA is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with PyVISA; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

"""All data types that are defined by VPP-4.3.2.

The module exports all data types including the pointer and array types.  This
means "ViUInt32" and such.

"""

__version__ = "$Revision$"
# $Source$


# ctypes and os shouldn't be re-exported.
import ctypes as _ctypes
import os as _os


# Part One: Type Assignments for VISA and Instrument Drivers, see spec table
# 3.1.1.
#
# Remark: The pointer and probably also the array variants are of no
# significance in Python because there is no native call-by-reference.
# However, as long as I'm not fully sure about this, they won't hurt.

def _type_dublet(ctypes_type):
    return (ctypes_type, _ctypes.POINTER(ctypes_type))

def _type_triplet(ctypes_type):
    return _type_dublet(ctypes_type) + (_ctypes.POINTER(ctypes_type),)

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

# The following three type triplets are defined rather pathologically, both in
# the spec and the reference .h file.  Therefore, I can't use _type_triplet.

ViBuf         = ViPByte
ViPBuf        = ViBuf
ViABuf        = _ctypes.POINTER(ViBuf)

ViString      = _ctypes.c_char_p  # ViPChar in the spec
ViPString     = _ctypes.c_char_p  # ViPChar in the spec
ViAString     = _ctypes.POINTER(ViString)

# It is impractical to have ViBuf defined as an array of unsigned chars,
# because ctypes forces me then to cast the string buffer to an array type.
# The only semantic difference is that ViString is null terminated while ViBuf
# is not (as I understand it).  However, in Python there is no difference.
# Since the memory representation is the same -- which is guaranteed by the C
# language specification -- the following ViBuf re-definitions are sensible:

ViBuf = ViPBuf = ViString
ViABuf        = _ctypes.POINTER(ViBuf)

ViRsrc        = ViString
ViPRsrc       = ViString
ViARsrc       = _ctypes.POINTER(ViRsrc)

ViStatus, ViPStatus, ViAStatus    = _type_triplet(ViInt32)
ViVersion, ViPVersion, ViAVersion = _type_triplet(ViUInt32)
ViObject, ViPObject, ViAObject    = _type_triplet(ViUInt32)
ViSession, ViPSession, ViASession = _type_triplet(ViObject)

ViAttr        = ViUInt32
ViConstString = _ctypes.POINTER(ViChar)


# Part Two: Type Assignments for VISA only, see spec table 3.1.2.  The
# difference to the above is of no significance in Python, so I use it here
# only for easier synchronisation with the spec.

ViAccessMode, ViPAccessMode = _type_dublet(ViUInt32)
ViBusAddress, ViPBusAddress = _type_dublet(ViUInt32)

ViBusSize     = ViUInt32

ViAttrState, ViPAttrState   = _type_dublet(ViUInt32)

# The following is weird, taken from news:zn2ek2w2.fsf@python.net
ViVAList      = _ctypes.POINTER(_ctypes.c_char)

ViEventType, ViPEventType, ViAEventType = _type_triplet(ViUInt32)

ViPAttr       = _ctypes.POINTER(ViAttr)
ViAAttr       = ViPAttr

ViEventFilter = ViUInt32

ViFindList, ViPFindList     = _type_dublet(ViObject)
ViEvent, ViPEvent           = _type_dublet(ViObject)
ViKeyId, ViPKeyId           = _type_dublet(ViString)
ViJobId, ViPJobId           = _type_dublet(ViUInt32)

# Class of callback functions for event handling, first type is result type
if _os.name == 'nt':
    ViHndlr = _ctypes.WINFUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent,
				  ViAddr)
else:
    ViHndlr = _ctypes.CFUNCTYPE(ViStatus, ViSession, ViEventType, ViEvent,
				ViAddr)
