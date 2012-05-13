from __future__ import print_function
from pyvisa import visa_attributes

def test_attributes():
    for value, info in visa_attributes.attributes.items():
        assert value == info.attribute_value
        assert info.attribute_name != ''
        assert repr(info) != ''
