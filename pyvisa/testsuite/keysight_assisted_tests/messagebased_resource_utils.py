# -*- coding: utf-8 -*-
"""Common test case for all message based resources.

"""
import ctypes
import gc
import time

from pyvisa import constants, errors

from .resource_utils import ResourceTestCase

try:
    import numpy as np  # type: ignore
except ImportError:
    np = None


class EventHandler:
    """Event handler.

    """

    def __init__(self) -> None:
        self.event_success = False
        self.srq_success = False
        self.io_completed = False
        self.handle = None
        self.session = None

    def handle_event(self, session, event_type, event, handle=None):
        """Event handler

        Ctypes handler are expected to return an interger.

        """
        self.session = session
        self.handle = handle
        if event_type == constants.EventType.service_request:
            self.event_success = True
            self.srq_success = True
            return 0
        if event_type == constants.EventType.io_completion:
            self.event_success = True
            self.io_completed = True
            return 0
        else:
            self.event_success = True
            return 0

    def simplified_handler(self, resource, event, handle=None):
        """Simplified handler that can be wrapped.

        """
        self.session = resource.session
        self.handle = handle
        event_type = event.event_type
        if event_type == constants.EventType.service_request:
            self.event_success = True
            self.srq_success = True
            return None  # was 0
        if event_type == constants.EventType.io_completion:
            self.event_success = True
            self.io_completed = True
            return None
        else:
            self.event_success = True
            return None


