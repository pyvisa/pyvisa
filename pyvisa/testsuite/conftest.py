# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function, absolute_import

import os
from mock import Mock
import ctypes

ctypes.cdll = Mock()

if os.name == 'nt':
    ctypes.windll = Mock()
