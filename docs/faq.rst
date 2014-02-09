.. _faq:

Frequently asked questions
==========================


Is *PyVISA* endorsed by National Instruments?
---------------------------------------------

No. *PyVISA* is developed independently of National Instrument as a wrapper
for the VISA library.


Who makes *PyVISA*?
-------------------

PyVISA was originally programmed by Torsten Bronger and Gregor Thalhammer, Innsbruck, Austria. It is based on earlier experiences by Thalhammer.

It was maintained from March 2012 to August 2013 by Florian Bauer.
It is currently maintained by Hernan E. Grecco <hernan.grecco@gmail.com>.

Take a look at AUTHORS_ for more information


I found a bug, how can I report it?
-----------------------------------

Please report it on the `Issue Tracker`_, including operating system, python version and library version.



OSError: dlopen(/Library/Frameworks/visa.framework/visa, 6): no suitable image found.  Did find:
	/Library/Frameworks/visa.framework/visa: no matching architecture in universal wrapper
	/Library/Frameworks/visa.framework/visa: no matching architecture in universal wrapper

It is possible to force OSX to run Python in 32 bit mode by
$ export VERSIONER_PYTHON_PREFER_32_BIT=yes

Which you could put in your .profile or .bashrc to run every time you open a new shell. But I didn’t want to default to 32 bit python, I’d rather force it into 32 bit mode when needed.

So, to my .profile I added
alias python386='arch -i386 python'

To force a script to execute under 32 bit Python, rather than including the line #!/usr/bin/python, I start my script with #!/usr/bin/env arch -i386 python.


Where can I get more information about VISA?
--------------------------------------------


* The original VISA docs:

  - `VISA specification`_ (scroll down to the end)
  - `VISA library specification`_
  - `VISA specification for textual languages`_

* The very good VISA manuals from `National Instruments's VISA pages`_:

  - `NI-VISA User Manual`_
  - `NI-VISA Programmer Reference Manual`_
  - `NI-VISA help file`_ in HTML

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


.. _`AUTHORS`: https://github.com/hgrecco/pyvisa/blob/master/AUTHORS
.. _`Issue Tracker`: https://github.com/hgrecco/pyvisa/issues
.. _