class MessagebasedResourceTestCase(ResourceTestCase):
    """Base test case for all message based resources.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = ""

    # Any test involving communication involve to first write to glider the
    # data then request it to send it back

    def setUp(self):
        """Create a resource using the address matching the type.

        """
        super().setUp()
        self.instr.write_termination = "\n"
        self.instr.read_termination = "\n"
        self.instr.timeout = 100

    def compare_user_handle(self, h1, h2):
        """Function comparing to user handle as passed to a callback.

        We need such an indirection because we cannot safely always return
        a Python object and most ctypes object do not compare equal.

        """
        if isinstance(h1, ctypes.Structure):
            return h1 == h2
        elif hasattr(h1, "value"):
            return h1.value == h2.value
        else:  # assume an array
            return all((i == j for i, j in zip(h1, h2)))

    def test_encoding(self):
        """Tets setting the string encoding.

        """
        self.assertEqual(self.instr.encoding, "ascii")
        self.instr.encoding = "utf-8"

        with self.assertRaises(LookupError):
            self.instr.encoding = "test"

    def test_termchars(self):
        """Test modifying the termchars.

        """
        # Write termination
        self.instr.write_termination = "\r\n"
        self.assertEqual(self.instr.write_termination, "\r\n")

        self.instr.read_termination = "\r\0"
        self.assertEqual(self.instr.read_termination, "\r\0")
        # self.assertEqual(self.instr.VI_ATTR_TERMCHAR, ord("\0"))
        self.assertEqual(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR), ord("\0")
        )
        # self.assertTrue(self.instr.VI_ATTR_TERMCHAR_EN)
        self.assertTrue(self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR_EN),)

        # Disable read termination
        self.instr.read_termination = None
        # self.assertEqual(self.instr.VI_ATTR_TERMCHAR, ord("\n"))
        self.assertEqual(
            self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR), ord("\n")
        )
        # self.assertFalse(self.instr.VI_ATTR_TERMCHAR_EN)
        self.assertFalse(self.instr.get_visa_attribute(constants.VI_ATTR_TERMCHAR_EN),)

        # Ban repeated term chars
        with self.assertRaises(ValueError):
            self.instr.read_termination = "\n\n"

    def test_write_raw_read_bytes(self):
        """Test writing raw data and reading a specific number of bytes.

        """
        # Reading all bytes at once
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        count = self.instr.write_raw(b"SEND\n")
        self.assertEqual(count, 5)
        self.instr.flush(constants.VI_READ_BUF)
        self.assertEqual(self.instr.read_bytes(5, chunk_size=2), b"test\n")

        # Reading one byte at a time
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        for ch in b"test\n":
            self.assertEqual(self.instr.read_bytes(1), ch.to_bytes(1, "little"))

        # Breaking on termchar XXX handle the case of breaking on end of message
        self.instr.read_termination = "\r"
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"te\rst\r\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.instr.read_bytes(100, break_on_termchar=True), b"te\r")
        self.assertEqual(self.instr.read_bytes(100, break_on_termchar=True), b"st\r")
        self.assertEqual(self.instr.read_bytes(1), b"\n")

        # Breaking on end of message
        self.instr.read_termination = "\n"
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.instr.read_bytes(100, break_on_termchar=True), b"test\n")

    def test_handling_exception_in_read_bytes(self):
        """Test handling exception in read_bytes (monkeypatching)

        """

        def false_read(session, size):
            raise errors.VisaIOError(constants.VI_ERROR_ABORT)

        read = self.instr.visalib.read
        self.instr.visalib.read = false_read
        with self.assertLogs(level="DEBUG") as cm:
            try:
                self.instr.read_bytes(1)
            except errors.VisaIOError:
                pass
            finally:
                self.instr.visalib.read = read
        self.assertIn("- exception while reading:", cm.output[1])

    def test_write_raw_read_raw(self):
        """Test writing raw data and reading an answer.

        """
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")
        self.assertEqual(self.instr.read_raw(size=2), b"test\n")

    def test_write_read(self):
        """Test writing and reading.

        """
        self.instr.write_termination = "\n"
        self.instr.read_termination = "\r\n"
        self.instr.write("RECEIVE")
        with self.assertWarns(UserWarning):
            self.instr.write("test\r\n")
        count = self.instr.write("SEND")
        self.assertEqual(count, 5)
        self.assertEqual(self.instr.read(), "test")

        # Missing termination chars
        self.instr.read_termination = "\r\n"
        self.instr.write("RECEIVE")
        self.instr.write("test")
        self.instr.write("SEND")
        with self.assertWarns(Warning):
            self.assertEqual(self.instr.read(), "test\n")

        # Dynamic termination
        self.instr.write_termination = "\r"
        self.instr.write("RECEIVE\n", termination=False)
        self.instr.write("test\r", termination="\n")
        self.instr.write("SEND", termination="\n")
        self.assertEqual(self.instr.read(termination="\r"), "test")

        # Test query
        self.instr.write_termination = "\n"
        self.instr.write("RECEIVE")
        self.instr.write("test\r")
        tic = time.time()
        self.assertEqual(self.instr.query("SEND", delay=0.5), "test")
        self.assertGreater(time.time() - tic, 0.5)

        # Test handling repeated term char
        self.instr.read_termination = "\n"
        for char in ("\r", None):
            self.instr.write_termination = "\n" if char else "\r"
            self.instr.write("RECEIVE", termination="\n")
            with self.assertWarns(Warning):
                self.instr.write("test\r", termination=char)
            self.instr.write("", termination="\n")
            self.instr.write("SEND", termination="\n")
            self.assertEqual(self.instr.read(), "test\r\r")

        # XXX not sure how to test encoding

    def test_handling_exception_in_read_raw(self):
        """Test handling exception in read_bytes (monkeypatching)

        """

        def false_read(session, size):
            raise errors.VisaIOError(constants.VI_ERROR_ABORT)

        read = self.instr.visalib.read
        self.instr.visalib.read = false_read
        with self.assertLogs(level="DEBUG"):
            try:
                self.instr.read()
            except errors.VisaIOError:
                pass
            finally:
                self.instr.visalib.read = read

    def test_write_ascii_values(self):
        """Test writing ascii values.

        """
        # Standard separator
        values = [1, 2, 3, 4, 5]
        self.instr.write("RECEIVE")
        count = self.instr.write_ascii_values("", values, "d")
        self.assertEqual(count, 10)
        self.instr.write("SEND")
        self.assertEqual(self.instr.read(), "1,2,3,4,5")

        # Non standard separator and termination
        self.instr.write_termination = "\r"
        self.instr.write("RECEIVE", termination="\n")
        self.instr.write_ascii_values("", values, "d", separator=";", termination=False)
        self.instr.write("", termination="\n")
        self.instr.write("SEND", termination="\n")
        self.assertEqual(self.instr.read(), "1;2;3;4;5")

        # Test handling repeated term char
        for char in ("\r", None):
            self.instr.write_termination = "\n" if char else "\r"
            self.instr.write("RECEIVE", termination="\n")
            with self.assertWarns(Warning):
                values = [1, 2, 3, 4, 5]
                self.instr.write_ascii_values(
                    "\r", values, "s", separator=";", termination=char
                )
            self.instr.write("", termination="\n")
            self.instr.write("SEND", termination="\n")
            self.assertEqual(self.instr.read(), "\r1;2;3;4;5\r")

    def test_write_binary_values(self):
        """Test writing binary data.

        """
        for hfmt, prefix in zip(("ieee", "hp", "empty"), (b"#210", b"#A\n\x00", b"")):
            self.subTest(hfmt)

            values = [1, 2, 3, 4, 5]
            self.instr.write_termination = "\n"
            self.instr.write("RECEIVE")
            count = self.instr.write_binary_values("", values, "h", header_fmt=hfmt)
            # Each interger encoded as h uses 2 bytes
            self.assertEqual(count, len(prefix) + 10 + 1)
            self.instr.write("SEND")
            self.assertEqual(
                self.instr.read_bytes(11 + len(prefix)),
                prefix + b"\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\n",
            )

            if hfmt == "hp":
                prefix = prefix[0:2] + prefix[-2::][::-1]
            self.instr.write_termination = "\r"
            self.instr.write("RECEIVE", termination="\n")
            self.instr.write_binary_values(
                "", values, "h", is_big_endian=True, termination=False, header_fmt=hfmt
            )
            self.instr.write("", termination="\n")
            self.instr.write("SEND", termination="\n")
            self.assertEqual(
                self.instr.read_bytes(11 + len(prefix)),
                prefix + b"\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\n",
            )

        # Test handling repeated term char
        self.subTest("Repeated term char")
        for char in ("\r", None):
            self.instr.write_termination = "\n" if char else "\r"
            self.instr.write("RECEIVE", termination="\n")
            with self.assertWarns(Warning):
                self.instr.write_binary_values(
                    "\r", values, "h", header_fmt=hfmt, termination=char
                )
            self.instr.write("", termination="\n")
            self.instr.write("SEND", termination="\n")
            self.assertEqual(
                self.instr.read(), "\r\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\r"
            )

        # Wrong header format
        with self.assertRaises(ValueError):
            self.instr.write_binary_values("", values, "h", header_fmt="zxz")

    def test_read_ascii_values(self):
        """Test reading ascii values.

        """
        # Standard separator
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
        values = self.instr.query_ascii_values(
            "SEND", converter="d", separator=";", delay=0.5
        )
        self.assertGreater(time.time() - tic, 0.5)
        self.assertIs(type(values[0]), int)
        self.assertEqual(values, [1, 2, 3, 4, 5])

        # Numpy container
        if np:
            self.instr.write("RECEIVE")
            self.instr.write("1,2,3,4,5")
            self.instr.write("SEND")
            values = self.instr.read_ascii_values(container=np.array)
            expected = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            self.assertIs(values.dtype, expected.dtype)
            np.testing.assert_array_equal(values, expected)

    def test_read_binary_values(self):
        """Test reading binary data.

        """
        # XXX test handling binary decoding issue (troublesome)
        self.instr.read_termination = "\r"
        # 3328 in binary short is \x00\r this way we can interrupt the
        # transmission midway to test some corner cases
        data = [1, 2, 3328, 3, 4, 5, 6, 7]
        for hfmt in ("ieee", "hp"):
            print(hfmt)
            self.subTest(hfmt)

            self.instr.write("RECEIVE")
            self.instr.write_binary_values(
                "", data, "h", header_fmt=hfmt, termination="\r\n"
            )
            self.instr.write("SEND")
            new = self.instr.read_binary_values(
                datatype="h",
                is_big_endian=False,
                header_fmt=hfmt,
                expect_termination=True,
                chunk_size=8,
            )
            self.instr.read_bytes(1)
            self.assertEqual(data, new)

            self.instr.write("RECEIVE")
            self.instr.write_binary_values(
                "", data, "h", header_fmt=hfmt, is_big_endian=True
            )

            new = self.instr.query_binary_values(
                "SEND",
                datatype="h",
                header_fmt=hfmt,
                is_big_endian=True,
                expect_termination=False,
                chunk_size=8,
                container=np.array if np else list,
            )
            self.instr.read_bytes(1)
            if np:
                np.testing.assert_array_equal(new, np.array(data, dtype=np.int16))
            else:
                self.assertEqual(data, new)

    def test_read_query_binary_values_invalid_header(self):
        """Test we properly handle an invalid header.

        """
        data = [1, 2, 3328, 3, 4, 5, 6, 7]
        self.instr.write("RECEIVE")
        self.instr.write_binary_values(
            "", data, "h", header_fmt="ieee", is_big_endian=True
        )
        self.instr.write("SEND")
        with self.assertRaises(ValueError):
            self.instr.read_binary_values(
                datatype="h",
                is_big_endian=False,
                header_fmt="invalid",
                expect_termination=True,
                chunk_size=8,
            )

        self.instr.write("RECEIVE")
        self.instr.write_binary_values(
            "", data, "h", header_fmt="ieee", is_big_endian=True
        )
        with self.assertRaises(ValueError):
            self.instr.query_binary_values(
                "*IDN",
                datatype="h",
                is_big_endian=False,
                header_fmt="invalid",
                expect_termination=True,
                chunk_size=8,
            )

    def test_handling_malformed_binary(self):
        """

        """
        pass

    def test_read_binary_values_unreported_length(self):
        """Test reading binary data.

        """
        self.instr.read_termination = "\r"
        # 3328 in binary short is \x00\r this way we can interrupt the
        # transmission midway to test some corner cases
        data = [1, 2, 3328, 3, 4, 5]
        for hfmt, header in zip(("ieee", "hp", "empty"), ("#10", "#A\x00\x00", "")):
            print(hfmt)
            self.subTest(hfmt)

            self.instr.write("RECEIVE")
            self.instr.write(
                header + "\x01\x00\x02\x00\x00\r\x03\x00\x04\x00\x05\x00",
                termination="\r\n",
            )
            self.instr.write("SEND")
            new = self.instr.read_binary_values(
                datatype="h",
                is_big_endian=False,
                header_fmt=hfmt,
                expect_termination=True,
                chunk_size=6,
                data_points=6,
            )
            self.instr.read_bytes(1)
            self.assertEqual(data, new)

            self.instr.write("RECEIVE")
            self.instr.write(
                header + "\x00\x01\x00\x02\r\x00\x00\x03\x00\x04\x00\x05",
                termination="\r\n",
            )
            new = self.instr.query_binary_values(
                "SEND",
                datatype="h",
                header_fmt=hfmt,
                is_big_endian=True,
                expect_termination=False,
                chunk_size=6,
                container=np.array if np else list,
                data_points=6,
            )
            self.instr.read_bytes(1)
            if np:
                np.testing.assert_array_equal(new, np.array(data, dtype=np.int16))
            else:
                self.assertEqual(data, new)

            # Check we do error on unreported/unspecified length
            self.instr.write("RECEIVE")
            self.instr.write(
                header + "\x01\x00\x02\x00\x00\r\x03\x00\x04\x00\x05\x00",
                termination="\r\n",
            )
            self.instr.write("SEND")
            with self.assertRaises(ValueError):
                self.instr.read_binary_values(
                    datatype="h",
                    is_big_endian=False,
                    header_fmt=hfmt,
                    expect_termination=True,
                    chunk_size=6,
                )

    def test_delay_in_query_ascii(self):
        """Test handling of the delay argument in query_ascii_values.

        """
        # Test using the instrument wide delay
        self.instr.query_delay = 1.0
        self.instr.write("RECEIVE")
        self.instr.write("1,2,3,4,5")
        tic = time.perf_counter()
        values = self.instr.query_ascii_values("SEND")
        self.assertGreater(time.perf_counter() - tic, 1.0)
        self.assertIs(type(values[0]), float)
        self.assertEqual(values, [1.0, 2.0, 3.0, 4.0, 5.0])

        # Test specifying the delay
        self.instr.query_delay = 0.0
        self.instr.write("RECEIVE")
        self.instr.write("1,2,3,4,5")
        tic = time.perf_counter()
        values = self.instr.query_ascii_values("SEND", delay=1.0)
        self.assertGreater(time.perf_counter() - tic, 1.0)
        self.assertIs(type(values[0]), float)
        self.assertEqual(values, [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_delay_in_query_binary(self):
        """Test handling of the delay argument in query_ascii_values.

        """
        header = "#10"
        data = [1, 2, 3328, 3, 4, 5]
        # Test using the instrument wide delay
        self.instr.query_delay = 1.0
        self.instr.write("RECEIVE")
        self.instr.write(
            header + "\x00\x01\x00\x02\r\x00\x00\x03\x00\x04\x00\x05",
            termination="\r\n",
        )
        tic = time.perf_counter()
        new = self.instr.query_binary_values(
            "SEND",
            datatype="h",
            header_fmt="ieee",
            is_big_endian=True,
            expect_termination=False,
            chunk_size=6,
            data_points=6,
        )

        self.assertGreater(time.perf_counter() - tic, 1.0)
        self.assertEqual(data, new)

        # Test specifying the delay
        self.instr.query_delay = 0.0
        self.instr.write("RECEIVE")
        self.instr.write(
            header + "\x00\x01\x00\x02\r\x00\x00\x03\x00\x04\x00\x05",
            termination="\r\n",
        )
        tic = time.perf_counter()
        new = self.instr.query_binary_values(
            "SEND",
            datatype="h",
            header_fmt="ieee",
            is_big_endian=True,
            expect_termination=False,
            chunk_size=6,
            data_points=6,
            delay=1.0,
        )

        self.assertGreater(time.perf_counter() - tic, 1.0)
        self.assertEqual(data, new)

    def test_stb(self):
        """Test reading the status byte.

        """
        self.assertTrue(0 <= self.instr.stb <= 256)
        self.assertTrue(0 <= self.instr.read_stb() <= 256)

    def test_wait_on_event(self):
        """Test waiting on a VISA event.

        """
        event_type = constants.EventType.service_request
        event_mech = constants.EventMechanism.queue
        wait_time = 2000  # set time that program waits to receive event
        self.instr.enable_event(event_type, event_mech, None)
        self.instr.write("RCVSLOWSRQ")
        self.instr.write("1")
        self.instr.write("SENDSLOWSRQ")
        try:
            response = self.instr.wait_on_event(event_type, wait_time)
        finally:
            self.instr.disable_event(event_type, event_mech)

        self.assertFalse(response.timed_out)
        self.assertEqual(response.event.event_type, constants.EventType.service_request)
        self.assertEqual(self.instr.read(), "1")

        with self.assertWarns(FutureWarning):
            response.event_type
        with self.assertWarns(FutureWarning):
            response.context

    def test_wait_on_event_timeout(self):
        """Test waiting on a VISA event.

        """
        event_type = constants.EventType.service_request
        event_mech = constants.EventMechanism.queue
        # Emit a clear to avoid dealing with previous requests
        self.instr.clear()
        self.instr.enable_event(event_type, event_mech, None)
        try:
            response = self.instr.wait_on_event(event_type, 10, capture_timeout=True)
        finally:
            self.instr.disable_event(event_type, event_mech)
        self.assertTrue(response.timed_out)
        self.assertEqual(response.event.event_type, event_type)

        with self.assertRaises(errors.VisaIOError):
            self.instr.enable_event(event_type, event_mech, None)
            try:
                response = self.instr.wait_on_event(event_type, 10)
            finally:
                self.instr.disable_event(event_type, event_mech)

    def test_managing_visa_handler(self):
        """Test using visa handlers.

        """

        def _test(handle):
            handler = EventHandler()
            event_type = constants.EventType.service_request
            event_mech = constants.EventMechanism.handler
            user_handle = self.instr.install_handler(
                event_type, handler.handle_event, user_handle=handle
            )
            self.instr.enable_event(event_type, event_mech, None)
            self.instr.write("RCVSLOWSRQ")
            self.instr.write("1")
            self.instr.write("SENDSLOWSRQ")

            try:
                t1 = time.time()
                while not handler.event_success:
                    if (time.time() - t1) > 2:
                        break
                    time.sleep(0.1)
            finally:
                self.instr.disable_event(event_type, event_mech)
                self.instr.uninstall_handler(
                    event_type, handler.handle_event, user_handle
                )

            self.assertEqual(handler.session, self.instr.session)
            self.assertTrue(self.compare_user_handle(handler.handle, user_handle))
            self.assertTrue(handler.srq_success)
            self.assertEqual(self.instr.read(), "1")
            self.instr.clear()

        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

            def __eq__(self, other):
                if type(self) is not type(other):
                    return False
                return self.x == other.x and self.y == other.y

        for handle in (1, 1.0, "1", [1], [1.0], Point(1, 2)):
            print(handle)
            _test(handle)

    def test_wrapping_handler(self):
        """Test wrapping a handler using a Resource."""
        handler = EventHandler()
        event_type = constants.EventType.service_request
        event_mech = constants.EventMechanism.handler
        wrapped_handler = self.instr.wrap_handler(handler.simplified_handler)
        user_handle = self.instr.install_handler(event_type, wrapped_handler, 1)
        self.instr.enable_event(event_type, event_mech, None)
        self.instr.write("RCVSLOWSRQ")
        self.instr.write("1")
        self.instr.write("SENDSLOWSRQ")

        try:
            t1 = time.time()
            while not handler.event_success:
                if (time.time() - t1) > 2:
                    break
                time.sleep(0.1)
        finally:
            self.instr.disable_event(event_type, event_mech)
            self.instr.uninstall_handler(event_type, wrapped_handler, user_handle)

        self.assertEqual(handler.session, self.instr.session)
        self.assertTrue(self.compare_user_handle(handler.handle, user_handle))
        self.assertTrue(handler.srq_success)
        self.assertEqual(self.instr.read(), "1")

    def test_handling_invalid_handler(self):
        """Test handling an error related to a wrong handler type."""
        with self.assertRaises(errors.VisaTypeError):
            event_type = constants.EventType.service_request
            self.instr.install_handler(event_type, 1, object())

    def test_uninstalling_missing_visa_handler(self):
        """Test uninstalling a visa handler that was not registered."""
        handler1 = EventHandler()
        handler2 = EventHandler()
        event_type = constants.EventType.service_request
        self.instr.install_handler(event_type, handler1.handle_event)
        with self.assertRaises(errors.UnknownHandler):
            self.instr.uninstall_handler(event_type, handler2.handle_event)

        self.instr.uninstall_handler(event_type, handler1.handle_event)

        with self.assertRaises(errors.UnknownHandler):
            self.instr.uninstall_handler(event_type, handler2.handle_event)

    def test_handler_clean_up_on_resource_del(self):
        """Test that handlers are properly cleaned when a resource is deleted.

        """
        handler = EventHandler()
        event_type = constants.EventType.service_request
        self.instr.install_handler(event_type, handler.handle_event)

        self.instr = None
        gc.collect()
        self.assertFalse(self.rm.visalib.handlers)

    def test_uninstall_all_handlers(self):
        """Test uninstall all handlers from all sessions.

        """
        handler = EventHandler()
        event_type = constants.EventType.service_request
        self.instr.install_handler(event_type, handler.handle_event)

        self.rm.visalib.uninstall_all_visa_handlers(None)
        self.assertFalse(self.rm.visalib.handlers)

    def test_manual_async_read(self):
        """Test handling IOCompletion event which has extra attributes."""
        # Prepare message
        self.instr.write_raw(b"RECEIVE\n")
        self.instr.write_raw(b"test\n")
        self.instr.write_raw(b"SEND\n")

        # Enable event handling
        event_type = constants.EventType.io_completion
        event_mech = constants.EventMechanism.queue
        wait_time = 2000  # set time that program waits to receive event
        self.instr.enable_event(event_type, event_mech, None)

        try:
            visalib = self.instr.visalib
            buffer, job_id, status_code = visalib.read_asynchronously(
                self.instr.session, 10
            )
            self.assertIs(buffer, visalib.get_buffer_from_id(job_id))
            response = self.instr.wait_on_event(event_type, wait_time)
        finally:
            self.instr.disable_event(event_type, event_mech)

        self.assertEqual(response.event.status, constants.StatusCode.success)
        self.assertEqual(bytes(buffer), bytes(response.event.buffer))
        self.assertEqual(bytes(response.event.data), b"test\n")
        self.assertEqual(response.event.return_count, 5)
        self.assertEqual(response.event.operation_name, "viReadAsync")

    def test_shared_locking(self):
        """Test locking/unlocking a resource.

        """
        instr2 = self.rm.open_resource(str(self.rname))
        instr3 = self.rm.open_resource(str(self.rname))

        key = self.instr.lock()
        instr2.lock(requested_key=key)

        self.assertTrue(self.instr.query("*IDN?"))
        self.assertTrue(instr2.query("*IDN?"))
        with self.assertRaises(errors.VisaIOError):
            instr3.query("*IDN?")

        # Share the lock for a limited time
        with instr3.lock_context(requested_key=key) as key2:
            self.assertTrue(instr3.query("*IDN?"))
            self.assertEqual(key, key2)

        # Stop sharing the lock
        instr2.unlock()

        with self.assertRaises(errors.VisaIOError):
            instr2.query("*IDN?")
        with self.assertRaises(errors.VisaIOError):
            instr3.query("*IDN?")

        self.instr.unlock()

        self.assertTrue(instr3.query("*IDN?"))

    def test_exclusive_locking(self):
        """Test locking/unlocking a resource.

        """
        instr2 = self.rm.open_resource(str(self.rname))

        self.instr.lock_excl()
        with self.assertRaises(errors.VisaIOError):
            instr2.query("*IDN?")

        self.instr.unlock()

        self.assertTrue(instr2.query("*IDN?"))

        # Share the lock for a limited time
        with self.instr.lock_context(requested_key="exclusive") as key:
            self.assertIsNone(key)
            with self.assertRaises(errors.VisaIOError):
                instr2.query("*IDN?")
