.. _faq-visa-distributions:

IVI VISA Distributions
=======================

There are several IVI VISA distributions that will function as a PyVISA backend.
(and others, this list is not exclusive.)

  - `NI-VISA Download`_
  - `NI-VISA help file`_ in HTML (download in PDF, upper right corner)
  - `R&S-VISA Download`_
  - `R&S Basics of Instrument Remote Control`_
  - `Keysight-VISA Download`_

.. _`NI-VISA Download`:
       https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#460225
.. _`NI-VISA help file`:
       https://www.ni.com/docs/en-US/bundle/ni-visa/page/ni-visa/help_file_title.html
.. _`R&S-VISA Download`:
       https://www.rohde-schwarz.com/us/applications/r-s-visa-application-note_56280-148812.html
.. _`R&S Basics of Instrument Remote Control`:
       https://www.rohde-schwarz.com/us/driver-pages/remote-control/automation-by-remote-control-step-by-step_231238.html
.. _`Keysight-VISA Download`:
       https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html

VISA external configuration utility for the IVI backend
========================================================

Managing system VISA resources -
---------------------------------

The three mentioned VISA distributions all come with a utility to manage VISA
resource configurations.  This utility is refered to as the external
configuration utility.  The VISA external configuration utility is used to
manage instrument attributes used to configure buses, instruments, and aliases.
This configuration in turn can be used by PyVISA to manage instrument
configurations in a more user friendly manner than is otherwise afforded.

.. note::

    Not all VISA implementations handle settings configured in the external
    utility the same.  For instance, in NI-VISA, if a serial port is configured
    for baudrate = 115000, the default value will still be configured as 9600.
    To pass the VISA configured value to a new instrument instance, access mode
    must be set to constants.VI_LOAD_CONFIG (see below), otherwise, the default
    value of 9600 will be passed to the instrument instance.  R&S-VISA doesn't
    work this way.  Keysight VISA functionality has not been verified at the
    time of this writing.
     
	open_resource(instr, access_mode=constants.VI_LOAD_CONFIG)

    The important thing to remember is that most values set in the VISA
    external configuration utility are passed to PyVISA at instantiation of an 
    instrument by default.  NI-VISA serial ports are an exception that require:

    "open_resource(instr, access_mode=constants.VI_LOAD_CONFIG)".

Set VISA instrument alias -
---------------------------

A VISA instrument alias is one of the attributes that can be managed by the
external configuration utility. An alias is another way to refer to an
instrument.  PyVISA can open an instrument using either the resource name or
the alias. Resource names are of the form 'GPIB0::3::INSTR', 'ASRL3::INSTR',
'USB0::0x0699::0x0401::C021095::INSTR'.  What can be observed from these
examples is that resource names are very hardware dependent.  All three of
these resource names could refer to a DMM.  If the PyVISA app is coded with the
resource name then any time the instrument needs to be changed out, say to
send an instrument for calibration, or the app needs to be propagated to
multiple systems the names will have to be changed in the app source code.
Alternately, the alias 'DMM' could be assigned to any of these instruments
using the external configuration utility.  If the source code uses the alias,
no source code changes would be required.  One would simply add a new
compatible instrument with the same alias using the external configuration
utility.

Aliases provide a more robust way to refer to instruments for applications that
must be propagated across multiple systems.  It also makes subsituting
alternate instruments easier when required for maintenance or calibration.

Find instruments and test communications -
------------------------------------------------------------------------------

Are instrument communications problems being caused by an instrument, the
configuration, or a bug in the Python app?  Communications problems can be time
consuming to troubleshoot in the Python app but very simple using the external
configuration utility.  All three VISA distributions come with capabilites to
monitor VISA communications, locate instruments, and send commands/receive
responses.  GPIB buses are notoriously finicky to troubleshoot since they are
dependent on address configurations, adpater cards, cabling, etc.  Serial can
also be problematic in cases of PC versus instrument port settings mismatch.
What about LAN LXI instrumentals or remote instruments running on another host?
These can all be found, configured, and tested using the VISA vendors tools
associated with the VISA configuration utilities.

.. note::

    This information was gleaned from experience with NI-VISA 2022 Q3 package
    for Windows.  If you have better info for Keysight or Rohde&Schwarz VISA
    for Windows, Linux or MAC please share your knowledge.
