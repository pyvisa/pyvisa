# -*- coding: utf-8 -*-
"""
    pyvisa.cmd_line_tools
    ~~~~~~~~~~~~~~~~~~~~~

    Command line tools used for debugging and testing.

    This file is part of PyVISA.

    :copyright: 2019 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import



def visa_main(command=None):
    import argparse
    parser = argparse.ArgumentParser(description='PyVISA command-line utilities')

    parser.add_argument('--backend', '-b', dest='backend', action='store', default=None,
                        help='backend to be used (default: ivi)')

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
