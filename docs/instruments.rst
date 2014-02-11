.. _instruments:

Instruments
===========

.. class:: Instrument(resource_name[, **keyw])

   represents an instrument, e.g. a measurement device.  It is
   independent of a particular bus system, i.e. it may be a GPIB,
   serial, USB, or whatever instrument.  However, it is not possible
   to perform bus-specific operations on instruments created by this
   class.  For this, have a look at the specialised classes like
   :class:`GpibInstrument` (section :ref:`sec:gpib-devices`).

   The parameter *resource_name* takes the same syntax as resource
   specifiers in VISA.  Thus, it begins with the bus system followed
   by `"::"`, continues with the location of the device within the bus
   system, and ends with an optional `"::INSTR"`.

   Possible keyword arguments are:

   +-----------------+-------------------------------------------+
   | Keyword         | Description                               |
   +=================+===========================================+
   | *timeout*       | timeout in seconds for all device         |
   |                 | operations, see  section                  |
   |                 | :ref:`sec:timeouts`. Default: 5           |
   +-----------------+-------------------------------------------+
   | *chunk_size*    | Length of read data chunks in bytes, see  |
   |                 | section :ref:`sec:chunk-length`. Default: |
   |                 | 20kB                                      |
   +-----------------+-------------------------------------------+
   | *values_format* | Data format for lists of read values, see |
   |                 | section :ref:`sec:reading-binary-data`.   |
   |                 | Default: `ascii`                          |
   +-----------------+-------------------------------------------+
   | *term_char*     | termination characters, see  section      |
   |                 | :ref:`sec:termchars`. Default: `None`     |
   +-----------------+-------------------------------------------+
   | *send_end*      | whether to assert END after each write    |
   |                 | operation, see  section                   |
   |                 | :ref:`sec:termchars`. Default: `True`     |
   +-----------------+-------------------------------------------+
   | *delay*         | delay in seconds after each write         |
   |                 | operation, see  section                   |
   |                 | :ref:`sec:termchars`. Default: 0          |
   +-----------------+-------------------------------------------+
   | *lock*          | whether you want to have exclusive access |
   |                 | to the device.  Default: `VI_NO_LOCK`     |
   +-----------------+-------------------------------------------+

   .. index::
      single: keyword arguments, common
      single: timeout
      single: chunk_size
      single: values_format
      single: term_char
      single: send_end
      single: delay
      single: lock

   For further information about the locking mechanism,  see `The VISA library
   implementation <http://pyvisa.sourceforge.net/vpp43.html>`_.

The class :class:`Instrument` defines the following methods and attributes:


.. method:: Instrument.write(message)

   writes the string *message* to the instrument.


.. method:: Instrument.read()

   returns a string sent from the instrument to the computer.


.. method:: Instrument.read_values([format])

   returns a list of decimal values (floats) sent from the instrument to the
   computer.  See section :ref:`sec:more-complex-example` above.  The list may
   contain only one element or may be empty.

   The optional *format* argument
   overrides the setting of  *values_format*.  For information about that, see
   section :ref:`sec:reading-binary-data`.


.. method:: Instrument.ask(message)

   sends the string *message* to the instrument and returns the answer  string from
   the instrument.


.. method:: Instrument.ask_for_values(message[, format])

   sends the string *message* to the instrument and reads the answer as a  list of
   values, just as `read_values()` does.

   The optional *format* argument overrides the setting of  *values_format*.  For information about that, see
   section :ref:`sec:reading-binary-data`.


.. method:: Instrument.clear()

   resets the device.  This operation is highly bus-dependent.  I refer you to  the
   original VISA documentation, which explains how this is achieved for VXI,  GPIB,
   serial, etc.


.. method:: Instrument.trigger()

   sends a trigger signal to the instrument.


.. method:: Instrument.read_raw()

   returns a string sent from the instrument to the computer.  In contrast to
   `read()`, no termination characters are checked or stripped.  You get  the
   pristine message.


