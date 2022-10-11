.. _faq-faq:

Miscellaneous questions
=======================


Is *PyVISA* endorsed by National Instruments?
---------------------------------------------

No. *PyVISA* is developed independently of National Instrument as a wrapper
for the VISA library.


Who makes *PyVISA*?
-------------------

PyVISA was originally programmed by Torsten Bronger and Gregor Thalhammer.
It is based on earlier experiences by Thalhammer.

It was maintained from March 2012 to August 2013 by Florian Bauer.
It was maintained from August 2013 to December 2017 by Hernan E. Grecco <hernan.grecco@gmail.com>.
It is currently maintained by Matthieu Dartiailh <m.dartiailh@gmail.com>

Take a look at AUTHORS_ for more information


Is PyVISA thread-safe?
----------------------

Yes, PyVISA is thread safe starting from version 1.6.


I have an error in my program and I am having trouble to fix it
---------------------------------------------------------------

PyVISA provides useful logs of all operations. Add the following commands to
your program and run it again::

    import pyvisa
    pyvisa.log_to_screen()


I found a bug, how can I report it?
-----------------------------------

Please report it on the `Issue Tracker`_, including operating system, python
version and library version. In addition you might add supporting information
by pasting the output of this command::

    pyvisa-info


Error: Image not found
----------------------

This error occurs when you have provided an invalid path for the VISA library.
Check that the path provided to the constructor or in the configuration file


Error: Could not found VISA library
-----------------------------------

This error occurs when you have not provided a path for the VISA library and
PyVISA is not able to find it for you. You can solve it by providing the
library path to the ``VisaLibrary`` or ``ResourceManager`` constructor::

    >>> visalib = VisaLibrary('/path/to/library')

or::

    >>> rm = ResourceManager('Path to library')

or creating a configuration file as described in :ref:`intro-configuring`.


Error: `visa` module has no attribute `ResourceManager`
-------------------------------------------------------

The https://github.com/visa-sdk/visa-python provides a visa package that can
conflict with :py:mod:`visa` module provided by PyVISA, which is why the
:py:mod:`visa` module is deprecated and it is preferred to import
:py:mod:`pyvisa` instead of :py:mod:`visa`. Both modules provides the
same interface and no other changes should be needed.


Error: No matching architecture
-------------------------------

This error occurs when you the Python architecture does not match the VISA
architecture.

.. note:: PyVISA tries to parse the error from the underlying foreign function
   library to provide a more useful error message. If it does not succeed, it
   shows the original one.

   In Mac OS X the original error message looks like this::

    OSError: dlopen(/Library/Frameworks/visa.framework/visa, 6): no suitable image found.  Did find:
        /Library/Frameworks/visa.framework/visa: no matching architecture in universal wrapper
        /Library/Frameworks/visa.framework/visa: no matching architecture in universal wrapper

   In Linux the original error message looks like this::

    OSError: Could not open VISA library:
        Error while accessing /usr/local/vxipnp/linux/bin/libvisa.so.7:/usr/local/vxipnp/linux/bin/libvisa.so.7: wrong ELF class: ELFCLASS32


First, determine the details of your installation with the help of the
following debug command::

    pyvisa-info

You will see the 'bitness' of the Python interpreter and at the end you will
see the list of VISA libraries that PyVISA was able to find.

The solution is to:

  1. Install and use a VISA library matching your Python 'bitness'

     Download and install it from **National Instruments's VISA**. Run the
     debug command again to see if the new library was found by PyVISA. If not,
     create a configuration file as described in :ref:`intro-configuring`.

     If there is no VISA library with the correct bitness available, try
     solution 2.

or

  2. Install and use a Python matching your VISA library 'bitness'

     In Windows and Linux: Download and install Python with the matching
     bitness. Run your script again using the new Python

     In Mac OS X, Python is usually delivered as universal binary (32 and
     64 bits).

     You can run it in 32 bit by running::

        arch -i386 python myscript.py

     or in 64 bits by running::

        arch -x86_64 python myscript.py

     You can create an alias by adding the following line

        alias python32="arch -i386 python"

     into your .bashrc or .profile or ~/.bash_profile (or whatever file
     depending on which shell you are using.)

     You can also create a `virtual environment`_ for this.


OSError: Could not open VISA library: function 'viOpen' not found
-----------------------------------------------------------------

Starting with Python 3.8, the .dll load behavior has changed on Windows (see
`https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew`_). This causes
some versions of Keysight VISA to fail to load because it cannot find its .dll
dependencies. You can solve it by creating a configuration file and setting `dll_extra_paths`
as described in :ref:`intro-configuring`.


VisaIOError: VI_ERROR_SYSTEM_ERROR: Unknown system error:
---------------------------------------------------------

