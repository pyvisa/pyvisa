import vpp43
from vpp43_constants import *
import re, time

class ResourceManager(object):
    def __init__(self):
        self.session = vpp43.open_default_resource_manager()
        self.__close = vpp43.close  # needed for __del__
    def __del__(self):
        self.__close(self.session)
    def __repr__(self):
        return "ResourceManager()"

resource_manager = ResourceManager()

class Instrument(object):
    chunk_size = 1024
    __termination_characters = ""
    __delay = 0.0
    def __init__(self, instrument_name, timeout = VI_TMO_IMMEDIATE):
        self.vi = vpp43.open(resource_manager.session, instrument_name + "::INSTR",
                             VI_NO_LOCK, timeout)
        self.instrument_name = instrument_name
        self.__close = vpp43.close  # needed for __del__
    def __del__(self):
        self.__close(self.vi)
    def __repr__(self):
        return "Instrument(%s)" % self.instrument_name
    def write(self, message):
        if self.__termination_characters and \
           not message.endswith(self.__termination_characters):
            message += self.__termination_characters
        vpp43.write(self.vi, message)
        if self.__delay:
            time.sleep(self.__delay)
    def read(self):
        generate_warnings_original = vpp43.generate_warnings
        vpp43.generate_warnings = False
        try:
            buffer = ""
            chunk = vpp43.read(self.vi, self.chunk_size)
            buffer += chunk
            while vpp43.get_status() == VI_SUCCESS_MAX_CNT:
                chunk = vpp43.read(self.vi, self.chunk_size)
                buffer += chunk
        finally:
            vpp43.generate_warnings = generate_warnings_original
        if self.__termination_characters != "":
            if not buffer.endswith(self.__termination_characters):
                raise "read string doesn't end with termination characters"
            return buffer[:-len(self.__termination_characters)]
        return buffer
    def get_attribute(self, attribute_code):
        return vpp43.get_attribute(self.vi, attribute_code)
    def set_attribute(self, attribute_code, attribute_value):
        vpp43.set_attribute(self.vi, attribute_code, attribute_value)
    def __set_termination_characters(self, termination_characters):
        self.__termination_characters = ""
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, 0)
        if termination_characters == "":
            return
        match = re.match(r"(?P<main>.*?)(?:\s+(?P<NOEND>NOEND))?"\
                         "(?:\s+DELAY\s+(?P<DELAY>\d+(\.\d*)?|\d*\.\d+)\s*)?$",
                         termination_characters, re.DOTALL)
        if match is None:
            raise "termination characters were malformed"
        if match.group("NOEND"):
            vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_FALSE)
        else:
            vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_TRUE)
        if match.group("DELAY"):
            __delay = float(match.group("DELAY"))
        termination_characters = match.group("main")
        last_char = termination_characters[-1]
        if termination_characters[:-1].find(last_char) != -1:
            raise "ambiguous ending in termination characters"
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR, ord(last_char))
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_TRUE)
        self.__termination_characters = termination_characters
    def __get_termination_characters(self):
        return self.__termination_characters
    termination_characters = property(__get_termination_characters,
                                      __set_termination_characters, None, None)

def testpyvisa():
    print "Test start"
    maid = Instrument("GPIB::10")
    maid.termination_characters = "\r NOEND DELAY 3"
    maid.write("VER")
    result = maid.read()
    print result, len(result)
    print maid.get_attribute(VI_ATTR_TERMCHAR)
    print maid.get_attribute(VI_ATTR_TERMCHAR_EN)
    print "Test end"

if __name__ == '__main__':
    testpyvisa()
