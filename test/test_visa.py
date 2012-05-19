#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    test_visa.py - PyVISA test code for visa.py
#
#    Copyright © 2012
#                Florian Bauer <fbauer.devel@gmail.com>
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
from __future__ import print_function
from pyvisa import visa
import pytest



class TestGpibInstrument:
    
    def pytest_funcarg__instrument(self, request):
        monkeypatch = request.getfuncargvalue('monkeypatch')
        monkeypatch.setattr(visa.GpibInstrument,
                            'interface_type',
                            visa.VI_INTF_GPIB)
        monkeypatch.setattr(visa.GpibInstrument, 'stb', 0x40)

        return visa.GpibInstrument(1)
    
    @pytest.mark.parametrize('timeout', [None, 0, 25, 4294967])
    def test_wait_for_srq(self, instrument, timeout):
        instrument.wait_for_srq(timeout)

    @pytest.mark.parametrize('timeout', [-1, 4294968])
    def test_wait_for_srq_raises(self, instrument, timeout):
        with pytest.raises(ValueError):
            instrument.wait_for_srq(timeout)
