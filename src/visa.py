#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    visa.py - High-level object-oriented VISA implementation
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#		      Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of PyVISA.
#
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    PyVISA is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.	See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with PyVISA; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import vpp43
from vpp43_constants import *
from visa_exceptions import *
import re, time, warnings, atexit, struct

def _removefilter(action, message="", category=Warning, module="", lineno=0,
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

def _warn_for_invalid_keyword_arguments(keyw, allowed_keys):
    for key in keyw.iterkeys():
	if key not in allowed_keys:
	    warnings.warn("Keyword argument \"%s\" unknown" % key,
			  stacklevel = 3)

def _filter_keyword_arguments(keyw, selected_keys):
    result = {}
    for key, value in keyw.iteritems():
	if key in selected_keys:
	    result[key] = value
    return result

class ResourceTemplate(object):
    import vpp43 as _vpp43
    """The abstract base class of the VISA implementation.  It covers
    life-cycle services: opening and closing of vi's.

    Don't instantiate it!

    """
    vi = None
    def __init__(self, resource_name=None, **keyw):
	_warn_for_invalid_keyword_arguments(keyw, ("lock", "timeout"))
	if self.__class__ is ResourceTemplate:
	    raise TypeError, "trying to instantiate an abstract class"
	if resource_name is not None:  # is none for the resource manager
	    warnings.filterwarnings("ignore", "VI_SUCCESS_DEV_NPRESENT")
	    self.vi = vpp43.open(resource_manager.session, resource_name,
				 keyw.get("lock", VI_NO_LOCK),
				 VI_TMO_IMMEDIATE)
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
	    _removefilter("ignore", "VI_SUCCESS_DEV_NPRESENT")
	    timeout = keyw.get("timeout", 5)
	    if timeout is None:
		vpp43.set_attribute(self.vi, VI_ATTR_TMO_VALUE,
				    VI_TMO_INFINITE)
	    else:
		self.timeout = timeout
    def __del__(self):
	self.close()
    def __set_timeout(self, timeout=5):
	if not(0 <= timeout <= 4294967):
	    raise ValueError("timeout value is invalid")
	vpp43.set_attribute(self.vi, VI_ATTR_TMO_VALUE, int(timeout * 1000))
    def __get_timeout(self):
	timeout = vpp43.get_attribute(self.vi, VI_ATTR_TMO_VALUE)
	if timeout == VI_TMO_INFINITE:
	    raise NameError("no timeout is specified")
	return timeout / 1000.0
    def __del_timeout(self):
	timeout = self.__get_timeout()	# just to test whether it's defined
	vpp43.set_attribute(self.vi, VI_ATTR_TMO_VALUE, VI_TMO_INFINITE)
    timeout = property(__get_timeout, __set_timeout, __del_timeout, None)
    def __get_resource_class(self):
	return vpp43.get_attribute(self.vi, VI_ATTR_RSRC_CLASS).upper()
    resource_class = property(__get_resource_class, None, None, None)
    def __get_resource_name(self):
	return vpp43.get_attribute(self.vi, VI_ATTR_RSRC_NAME)
    resource_name = property(__get_resource_name, None, None, None)
    def close(self):
	if self.vi is not None:
	    self._vpp43.close(self.vi)
	    self.vi = None


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

def _destroy_resource_manager():
    # delete self-reference
    del ResourceManager.__it__
atexit.register(_destroy_resource_manager)

def get_instruments_list(use_aliases=True):
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


# The bits in the bitfield mean the following:
#
# bit number   if set / if not set
#     0		 binary/ascii
#     1		 double/single (IEEE floating point)
#     2		 big-endian/little-endian
#
# This leads to the following constants:

ascii	   = 0
single	   = 1
double	   = 3
big_endian = 4

CR = "\r"
LF = "\n"

class Instrument(ResourceTemplate):
    """Class for all kinds of Instruments.

    It can be instantiated, however, if you want to use special features of a
    certain interface system (GPIB, USB, RS232, etc), you must instantiate one
    of its child classes.

    """
    chunk_size = 20*1024   # How many bytes are read per low-level call
    __term_chars = ""	   # See below
    delay = 0.0		   # Seconds to wait after each high-level write
    values_format = ascii  # floating point data value format
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
	chunk_size -- size of data packets in bytes that are read from the
	    device.
	lock -- whether you want to have exclusive access to the device.
	    Default: VI_NO_LOCK
	delay -- waiting time in seconds after each write command. Default: 0
	send_end -- whether to assert end line after each write command.
	    Default: True
	values_format -- floating point data value format.  Default: ascii (0)

	"""
	_warn_for_invalid_keyword_arguments(keyw, ("timeout", "term_chars",
						   "chunk_size", "lock",
						   "delay", "send_end",
						   "values_format"))
	ResourceTemplate.__init__(self, resource_name,
				  **_filter_keyword_arguments(keyw, ("timeout",
								     "lock")))
	self.term_chars	   = keyw.get("term_chars", "")
	self.chunk_size	   = keyw.get("chunk_size", self.chunk_size)
	self.delay	   = keyw.get("delay", 0.0)
	self.send_end	   = keyw.get("send_end", True)
	self.values_format = keyw.get("values_format", self.values_format)
	# I validate the resource class by requesting it from the instrument
	if self.resource_class != "INSTR":
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
    def _strip_term_chars(self, buffer):
	if self.__term_chars != "":
	    if buffer.endswith(self.__term_chars):
		buffer = buffer[:-len(self.__term_chars)]
	    else:
		warnings.warn("read string doesn't end with "
			      "termination characters", stacklevel = 2)
	return buffer.rstrip(CR+LF)
    def read_raw(self):
	warnings.filterwarnings("ignore", "VI_SUCCESS_MAX_CNT")
	try:
	    buffer = ""
	    chunk = vpp43.read(self.vi, self.chunk_size)
	    buffer += chunk
	    while vpp43.get_status() == VI_SUCCESS_MAX_CNT:
		chunk = vpp43.read(self.vi, self.chunk_size)
		buffer += chunk
	finally:
	    _removefilter("ignore", "VI_SUCCESS_MAX_CNT")
	return buffer
    def read(self):
	"""Read a string from the device.

	Reading stops when the device stops sending (e.g. by setting
	appropriate bus lines), or the termination characters sequence was
	detected.  Attention: Only the last character of the termination
	characters is really used to stop reading, however, the whole sequence
	is compared to the ending of the read string message.  If they don't
	match, a warning is issued.

	Parameters: None

	Return value:
	The string read from the device.

	"""
	return self._strip_term_chars(self.read_raw())
    def read_values(self, format=None):
	if not format:
	    format = self.values_format
	if format & 0x01 == ascii:
	    float_regex = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\d*\.\d+)"
				     "(?:[eE][-+]?\d+)?")
	    return [float(raw_value) for raw_value in
		    float_regex.findall(self.read())]
	# Okay, we need to read binary data
	original_term_chars = self.term_chars
	self.term_chars = ""
	try:
	    data = self.read_raw()
	finally:
	    self.term_chars = original_term_chars
	if data[0] == "#" and data[1].isdigit() and int(data[1]) > 0:
	    number_of_digits = int(data[1])
	    # I store data and data_length in two separate variables in case
	    # that data is too short.  FixMe: Maybe I should raise an error if
	    # it's too long and the trailing part is not just CR/LF.
	    data_length = int(data[2:2+number_of_digits])
	    data = data[2+number_of_digits:2+number_of_digits + data_length]
	elif data[0:2] == "#0" and data[-1] == "\n":
	    data = data[2:-1]
	    data_length = len(data)
	else:
	    raise "unrecognized binary data format"
	if format & 0x04 == big_endian:
	    endianess = ">"
	else:
	    endianess = "<"
	try:
	    if format & 0x03 == single:
		result = list(struct.unpack(endianess +
					    str(data_length/4) + "f", data))
	    elif format & 0x03 == double:
		result = list(struct.unpack(endianess +
					    str(data_length/8) + "d", data))
	    else:
		raise "unknown data values format requested"
	except struct.error:
	    raise "binary data was malformed"
	return result
    def read_floats(self):
	warnings.warn("read_floats() is deprecated.  Use read_values()",
		      stacklevel = 2)
	return self.read_values(format=ascii)
    def ask(self, message):
	self.write(message)
	return self.read()
    def ask_for_values(self, message, format=None):
	self.write(message)
	return self.read_values(format)
    def clear(self):
	vpp43.clear(self.vi)
    def trigger(self):
	"""Sends a software trigger to the device."""
	vpp43.set_attribute(self.vi, VI_ATTR_TRIG_ID, VI_TRIG_SW)
	vpp43.assert_trigger(self.vi, VI_TRIG_PROT_DEFAULT)
    def __set_term_chars(self, term_chars):
	"""Set a new termination character sequence.  See below the property
	"term_char"."""
	# First, reset termination characters, in case something bad happens.
	self.__term_chars = ""
	vpp43.set_attribute(self.vi, VI_ATTR_TERMCHAR_EN, VI_FALSE)
	if term_chars == "":
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
    def __del_term_chars(self):
	self.term_chars = ""
    term_chars = property(__get_term_chars, __set_term_chars, __del_term_chars)
    r"""Set or read a new termination character sequence (property).

    Normally, you just give the new termination sequence, which is appended to
    each write operation (unless it's already there), and expected as the
    ending mark during each read operation.  A typical example is CR+LF or just
    CR.	 If you assign "" to this property, the termination sequence is
    deleted.

    The default is "".

    """
    def __set_send_end(self, send):
	if send:
	    vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_TRUE)
	else:
	    vpp43.set_attribute(self.vi, VI_ATTR_SEND_END_EN, VI_FALSE)
    def __get_send_end(self):
	return vpp43.get_attribute(self.vi, VI_ATTR_SEND_END_EN) == VI_TRUE
    send_end = property(__get_send_end, __set_send_end)

class GpibInstrument(Instrument):
    """Class for GPIB instruments.

    This class extents the Instrument class with special operations and
    properties of GPIB instruments.

    """
    def __init__(self, gpib_identifier, board_number=0, **keyw):
	"""Class constructor.

	parameters:
	gpib_identifier -- if it's a string, it is interpreted as the
	    instrument's VISA resource name.  If it's a number, it's the
	    instrument's GPIB number.
	board_number -- (default: 0) the number of the GPIB bus.

	Other keyword arguments are passed to the constructor of class
	Instrument.

	"""
	_warn_for_invalid_keyword_arguments(keyw, ("timeout", "term_chars",
						   "chunk_size", "lock",
						   "delay", "send_end",
						   "values_format"))
	if isinstance(gpib_identifier, int):
	    resource_name = "GPIB%d::%d" % (board_number, gpib_identifier)
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
	vpp43.enable_event(self.vi, VI_EVENT_SERVICE_REQ, VI_QUEUE)
    def __del__(self):
	if self.vi is not None:
	    self.__switch_events_off()
	    Instrument.__del__(self)
    def __switch_events_off(self):
	self._vpp43.disable_event(self.vi, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)
	self._vpp43.discard_events(self.vi, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)
    def wait_for_srq(self, timeout=25):
	vpp43.enable_event(self.vi, VI_EVENT_SERVICE_REQ, VI_QUEUE)
	if timeout and not(0 <= timeout <= 4294967):
	    raise ValueError("timeout value is invalid")
	starting_time = time.clock()
	while True:
	    if timeout is None:
		adjusted_timeout = VI_TMO_INFINITE
	    else:
		adjusted_timeout = int((starting_time + timeout - time.clock())
				       * 1000)
		if adjusted_timeout < 0:
		    adjusted_timeout = 0
	    event_type, context = \
		vpp43.wait_on_event(self.vi, VI_EVENT_SERVICE_REQ,
				    adjusted_timeout)
	    vpp43.close(context)
	    if vpp43.read_stb(self.vi) & 0x40:
		break
	vpp43.discard_events(self.vi, VI_EVENT_SERVICE_REQ, VI_QUEUE)

class Interface(ResourceTemplate):
    """Base class for GPIB interfaces.

    You may wonder why this exists since the only child class is Gpib().  I
    don't know either, but the VISA specification says that there are
    attributes that only "interfaces that support GPIB" have and other that
    "all" have.

    FixMe: However, maybe it's better to merge both classes.  In any case you
    should not instantiate this class."""
    def __init__(self, interface_name):
	"""Class constructor.

	Parameters:
	interface_name -- VISA resource name of the interface.	May be "GPIB0"
	    or "GPIB1::INTFC".

	"""
	ResourceTemplate.__init__(self, interface_name)
	# I validate the resource class by requesting it from the interface
	if self.resource_class != "INTFC":
	    raise "resource is not an interface"
    def __repr__(self):
	return "Interface(%s)" % self.resource_name

class Gpib(Interface):
    """Class for GPIB interfaces (rather than instruments)."""
    def __init__(self, board_number=0):
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
    keithley = GpibInstrument(12)
    milliseconds = 500
    number_of_values = 10
    keithley.write("F0B2M2G0T2Q%dI%dX" % (milliseconds, number_of_values))
    keithley.trigger()
    keithley.wait_for_srq()
    print keithley.read_values()
    print "Average: ", sum(voltages) / len(voltages)
    print "Test end"

if __name__ == '__main__':
    testpyvisa()
