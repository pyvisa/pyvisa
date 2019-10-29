# -*- coding: utf-8 -*-
"""Test the shell.

"""
import time
from contextlib import redirect_stdout
from io import StringIO
from subprocess import Popen, PIPE
from threading import Thread, Event, Lock

from pyvisa.shell import VisaShell

from .. import BaseTestCase
from . import RESOURCE_ADDRESSES, ALIASES


class SubprocessOutputPoller:
    """Continuously check the stdout of a subprocess.

    """
    def __init__(self, process):
        super().__init__()
        self.process = process
        self._lines = []
        self._lines_lock = Lock()
        self._last_seen = time.monotonic()
        self.data_ready = Event()
        self._polling_thread = Thread(target=self.poll_stdout)
        self._ready_thread = Thread(target=self.check_ready)

        # Start background threads
        self._polling_thread.start()
        self._ready_thread.start()

    def poll_stdout(self):
        """Continously read stdout and update the lines.

        When no new data arrive after 1s consider that the data are ready.

        """
        for l in iter(self.process.stdout.readline, b''):
            with self._lines_lock:
                self._lines.append(l.rstrip())
                self._last_seen = time.monotonic()

    def check_ready(self):
        """Check if we got complete data.

        """
        while True:
            sleep(time.sleep(0.1))
            if time.monotonic() - self._last_seen > 1:
                self.data_ready.set()
            if not self._polling_thread.is_alive():
                break

    def get_lines(self):
        """Get the collected lines.

        """
        with self._lines_lock:
            lines = self._lines
            self._lines = []

        self.data_ready.clear()
        return lines

    def shutdown(self):
        """Wait for threads to die after the process is done.

        """
        self._polling_thread.join()
        self._ready_thread.join()


class TestVisaShell(BaseTestCase):
    """Test the VISA shell.

    """
    def setUp(self):
        """Start the shell in a subprocess.

        """
        self.shell = Popen(["pyvisa-shell"], stdin=PIPE, stdout=PIPE)
        self.reader = SubprocessOutputPoller()
        self.reader.data_ready.wait()
        self.reader.get_lines()

    def open_resource(self):
        lines = self.communicate(
            f"open {list(RESOURCE_ADDRESSES.values())[0]}")
        self.assertIn(b"has been opened.\n", lines[0])

    def communicate(self, msg):
        """Write a message on stdin and collect the answer.

        """
        self.shell.stdin.write(msg.encode("ascii") + b"\n")
        self.shell.stdin.flush()
        self.reader.data_ready.wait()
        returnself.reader.get_lines()

    def tearDown(self):
        if self.shell:
            self.shell.stdin.write(b'exit\n')
            self.shell.stdin.flush()
            self.shell.stdin.close()
            self.shell.terminate()
            self.shell.wait(0.1)
            self.reader.shutdown()

    def test_list(self):
        """Test listing the connected resources.

        """
        lines = self.communicate("list")

        msg = []
        for i, rsc in enumerate(RESOURCE_ADDRESSES.values()):
            msg.append(f"({i:2d}) {rsc}")
            if rsc in ALIASES:
                msg.append(f"     alias: {ALIASES[rsc]}")

        for l, m in zip(lines, msg):
            self.assertEqual(l, m.encode('ascii'))

    def test_list_handle_error(self):
        """Test handling an error in listing resources.

        """
        shell = VisaShell()
        shell.resource_manager = None
        temp_stdout = StringIO()
        with redirect_stdout(temp_stdout):
            shell.do_list("")
        output = temp_stdout.getvalue()
        self.assertIn('AttributeError', output)

    def test_open_no_args(self):
        """Test opening without any argument.

        """
        lines = self.communicate("open")
        self.assertEqual(b"A resource name must be specified.\n", lines)

    def test_open_by_number(self):
        """Test opening based on the index of the resource.

        """
        lines = self.communicate("open 0")
        self.assertEqual(b'Not a valid resource number. Use the command "list".',
                         lines[0])

        lines = self.communicate("list")
        lines = self.communicate("open 0")
        rsc = list(RESOURCE_ADDRESSES.values())[0]
        self.assertIn(
            f"{rsc} has been opened.".encode('ascii'),
            lines[0]
        )

        lines = self.communicate("open 0")
        self.assertEqual(
            (b'You can only open one resource at a time. '
             b'Please close the current one first.\n'),
            lines[0])

    def test_open_by_address(self):
        """Test opening based on the resource address.

        """
        rsc = list(RESOURCE_ADDRESSES.values())[0]
        lines = self.communicate(f"open {rsc}")
        self.assertIn(
            f"{rsc} has been opened.\n".encode('ascii'),
            lines[0]
        )

    def test_open_handle_exception(self):
        """Test handling an exception during opening.

        """
        rsc = list(RESOURCE_ADDRESSES.values())[0]
        lines = self.communicate('open ""')
        self.assertIn(b"VI_ERROR_INV_RSRC_NAME", lines[0])

    def test_handle_double_open(self):
        """Test handling before closing resource.

        """
        rsc = list(RESOURCE_ADDRESSES.values())[0]
        lines = self.communicate(f'open {rsc}')
        lines = self.communicate(f'open {rsc}')
        self.assertEqual(
            (b'You can only open one resource at a time. '
             b'Please close the current one first.\n'),
            lines[0])

    def test_command_on_closed_resource(self):
        """Test all the commands that cannot be run without opening a resource.

        """
        for cmd in ("close" "write", "read", "query", "termchar", "timeout", "attr"):
            lines = self.communicate(cmd)
            self.assertEqual(
                b'There are no resources in use. Use the command "open".\n',
                lines[0]
            )

    def test_close(self):
        """Test closing a resource.

        """
        rsc = list(RESOURCE_ADDRESSES.values())[0]
        lines = self.communicate("open {rsc}")
        lines = self.communicate("close")
        self.assertEqual(b'The resource has been closed.', lines[0])

        lines = self.communicate(f'open {rsc}')
        self.assertIn(b"has been opened.\n", lines[0])

    def test_close_handle_error(self):
        """Test handling an error while closing.

        """
        shell = VisaShell()
        shell.current = True
        temp_stdout = StringIO()
        with redirect_stdout(temp_stdout):
            shell.do_close("")
        output = temp_stdout.getvalue()
        self.assertIn('AttributeError', output)

    def test_query(self):
        """querying a value from the instrument.

        """
        self.open_resource()
        lines = self.communicate("query *IDN?")
        self.assertIn(b"Response: ", lines[0])

    def test_query_handle_error(self):
        """Test handling an error in query.

        """
        shell = VisaShell()
        shell.current = True
        temp_stdout = StringIO()
        with redirect_stdout(temp_stdout):
            shell.do_query("")
        output = temp_stdout.getvalue()
        self.assertIn('AttributeError', output)

