#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
# from vpp43_types import *

library = cdll.LoadLibrary("./libctypes-test.so")

handler_type = CFUNCTYPE(c_int,c_void_p)
library.test_function.argtypes=(handler_type,)
library.test_function.restype=None

def super(a):
    print "Wert:", a.contents.value

library.test_function(handler_type(super))
