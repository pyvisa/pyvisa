#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43_types.py - VISA VPP-4.3 data types (VPP-4.3.2 spec, section 3)
#	$Id$	
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#                     Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of pyvisa.
#
#    pyvisa is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    pyvisa is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with pyvisa; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from ctypes import *

# Part One: Type Assignments for VISA and Instrument Drivers, see spec table
# 3.1.1.
#
# Remark: The pointer and probably also the array variants are of no
# significance in Python because there is no native call-by-reference.
# However, as long as I'm not fully sure about this, they won't hurt.

def _type_dublet(ctypes_type):
    return (ctypes_type, POINTER(ctypes_type))

def _type_triplet(ctypes_type):
    return _type_dublet(ctypes_type) + (POINTER(ctypes_type),)

ViUInt32, ViPUInt32, ViAUInt32    = _type_triplet(c_ulong)
ViInt32, ViPInt32, ViAInt32       = _type_triplet(c_long)
ViUInt16, ViPUInt16, ViAUInt16    = _type_triplet(c_ushort)
ViInt16, ViPInt16, ViAInt16       = _type_triplet(c_short)
ViUInt8, ViPUInt8, ViAUInt8       = _type_triplet(c_ubyte)
ViInt8, ViPInt8, ViAInt8          = _type_triplet(c_byte)
ViAddr, ViPAddr, ViAAddr          = _type_triplet(c_void_p)
ViChar, ViPChar, ViAChar          = _type_triplet(c_char)
ViByte, ViPByte, ViAByte          = _type_triplet(c_ubyte)
ViBoolean, ViPBoolean, ViABoolean = _type_triplet(ViUInt16)
ViReal32, ViPReal32, ViAReal32    = _type_triplet(c_float)
ViReal64, ViPReal64, ViAReal64    = _type_triplet(c_double)

# The following three type triplets are defined rather pathologically, both in
# the spec and the reference .h file.  Therefore, I can't use _type_triplet.

ViBuf         = ViPByte
ViPBuf        = ViPByte
ViABuf        = POINTER(ViBuf)

ViString      = ViPChar
ViPString     = ViPChar
ViAString     = POINTER(ViString)

ViRsrc        = ViString
ViPRsrc       = ViString
ViARsrc       = POINTER(ViRsrc)

ViStatus, ViPStatus, ViAStatus    = _type_triplet(ViInt32)
ViVersion, ViPVersion, ViAVersion = _type_triplet(ViUInt32)
ViObject, ViPObject, ViAObject    = _type_triplet(ViUInt32)
ViSession, ViPSession, ViASession = _type_triplet(ViObject)

ViAttr        = ViUInt32
ViConstString = POINTER(ViChar)


# Part Two: Type Assignments for VISA only, see spec table 3.1.2.  The
# difference to the above is of no significance in Python, so I use it here
# only for easier synchronisation with the spec.

ViAccessMode, ViPAccessMode = _type_dublet(ViUInt32)
ViBusAddress, ViPBusAddress = _type_dublet(ViUInt32)

ViBusSize     = ViUInt32

ViAttrState, ViPAttrState   = _type_dublet(ViUInt32)

# The following is weird, taken from news:zn2ek2w2.fsf@python.net
ViVAList      = POINTER(c_char)

ViEventType, ViPEventType, ViAEventType = _type_triplet(ViUInt32)

ViPAttr       = POINTER(ViAttr)
ViAAttr       = ViPAttr

ViEventFilter = ViUInt32

ViFindList, ViPFindList     = _type_dublet(ViObject)
ViEvent, ViPEvent           = _type_dublet(ViObject)
ViKeyId, ViPKeyId           = _type_dublet(ViString)
ViJobId, ViPJobId           = _type_dublet(ViUInt32)

ViHndlr       = CFUNCTYPE(ViSession, ViEventType, ViEvent, ViAddr)