.. attribute:: Instrument.timeout

   The timeout in seconds for each I/O operation.  See  section :ref:`sec:timeouts`
   for further information.


.. attribute:: Instrument.term_chars

   The termination characters for each read and write operation.  See  section
   :ref:`sec:termchars` for further information.


.. attribute:: Instrument.send_end

   Whether or not to assert EOI (or something equivalent, depending on the
   interface type) after each write operation.  See section :ref:`sec:termchars`
   for further information.


.. attribute:: Instrument.delay

   Time in seconds to wait after each write operation.  See  section
   :ref:`sec:termchars` for further information.


.. attribute:: Instrument.values_format

   The format for multi-value data sent from the instrument to the computer.  See
   section :ref:`sec:reading-binary-data` for further information.


.. _sec:gpib-devices:



Common properties of instrument variables
-----------------------------------------


.. _sec:timeouts:

Timeouts
~~~~~~~~

Very most VISA I/O operations may be performed with a timeout.  If a timeout is
set, every operation that takes longer than the timeout is aborted and an
exception is raised.  Timeouts are given per instrument.

For all PyVISA objects, a timeout is set with

.. code-block:: python

   my_device.timeout = 25

Here, `my_device` may be a device, an interface or whatever, and its timeout is
set to 25 seconds.  Floating-point values are allowed.  If you set  it to zero,
all operations must succeed instantaneously.  You must not set it  to `None`.
Instead, if you want to remove the timeout, just say

.. code-block:: python

   del my_device.timeout

Now every operation of the resource takes as long as it takes, even
indefinitely if necessary.

The default timeout is 5 seconds, but you can change it when creating the  device object:   ::

   my_instrument = instrument("ASRL1", timeout = 8)

This creates the object variable `my_instrument` and sets its timeout to 8
seconds.  In this context, a timeout value of `None` is allowed, which
removes the timeout for this device.

Note that your local VISA library may round up this value heavily. I experienced this effect with my National
Instruments VISA implementation, which rounds off to 0, 1, 3 and 10 seconds.


.. _sec:chunk-length:

Chunk length
~~~~~~~~~~~~

If you read data from a device, you must store it somewhere.  Unfortunately,
PyVISA must make space for the data *before* it starts reading, which  means
that it must know how much data the device will send.  However, it  doesn't know
a priori.

Therefore, PyVISA reads from the device in *chunks*.  Each chunk is
20 kilobytes long by default.  If there's still data to be read, PyVISA repeats
the procedure and eventually concatenates the results and returns it to you.
Those 20 kilobytes are large enough so that mostly one read cycle is
sufficient.

The whole thing happens automatically, as you can see.  Normally
you needn't  worry about it.  However, some devices don't like to send data in
chunks.  So  if you have trouble with a certain device and expect data lengths
larger than  the default chunk length, you should increase its value by saying
e.g.   ::

   my_instrument.chunk_size = 102400

This example sets it to 100 kilobytes.


.. _sec:reading-binary-data:

Reading binary data
-------------------

Some instruments allow for sending the measured data in binary form.  This has
the advantage that the data transfer is much smaller and takes less time.
PyVISA currently supports three forms of transfers:

ascii
   This is the default mode.  It assumes a normal string with comma-  or
   whitespace-separated values.

single
   The values are expected as a binary sequence of IEEE floating  point values with
   single precision (i.e. four bytes each).
   All  flavours of binary data streams defined in IEEE488.2 are supported,  i.e.
   those beginning with *<header>#<digit>*,
   where *<header>* is optional, and  *<digit>* may also be
   "0".

double
   The same as **single**, but with values of double precision  (eight bytes each).

You can set the form of transfer with the property `values_format`, either
with the generation of the object,

.. code-block:: python

   my_instrument = instrument("GPIB::12", values_format = single)

or later by setting the property directly::

   my_instrument.values_format = single

