import vpp43
from vpp43_constants import *
import re, time

class ResourceTemplate(object):
    """The abstract base class of the VISA implementation.  It covers
    life-cycle services: opening and closing of vi's.

    """
    vi = None
    def __init__(self, resource_name = None, lock = VI_NO_LOCK, timeout =
                 VI_TMO_IMMEDIATE):
        if self.__class__ is ResourceTemplate:
            raise TypeError, "trying to instantiate an abstract class"
        if resource_name is not None:
            self.vi = vpp43.open(resource_manager.session, resource_name, lock,
                                 timeout)
        self.__close = vpp43.close  # needed for __del__
    def __del__(self):
        if self.vi is not None:
            self.__close(self.vi)

class ResourceManager(vpp43.Singleton, ResourceTemplate):
    def init(self):
        ResourceTemplate.__init__(self)
        # I have "session" as an alias because the specification calls the "vi"
        # handle "session" for the resource manager.
        self.session = self.vi = vpp43.open_default_resource_manager()
    def __repr__(self):
        return "ResourceManager()"

resource_manager = ResourceManager()

class Instrument(ResourceTemplate):
    chunk_size = 1024
    __termination_characters = ""
    delay = 0.0
    def __init__(self, instrument_name, timeout = VI_TMO_IMMEDIATE):
        ResourceTemplate.__init__(self, instrument_name + "::INSTR",
                                  VI_NO_LOCK, timeout)
        self.instrument_name = instrument_name
    def __repr__(self):
        return "Instrument(%s)" % self.instrument_name
    def write(self, message):
        if self.__termination_characters and \
           not message.endswith(self.__termination_characters):
            message += self.__termination_characters
        vpp43.write(self.vi, message)
        if self.delay > 0.0:
            time.sleep(self.delay)
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
    def __set_termination_characters(self, termination_characters):
        """Set a new termination character sequence.  See below the property
        "termination_character".

        """
        self.__termination_characters = ""
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_FALSE)
        if termination_characters == "":
            return
        match = re.match(r"(?P<main>.*?)"\
                         "(((?<=.) +|\A)"\
                         "(?P<NOEND>NOEND))?"\
                         "(((?<=.) +|\A)DELAY\s+"\
                         "(?P<DELAY>\d+(\.\d*)?|\d*\.\d+)\s*)?$",
                         termination_characters, re.DOTALL)
        if match is None:
            raise "termination characters were malformed"
        if match.group("NOEND"):
            vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_FALSE)
        else:
            vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_TRUE)
        if match.group("DELAY"):
            self.delay = float(match.group("DELAY"))
        else:
            self.delay = 0.0
        termination_characters = match.group("main")
        if not termination_characters:
            return
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
    r"""Set or read a new termination character sequence (property).

    Normally, you just give the new termination sequence, which is appended
    to each write operation (unless it's already there), and expected as
    the ending mark during each read operation.  A typical example is
    "\n\r" or just "\r".  If you assign "" to this property, the
    termination sequence is deleted.

    There are two further options, which are inspired by HTBasic (yuck),
    that you can append to the string: "NOEND" disables the asserting of
    the EOI line after each write operation (thus, enabled by default), and
    "DELAY <float>" sets a delay time in seconds that is waited after each
    write operation.  So you could give "\r NOEND DELAY 0.5" as the new
    termination character sequence.  Spaces before "NOEND" and "DELAY"
    are ignored, but only if non-spaces preceed it.  Therefore, " NOEND" is
    interpreted as a six-character termination sequence.

    The default is "".

    """

class Interface(ResourceTemplate):
    def __init__(self, interface_name):
        ResourceTemplate.__init__(self, interface_name + "::INTFC")
        self.interface_name = interface_name
    def __repr__(self):
        return "Interface(%s)" % self.interface_name

class Gpib(Interface):
    def __init__(self, board_number = 0):
        Interface.__init__("GPIB" + str(board_number))
        self.board_number = board_number
    def __repr__(self):
        return "Gpib(%s)" % self.board_number
    def send_ifc(self):
        vpp43.gpib_send_ifc(self.vi)

def testpyvisa():
    print "Test start"
    maid = Instrument("GPIB::10")
    maid.termination_characters = "\r"
    maid.write("VER")
    result = maid.read()
    print result, len(result)
    print "Test end"

if __name__ == '__main__':
    testpyvisa()