# XXX keep updating
    # def test_read_write(self):
    #     """Test writing/reading values from the resource.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"write *IDN?")
    #     stdout, stderr = self.shell.communicate(b"read")
    #     self.assertIn(b"Response: ", stdout)

    # def test_read_handle_error(self):
    #     """Test handling an error in read.

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_read("")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)

    # def test_write_handle_error(self):
    #     """Test handling an error in write.

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_write("")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)

    # def test_timeout_get(self):
    #     """Test accessing the timeout.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"timeout")
    #     self.assertIn("Timeout: ", stdout)

    # def test_timeout_get_handle_error(self):
    #     """Test handling an error in getting teh timeout.

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_timeout("")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)

    # def test_timeout_set(self):
    #     """Test setting the timeout.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"timeout 1000")
    #     self.assertIn(b"Done", stdout)
    #     stdout, stderr = self.shell.communicate(b"timeout")
    #     self.assertIn("Timeout: 1000ms", stdout)

    # def test_timeout_set_handle_error(self):
    #     """Test handling an error in setting the timeout

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_timeout("1000")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)

    # def test_attr_no_args(self):
    #     """Test getting the list of attributes

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr")
    #     self.assertIn(b"VISA name", stdout)

    # def test_attr_too_many_args(self):
    #     """Test handling wrong args to attr.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr 1 2 3")
    #     self.assertIn(b"Invalid syntax, use `attr <name>` to get;"
    #                   b" or `attr <name> <value>` to set", stdout)

    # def test_attr_get_set_by_VI_non_boolean(self):
    #     """Test getting/setting an attr using the VI_ name (int value)

    #     """
    #     self.open_resource()
    #     msg = b"attr VI_ATTR_TERMCHAR {}".format(ord("\r"))
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Done", stdout)

    #     stdout, stderr = self.shell.communicate(b"attr VI_ATTR_TERMCHAR")
    #     self.assertIn(b"\r", stdout)

    # def test_attr_get_set_by_VI_boolean(self):
    #     """Test getting/setting an attr using the VI_ name (bool value)

    #     """
    #     self.open_resource()
    #     msg = f"attr VI_ATTR_TERMCHA_EN False"
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Done", stdout)

    #     stdout, stderr = self.shell.communicate(b"attr VI_ATTR_TERMCHAR")
    #     self.assertIn(b"False", stdout)

    # def test_attr_get_by_VI_handle_error(self):
    #     """Test accessing an attr by an unknown VI name.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr VI_test")
    #     self.assertIn(b"AttributeError", stdout)

    # def test_attr_get_by_name(self):
    #     """Test accessing an attr by Python name.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr allow_dma")
    #     self.assertTrue(b"True" in stdout or b"False" in stdout)

    # def test_attr_get_by_name_handle_error(self):
    #     """Test accessing an attr by an unknown Python name.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr test")
    #     self.assertIn(b"AttributeError", stdout)

    # def test_attr_set_by_VI_handle_error_unknown_attr(self):
    #     """Test handling issue in setting VI attr which does not exist.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"attr VI_test test")
    #     self.assertIn(b"AttributeError", stdout)

    # def test_attr_set_by_VI_handle_error_non_boolean(self):
    #     """Test handling issue in setting VI attr. (non boolean value)

    #     """
    #     self.open_resource()
    #     msg = f"attr VI_ATTR_TERMCHA_EN Test"
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Error", stdout)

    # def test_attr_set_by_VI_handle_error_non_interger(self):
    #     """Test handling issue in setting VI attr. (non integer value)

    #     """
    #     self.open_resource()
    #     msg = f"attr VI_ATTR_TERMCHAR Test"
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Error", stdout)

    # def test_attr_set_by_VI_handle_error_wrong_value(self):
    #     """Test handling issue in setting VI attr by name. (wrong value)

    #     """
    #     self.open_resource()
    #     msg = f"attr VI_ATTR_TERMCHAR -1"
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Error", stdout)

    # def test_attr_set_by_name_handle_error(self):
    #     """Test handling attempt to set attr by name (which is not supported).

    #     """
    #     self.open_resource()
    #     msg = f"attr allow_dma Test"
    #     stdout, stderr = self.shell.communicate(msg.encode("ascii"))
    #     self.assertIn(b"Setting Resource Attributes by python name is not yet "
    #                   b"supported.", stdout)

    # def test_complete_attr(self):
    #     """Test providing auto-completion for attrs.

    #     """
    #     shell = VisaShell()
    #     shell.current = shell.do_open(RESOURCE_ADDRESSES[0])
    #     completions = shell.complete_attr("VI_ATTR_TERM", 0, 0, 0)
    #     self.assertIn('VI_ATTR_TERMCHAR', completions)
    #     self.assertIn('VI_ATTR_TERMCHAR_EN', completions)

    #     shell.complete_attr("allow_d", 0, 0, 0)
    #     self.assertIn('allow_dma', completions)

    # def test_termchar_get_handle_error(self):
    #     """Test handling error when getting the termchars.

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_termchar("")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)

    # def test_termchar_get_set_both_identical(self):
    #     """Test setting both termchars to the same value.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"termchar CR")
    #     self.assertIn(b"Done", stdout)

    #     stdout, stderr = self.shell.communicate(b"termchar")
    #     self.assertIn(rb"Termchar read: \r write: \r", stdout)

    # def test_termchar_get_set_both_different(self):
    #     """Test setting both termchars to different values.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"termchar CR NUL")
    #     self.assertIn(b"Done", stdout)

    #     stdout, stderr = self.shell.communicate(b"termchar")
    #     self.assertIn(rb"Termchar read: \r write: \0", stdout)

    # def test_termchar_set_too_many_args(self):
    #     """Test handling to many termchars to termchar.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"termchar 1 2 3")
    #     self.assertIn(b"Invalid syntax", stdout)

    # def test_termchar_set_handle_error_wrong_value(self):
    #     """Test handling wrong value in setting termchar.

    #     """
    #     self.open_resource()
    #     stdout, stderr = self.shell.communicate(b"termchar tt")
    #     self.assertIn(b"use CR, LF, CRLF, NUL or None to set termchar", stdout)

    # def test_termchar_set_handle_error(self):
    #     """Test handling an error in setting the termchars.

    #     """
    #     shell = VisaShell()
    #     shell.current = True
    #     temp_stdout = StringIO()
    #     with redirect_stdout(temp_stdout):
    #         shell.do_termchar("CR")
    #     output = temp_stdout.getvalue()
    #     self.assertIn('AttributeError', output)
