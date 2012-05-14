#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    __init__.py - PyVISA's package initialisation.
#
#    Copyright © 2005, 2006, 2007, 2008
#                Torsten Bronger <bronger@physik.rwth-aachen.de>,
#                Gregor Thalhammer <gth@users.sourceforge.net>.
#  
#    This file is part of PyVISA.
#  
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the MIT licence:
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

import vpp43_constants as _constants
from vpp43_types import *
from visa_messages import completion_and_error_messages
import string

viRO = 'readonly'
viRW = 'readwrite'
viGlobal = 'Global'
viLocal = 'Local'

class _AttrRange:
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
    def __contains__(self, item):
        if item >= self.minimum and item<=self.maximum:
            return True
        else:
            return False

    def tostring(self, val):
        if val in self:
            return str(val)
        else:
            raise IndexError

    def fromstring(self, strval):
        val = int(strval) #FIXME: always int? (long, double)
        return val

class _AttrSet:
    """encapsulates named attributes values,
    for conversion between name and value"""
    def __init__(self, *args):
        self.NameSet = args
        self.namedict = {}
        self.valuedict = {}
        for name in args:
            value = _constants.__dict__[name]
            self.namedict[value] = name
            self.valuedict[name] = value

    def __repr__(self):
        return repr(self.valuedict)
    
    def __contains__(self, item):
        return item in self.NameSet

    #def __getitem__(self, key):
    #    return self.tostring(key)

    def tostring(self, value):
        return self.namedict.get(value, None)

    def fromstring(self, name):
        return self.valuedict.get(name, None)

class _AttrBitSet(_AttrSet):
    """class for set of attribute values that can be ORed together"""

    def __contains__(self, bitfield): #Fixme: more strict test for validity, test for zero
        """True if at least on of allowed bits is set"""
        for bit in self.namedict:
            if bit & bitfield:
                return True
        else:
            return False

    def tostring(self, bitfield):
        s = ''
        for bit in self.namedict.keys():
            if bit & bitfield:
                if not s:
                    s = self.namedict[bit]
                else:
                    s = s + ' | ' + self.namedict[bit]
            if self.namedict.has_key(0) and bitfield == 0: #no bit set: special name
                s = self.namedict[0]
        return s

    def fromstring(self, expr):
        bitfield = 0
        for s in map(string.strip, string.split(expr, '|')): #split at | and remove whitespace
            bitfield = bitfield | self.valuedict[s]
        return bitfield

class viAttrInfo:
    """container for information about attribute (attribute name,
    value, access restriction, scope (local for session or global for
    device), ctypes data type, range of possible values, short and
    long description"""
    
    def __init__(self, access, scope, datatype, values, shortdesc,
                 description, attribute = None, name = None):
        self.access = access
        self.scope = scope
        self.datatype = datatype
        self.values = values
        self.description = description
        self.attribute_name = name
        self.attribute_value = attribute

    def __repr__(self):
        #s = repr(self.typecode) + repr(self.values)
        #return s
        return repr(self.__dict__)


#VISA Template Attributes
#Table 3.2.1

