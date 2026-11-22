# -*- coding: utf-8 -*-
"""Test the help and the message based commands of the interactive shell."""

import io

import pytest

from pyvisa import shell


class FakeResource:
    """Resource recording the messages sent through the shell."""

    def __init__(self):
        self.sent = []

    def write(self, message):
        self.sent.append(("write", message))

    def read(self):
        self.sent.append(("read", None))
        return "answer"

    def query(self, message):
        self.sent.append(("query", message))
        return "answer"


@pytest.fixture
def visa_shell(monkeypatch):
    """Shell using a fake resource, which does not need a VISA library."""
    monkeypatch.setattr(shell, "ResourceManager", lambda library_path: None)
    visa_shell = shell.VisaShell()
    # The help is written to the stdout of the shell, not to the print output.
    visa_shell.stdout = io.StringIO()
    visa_shell.current = FakeResource()
    return visa_shell


@pytest.mark.parametrize("command", ["write", "read", "query"])
def test_help_describes_message_commands(visa_shell, command):
    """The help of the message commands tells what each of them does."""
    visa_shell.onecmd(f"help {command}")
    out = visa_shell.stdout.getvalue()
    # The help of write used to suggest "send *IDN?", which is not a command.
    assert "send *IDN?" not in out
    assert command in out


def test_help_write_tells_that_nothing_is_read(visa_shell):
    visa_shell.onecmd("help write")
    assert "without reading a response" in visa_shell.stdout.getvalue()


def test_help_query_tells_that_the_response_is_printed(visa_shell):
    visa_shell.onecmd("help query")
    assert "print its response" in visa_shell.stdout.getvalue()


def test_write_sends_the_command_and_prints_nothing(visa_shell, capsys):
    visa_shell.onecmd("write *RST")
    assert visa_shell.current.sent == [("write", "*RST")]
    assert capsys.readouterr().out == ""


def test_read_prints_the_response_without_sending(visa_shell, capsys):
    visa_shell.onecmd("read")
    assert visa_shell.current.sent == [("read", None)]
    assert capsys.readouterr().out == "answer\n"


def test_query_prints_the_response(visa_shell, capsys):
    visa_shell.onecmd("query *IDN?")
    assert visa_shell.current.sent == [("query", "*IDN?")]
    assert capsys.readouterr().out == "Response: answer\n"
