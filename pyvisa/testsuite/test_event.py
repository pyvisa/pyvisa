# -*- coding: utf-8 -*-
"""Test events classes.

This file is part of PyVISA.

:copyright: 2019-2020 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
import logging

from pyvisa import logger, constants, errors
from pyvisa.events import Event

from . import BaseTestCase


class TestEvent(BaseTestCase):
    """Test Event functionalities.

    """

    def setUp(self):
        self.old = Event._event_classes.copy()

    def tearDown(self):
        Event._event_classes = self.old

    def test_register(self):

        self.assertIs(Event._event_classes[constants.EventType.clear], Event)

    def test_double_register_event_cls(self):
        class SubEvent(Event):
            pass

        with self.assertLogs(level=logging.DEBUG, logger=logger):
            Event.register(constants.EventType.clear)(SubEvent)

        self.assertIs(Event._event_classes[constants.EventType.clear], SubEvent)

    def test_register_event_cls_missing_attr(self):
        class SubEvent(Event):
            pass

        with self.assertRaises(TypeError):
            Event.register(constants.EventType.exception)(SubEvent)

        self.assertIsNot(Event._event_classes[constants.EventType.exception], SubEvent)

    def test_event_context(self):

        event = Event(None, constants.EventType.clear, 1)
        self.assertEqual(event.context, 1)

        event.close()
        with self.assertRaises(errors.InvalidSession):
            event.context