Setting this option affects the methods `read_values()` and
`ask_for_values()`.  In particular, you must assure separately that the
device actually sends in this format.    In some cases it may be necessary to
set the *byte order*, also known as  *endianness*.  PyVISA assumes little-endian
as default.  Some instruments  call this "swapped" byte order.  However, there
is also big-endian byte  order.  In this case you have to append `|
big_endian` to your values  format::

   my_instrument = instrument("GPIB::12", values_format = single | big_endian)


.. _sec:binary-example:


Example
~~~~~~~

In order to demonstrate how easy reading binary data can be, remember our
example from section :ref:`sec:more-complex-example`.  You just have to append
the lines

.. code-block:: python

   keithley.write("format:data sreal")
   keithley.values_format = single

to the initialisation commands, and all measurement data will be transmitted as
binary.  You will only notice the increased speed, as PyVISA converts it into
the same list of values as before.


.. _sec:termchars:

Termination characters
----------------------

Somehow the computer must detect when the device is finished with sending a
message.  It does so by using different methods, depending on the bus system.
In most cases you don't need to worry about termination characters because the
defaults are very good.  However, if you have trouble, you may influence
termination characters with PyVISA.

Termination characters may be one
character or a sequence of characters.  Whenever this character or sequence
occurs in the input stream, the read  operation is terminated and the read
message is given to the calling  application.  The next read operation continues
with the input stream  immediately after the last termination sequence.  In
PyVISA, the termination  characters are stripped off the message before it is
given to you.

You may set termination characters for each instrument, e.g.

.. code-block:: python

   my_instrument.term_chars = CR

Alternatively you can give it when creating your instrument object::

   my_instrument = instrument("GPIB::10", term_chars = CR)

The default value depends on the bus system.  Generally, the sequence is empty,
in particular for GPIB .  For RS232 it's `CR` .

Well, the real default is not `""` (the empty string) but `None`.
There is a subtle difference:
`""` really means the termination characters are not used at all, neither for
read nor for write operations.  In contrast, `None` means that every write
operation is implicitly terminated with  `CR+LF` .  This works well with most
instruments.

All CRs and LFs are stripped from the end of a read string, no
matter how `term_chars` is set.

The termination characters sequence is an
ordinary string.  `CR` and  `LF` are just string constants that allow
readable access to `"\\r"`  and `"\\n"`.  Therefore, instead of `CR+LF`, you
can also write  `"\\r\\n"`, whichever you like more.


`delay` and `send_end`
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   single: delay
   single: send_end

There are two further options related to message termination, namely
`send_end` and `delay`.  `send_end` is a boolean.  If it's  `True` (the
default), the EOI line is asserted after each write operation,  signalling the
end of the operation.  EOI is GPIB-specific but similar action  is taken for
other interfaces.

The argument `delay` is the time in seconds to wait after
each write  operation.  So you could write::

   my_instrument = instrument("GPIB::10", send_end = False, delay = 1.2)

.. index:: single: EOI line

This will set the delay to 1.2 seconds, and the EOI line is omitted.  By the
way, omitting EOI is *not* recommended, so if you omit it nevertheless, you
should know what you're doing.


GPIB devices
------------


.. class:: GpibInstrument(gpib_identifier[, board_number[, **keyw]])

   represents a GPIB instrument.  If *gpib_identifier* is a string, it is
   interpreted as a VISA resource name (section :ref:`sec:visa-resource-names`).
   If it is a number, it denotes the device number at the GPIB bus.

   The optional *board_number* defaults to zero.  If you have more that one  GPIB bus system
   attached to the computer, you can select the bus with this  parameter.

   The keyword arguments are interpreted the same as with the class
   :class:`Instrument`.

.. note::

   Since this class is derived from the class :class:`Instrument`, please refer  to
   section :ref:`sec:general-devices` for the basic operations.
   :class:`GpibInstrument` can do everything that :class:`Instrument` can do, so
   it simply extends the original class with GPIB-specific operations.

