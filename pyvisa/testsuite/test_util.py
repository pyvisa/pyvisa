# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function, absolute_import

from pyvisa.testsuite import BaseTestCase

from pyvisa import util


class TestParser(BaseTestCase):

    def test_parse_binary(self):
        s = b'#@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xde\x8b<@\xde\x8b<@\xde\x8b<' \
            b'@\xde\x8b<@\xe0\x8b<@\xe0\x8b<@\xdc\x8b<@\xde\x8b<@\xe2\x8b<@\xe0\x8b<'
        e = [0.01707566, 0.01707566, 0.01707566, 0.01707566, 0.01707375,
             0.01707375, 0.01707375, 0.01707375, 0.01707470, 0.01707470,
             0.01707280, 0.01707375, 0.01707566, 0.01707470]
        p = util.parse_binary(s, is_big_endian=False, is_single=True)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)
