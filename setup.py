#!/usr/bin/env python

from distutils.core import setup

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(name = 'pyvisa',
      description = 'pyvisa, a python package to support the VISA I/O standard',
      version = '0.1',
      long_description = 'visa, a package to support the VISA I/O standard',
      author = 'Gregor Thalhammer, Torsten Bronger',
      author_email = 'Gregor.Thalhammer@uibk.ac.at',
      url = 'http://sourceforge.net/projects/pyvisa',
      classifiers = classifiers,
      py_modules = ['visa', 'visa_messages', 'vpp43_types', 'vpp43_constants'])
