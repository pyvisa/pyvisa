.. _intro-communication:

Communicating with your instrument
==================================

.. include:: ../substitutions.sub

.. note:: If you have been using PyVISA before version 1.5, you might want to
          read :ref:`faq-migrating`.


An example
----------

Let's go *in medias res* and have a look at a simple example::

    >>> import pyvisa
    >>> rm = pyvisa.ResourceManager()
    >>> rm.list_resources()
    ('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::14::INSTR')
    >>> my_instrument = rm.open_resource('GPIB0::14::INSTR')
    >>> print(my_instrument.query('*IDN?'))

This example already shows the two main design goals of PyVISA: preferring
simplicity over generality, and doing it the object-oriented way.

After importing ``pyvisa``, we create a ``ResourceManager`` object. If called
without arguments, PyVISA will prefer the default backend (IVI) which tries to
find the VISA shared library for you. If it fails it will fall back to
pyvisa-py if installed. You can check what backend is used and the location of
the shared library used, if relevant, simply by:

    >>> print(rm)
    <ResourceManager('/path/to/visa.so')>

.. note::

    In some cases, PyVISA is not able to find the library for you resulting in
    an ``OSError``. To fix it, find the library path yourself and pass it to
    the ResourceManager constructor. You can also specify it in a configuration
    file as discussed in :ref:`intro-configuring`.


Once that you have a ``ResourceManager``, you can list the available resources
using the ``list_resources`` method. The output is a tuple listing the
:ref:`intro-resource-names`. You can use a dedicated regular expression syntax
to filter the instruments discovered by this method. The syntax is described in
details in |list_resources|. The default value is '?*::INSTR' which means that
by default only instrument whose resource name ends with '::INSTR' are listed
(in particular USB RAW resources and TCPIP SOCKET resources are not listed).

In this case, there is a GPIB instrument with instrument number 14, so you ask
the ``ResourceManager`` to open "'GPIB0::14::INSTR'" and assign the returned
object to the *my_instrument*.

Notice ``open_resource`` has given you an instance of ``GPIBInstrument`` class
(a subclass of the more generic ``Resource``).

    >>> print(my_instrument)
    <GPIBInstrument('GPIB::14')>

There many ``Resource`` subclasses representing the different types of
resources, but you do not have to worry as the ``ResourceManager`` will provide
you with the appropriate class. You can check the methods and attributes of
each class in the :ref:`api_resources`

Then, you query the device with the following message: ``'\*IDN?'``.
Which is the standard GPIB message for "what are you?" or -- in some cases --
"what's on your display at the moment?". ``query`` is a short form for a
``write`` operation to send a message, followed by a ``read``.

So::

    >>> my_instrument.query("*IDN?")

is the same as::

    >>> my_instrument.write('*IDN?')
    >>> print(my_instrument.read())


.. note::

    You can access all the opened resources by calling
    ``rm.list_opened_resources()``. This will return a list of ``Resource``,
    however note that this list is not dynamically updated.


Getting the instrument configuration right
------------------------------------------

For most instruments, you actually need to properly configure the instrument
so that it understands the message sent by the computer (in particular how to
identifies the end of the commands) and so that computer knows when the
instrument is done talking. If you don't you are likely to see a |VisaIOError|
reporting a timeout.

For message based instruments (which covers most of the use cases), this
usually consists in properly setting the |read_termination| and
|write_termination| attribute of the resource. Resources have more attributes
described in :ref:`intro-resources`, but for now we will focus on those two.

The first place to look for the values you should set for your instrument is
the manual. The information you are looking is usually located close to the
beginning of the IO operation section of the manual. If you cannot find the
value, you can try to iterate through a couple of standard values but this is
not recommended approach.

Once you have that information you can try to configure your instrument and
start communicating as follows::

    >>> my_instrument.read_termination = '\n'
    >>> my_instrument.write_termination = '\n'
    >>> my_instrument.query('*IDN?')

