:orphan:

.. -*- mode: rst; coding: utf-8; ispell-local-dictionary: "british"; -*-


PyVISA: Python wrapper for the VISA library
===========================================

.. image:: _static/logo-full.jpg
   :alt: PyVISA
   :class: floatingflask


The PyVISA package enables you to control all kinds of measurement equipment
through various busses (GPIB, RS232, USB) with Python programs.  As an example,
reading self-identification from a Keithley Multimeter with GPIB number 12 is
as easy as three lines of Python code::

    import visa
    keithley = visa.instrument("GPIB::12")
    print(keithley.ask("*IDN?"))

(That's the whole program; really!) It is tailored to work on Windows,
Linux and Mac; with arbitrary adapters (e.g. National Instruments, Agilent,
Tektronix, Stanford Research Systems).  In order to achieve this, PyVISA
relies on an external library file which is bundled with hardware and software
of those vendors.  (So only in rare cases you have to purchase it separately.)

PyVISA implements convenient and Pythonic programming in two layers:

1. A wrapper module around the visa library.
   This module
Additionally, there is the lower level module ``vpp43``, which directly
   calls the VISA functions from Python.  See the `PyVISA low-level
   implementation`_ for more information.  This is only for people who need
   full control or the official VISA functions for some reason.

2. An object-oriented Python module has been created simply called ``visa``.
   It is the recommended way to use PyVISA.  See the `PyVISA manual`_ for more
   information.


PyVISA is free open-source software.  The `PyVISA project page`_ contains the
bug tracker and the download area.

Projects using PyVISA so far:

* `pyvLab`_ -- program to control VISA-talking instruments.
* `Lantz`_ -- a Python instrumentation toolkit.

.. _`pyvLab`: http://pyvlab.sourceforge.net/
.. _`Lantz`: https://lantz.readthedocs.org/


General overview
----------------

The programming of measurement instruments can be real pain.  There are many
different protocols, sent over many different interfaces and bus systems (GPIB,
RS232, USB).  For every programming language you want to use, you have to find
libraries that support both your device and its bus system.

In order to ease this unfortunate situation, the VISA [#]_ specification was
defined in the middle of the 90ies.  Today VISA is implemented on all
significant operating systems.  A couple of vendors offer VISA libraries,
partly with free download.  These libraries work together with arbitrary
peripherical devices, although they may be limited to certain interface
devices, such as the vendor's GPIB card.

.. [#] Virtual Instrument Software Architecture

The VISA specification has explicit bindings to Visual Basic, C, and G
(LabVIEW's graphical language).  However, you can use VISA with any language
capable of calling functions in a DLL.  Python is such a language.


VISA and Python
---------------

Python has a couple of features that make it very interesting for measurement
controlling:

* Python is an easy-to-learn scripting language with short development cycles.

* It represents a high abstraction level [#]_, which perfectly blends with the
  abstraction level of measurement programs.

* It has a very rich set of native libraries, including numerical and plotting
  modules for data analysis and visualisation.

* A large set of books (in many languages) and on-line publications is
  available.

* You can download it for free at http://www.python.org.

.. [#] For example, you don't need to care about the underlying operating
       system with all its peculiarities.


.. toctree::
    :maxdepth: 1

    pyvisa
    vpp43


Links
-----

* The original VISA docs:

  - `VISA specification`_ (scroll down to the end)
  - `VISA library specification`_
  - `VISA specification for textual languages`_

* The very good VISA manuals from `National Instruments's VISA pages`_:

  - `NI-VISA User Manual`_
  - `NI-VISA Programmer Reference Manual`_
  - `NI-VISA help file`_ in HTML

.. _`PyVISA manual`: http://pyvisa.sourceforge.net/pyvisa.html
.. _`as PDF`: http://pyvisa.sourceforge.net/pyvisa.pdf
.. _`PyVISA project page`: http://sourceforge.net/projects/pyvisa/
.. _`PyVISA low-level implementation`: http://pyvisa.sourceforge.net/vpp43.html
.. _`VISA specification`:
       http://www.ivifoundation.org/Downloads/Specifications.htm
.. _`VISA library specification`:
       http://www.ivifoundation.org/Downloads/Class%20Specifications/vpp43.doc
.. _`VISA specification for textual languages`:
       http://www.ivifoundation.org/Downloads/Class%20Specifications/vpp432.doc
.. _`National Instruments's VISA pages`: http://ni.com/visa/
.. _`NI-VISA Programmer Reference Manual`:
       http://digital.ni.com/manuals.nsf/websearch/87E52268CF9ACCEE86256D0F006E860D
.. _`NI-VISA help file`:
       http://digital.ni.com/manuals.nsf/websearch/21992F3750B967ED86256F47007B00B3
.. _`NI-VISA User Manual`:
       http://digital.ni.com/manuals.nsf/websearch/266526277DFF74F786256ADC0065C50C


..  LocalWords:  rst british reST ies vpp pyvisa docs pyvLab