If you have an issue creating a pyvisa.ResourceManager object, first enable screen
logging (pyvisa.log_to_screen()) to ensure it is correctly finding the dll files.
If it is correctly finding the dlls, you may see an error similar to:
*  viOpenDefaultRM('<ViObject object at 0x000002B6CA4658C8>',) -> -1073807360
This issue was resolved by reinstalling python. It seems that something within the ctypes
may have been corrupted.
[https://github.com/pyvisa/pyvisa/issues/538]


Using USB-GPIB adapters but no GPIB resources are listed:
---------------------------------------------------------

This issue primarily arises when using a Keithley GPIB-USB cable or other non-NI brands. 

Issue: When connecting the cable from an instrument, the device manager recognizes the connection. However, it is not recognized by PyVisa or any other applications such as NI-VISA or TekVisa. 

Make sure you have the correct driver of your cable installed. For the Keithley KUSB-488B, the driver can be found here: https://www.tek.com/en/support/software/driver/4-0-0

Ensure that the driver is compatible with your software version and OS. If Windows 11 is installed, for example, the above driver will not work. Additionally, when plugging the cable in, see if the indicator lights (if present) are on and lit. If not, use another cable. If the computer itself in Device Manager does not recognize the connection, then it is most likely a problem with the connection or the instrument may require further configuration to prepare it for remote programming. 

There are various options for Visa applications to check on the status and information of the instrument. The recommended ones are either TekVisa or NI-Visa. For Keithley cables, TekVisa is recommended. However, do not install these simultaneously. If both programs are installed, the connection will not be properly detected and a variety of other errors may occur. If both are already downloaded on the same machine, cleanly and completely uninstall both and reinstall the chosen Visa application. If you believe that there may be conflicting a great deal of installation files from these applications and others, it may be conducive to restart on another machine and ensure that nothing is installed more than once. Along with using ``pip uninstall`` (for Spyder, if using another platform using the corresponding uninstall command), the "Add or Remove Programs" in Control Panel for Windows can be used. Again, use the corresponding version depending on the OS. Restart your computer to make sure the changes are implemented accordingly. 

TekVisa Installation - https://www.tek.com/en/support/software/driver/tekvisa-connectivity-software-v411

NI Package Manager Installation - https://www.ni.com/en-us/support/downloads/software-products/download.package-manager.html

NI-Max and NI-VISA might require a reinstallation of the ``.dllwin32`` file. The program will let you know and guide you through the reinstallation. You can either install the file again or (easier) remove the NI application all together and reinstall it. If there is no warning, then you can assume it is installed correctly. Within TekVisa, make sure to enable all categories, as by default the "GPIB" option will be unselected. To do this, press on the "Search Criteria" option and enable the corresponding attributes. 

Another common error in this installation is ``VISA: (Hex 0xBFFF0011) Insufficient location information or the device or resource is not present in the system.``. Although this error might appear with the NI-VISA, it does not necessarily mean that PyVisa will not detect the instrument. It is still worthwhile to print the opened resources from the PyVisa Resource Manager as the instrument may show up. 



Where can I get more information about VISA?
--------------------------------------------


* The original VISA docs:

  - `VISA specification`_ (scroll down to the end)
  - `VISA library specification`_
  - `VISA specification for textual languages`_

* The very good VISA manuals from `National Instruments's VISA`_:

  - `NI-VISA User Manual`_
  - `NI-VISA Programmer Reference Manual`_
  - `NI-VISA help file`_ in HTML

.. _`VISA specification`:
       http://www.ivifoundation.org/Downloads/Specifications.htm
.. _`VISA library specification`:
       http://www.ivifoundation.org/Downloads/Class%20Specifications/vpp43.doc
.. _`VISA specification for textual languages`:
       http://www.ivifoundation.org/Downloads/Class%20Specifications/vpp432.doc
.. _`National Instruments's VISA`: http://ni.com/visa/
.. _`NI-VISA Programmer Reference Manual`:
       http://digital.ni.com/manuals.nsf/websearch/87E52268CF9ACCEE86256D0F006E860D
.. _`NI-VISA help file`:
       http://digital.ni.com/manuals.nsf/websearch/21992F3750B967ED86256F47007B00B3
.. _`NI-VISA User Manual`:
       http://digital.ni.com/manuals.nsf/websearch/266526277DFF74F786256ADC0065C50C


.. _`AUTHORS`: https://github.com/pyvisa/pyvisa/blob/main/AUTHORS
.. _`Issue Tracker`: https://github.com/pyvisa/pyvisa/issues
.. _`virtual environment`: http://www.virtualenv.org/en/latest/

.. _`https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew`:
       https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
