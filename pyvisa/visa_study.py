# -*- coding: utf-8 -*-
"""
    visa_study
    ~~~~~~~~~~

    Alternative high-level VISA implementation.

    This file is part of PyVISA.

    :copyright: (c) 2012 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

"""visa_study.py defines an Python interface to the VISA library
"""

__version__ = "$Revision$"
# $Source$

import os
import types
import logging
from ctypes import *

from visa_messages import *
from vpp43_types import *
from vpp43_constants import *
from visa_attributes import attributes_s, attributes


log = logging.getLogger('visa')


#load Visa library
if os.name == 'nt':
    visa = windll.visa32
elif os.name == 'posix':
    visa = cdll.LoadLibrary('libvisa.so')
else:
    raise Exception("No implementation for your platform available.")


class VisaError(IOError):
    """Base class for VISA errors"""

    def __init__(self, value):
        IOError.__init__(self)
        self.value = value

    def __str__(self):
        if self.value:
            (shortdesc, longdesc) = completion_and_error_messages[self.value]
            hexvalue = self.value  # convert errorcodes (negative) to long
            if hexvalue < 0:
                hexvalue += 0x100000000
            return shortdesc + " (%X): " % hexvalue + longdesc


# Checks return values for errors
def CheckStatus(status):
    #status = ViStatus(status).value
    if status < 0:
        raise VisaError(status)
    else:
        return status

#implement low level VISA functions

#VISA Resource Management
visa.viOpenDefaultRM.restype = CheckStatus
visa.viOpen.restype = CheckStatus
visa.viFindRsrc.restype = CheckStatus
visa.viFindNext.restype = CheckStatus
visa.viParseRsrc.restype = CheckStatus
visa.viParseRsrcEx.restype = CheckStatus
visa.viClose.restype    = CheckStatus
visa.viGetAttribute.restype = CheckStatus
visa.viSetAttribute.restype = CheckStatus


def OpenDefaultRM():
    """Return a session to the Default Resource Manager resource."""
    sesn = ViSession()
    result = visa.viOpenDefaultRM(byref(sesn))
    return result, sesn.value


def Open(sesn, rsrcName, accessMode, openTimeout):
    """Open a session to the specified device."""
    sesn = ViSession(sesn)
    rsrcName = ViRsrc(rsrcName)
    accessMode = ViAccessMode(accessMode)
    openTimout = ViUInt32(openTimeout)
    vi = ViSession()
    result = visa.viOpen(sesn, rsrcName, accessMode, openTimeout, byref(vi))
    return result, vi.value


def FindRsrc(session, expr):
    """Query a VISA system to locate the resources associated with a
    specified interface.

    This operation matches the value specified in the expr parameter
    with the resources available for a particular interface.

    In comparison to the original VISA function, this returns the
    complete list of found resources."""

    sesn = ViSession(session)
    expr = ViString(expr)
    findList = ViFindList()
    retcnt = ViUInt32()
    instrDesc = c_buffer('\000', 256)

    resource_list = []
    result = visa.viFindRsrc(sesn, expr, byref(findList), byref(retcnt), instrDesc)
    if result >= 0:
        resource_list.append(instrDesc.value)
        for i in range(1, retcnt.value):
            visa.viFindNext(findList, instrDesc)
            resource_list.append(instrDesc.value)
        visa.viClose(findList)
    return resource_list


def ParseRsrc(sesn, rsrcName):
    """Parse a resource string to get the interface information."""
    intfType = ViUInt16()
    intfNum = ViUInt16()
    result = visa.viParseRsrc(
        ViSession(sesn),
        ViRsrc(rsrcName),
        byref(intfType),
        byref(intfNum))
    return result, intfType.value, intfNum.value


def ParseRsrcEx(sesn, rsrcName):
    """Parse a resource string to get extended interface information."""
    intfType = ViUInt16()
    intfNum = ViUInt16()
    rsrcClass = c_buffer(256)
    unaliasedExpandedRsrcName = c_buffer(256)
    aliasIfExists = c_buffer(256)
    result = visa.viParseRsrcEx(sesn, rsrcName, byref(intfType), byref(intfNum),
                                rsrcClass, unaliasedExpandedRsrcName, aliasIfExists)
    return (result, intfType.value, intfNum.value, rsrcClass.value,
            unaliasedExpandedRsrcName.value, aliasIfExists.value)


# VISA Resource Template
def Close(object):
    """Close the specified session, event, or find list.

    This operation closes a session, event, or a find list. In this
    process all the data structures that had been allocated for the
    specified vi are freed."""
    result = visa.viClose(ViObject(object))
    return result


def GetAttribute(vi, attribute):
    """Retrieve the state of an attribute. Argument can be numeric or
    string argument"""
    #convert argument to numeric (attr_value)
    if isinstance(attribute, types.StringTypes):
        attr_name, attr_info = attribute, attributes_s[attribute]
        attr_value = attr_info.attribute_value
    else:
        attr_value,  attr_info = attribute, attributes[attribute]
        attr_name = attr_info.attribute_name

    #call viGetAttribute, convert output to proper data type
    attr_type = attr_info.datatype
    if attr_type is ViString:
        attr_val = c_buffer(256)
        result = visa.viGetAttribute(vi, attr_value, attr_val)
    elif attr_type is ViBuf:
        attr_val = c_void_p()
        result = visa.viGetAttribute(vi, attr_value, byref(attr_val))
    else:
        attr_val = attr_type(attr_value)
        result = visa.viGetAttribute(vi, attr_value, byref(attr_val))
    val = attr_val.value

    #convert result to string
    if attr_info.values:
        value_ext = attr_info.values.tostring(val)
    else:
        if isinstance(val, (types.IntType, types.LongType)):
            value_ext = str(val) + " (%s)" % hex(val)
        else:
            value_ext = str(val)

    return attr_name, val, value_ext


def SetAttribute(vi, attribute, value):
    """Set attribute"""
    #convert attribute to numeric ('attr_value')
    if isinstance(attribute, types.StringTypes):
        attr_name, attr_info = attribute, attributes_s[attribute]
        attr_value = attr_info.attribute_value
    else:
        attr_value,  attr_info = attribute, attributes[attribute]
        attr_name = attr_info.attribute_name

    #convert value to numeric ('val'), when appropriate
    if isinstance(value, types.StringTypes):
        if attr_info.values:
            val = attr_info.values.fromstring(value)
        else:  # fallback, FIXME
            val = str(value)
            print('conversion from string argument not possible')
    else:
        val = value

    cval = attr_info.datatype(val)
    result = visa.viSetAttribute(vi, attr_value, cval)

    return result

#Basic I/O

visa.viWrite.restype = CheckStatus
def Write(vi, buf):
    vi = ViSession(vi)
    buf = c_buffer(buf, len(buf))
    count = ViUInt32(len(buf))
    retCount = ViUInt32()
    log.debug("Write: %s", buf)
    result = visa.viWrite(vi, buf, count, byref(retCount))
    return retCount.value


visa.viRead.restype = CheckStatus
def Read(vi, count):
    vi = ViSession(vi)
    buf = create_string_buffer(count)
    count = ViUInt32(count)
    retCount = ViUInt32()
    result = visa.viRead(vi, buf, count, byref(retCount))
    log.debug("Read: buffer length %d at %s", sizeof(buf), hex(addressof(buf)))
    return result, buf.raw[0:retCount.value]


visa.viWriteAsync.restype = CheckStatus
def WriteAsync(vi, buf):
    vi = ViSession(vi)
    buf = c_buffer(buf, len(buf))
    count = ViUInt32(len(buf))
    jobId = ViJobId()
    result = visa.viWriteAsync(vi, buf, count, byref(jobId))
    return jobId.value


visa.viReadAsync.restype = CheckStatus
def ReadAsync(vi, count):
    buf = create_string_buffer(count)  # FIXME: buffer needs to survive garbage collection!
    jobId = ViJobId()
    log.debug("ReadAsync: buffer length %d at %s", sizeof(buf), hex(addressof(buf)))
    visa.viReadAsync(ViSession(vi),
                     buf,
                     ViUInt32(count),
                     byref(jobId))
    return jobId.value


visa.viGpibControlREN.restype = CheckStatus
def GpibControlREN(vi, mode):
    vi = ViSession(vi)
    mode = ViUInt16(mode)
    result = visa.viGpibControlREN(vi, mode)


#Event management

visa.viEnableEvent.restype = CheckStatus
def EnableEvent(vi, eventType, mechanism):
    visa.viEnableEvent(vi, eventType, mechanism, 0)


visa.viInstallHandler.restype = CheckStatus
visa.viInstallHandler.argtypes = [ViSession, ViEventType, ViHndlr, ViAddr]
# FIXME: dangerous ViAddr
def InstallHandler(vi, eventType, handler, userHandle):
    userHandle = ViAddr(userHandle)
    visa.viInstallHandler(vi, eventType, handler, userHandle)


#higher level classes and metho)ds

class ResourceManager:

    def __init__(self):
        result, self.session = OpenDefaultRM()

    def __del__(self):
        Close(self.session)

    def find_resource(self, expression):
        resource_list = FindRsrc(self.session, expression)
        return resource_list

    def parse_resource(self, resource_name):
        """give information about resource"""
        result, interface_type, interface_number, \
                rsrcClass, unaliasedExpandedRsrcName, \
                aliasIfExists = ParseRsrcEx(self.session, resource_name)
        return interface_type, interface_number, \
               rsrcClass, unaliasedExpandedRsrcName, \
               aliasIfExists

    def open(self, resourceName, exclusiveLock=None, loadConfig=None, openTimeout=1000):
        accessMode = 0
        if exclusiveLock:
            accessMode = accessMode | VI_EXCLUSIVE_LOCK
        if loadConfig:
            accessMode = accessMode | VI_LOAD_CONFIG
        result, vi = Open(self.session, resourceName, accessMode, openTimeout)
        return Resource(vi)


class Resource:

    def __init__(self, vi):
        self.session = vi

    #def __del__(self): #shit happens
    #    self.close()

    def write(self, buf):
        return Write(self.session, buf)

    def read(self, maxcount=None):
        if maxcount:
            result, buf = Read(self.session, maxcount)
            return buf
        else:
            accumbuf = ''
            while 1:
                result, buf = Read(self.session, 1024)
                accumbuf = accumbuf + buf
                if result in (VI_SUCCESS, VI_SUCCESS_TERM_CHAR):
                    return accumbuf

    def getattr(self, attribute):
        attrvalue = GetAttribute(self.session, attribute)
        return attrvalue

    def setattr(self, attribute, value):
        SetAttribute(self.session, attribute, value)

    def setlocal(self):
        #VI_GPIB_REN_DEASSERT        = 0
        #VI_GPIB_REN_ASSERT          = 1
        #VI_GPIB_REN_DEASSERT_GTL    = 2
        #VI_GPIB_REN_ASSERT_ADDRESS  = 3
        #VI_GPIB_REN_ASSERT_LLO      = 4
        #VI_GPIB_REN_ASSERT_ADDRESS_LLO = 5
        #VI_GPIB_REN_ADDRESS_GTL     = 6

        mode = 6
        #Test Marconi 2019: 0 local, 1 remote, 2 local, 4 local lockout, 5 local, 6 local
        GpibControlREN(self.session, mode)

    def close(self):
        Close(self.session)

    def install_handler(self, eventType, handler, user_handle):
        return InstallHandler(self.session,
                              eventType,
                              handler,
                              user_handle)

    def enable_event(self, eventType, mechanism):
        return EnableEvent(self.session, eventType, mechanism)
