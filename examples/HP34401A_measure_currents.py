#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    HP34401A_measure_currents.py - functions with PyVisa to monitor currents
#      using a HP34401A multimeter. It supposes that there is only one GPIB
#      instrument (the HP34401A multimeter) plugged to the computer.
#      To use this example just put the example in the directory where you
#      call python then just run:
#      $> python
#      >>> from HP34401A_measure_currents.py import *
#      >>> contMeasA( "file.csv" )
#      Hit Ctrl-C when you have finished
#      Use your favorite plotting program to review the measurements (GnuPlot
#       is a good candidate)
#      $> gnuplot
#      >>> set datafile separator ";"
#      >>> plot 'file.csv' using 1:2 with lines
#
#    Copyright © 2014
#                Manuel Yguel <manuel.yguel@strataggem.com>,
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


import visa, string


# get ressources
def initVisa():
    return visa.ResourceManager()

rm = initVisa()

#Initialize multimeter
def initMultimeter():
    rm = visa.ResourceManager()
    lst = rm.list_resources()
    m_name = ""
    for i in lst:
      if not ( -1 == i.find("GPIB") ) and not( -1 == i.find("22") ):
        m_name = i
    m = rm.open_resource(m_name)
    print( m.query("*IDN?") )
    m.write("*RST")
    m.write("*CLS")
    return m

m = initMultimeter()

def reset():
    m.write("*RST")
    m.write("*CLS")

#Read Voltagem
def confV():
    m.write("CONF:VOLT:DC AUTO")

def printV():
    str_volt_val = m.query("READ?")
    volt_val = float(str_volt_val[:-1])
    print( "Voltage value: " + str(volt_val) + "V" )

def takeV():
    str_volt_val = m.query("READ?")
    return float(str_volt_val[:-1])

#read Current
def confA():
    m.write("CONF:CURR:DC AUTO")

#R_val = volt_val / curr_val
#print( "Resistance equivalente: " + str(R_val) + "Ohms" )


#Measure current in one function
def printA():
    str_curr_val = m.query("READ?")
    curr_val = float(str_curr_val[:-1])
    print( "Current value: " + str(curr_val) + "A" )

def takeA():
    str_curr_val = m.query("READ?")
    return float(str_curr_val[:-1])

def maxSpeedA():
    reset()
    m.write("DISPlay OFF")
    m.write("CONFigure:CURRent:DC AUTO")
    m.write("CURRent:RESolution MAXimum")
    m.write("CURRent:NPLCycles MINimum" )
    m.write("ZERO:AUTO OFF" )
    #This does not change speed (even if recommended) but
    # when commented improves very much the results and
    # the precision
    #m.write("CURRENT:RANge:AUTO OFF" )
    m.write("TRIGger:SOURce IMMediate" )
    m.write("TRIGger:DELay 0" )


import time
#Measure current at max multimeter speed until Ctrl-C is hit
# @param[in,out] filename  This is the name of the file where
#  measurements are recorded. The measurements are recorded
#  in a csv format with a semi-colon ';' separator. The first
#  column record a time stamp in seconds for each measurement
def contMeasA( filename ):
    maxSpeedA()
    fd=None
    try:
        fd=open(filename,'w')
        t = time.clock()
        while True:
            delta_t = time.clock() - t
            v = takeA()
            fd.write( str( delta_t ) + ";" + str(v) + "\n" )
    finally:
        if fd:
            fd.close()

