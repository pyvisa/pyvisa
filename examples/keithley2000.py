#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    keithley2000.py - PyVISA test code for Keithley 2000 multimeter
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

from __future__ import division, unicode_literals, print_function, absolute_import

import visa


def test_keithley2000(monkeypatch):
    monkeypatch.setattr(visa.GpibInstrument, "interface_type", VI_INTF_GPIB)
    monkeypatch.setattr(visa.GpibInstrument, "stb", 0x40)
    print("Test start")
    keithley = visa.GpibInstrument(12)
    milliseconds = 500
    number_of_values = 10
    keithley.write(
        ("F0B2M2G0T2Q%dI%dX" % (milliseconds, number_of_values)).encode("ascii")
    )
    keithley.trigger()
    keithley.wait_for_srq()
    voltages = keithley.read_floats()
    if voltages:
        print("Average: ", sum(voltages) / len(voltages))
    print("Test end")
