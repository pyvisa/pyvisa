:orphan:


PyVISA: Control your instruments with Python
============================================

.. image:: _static/logo-full.jpg
   :alt: PyVISA
   :class: floatingflask


PyVISA is a Python package that enables you to control all kinds of measurement
devices independently of the interface (e.g. GPIB, RS232, USB, Ethernet). As
an example, reading self-identification from a Keithley Multimeter with GPIB
number 12 is as easy as three lines of Python code::

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> rm.list_resources()
    ('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')
    >>> inst = rm.open_resource('GPIB0::12::INSTR')
    >>> print(inst.query("*IDN?"))

(That's the whole program; really!) It works on Windows, Linux and Mac;
with arbitrary adapters (e.g. National Instruments, Agilent, Tektronix,
Stanford Research Systems).


General overview
----------------

The programming of measurement instruments can be real pain. There are many
different protocols, sent over many different interfaces and bus systems
(e.g. GPIB, RS232, USB, Ethernet). For every programming language you want
to use, you have to find libraries that support both your device and its bus
system.

In order to ease this unfortunate situation, the Virtual Instrument Software
Architecture (VISA) specification was defined in the middle of the 90ies.
VISA is a standard for configuring, programming, and troubleshooting
instrumentation systems comprising GPIB, VXI, PXI, Serial, Ethernet, and/or
USB interfaces.

Today VISA is implemented on all significant operating systems. A couple
of vendors offer VISA libraries, partly with free download.  These libraries
work together with arbitrary peripherical devices, although they may be
limited to certain interface devices, such as the vendor's GPIB card.

The VISA specification has explicit bindings to Visual Basic, C, and G
(LabVIEW's graphical language). However, you can use VISA with any language
capable of calling functions in a shared library (`.dll`, `.so`, `.dylib`).
PyVISA is Python wrapper for such shared library ... and more.


User guide
----------

.. toctree::
    :maxdepth: 1

    getting
    configuring
    tutorial
    rvalues
    example
    resources
    backends
    shell
    architecture

More information
----------------

.. toctree::
    :maxdepth: 1

    names
    migrating
    contributing
    faq
    getting_nivisa
    api/index


..  LocalWords:  rst british reST ies vpp pyvisa docs pyvLab
