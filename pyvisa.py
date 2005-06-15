import vpp43
from vpp43_constants import *
from visa_exceptions import *
import re, time, warnings

def removefilter(action, message="", category=Warning, module="", lineno=0,
		 append=0):
    """Remove all entries from the list of warnings filters that match the
    given filter.

    It is the opposite to warnings.filterwarnings() and has the same parameters
    as it."""
    import re
    item = (action, re.compile(message, re.I), category, re.compile(module),
	    lineno)
    new_filters = []
    for filter in warnings.filters:
	equal = 1
	for j in xrange(len(item)):
	    if item[j] != filter[j]:
		equal = 0
		break
	if not equal:
	    new_filters.append(filter)
    if len(warnings.filters) == len(new_filters):
	warnings.warn("Warning filter not found", stacklevel = 2)
    warnings.filters = new_filters

_resources = {}
"""Holds all session vi's.  The keys are the session vi's, the items the object
instances.  Managed by ResourceTemplate."""

class ResourceTemplate(object):
    """The abstract base class of the VISA implementation.  It covers
    life-cycle services: opening and closing of vi's.

    Don't instantiate it!

    """
    vi = None
    def __init__(self, resource_name=None, lock=VI_NO_LOCK,
		 timeout=VI_TMO_IMMEDIATE):
	# needed for __del__ when script is being terminated
	self.__close = vpp43.close
	if self.__class__ is ResourceTemplate:
	    raise TypeError, "trying to instantiate an abstract class"
	if resource_name is not None:  # is none for the resource manager
	    warnings.filterwarnings("ignore", "VI_SUCCESS_DEV_NPRESENT")
	    self.vi = vpp43.open(resource_manager.session, resource_name, lock,
				 timeout)
	    if vpp43.get_status() == VI_SUCCESS_DEV_NPRESENT:
		# okay, the device was not ready when we opened the session.
		# Now it gets five seconds more to become ready.  Every 0.1
		# seconds we probe it with viClear.
		passed_time = 0	 # in seconds
		while passed_time < 5.0:
		    time.sleep(0.1)
		    passed_time += 0.1
		    try:
			vpp43.clear(self.vi)
		    except VisaIOError, error:
			if error.error_code == VI_ERROR_NLISTENERS:
			    continue
			else:
			    raise
		    break
		else:
		    # Very last chance, this time without exception handling
		    time.sleep(0.1)
		    passed_time += 0.1
		    vpp43.clear(self.vi)
	    removefilter("ignore", "VI_SUCCESS_DEV_NPRESENT")
	_resources[self.vi] = self
    def __del__(self):
	# vpp43.close() may be already unbound when the script is being shut
	# down, so I use its alias self.__close().
	if self.vi is not None:
	    del _resources[self.vi]
	    self.__close(self.vi)

class ResourceManager(vpp43.Singleton, ResourceTemplate):
    """Singleton class for the default resource manager."""
    def init(self):
	"""Singleton class constructor."""
	ResourceTemplate.__init__(self)
	# I have "session" as an alias because the specification calls the "vi"
	# handle "session" for the resource manager.
	self.session = self.vi = vpp43.open_default_resource_manager()
    def __repr__(self):
	return "ResourceManager()"

resource_manager = ResourceManager()

