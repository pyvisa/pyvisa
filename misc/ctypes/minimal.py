#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *

def check_status(status):
    """Check return values for errors."""
    global visa_status
    visa_status = status
    if status < 0:
        print "Status: %d" % status
        raise "Fehler!"
    return status

library = windll.visa32
library.__getattr__("viOpenDefaultRM").restype = check_status
library.__getattr__("viSPrintf").restype = check_status
library.__getattr__("viOpen").restype = check_status
library.__getattr__("viWrite").restype = check_status
library.__getattr__("viRead").restype = check_status

vi = c_ulong()

library.viOpenDefaultRM(byref(vi))
print "Session: %d, Status: %d" % (vi.value,
                                   visa_status)
instr_vi = c_ulong()
library.viOpen(vi, "GPIB0::10::INSTR", 0, 0, byref(instr_vi))

retcount = c_ulong()
library.viWrite(instr_vi, "VER\r", 6, byref(retcount))
print "Retcount: %d" % retcount.value

buffer = create_string_buffer(100)
library.viRead(instr_vi, buffer, 100, byref(retcount))
print "Retcount: %d\nResponse: %s" % (retcount.value, buffer.value)

buffer = create_string_buffer(100)
print library.viPrintf(instr_vi, "Hallo!")
