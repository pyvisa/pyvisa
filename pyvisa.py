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

def get_instruments_list(use_aliases = True):
    resource_names = []
    find_list, return_counter, instrument_description = \
               vpp43.find_resources(resource_manager.session, "?*::INSTR")
    resource_names.append(instrument_description)
    for i in xrange(return_counter - 1):
        resource_names.append(vpp43.find_next(find_list))
    result = []
    for resource_name in resource_names:
        interface_type, interface_board_number, resource_class, \
         unaliased_expanded_resource_name, alias_if_exists  = \
         vpp43.parse_resource_extended(resource_manager.session, resource_name)
        if alias_if_exists and use_aliases:
            result.append(alias_if_exists)
        else:
            result.append(resource_name[:-7])
    return result
        

class Instrument(ResourceTemplate):
    chunk_size = 1024
    __term_chars = ""
    delay = 0.0
    def __init__(self, instrument_name, **keyw):
        timeout = keyw.get("timeout", VI_TMO_IMMEDIATE)
        if instrument_name.find("::") == -1:
            resource_name = instrument_name  # probably an alias
        elif instrument_name[-7:].upper() == "::INSTR":
            resource_name = instrument_name
        else:
            resource_name = instrument_name + "::INSTR"
        ResourceTemplate.__init__(self, resource_name, VI_NO_LOCK, timeout)
        self.term_chars = keyw.get("term_chars", "")
        self.instrument_name = instrument_name
    def __repr__(self):
        return "Instrument(%s)" % self.instrument_name
    def write(self, message):
        if self.__term_chars and \
           not message.endswith(self.__term_chars):
            message += self.__term_chars
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
        if self.__term_chars != "":
            if not buffer.endswith(self.__term_chars):
                raise "read string doesn't end with termination characters"
            return buffer[:-len(self.__term_chars)]
        return buffer
    def __set_term_chars(self, term_chars):
        """Set a new termination character sequence.  See below the property
        "term_char".

        """
        self.__term_chars = ""
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_FALSE)
        if term_chars == "":
            return
        match = re.match(r"(?P<main>.*?)"\
                         "(((?<=.) +|\A)"\
                         "(?P<NOEND>NOEND))?"\
                         "(((?<=.) +|\A)DELAY\s+"\
                         "(?P<DELAY>\d+(\.\d*)?|\d*\.\d+)\s*)?$",
                         term_chars, re.DOTALL)
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
        term_chars = match.group("main")
        if not term_chars:
            return
        last_char = term_chars[-1]
        if term_chars[:-1].find(last_char) != -1:
            raise "ambiguous ending in termination characters"
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR, ord(last_char))
        vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_TRUE)
        self.__term_chars = term_chars
    def __get_term_chars(self):
        return self.__term_chars
    term_chars = property(__get_term_chars,
                                      __set_term_chars, None, None)
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
        Interface.__init__(self, "GPIB" + str(board_number))
        self.board_number = board_number
    def __repr__(self):
        return "Gpib(%s)" % self.board_number
    def send_ifc(self):
        vpp43.gpib_send_ifc(self.vi)

def testpyvisa():
    print "Test start"
    print get_instruments_list()
    Gpib().send_ifc()
    time.sleep(20)
    maid = Instrument("maid", term_chars = "\r")
    maid.write("VER")
    result = maid.read()
    print result, len(result)
    print "Test end"

if __name__ == '__main__':
    testpyvisa()
