# -*- coding: utf-8 -*-
"""
    pyvisa.resources.helpers
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from ..compat import string_types
from .. import constants


def _redoc(attribute_name, doc, extra_doc=''):
    if isinstance(attribute_name, string_types):
        if doc is None:
            doc = ''
        if not doc.endswith('\n\n'):
            doc += '\n\n'
        doc += ':VISA Attribute: %s.' % attribute_name
        if extra_doc:
            doc += '\n' + extra_doc
        attribute_name = getattr(constants, attribute_name)

    return attribute_name, doc


def attr(attribute_name, doc=None, ro=False):
    attribute_name, doc = _redoc(attribute_name, doc)

    def getter(self):
        return self.get_visa_attribute(attribute_name)

    if ro:
        return property(fget=getter, doc=doc)

    def setter(self, value):
        self.set_visa_attribute(attribute_name, value)

    return property(fget=getter, fset=setter, doc=doc)


def enum_attr(attribute_name, enum_type, doc=None, ro=False):
    attribute_name, doc = _redoc(attribute_name, doc,
                                 ':type: :class:%s.%s' % (enum_type.__module__, enum_type.__name__))

    def getter(self):
        return enum_type(self.get_visa_attribute(attribute_name))

    if ro:
        return property(fget=getter, doc=doc)

    def setter(self, value):
        if value not in enum_type:
            raise ValueError('%r is an invalid value for attribute %s, should be a %r',
                             value, attribute_name, enum_type)
        self.set_visa_attribute(attribute_name, value)

    return property(fget=getter, fset=setter, doc=doc)


def range_attr(attribute_name, min_value, max_value, doc=None, ro=False):
    attribute_name, doc = _redoc(attribute_name, doc,
                                 ':range: %s <= value <= %s\n' % (min_value, max_value))

    def getter(self):
        return self.get_visa_attribute(attribute_name)

    if ro:
        return property(fget=getter, doc=doc)

    def setter(self, value):
        if not min_value <= value <= max_value:
            raise ValueError('%r is an invalid value for attribute %s, should be between %r and %r',
                             value, attribute_name, min_value, max_value)
        self.set_visa_attribute(attribute_name, value)

    return property(fget=getter, fset=setter, doc=doc)


def boolean_attr(attribute_name, doc=None, ro=False):
    attribute_name, doc = _redoc(attribute_name, doc,
                                 ':type: bool')

    def getter(self):
        return self.get_visa_attribute(attribute_name) == constants.VI_TRUE

    if ro:
        return property(fget=getter, doc=doc)

    def setter(self, value):
        self.set_visa_attribute(attribute_name, constants.VI_TRUE if value else constants.VI_FALSE)

    return property(fget=getter, fset=setter, doc=doc)


def char_attr(attribute_name, doc=None, ro=False):
    attribute_name, doc = _redoc(attribute_name, doc,
                                 ':range: 0 <= x <= 255\n:type: int')

    def getter(self):
        return chr(self.get_visa_attribute(attribute_name))

    if ro:
        return property(fget=getter, doc=doc)

    def setter(self, value):
        self.set_visa_attribute(attribute_name, ord(value))

    return property(fget=getter, fset=setter, doc=doc)

