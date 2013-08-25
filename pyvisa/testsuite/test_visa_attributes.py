from __future__ import print_function
from pyvisa import visa_attributes
import pytest

def test_attributes():
    for value, info in visa_attributes.attributes.items():
        assert value == info.attribute_value
        assert info.attribute_name != ''
        assert repr(info) != ''

def test_attr_range():
    my_range = visa_attributes._AttrRange(0, 10)
    assert my_range.minimum == 0
    assert my_range.maximum == 10
    assert 0 in my_range
    assert 10 in my_range
    assert 11 not in my_range
    with pytest.raises(IndexError):
        assert my_range.tostring(11)
    assert my_range.tostring(10) == "10"
    assert my_range.fromstring("11") == 11
    
def test_attr_set():
    with pytest.raises(KeyError):
        my_set = visa_attributes._AttrSet(0)
    my_set = visa_attributes._AttrSet('VI_NO_LOCK', 'VI_EXCLUSIVE_LOCK', 'VI_SHARED_LOCK')
    assert 'VI_NO_LOCK' in my_set
    assert 'foo' not in my_set
    assert my_set.fromstring('VI_NO_LOCK') == 0
    assert my_set.tostring(0) == 'VI_NO_LOCK'
    assert my_set.tostring(1) == 'VI_EXCLUSIVE_LOCK'
    assert my_set.tostring(2) == 'VI_SHARED_LOCK'
    
def test_attr_bit_set():
    with pytest.raises(KeyError):
        my_set = visa_attributes._AttrBitSet(0)
    my_set = visa_attributes._AttrBitSet('VI_NO_LOCK', 'VI_EXCLUSIVE_LOCK', 'VI_SHARED_LOCK')
    assert 0 not in my_set
    assert 1 in my_set
    assert 3 in my_set
    assert 4 not in my_set
    assert 5 in my_set
    #assert 'foo' not in my_set
    assert my_set.fromstring('VI_NO_LOCK') == 0
    assert my_set.fromstring('VI_NO_LOCK|VI_EXCLUSIVE_LOCK') == 1
    assert my_set.tostring(0) == 'VI_NO_LOCK'
    assert my_set.tostring(1) == 'VI_EXCLUSIVE_LOCK'
    assert my_set.tostring(2) == 'VI_SHARED_LOCK'
    assert my_set.tostring(3) == 'VI_EXCLUSIVE_LOCK | VI_SHARED_LOCK'
    