Here we use `'\n'` known as 'line feed'. This is a common value, another one is
`'\r'` i.e. 'carriage return', and in some cases the null byte '\0' is used.

In an ideal world, this will work and you will be able to get an answer from
your instrument. If it does not, it means the settings are likely wrong (the
documentation does not always shine by its clarity). In the following we will
discuss common debugging tricks, if nothing works feel free to post on the
PyVISA `issue tracker`_. If you do be sure to describe in detail your setup and
what you already attempted.

.. _`issue tracker`: https://github.com/pyvisa/pyvisa/issues

.. note::

    The particular case of reading back large chunk of data either in ASCII
    or binary format is not discussed below but in :ref:`intro-rvalues`.

Making sure the instrument understand the command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using query, we are testing both writing to and reading from the
instrument. The first thing to do is to try to identify if the issue occurs
during the write or the read operation.

If your instrument has a front panel, you can check for errors (some instrument
will display a transient message right after the read). If an error occurs,
it may mean your command string contains a mistake or the instrument is using
a different set of command (some instrument supports both a legacy set of
commands and SCPI commands). If you see no error it means that either the
instrument did not detect the end of your message or you just cannot read it.
The next step is to determine in what situation we are.

To do so, you can look for a command that would produce a visible/measurable
change on the instrument and send it. In the absence of errors, if the expected
change did not occur it means the instrument did not understand that the
command was complete. This points out to an issue with the |write_termination|.
At this stage, you can go back to the manual (some instruments allow to switch
between the recognized values), or try standards values (such as `'\n'`,
`'\r'`, combination of those two, `'\0'`).

Assuming you were able to confirm that the instrument understood the command
you sent, it means the reading part is the issue, which is easier to
troubleshoot. You can try different standard values for the |read_termination|,
but if nothing works you can use the |read_bytes| method. This method will read
at most the number of bytes specified. So you can try reading one byte at a
time till you encounter a time out. When that happens most likely the last
character you read is the termination character. Here is a quick example:

.. code:: python

    my_instrument.write('*IDN?')
    while True:
        print(my_instrument.read_bytes(1))

If |read_bytes| times out on the first read, it actually means that the
instrument did not answer. If the instrument is old it may be because your are
too fast for it, so you can try waiting a bit before reading (using
`time.sleep` from Python standard library). Otherwise, you either use a command
that does not cause any answer or actually your write does not work (go back
up a couple of paragraph).

.. note::

    Some instruments may be slow in answering and may require you to either
    increase the timeout or specify a delay between the write and read
    operation. This can be done globally using |query_delay| or passing
    ``delay=0.1`` for example to wait 100 ms after writing before reading.

.. note::

    When transferring large amount of data the total transfer time may exceed
    the timeout value in which case increasing the timeout value should fix
    the issue.

.. note::

    It is possible to disable the use of teh termination character to detect
    the end of an input message by setting |read_termination| to ``""``. Care
    has to be taken for the case of serial instrument for which the method used
    to determine the end of input is controlled by the |end_input| attribute
    and is set by default to use the termination character. To fully disable
    the use of the termination character its value should be changed.

The above focused on using only PyVISA,  if you are running Windows, or MacOS
you are likely to have access to third party tools that can help. Some tips to
use them are given in the next section.

.. note::

    Some instruments do not react well to a communication error, and you may
    have to restart it to get it to work again.

Using third-party softwares
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The implementation of VISA from National Instruments and Keysight both come
with tools (NIMax, Keysight Connection Expert) that can be used to figure out
what is wrong with your communication setup.

In both cases, you can open an interactive communication session to your
instrument and tune the settings using a GUI (which can make things easier).
The basic procedure is the one described above, if you can make it work in
one of those tools you should be able, in most cases, to get it to work in
PyVISA. However if it does not work using those tools, it won't work in
PyVISA.


Hopefully those simple tips will allow you to get through. In some cases, it
may not be the case and you are always welcome to ask for help (but realize
that the maintainers are unlikely to have access to the instrument you are
having trouble with).
