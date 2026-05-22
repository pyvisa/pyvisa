# -*- coding: utf-8 -*-
"""Binary transfer adapter over shared backend contract definitions."""

import pytest

from pyvisa.testing.contracts.test_binary_value_contracts import *  # noqa: F403
from pyvisa.testing.requirements import require_visa_lib

from . import require_pyvisa_tester_assisted

pytestmark = [
    require_visa_lib,
    require_pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_shared,
]
