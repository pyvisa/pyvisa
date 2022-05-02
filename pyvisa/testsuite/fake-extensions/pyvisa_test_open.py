# -*- coding: utf-8 -*-
"""

"""
from pyvisa.highlevel import VisaLibraryBase
from pyvisa.util import LibraryPath
from pyvisa import constants


class FakeResource:
    def close(self):
        pass


class FalseVISALib(VisaLibraryBase):
    pass

    @staticmethod
    def get_library_paths():
        return (LibraryPath("unset"),)

    def _init(self):
        pass

    def open_resource(self, *args, **kwargs):
        self.open_resource_called = True
        return FakeResource()

    def open_default_resource_manager(self):
        return 1, constants.StatusCode.success

    def close(self, session):
        pass


WRAPPER_CLASS = FalseVISALib
