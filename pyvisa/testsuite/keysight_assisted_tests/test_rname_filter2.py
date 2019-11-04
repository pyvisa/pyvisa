# -*- coding: utf-8 -*-
"""Common test case for all message based resources.

"""
from . import require_virtual_instr


@require_virtual_instr
class TestFilter2(BaseTestCase):

    def setUp(self):
        """Create a ResourceManager with the default backend library.

        """
        self.rm = ResourceManager()

    def tearDown(self):
        """Close the ResourceManager.

        """
        self.rm.close()

    def _test_filter2(self, expr, *correct):

        resources = self.rm.list_resources(expr.split("{")[0])
        ok = tuple(resources[n] for n in correct)
        filtered = rname.filter2(resources, expr,
                                 lambda rsc: self.rm.open_resource(rsc))
        self.assertSequenceEqual(filtered, ok)

    def test_filter2_optional_clause_with_connection(self):
        self._test_filter2('?*::INSTR{VI_ATTR_TERMCHAR == 0)}')
        # Linefeed \n is 10
        self._test_filter2('TCPIP::?*::INSTR{VI_ATTR_TERMCHAR == 10)}')
