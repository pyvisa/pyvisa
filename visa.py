# -*- coding: utf-8 -*-
"""
    pyvisa.visa
    ~~~~~~~~~~~

    Module to provide an import shortcut for the most common VISA operations.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from pyvisa import logger, __version__, log_to_screen, constants
from pyvisa.highlevel import ResourceManager
from pyvisa.errors import (Error, VisaIOError, VisaIOWarning, VisaTypeError,
                           UnknownHandler, OSNotSupported, InvalidBinaryFormat,
                           InvalidSession, LibraryError)
# This is needed to registry all resources.
from pyvisa.resources import Resource

def visa_main(command=None):
    import argparse
    parser = argparse.ArgumentParser(description='PyVISA command-line utilities')

    parser.add_argument('--backend', '-b', dest='backend', action='store', default=None,
                        help='backend to be used (default: ni)')

    if not command:
        subparsers = parser.add_subparsers(title='command', dest='command')

        info_parser = subparsers.add_parser('info', help='print information to diagnose PyVISA')

        console_parser = subparsers.add_parser('shell', help='start the PyVISA console')

    args = parser.parse_args()
    if command:
        args.command = command
    if args.command == 'info':
        from pyvisa import util
        util.get_debug_info()
    elif args.command == 'shell':
        from pyvisa import shell
        shell.main('@' + args.backend if args.backend else '')

def visa_shell():
    visa_main('shell')

def visa_info():
    visa_main('info')

if __name__ == '__main__':
    visa_main()
