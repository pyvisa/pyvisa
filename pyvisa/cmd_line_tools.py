# -*- coding: utf-8 -*-
"""Command line tools used for debugging and testing.

This file is part of PyVISA.

:copyright: 2019-2022 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
from typing import Optional


def visa_main(command: Optional[str] = None) -> None:
    """Run the main entry point for command line tools.

    Parameters
    ----------
    command : str, optional
        What command to invoke, if None the value is read from the command
        line arguments

    """
    import argparse

    parser = argparse.ArgumentParser(description="PyVISA command-line utilities")

    parser.add_argument(
        "--backend",
        "-b",
        dest="backend",
        action="store",
        default=None,
        help="backend to be used (default: ivi)",
    )

    if not command:
        subparsers = parser.add_subparsers(title="command", dest="command")

        subparsers.add_parser("info", help="print information to diagnose PyVISA")

        subparsers.add_parser("shell", help="start the PyVISA console")

    args = parser.parse_args()
    if command:
        args.command = command
    if args.command == "info":
        from pyvisa import util

        util.get_debug_info()
    elif args.command == "shell":
        from pyvisa import shell

        shell.main("@" + args.backend if args.backend else "")
    else:
        raise ValueError(
            f"Unknown command {args.command}. Valid values are: info and shell"
        )


def visa_shell() -> None:
    """Run the VISA shell CLI program."""
    visa_main("shell")


def visa_info() -> None:
    """Summarize the infos about PyVISA and VISA."""
    visa_main("info")
