# -*- coding: utf-8 -*-
"""Common test case for all message based resources.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import time
import unittest

from pyvisa import constants

from .resource_utils import ResourceTestCase

try:
    import numpy as np
except ImportError:
    np = None


class EventHandler:
    """Event handler.

    """

    def __init__(self):
        self.event_success = False
        self.srq_success = False
        self.io_completed = False

    def handle_event(self, instrument, event_type, event, handle=None):
        """Event handler

        """
        if (event_type == visa.constants.EventType.service_request):
            self.event_success = True
            self.srq_success = True
            return 0
        if (event_type == visa.constants.EventType.io_completion):
            self.event_success = True
            self.io_completed = True
            return 0
        else:
            self.event_success = True
            return 0


# Add extra tests for attributes (manual term_char, manual term_char enabled)
class MessagebasedResourceTestCase(ResourceTestCase):
    """Base test case for all message based resources.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = ''

    # Any test involving communication involve to first write to glider the
    # data then request it to send it back

    def setup(self):
        """Create a resource using the address matching the type.

        """
        super().setup()
        self.instr.write_termination = '\n'
        self.instr.read_termination = '\n'
        self.instr.timeout = 100

    def test_encoding(self):
        """Tets setting the string encoding.

        """
        self.assertEqual(self.instr.encoding, 'ascii')
        self.instr.encoding = 'utf-8'

        with self.assertRaises(LookupError):
            self.instr.encoding = 'test'

    def test_termchars(self):
        """Test modifying the termchars.

        """
        # Write termination
        self.instr.write_termination = "\r\n"
        self.assertEqual(self.instr.write_termination, "\r\n")

        self.instr.read_termination = "\r\0"
        self.assertEqual(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR),
            ord("\0")
        )
        self.assertTrue(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR_EN),
        )

        # Disable read termination
        self.read_termination = None
        self.assertEqual(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR),
            ord("\n")
        )
        self.assertFalse(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR_EN),
        )

        # Ban repeated term chars
        with self.assertRaises(ValueError):
            self.instr.read_termination = "\n\n"

    def test_write_raw_read_bytes(self)
        """Test writing raw data and reading a specific number of bytes.

        """
        # Reading all bytes at once
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.read_bytes(5, chunk_size=2), "test\n")

        # Reading one byte at a time
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        for ch in b"test\n":
            self.assertEqual(self.instr.read_bytes(1), ch)

        # Breaking on termchar
        self.instr.read_termination = "\r"
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"te\rst\r\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.read_bytes(100), "te\r")
        self.assertEqual(self.read_bytes(100), "st\r")
        self.assertEqual(self.read_bytes(1), "\n")

    def test_write_raw_read_raw(self):
        """Test writing raw data and reading an answer.

        """
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.read_raw(size=2), "test\n")

    def test_write_read(self):
        """Test writing and reading.

        """
        self.instr.read_termination = '\r\n'
        self.instr.write("RECEIVE")
        self.instr.write("test\r")
        self.instr.write("SEND")
        self.assertEqual(self.read(), "test")

        # Dynamic termination
        self.instr.write_termination = "\r"
        self.instr.write("RECEIVE", termination="\n")
        self.instr.write("test\r", termination="\n")
        self.instr.write("SEND", termination="\n")
        self.assertEqual(self.read(termination="\r"), "test")

        # Test query
        elf.instr.write_termination = "\n"
        self.instr.write("RECEIVE")
        self.instr.write("test\r")
        tic = time.time()
        self.assertEqual(self.query("SEND", delay=0.5), "test")
        self.assertGreater(time.time()-tic, 0.5)

        # XXX not sure how to test encoding

    def test_write_ascii_values(self):
        """Test writing ascii values.

        """
        # Standard separator
        l = [1, 2, 3, 4, 5]
        self.instr.write("RECEIVE")
        self.instr.write_ascii_values("", l, "d")
        self.instr.write("SEND")
        self.assertEqual(self.instr.read(), "1,2,3,4,5")

        # Non standard separator and termination
        self.instr.write_termination = "\r"
        self.instr.write("RECEIVE", termination="\n")
        self.instr.write_ascii_values("", l, "d", separator=";",
                                      termination="\n")
        self.instr.write("SEND", termination="\n")
        self.assertEqual(self.instr.read(), "1:2:3:4:5")

    def test_write_binary_values(self):
        """Test writing binary data.

        """
        for hfmt, prefix in zip(("ieee", "hp", "empty"),
                                (b"#210", b"#A\n\x00", b"")):
            self.subTest(hfmt)

            l = [1, 2, 3, 4, 5]
            self.instr.write("RECEIVE")
            self.instr.write_binary_values("", l, "h", header_fmt=hfmt)
            self.instr.write("SEND")
            self.assertEqual(self.instr.read_bytes(11),
                             prefix + b"\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\n")

            if hfmt == "hp":
                prefix = prefix[0:2] + prefix[-1] = prefix[-2]
            self.instr.write_termination = "\r"
            self.instr.write("RECEIVE", termination="\n")
            self.instr.write_binary_values("", l, "h", is_big_endian=True,
                                           termination="\n", header_fmt=hfmt)
            self.instr.write("SEND", termination="\n")
            self.assertEqual(self.instr.read_bytes(11),
                             prefix + b"\x00\x01\x00\x02\x00\x01\x00\x04\x00\x05\n")

    def test_read_ascii_values(self):
        """Test reading ascii values.

        """
        # Standard separator
        l = [1, 2, 3, 4, 5]
        self.instr.write("RECEIVE")
        self.instr.write("1,2,3,4,5")
        self.instr.write("SEND")
        values = self.instr.read_ascii_values()
        self.assertIs(type(values[0]), float)
        self.assertEqual(values, [1.0, 2.0, 3.0, 4.0, 5.0])

        # Non standard separator and termination
        self.instr.write("RECEIVE")
        self.instr.write("1;2;3;4;5")
        tic = time.time()
        values = self.instr.query_ascii_values("SEND", converter='d',
                                               separator=';', delay=0.5)
        self.assertGreater(time.time()-tic, 0.5)
        self.assertIs(type(values[0]), int)
        self.assertEqual(values, [1, 2, 3, 4, 5])

        # Numpy container
        if np:
            self.instr.write("RECEIVE")
            self.instr.write("1;2;3;4;5")
            self.instr.write("SEND")
            values = self.instr.read_ascii_values(container=np.array)
            self.assertIs(values.dtype, np.float64)
            np.testing.assert_array_equal(values, np.array([1, 2, 3, 4, 5]))

    def test_read_binary_values(self):
        """Test reading binary data.

        """
        self.instr.read_termination = '\r'
        # 3328 in binary short is \x00\r this way we can interrupt the
        # transmission midway to test some corner cases
        data = [1, 2, 3328, 3, 4, 5, 6, 7]
        for hfmt in ("ieee", "hp", "empty"):
            self.subTest(hfmt)

            self.instr.write("RECEIVE")
            self.instr.write_binary_values("", data, "h", header_fmt=hfmt,
                                           write_termination='\r\n')
            self.instr.write("SEND")
            new = self.instr.read_binary_values(datatype='h',
                                                is_big_endian=False,
                                                header_fmt=hfmt,
                                                expect_termination=True,
                                                chunk_size=8)
            self.instr.read_bytes(1)
            self.assertEqual(data, new)

            self.instr.write("RECEIVE")
            self.instr.write_binary_values("", data, "h", header_fmt=hfmt,
                                           is_big_endiam=True)
            self.instr.write("SEND")
            new = self.instr.read_binary_values(datatype='h',
                                                is_big_endian=False,
                                                header_fmt=hfmt,
                                                is_big_endian=True,
                                                expect_termination=False,
                                                chunk_size=8,
                                                container= np.array if np else list)
            self.read_bytes(1)
            if np:
                np.testing.assert_array_equal(new,
                                              np.array(data, dtype=np.int16))
            else:
                self.assertEqual(data, new)


    def test_stb(self):
        """Test reading the status byte.

        """
        self.assertEqual(self.instr.stb, 0)
        self.assertEqual(self.instr.read_stb(), 0)

    def test_wait_on_event(self):
        """Test waiting on a VISA event.

        """
        event_type = constants.EventType.service_request
        event_mech = constants.EventMechanism.queue
        wait_time = 2000 # set time that program waits to receive event
        self.instrument.enable_event(event_type, event_mech, None)
        self.instrument.write("RCVSLOWSRQ")
        self.instrument.write("SENDSLOWSRQ")
        try:
            response = self.instrument.wait_on_event(event_type, wait_time)
        finally:
            self.instrument.disable_event(event_type, event_mech)
        self.assertFalse(response.timed_out)
        self.assertEqual(response.event_type, constants.EventType.service_request)

    def test_managing_visa_handler(self):
        """Test using visa handlers.

        """
        handler = EventHandler()
        event_type = visa.constants.EventType.service_request
        event_mech = visa.constants.EventMechanism.handler
        self.instr.install_handler(event_type, handler.handle_event)
        self.instr.enable_event(event_type, event_mech, None)
        self.instr.write("RCVSLOWSRQ")
        self.instr.write("SENDSLOWSRQ")

        try:
            t1 = time.time()
            while not handler.event_success:
                if (time.time() - t1) > 2:
                    break
                time.sleep(0.1)
        finally:
            self.instr.disable_event(event_type, eventMech)
            self.instr.uninstall_handler(event_type, event_hndlr)

        self.assertTrue(handler.srq_success)
