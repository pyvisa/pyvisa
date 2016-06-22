.. _getting_nivisa:

NI-VISA Installation
====================

In every OS, the NI-VISA library bitness (i.e. 32- or 64-bit) has to match the Python bitness. So first you need to install a NI-VISA that works with your OS and then choose the Python version matching the installed NI-VISA bitness.

PyVISA includes a debugging command to help you troubleshoot this (and other things)::

    python -m visa info

According to National Instruments, NI VISA **5.4.1** is available for:

.. note:: If NI-VISA is not available for your system, take a look at the :ref:`faq`.


Mac OS X
--------

Download `NI-VISA for Mac OS X`_

Supports:

- Mac OS X 10.7.x x86 and x86-64
- Mac OS X 10.8.x

*64-bit VISA applications are supported for a limited set of instrumentation buses. The supported buses are ENET-Serial, USB, and TCPIP. Logging VISA operations in NI I/O Trace from 64-bit VISA applications is not supported.*

Windows
-------

Download `NI-VISA for Windows`_

Suports:

- Windows Server 2003 R2 (32-bit version only)
- Windows Server 2008 R2 (64-bit version only)
- Windows 8 x64 Edition (64-bit version)
- Windows 8 (32-bit version)
- Windows 7 x64 Edition (64-bit version)
- Windows 7 (32-bit version)
- Windows Vista x64 Edition (64-bit version)
- Windows Vista (32-bit version)
- Windows XP Service Pack 3

*Support for Windows Server 2003 R2 may require disabling physical address extensions (PAE).*

Linux
-----

Download `NI-VISA for Linux`_

Supports:

- openSUSE 12.2
- openSUSE 12.1
- Red Hat Enterprise Linux Desktop + Workstation 6
- Red Hat Enterprise Linux Desktop + Workstation 5
- Scientific Linux 6.x
- Scientific Linux 5.x

*Currently, only 32-bit applications are supported on the x86-64 architecture.*

.. note:: NI-VISA runs on other linux distros but the installation is more cumbersome.

.. _`NI-VISA for Mac OS X`: http://www.ni.com/download/ni-visa-14.0.2/5075/en/
.. _`NI-VISA for Windows`: http://www.ni.com/download/ni-visa-5.4.1/4626/en/
.. _`NI-VISA for Linux`: http://www.ni.com/download/ni-visa-5.4.1/4629/en/
