import os
from mock import Mock
import ctypes

ctypes.cdll = Mock()

if os.name == 'nt':
    ctypes.windll = Mock()