The class :class:`GpibInstrument` defines the following methods:


.. method:: GpibInstrument.wait_for_srq([timeout])

   waits for a serial request (SRQ) coming from the instrument.  Note that this
   method is not ended when *another* instrument signals an SRQ, only  *this*
   instrument.

   The *timeout* argument, given in seconds, denotes the maximal
   waiting  time.  The default value is 25 (seconds).  If you pass `None` for the
   timeout, this method waits forever if no SRQ arrives.


.. class:: Gpib([board_number])

   represents a GPIB board.  Although most setups have at most one GPIB  interface
   card or USB-GPIB device (with board number 0), theoretically you  may have more.
   Be that as it may, for board-level operations, i.e.  operations that affect the
   whole bus with all connected devices, you must  create an instance of this
   class.

   The optional GPIB board number *board_number* defaults to 0.

The class :class:`Gpib` defines the following method:


.. method:: Gpib.send_ifc()

   pulses the interface clear line (IFC) for at least 0.1 seconds.

.. note::

   You needn't store the board instance in a variable.  Instead, you may send an
   IFC signal just by saying `Gpib().send_ifc()`.


.. _sec:serial-devices:

Serial devices
--------------

Please note that "serial instrument" means only RS232 and parallel port
instruments, i.e. everything attached to COM and LPT.  In particular, it does
not include USB instruments.  For USB you have to use :class:`Instrument`
instead.


.. class:: SerialInstrument(resource_name[, **keyw])

   represents a serial instrument. `resource_name` is the VISA resource name, see
   section :ref:`sec:visa-resource-names`.    The general keyword arguments are
   interpreted the same as with the class  :class:`Instrument`.  The only
   difference is the default value for  *term_chars*: For serial instruments,
   `CR` (carriage return) is used to terminate readings and writings.

.. note::

   Since this class is derived from the class :class:`Instrument`, please refer  to
   section :ref:`sec:general-devices` for all operations.
   :class:`SerialInstrument` can do everything that :class:`Instrument` can do.

The class :class:`SerialInstrument` defines the following additional properties.
Note that all properties can also be given as keyword arguments when calling
the class constructor or :func:`instrument`.


.. attribute:: SerialInstrument.baud_rate

   The communication speed in baud.  The default value is 9600.


.. attribute:: SerialInstrument.data_bits

   Number of data bits contained in each frame.  Its value must be from 5 to 8.
   The default is 8.


.. attribute:: SerialInstrument.stop_bits

   Number of stop bits contained in each frame.  Possible values are 1, 1.5,  and
   2.  The default is 1.


.. attribute:: SerialInstrument.parity

   The parity used with every frame transmitted and received.  Possible values
   are:

   +----------------+-----------------------------------------+
   | Value          | Description                             |
   +================+=========================================+
   | *no_parity*    | no parity bit is used                   |
   +----------------+-----------------------------------------+
   | *odd_parity*   | the parity bit causes odd parity        |
   +----------------+-----------------------------------------+
   | *even_parity*  | the parity bit causes even parity       |
   +----------------+-----------------------------------------+
   | *mark_parity*  | the parity bit exists but it's always 1 |
   +----------------+-----------------------------------------+
   | *space_parity* | the parity bit exists but it's always 0 |
   +----------------+-----------------------------------------+

   The default value is *no_parity*.


.. attribute:: SerialInstrument.end_input

   This determines the method used to terminate read operations.  Possible  values
   are:

   +------------------------+--------------------------------------------+
   | Value                  | Description                                |
   +========================+============================================+
   | *last_bit_end_input*   | read will terminate as soon as a character |
   |                        | arrives with its last data bit set         |
   +------------------------+--------------------------------------------+
   | *term_chars_end_input* | read will terminate as soon as the   last  |
   |                        | character of *term_chars* is received      |
   +------------------------+--------------------------------------------+

   The default value is *term_chars_end_input*.


