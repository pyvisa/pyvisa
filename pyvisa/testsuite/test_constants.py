# -*- coding: utf-8 -*-
"""Test objects from constants.

This file is part of PyVISA.

:copyright: 2019-2020 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
from pyvisa.constants import DataWidth

from . import BaseTestCase


class TestDataWidth(BaseTestCase):
    def test_conversion_from_literal(self):

        for v, e in zip(
            (8, 16, 32, 64),
            (DataWidth.bit_8, DataWidth.bit_16, DataWidth.bit_32, DataWidth.bit_64),
        ):
            self.assertEqual(DataWidth.from_literal(v), e)

        with self.assertRaises(ValueError):
            DataWidth.from_literal(0)
