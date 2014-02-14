:orphan:


PyVISA: Python wrapper for the VISA library
===========================================

.. image:: _static/logo-full.jpg
   :alt: PyVISA
   :class: floatingflask


.. warning:: This documentation corresponds to PyVISA 1.5 which is currently
             under development. You can install it from the GitHub using the
             following command::

                 pip install https://github.com/hgrecco/pyvisa/zipball/master

             The old documentations is here: http://pyvisa.readthedocs.org/en/1.4/


The PyVISA package enables you to control all kinds of measurement equipment
through various busses (GPIB, RS232, USB) with Python programs.  As an example,
reading self-identification from a Keithley Multimeter with GPIB number 12 is
as easy as three lines of Python code::

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> rm.list_resources()
    ['ASRL1', 'ASRL2', 'GPIB::12']
    >>> keithley = rm.instrument("GPIB::12")
    >>> print(keithley.ask("*IDN?"))

(That's the whole program; really!) It works on Windows, Linux and Mac;
with arbitrary adapters (e.g. National Instruments, Agilent, Tektronix,
Stanford Research Systems).  In order to achieve this, PyVISA relies on
an external library file which is bundled with hardware and software
of those vendors.


General overview
----------------

The programming of measurement instruments can be real pain. There are many
different protocols, sent over many different interfaces and bus systems (GPIB,
RS232, USB). For every programming language you want to use, you have to find
libraries that support both your device and its bus system.

In order to ease this unfortunate situation, the VISA (Virtual Instrument
Software Architecture specification was defined in the middle of the 90ies.
Today VISA is implemented on all significant operating systems. A couple
of vendors offer VISA libraries, partly with free download.  These libraries
work together with arbitrary peripherical devices, although they may be
limited to certain interface devices, such as the vendor's GPIB card.

The VISA specification has explicit bindings to Visual Basic, C, and G
(LabVIEW's graphical language). However, you can use VISA with any language
capable of calling functions in a shared library (`.dll`, `.so`, `.dylib`).
PyVISA is Python wrapper for such shared library.


User guide
----------

.. toctree::
    :maxdepth: 1

    getting
    tutorial
    configuring
    advanced
    instruments
    architecture

More information
----------------

.. toctree::
    :maxdepth: 1

    migrating
    contributing
    faq
    api/index


Legacy Modules
--------------

.. toctree::
    :maxdepth: 1

    legacy_visa
    legacy_vpp43
    api/legacy


..  LocalWords:  rst british reST ies vpp pyvisa docs pyvLab
