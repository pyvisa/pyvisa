#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)


def read(filename):
    with open(filename, 'rb') as f:
        return f.read().decode('utf8')


long_description = '\n\n'.join([read('README.rst'),
                                read('AUTHORS'),
                                read('CHANGES')])

__doc__ = long_description

setup(name='PyVISA',
      description='Python VISA bindings for GPIB, RS232, TCPIP and USB instruments',
      version='1.11.0.dev',
      long_description=long_description,
      author='Torsten Bronger, Gregor Thalhammer',
      author_email='bronger@physik.rwth-aachen.de',
      maintainer='Matthieu C. Dartiailh',
      maintainer_email='m.dartiailh@gmail.com',
      url='https://github.com/pyvisa/pyvisa',
      test_suite='pyvisa.testsuite.testsuite',
      keywords='VISA GPIB USB serial RS232 measurement acquisition',
      license='MIT License',
      python_requires='>=3.6',
      install_requires=[],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        ],
      packages=['pyvisa',
                'pyvisa.ctwrapper',
                'pyvisa.resources',
                'pyvisa.thirdparty',
                'pyvisa.testsuite',
                'pyvisa.testsuite.fake-extensions',
                'pyvisa.testsuite.fakelibs',
                'pyvisa.testsuite.keysight_assisted_tests'],
      package_data={'': ['*.dll']},
      platforms="Linux, Windows, Mac",
      entry_points={'console_scripts':
                    ['pyvisa-shell=pyvisa.cmd_line_tools:visa_shell',
                     'pyvisa-info=pyvisa.cmd_line_tools:visa_info']},
      py_modules=['visa'],
      use_2to3=False,
      zip_safe=False)
