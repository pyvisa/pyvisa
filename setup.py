#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    setup.py - Distutils setup script for PyVISA
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

from distribute_setup import use_setuptools
use_setuptools("0.6.24")
from setuptools import setup
from setuptools import find_packages

import distutils.dir_util
import shutil, os.path, atexit
import sys

try:
    distutils.dir_util.remove_tree("build")
except:
    pass

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
# The release name must be changed here and in doc/pyvisa.tex

setup(name = 'PyVISA',
      description = 'Python VISA bindings for GPIB, RS232, and USB instruments',
      version = '1.5',
      long_description = \
      """A Python package for support of the Virtual Instrument Software Architecture
(VISA), in order to control measurement devices and test equipment via GPIB,
RS232, or USB.  Homepage: http://pyvisa.sourceforge.net""",
      author = 'Torsten Bronger, Gregor Thalhammer',
      author_email = 'bronger@physik.rwth-aachen.de',
      maintainer_email = 'pyvisa-devel@lists.sourceforge.net',
      url = 'http://pyvisa.sourceforge.net',
      download_url = 'http://sourceforge.net/projects/pyvisa/',
      keywords = 'VISA GPIB USB serial RS232 measurement acquisition',
      license = 'MIT License',
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      packages = find_packages(),
      platforms = "Linux, Windows",
      py_modules = ['visa'],
      setup_requires = ["sphinx>=1.0", "Mock"],
      **extra)
