# -*- coding: utf-8 -*-
"""Resource capability stub adapter over shared backend contract definitions."""

import pytest

from pyvisa.testing.contracts.test_resource_capability_stubs import *  # noqa: F403
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.usefixtures("require_pyvisa_tester_profile"),
    pytest.mark.pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_shared,
]
