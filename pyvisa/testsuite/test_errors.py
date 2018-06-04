# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function, absolute_import

import pickle

from pyvisa.testsuite import BaseTestCase

from pyvisa import errors


class TestPicleUnpickle(BaseTestCase):
    def _test_pickle_unpickle(self, instance):
        pickled = pickle.dumps(instance)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, type(instance))
        for attr in instance.__dict__:
            self.assertEqual(getattr(instance, attr),
                             getattr(unpickled, attr))

    def test_VisaIOError(self):
        self._test_pickle_unpickle(errors.VisaIOError(0))

    def test_VisaIOWarning(self):
        self._test_pickle_unpickle(errors.VisaIOWarning(0))

    def test_UnknownHandler(self):
        self._test_pickle_unpickle(errors.UnknownHandler(0,0,0))

    def test_OSNotSupported(self):
        self._test_pickle_unpickle(errors.OSNotSupported(""))

    def test_InvalidBinaryFormat(self):
        self._test_pickle_unpickle(errors.InvalidBinaryFormat())

    def InvalidSession(self):
        self._test_pickle_unpickle(errors.InvalidSession())