attributes_s = {
    'VI_ATTR_RSRC_IMPL_VERSION': \
    viAttrInfo(
    viRO, viGlobal, ViVersion,
    _AttrRange(0, 0xFFFFFFFFL),
    'implementation version',
    "Resource version that uniquely identifies each of the different "\
    "revisions or implementations of a resource."
    ),

    'VI_ATTR_RSRC_LOCK_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViAccessMode,
    _AttrSet('VI_NO_LOCK', 'VI_EXCLUSIVE_LOCK', 'VI_SHARED_LOCK'),
    'lock state',
    "The current locking state of the resource. The resource can be "\
    "unlocked, locked with an exclusive lock, or locked with a shared "\
    "lock."
    ),
    
    'VI_ATTR_RSRC_MANF_ID': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16, _AttrRange(0, 0x3FFF),
    'resource manufacturer ID',
    "A value that corresponds to the VXI manufacturer ID of the "\
    "manufacturer that created the implementation."
    ),
    
    'VI_ATTR_RSRC_MANF_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'resource manufacturer name',
    "A string that corresponds to the VXI manufacturer name of the "\
    "manufacturer that created the implementation."
    ),

    'VI_ATTR_RSRC_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViRsrc, None,
    'resource name',
    "The unique identifier for a resource compliant with the address "\
    "structure presented in Section 4.4.1, Address String."
    ),

    'VI_ATTR_RSRC_SPEC_VERSION': \
    viAttrInfo(
    viRO, viGlobal, ViVersion, None,
    'resource specification version',
    "Resource version that uniquely identifies the version of the VISA "\
    "specification to which the implementation is compliant."
    ),
    
    'VI_ATTR_RSRC_CLASS': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'resource class',
    "Specifies the resource class (for example, INSTR)."
    ),

    #Generic INSTR Resource Attributes
    'VI_ATTR_INTF_NUM': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16, _AttrRange(0, 0xFFFF),
    'interface number',
    "Board number for the given interface."
    ),

    'VI_ATTR_INTF_TYPE': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16,
    _AttrSet('VI_INTF_VXI', 'VI_INTF_GPIB', 'VI_INTF_GPIB_VXI', 'VI_INTF_ASRL',
          'VI_INTF_TCPIP', 'VI_INTF_USB'),
    'interface type',
    "Interface type of the given session."
    ),
    
    'VI_ATTR_INTF_INST_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'interface name',
    "Human-readable text describing the given interface."
    ),

    #ASRL Specific INSTR Resource Attributes
    'VI_ATTR_ASRL_AVAIL_NUM': \
    viAttrInfo(
    viRO, viGlobal, ViUInt32, None, #0 to 0xFFFFFFFFL
    'number of bytes available at serial port',
    ""
    ),

    'VI_ATTR_ASRL_BAUD': \
    viAttrInfo(
    viRW, viGlobal, ViUInt32, None, #0 to 0xFFFFFFFFL
    'serial baud rate',
    ""
    ),

    'VI_ATTR_ASRL_DATA_BITS': \
    viAttrInfo(
    viRW, viGlobal, ViUInt16, _AttrRange(5, 8),
    '',
    ""
    ),
    
    'VI_ATTR_ASRL_PARITY': \
    viAttrInfo(
    viRW, viGlobal, ViUInt16,
    _AttrSet('VI_ASRL_PAR_NONE', 'VI_ASRL_PAR_ODD', 'VI_ASRL_PAR_EVEN',
             'VI_ASRL_PAR_MARK', 'VI_ASRL_PAR_SPACE'),
    '',
    ""
    ),
    
    'VI_ATTR_ASRL_STOP_BITS': \
    viAttrInfo(
    viRW, viGlobal, ViUInt16,
    _AttrSet('VI_ASRL_STOP_ONE', 'VI_ASRL_STOP_ONE5', 'VI_ASRL_STOP_TWO'),
    '',
    ""
    ),
    
    'VI_ATTR_ASRL_FLOW_CNTRL': \
    viAttrInfo(
    viRW, viGlobal, ViUInt16,
    _AttrBitSet('VI_ASRL_FLOW_NONE', 'VI_ASRL_FLOW_XON_XOFF',
             'VI_ASRL_FLOW_RTS_CTS', 'VI_ASRL_FLOW_DTR_DSR'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_END_IN': \
    viAttrInfo(
    viRW, viLocal, ViUInt16,
    _AttrSet('VI_ASRL_END_NONE', 'VI_ASRL_END_LAST_BIT',
              'VI_ASRL_END_TERMCHAR'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_END_OUT': \
    viAttrInfo(
    viRW, viLocal, ViUInt16,
    _AttrSet('VI_ASRL_END_NONE', 'VI_ASRL_END_LAST_BIT',
             'VI_ASRL_END_TERMCHAR', 'VI_ASRL_END_BREAK'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_CTS_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_DCD_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_DSR_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_DTR_STATE': \
    viAttrInfo(
    viRW, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_RI_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_RTS_STATE': \
    viAttrInfo(
    viRW, viGlobal, ViInt16,
    _AttrSet('VI_STATE_ASSERTED', 'VI_STATE_UNASSERTED', 'VI_STATE_UNKNOWN'),
    '',
    ""
    ),

    'VI_ATTR_ASRL_REPLACE_CHAR': \
    viAttrInfo(
    viRW, viLocal, ViUInt8, None, #0 to FFh,
    '',
    ""
    ),

    'VI_ATTR_ASRL_XON_CHAR': \
    viAttrInfo(
    viRW, viLocal, ViUInt8, None, #0 to FFh
    '',
    ""
    ),

    'VI_ATTR_ASRL_XOFF_CHAR': \
    viAttrInfo(
    viRW, viLocal, ViUInt8, None, #0 to FFh
    '',
    ""
    ),

    #Event Attributes: VI_EVENT_IO_COMPLETION
    'VI_ATTR_EVENT_TYPE': \
    viAttrInfo(
    viRO, None, ViEventType,
    _AttrSet('VI_EVENT_IO_COMPLETION'), #FIXME: add other Events
    'event type',
    "Unique logical identifier of the event type."
    ),

    'VI_ATTR_STATUS': \
    viAttrInfo(
    viRO, None, ViStatus,
    _AttrSet(*map(lambda x:x[0], completion_and_error_messages.values())),
             #list of status codes, FIXME
    'return code of asynchronous operation that has completed',
    ""
    ),

    'VI_ATTR_JOB_ID': \
    viAttrInfo(
    viRO, None, ViJobId, None,
    'job ID',
    ""
    ),

    'VI_ATTR_BUFFER': \
    viAttrInfo(
    viRO, None, ViBuf, None,
    'buffer address',
    "Address of a buffer that was used in an asynchronous operation."
    ),

    'VI_ATTR_RET_COUNT': \
    viAttrInfo(
    viRO, None, ViUInt32, None, #0 to ffffffffh
    'return count',
    "actual number of elements that were asynchronously transferred"
    ),

    'VI_ATTR_OPER_NAME': \
    viAttrInfo(
    viRO, None, ViString, None,
    'operation name',
    "The name of the operation generating the event."
    )
    
    }
"""List of VISA Attributes, as dictionary with string keys"""

attributes = {} #dict with attribute value (not name) as key
for name, info in attributes_s.iteritems():
    value = _constants.__dict__[name] #convert attribute name to value
    info.attribute_name = name 
    info.attribute_value = value
    attributes[value] = info

#print attr
    

