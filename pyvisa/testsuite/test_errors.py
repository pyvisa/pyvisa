# -*- coding: utf-8 -*-
"""Test the handling of errors.

"""
import pickle

from pyvisa import errors
from pyvisa.testsuite import BaseTestCase


class TestPicleUnpickle(BaseTestCase):
    def _test_pickle_unpickle(self, instance):
        pickled = pickle.dumps(instance)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, type(instance))
        for attr in instance.__dict__:
            self.assertEqual(getattr(instance, attr), getattr(unpickled, attr))

    def test_VisaIOError(self):
        self._test_pickle_unpickle(errors.VisaIOError(0))

    def test_VisaIOWarning(self):
        self._test_pickle_unpickle(errors.VisaIOWarning(0))

    def test_UnknownHandler(self):
        self._test_pickle_unpickle(errors.UnknownHandler(0, 0, 0))

    def test_OSNotSupported(self):
        self._test_pickle_unpickle(errors.OSNotSupported(""))

    def test_InvalidBinaryFormat(self):
        self._test_pickle_unpickle(errors.InvalidBinaryFormat())
        self._test_pickle_unpickle(errors.InvalidBinaryFormat("test"))

    def test_InvalidSession(self):
        self._test_pickle_unpickle(errors.InvalidSession())


class TestLibraryError(BaseTestCase):
    """Test the creation of Library errors.

    """

    def test_from_exception_not_found(self):
        """Test handling a missing library file.

        """
        exc = errors.LibraryError.from_exception(
            ValueError("visa.dll: image not found"), "visa.dll"
        )
        self.assertIn("File not found", str(exc))

    def test_from_exception_wrong_arch(self):
        """Test handling a library that report the wrong bitness.

        """
        exc = errors.LibraryError.from_exception(
            ValueError("visa.dll: no suitable image found. no matching architecture"),
            "visa.dll",
        )
        self.assertIn("No matching architecture", str(exc))

    def test_from_exception_wrong_filetype(self):
        """Test handling a library file of the wrong type.

        """
        exc = errors.LibraryError.from_exception(
            ValueError("visa.dll: no suitable image found."), "visa.dll"
        )
        self.assertIn("Could not determine filetype", str(exc))

    def test_from_exception_wrong_ELF(self):
        """Test handling a library file with a wrong ELF.

        """
        exc = errors.LibraryError.from_exception(
            ValueError("visa.dll: wrong ELF class"), "visa.dll"
        )
        self.assertIn("No matching architecture", str(exc))

    def test_from_exception_random(self):
        """Test handling a library for which the error is not a usual one.

        """
        exc = errors.LibraryError.from_exception(ValueError("visa.dll"), "visa.dll")
        self.assertIn("Error while accessing", str(exc))

    def test_from_exception_decode_error(self):
        """Test handling an error that decode to string.

        """

        class DummyExc(Exception):
            def __str__(self):
                raise b"\xFF".decode("ascii")

        exc = errors.LibraryError.from_exception(
            DummyExc("visa.dll: wrong ELF class"), "visa.dll"
        )
        self.assertEqual("Error while accessing visa.dll.", str(exc))

    # from_wrong_arch is exercised through the above tests.
