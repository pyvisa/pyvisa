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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import distutils.dir_util
import shutil, os.path, atexit

try:
    distutils.dir_util.remove_tree("build")
except:
    pass



# POSIX-specific code related to RPM package configuration; other users are free to
# bypass this section altogether.
if os.name == 'posix':
	# The following code may be very specific to my own home configuration,
	# although I hope that it's useful to other who try to create PyVISA packages,
	# too.
	#
	# The goal is to override an existing local RPM configuration.  Distutils only
	# works together with a widely untouched configuration, so I have to disable
	# any extisting one represented by the file ~/.rpmmacros.  I look for this file
	# and move it to ~/.rpmmacros.original.  After setup.py is terminated, this
	# renaming is reverted.
	#
	# Additionally, if a file ~/.rpmmacros.distutis exists, it is used for
	# ~/.rpmmacros while setup.py is running.  So you can still make use of things
	# like "%vendor" or "%packager".
    home_dir = os.environ['HOME']
    real_rpmmacros_name = os.path.join(home_dir, '.rpmmacros')
    distutils_rpmmacros_name = os.path.join(home_dir, '.rpmmacros.distutils')
    temp_rpmmacros_name = os.path.join(home_dir, '.rpmmacros.original')

    def restore_rpmmacros():
        shutil.move(temp_rpmmacros_name, real_rpmmacros_name)
    
    # I check whether temp_rpmmacros_name exists for two reasons: First, I don't
    # want to overwrite it, and secondly, I don't want this renaming to take place
    # twice.  This would happen otherwise, because setup.py is called more than
    # once per building session.
    if os.path.isfile(real_rpmmacros_name) and \
            not os.path.isfile(temp_rpmmacros_name):
        shutil.move(real_rpmmacros_name, temp_rpmmacros_name)
        if os.path.isfile(distutils_rpmmacros_name):
            shutil.copy(distutils_rpmmacros_name, real_rpmmacros_name)
        atexit.register(restore_rpmmacros)
    
    # FixMe: Maybe this should be done in Python itself (using distutils.dep_util),
    # eventually.
    os.system("make --directory=doc/")
    os.system("ln -s ../doc src/")

# The release name must be changed here and in doc/pyvisa.tex

setup(name = 'PyVISA',
      description = 'Python VISA bindings for GPIB, RS232, and USB instruments',
      version = '1.4',
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
      license = 'GNU General Public License',
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
      package_dir = {'pyvisa': 'src'},
      package_data = {'pyvisa': ['doc/pyvisa.pdf', 'doc/vpp43.txt']},
      packages = ['pyvisa'],
      platforms = "Linux, Windows",
      py_modules = ['visa'])