def get_instruments_list(use_aliases = True):
    """Get a list of all connected devices.

    Parameters:
    use_aliases -- if True, return an alias name for the device if it has one.
	Otherwise, always return the standard resource name like "GPIB::10".

    Return value:
    A list of strings with the names of all connected devices, ready for being
    used to open each of them.

    """
    # Phase I: Get all standard resource names (no aliases here)
    resource_names = []
    find_list, return_counter, instrument_description = \
	vpp43.find_resources(resource_manager.session, "?*::INSTR")
    resource_names.append(instrument_description)
    for i in xrange(return_counter - 1):
	resource_names.append(vpp43.find_next(find_list))
    # Phase two: If available and use_aliases is True, substitute the alias.
    # Otherwise, truncate the "::INSTR".
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
    """Class for all kinds of Instruments.

    It may be instantiated, however, if you want to use special features of a
    certain interface system (GPIB, USB, RS232, etc), you must instantiate one
    of its child classes.

    """
    chunk_size = 1024  # How many bytes are read per low-level call
    __term_chars = ""  # See below
    delay = 0.0	       # Seconds to wait after each high-level write
    def __init__(self, resource_name, **keyw):
	"""Constructor method.

	Parameters:
	resource_name -- the instrument's resource name or an alias, may be
	    taken from the list from get_instruments_list().
	
	Keyword arguments:
	timeout -- the VISA timeout for each low-level operation in
	    milliseconds.
	term_chars -- the termination characters for this device, see
	    description of class property "term_chars".

	"""
	timeout = keyw.get("timeout", VI_TMO_IMMEDIATE)
	ResourceTemplate.__init__(self, resource_name, VI_NO_LOCK, timeout)
	self.resource_name = resource_name
	self.term_chars = keyw.get("term_chars", "")
	# I validate the resource name by requesting it from the instrument
	resource_name = vpp43.get_attribute(self.vi, VI_ATTR_RSRC_NAME)
	# FixMe: Apparently it's not guaranteed that VISA returns the
	# *complete* resource name?
	if not resource_name.upper().endswith("::INSTR"):
	    raise "resource is not an instrument"
    def __repr__(self):
	return "Instrument(%s)" % self.resource_name
    def write(self, message):
	"""Write a string message to the device.

	Parameters:
	message -- the string message to be sent.  The term_chars are appended
	    to it, unless they are already.

	"""
	if self.__term_chars and \
	   not message.endswith(self.__term_chars):
	    message += self.__term_chars
	vpp43.write(self.vi, message)
	if self.delay > 0.0:
	    time.sleep(self.delay)
    def read(self):
	"""Read a string from the device.

	Reading stops when the device stops sending (e.g. by setting
	appropriate bus lines), or the termination characters sequence was
	detected.  Attention: Only the last characters of the termination
	characters is really used to stop reading, however, the whole sequence
	is compared to the ending of the read string message.  If they don't
	match, an exception is raised.

	Parameters: None

	Return value:
	The string read from the device.

	"""
	warnings.filterwarnings("ignore", "VI_SUCCESS_MAX_CNT")
	try:
	    buffer = ""
	    chunk = vpp43.read(self.vi, self.chunk_size)
	    buffer += chunk
	    while vpp43.get_status() == VI_SUCCESS_MAX_CNT:
		chunk = vpp43.read(self.vi, self.chunk_size)
		buffer += chunk
	finally:
	    removefilter("ignore", "VI_SUCCESS_MAX_CNT")
	if self.__term_chars != "":
	    if not buffer.endswith(self.__term_chars):
		raise "read string doesn't end with termination characters"
	    return buffer[:-len(self.__term_chars)]
	return buffer
    def __set_term_chars(self, term_chars):
	"""Set a new termination character sequence.  See below the property
	"term_char"."""
	# First, reset termination characters, in case something bad happens.
	self.__term_chars = ""
	vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_FALSE)
	if term_chars == "":
	    return
	# Second, parse the parameter term_chars.  There are three parts, the
	# last two optional: the sequence itself ("main"), the "NOEND", and the
	# "DELAY" options.
	match = re.match(r"(?P<main>.*?)"
			 "(((?<=.) +|\A)"
			 "(?P<NOEND>NOEND))?"
			 "(((?<=.) +|\A)DELAY\s+"
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
	# Only the last character in term_chars is the real low-level
	# termination character, the rest is just used for verification after
	# each read operation.
	last_char = term_chars[-1]
	# Consequently, it's illogical to have the real termination character
	# twice in the sequence (otherwise reading would stop prematurely).
	if term_chars[:-1].find(last_char) != -1:
	    raise "ambiguous ending in termination characters"
	vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR, ord(last_char))
	vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_TRUE)
	self.__term_chars = term_chars
    def __get_term_chars(self):
	"""Return the current termination characters for the device."""
	return self.__term_chars
    term_chars = property(__get_term_chars,
				      __set_term_chars, None, None)
    r"""Set or read a new termination character sequence (property).

    Normally, you just give the new termination sequence, which is appended
    to each write operation (unless it's already there), and expected as
    the ending mark during each read operation.	 A typical example is
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

class GpibInstrument(Instrument):
    """Class for GPIB instruments.

    This class extents the Instrument class with special operations and
    properties of GPIB instruments.

    """
    def _srq_event_handler(vi, event_type, context, user_handle):
	pass
    _srq_event_handler = staticmethod(_srq_event_handler)
    def __init__(self, gpib_identifier, bus_number = 0, **keyw):
	"""Class constructor.

	parameters:
	gpib_identifier -- if it's a string, it is interpreted as the
	    instrument's VISA resource name.  If it's a number, it's the
	    instrument's GPIB number.
	bus_number -- (default: 0) the number of the GPIB bus.

	Other keyword arguments are passed to the constructor of class
	Instrument.

	"""
	if isinstance(gpib_identifier, int):
	    resource_name = "GPIB%d::%d" % (bus_number, gpib_identifier)
	else:
	    resource_name = gpib_identifier
	Instrument.__init__(self, resource_name, **keyw)
	# Now check whether the instrument is really valid
	resource_name = vpp43.get_attribute(self.vi, VI_ATTR_RSRC_NAME)
	# FixMe: Apparently it's not guaranteed that VISA returns the
	# *complete* resource name?
	if not re.match(r"(visa://[a-z0-9/]+/)?GPIB[0-9]?"
			"::[0-9]+(::[0-9]+)?::INSTR$",
			resource_name, re.IGNORECASE):
	    raise "invalid GPIB instrument"
    def trigger(self):
	"""Sends a software trigger to the device."""
	vpp43.set_attribute(self.vi, VI_ATTR_TRIG_ID, VI_TRIG_SW)
	vpp43.assert_trigger(self.vi, VI_TRIG_PROT_DEFAULT)

class Interface(ResourceTemplate):
    """Base class for GPIB interfaces.

    You may wonder why this exists since the only child class is Gpib().  I
    don't know either, but the VISA specification says that there are attribute
    that only "interfaces that support GPIB" have and other that "all" have.

    FixMe: However, maybe it's better to merge both classes.  In any case you
    should not instantiate this class."""
    def __init__(self, interface_name):
	"""Class constructor.

	Parameters:
	interface_name -- VISA resource name of the interface.	May be "GPIB0"
	    or "GPIB1::INTFC".

	"""
	if interface_name[-7:].upper() == "::INTFC":
	    resource_name = interface_name
	else:
	    resource_name = interface_name + "::INTFC"
	ResourceTemplate.__init__(self, resource_name)
	self.interface_name = interface_name
    def __repr__(self):
	return "Interface(%s)" % self.interface_name

class Gpib(Interface):
    """Class for GPIB interfaces (rather than instruments)."""
    def __init__(self, board_number = 0):
	"""Class constructor.

	Parameters:
	board_number -- integer denoting the number of the GPIB board, defaults
	    to 0.
	
	"""
	Interface.__init__(self, "GPIB" + str(board_number))
	self.board_number = board_number
    def __repr__(self):
	return "Gpib(%s)" % self.board_number
    def send_ifc(self):
	"""Send "interface clear" signal to the GPIB."""
	vpp43.gpib_send_ifc(self.vi)

def testpyvisa():
    print "Test start"
#     print get_instruments_list()
#     Gpib().send_ifc()
#     time.sleep(20)
    maid = GpibInstrument("maid", term_chars = "\r")
    maid.write("VER")
    result = maid.read()
    print result, len(result)
    print "Test end"

if __name__ == '__main__':
    testpyvisa()
