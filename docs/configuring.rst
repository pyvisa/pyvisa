.. _configuring:


Configuring the NI backend
==========================

.. note:: The NI backend requires that you install first the NI-VISA library. You can get
          info here: (:ref:`getting_nivisa`)


In most cases PyVISA will be able to find the location of the shared visa library.
If this does not work or you want to use another one, you need to provide the library
path to the :class:`pyvisa.highlevel.ResourceManager` constructor::

    >>> rm = ResourceManager('Path to library')


You can make this library the default for all PyVISA applications by using
a configuration file called :file:`.pyvisarc` (mind the leading dot) in your
`home directory`_.

==========================  ==================================================
Operating System            Location
==========================  ==================================================
Windows NT                  :file:`<root>\\WINNT\\Profiles\\<username>`
--------------------------  --------------------------------------------------
Windows 2000, XP and 2003   :file:`<root>\\Documents and Settings\\<username>`
--------------------------  --------------------------------------------------
Windows Vista, 7 or 8       :file:`<root>\\Users\\<username>`
--------------------------  --------------------------------------------------
Mac OS X                    :file:`/Users/<username>`
--------------------------  --------------------------------------------------
Linux                       :file:`/home/<username>` (depends on the distro)
==========================  ==================================================

For example in Windows XP, place it in your user folder "Documents and Settings"
folder, e.g. :file:`C:\\Documents and Settings\\smith\\.pyvisarc` if "smith" is
the name of your login account.

This file has the format of an INI file. For example, if the library
is at :file:`/usr/lib/libvisa.so.7`, the file :file:`.pyvisarc` must
contain the following::

   [Paths]

   VISA library: /usr/lib/libvisa.so.7

Please note that `[Paths]` is treated case-sensitively.

You can define a site-wide configuration file at
:file:`/usr/share/pyvisa/.pyvisarc` (It may also be
:file:`/usr/local/...` depending on the location of your Python).
Under Windows, this file is usually placed at
:file:`c:\\Python27\\share\\pyvisa\\.pyvisarc`.

If you encounter any problem, take a look at the :ref:`faq`. There you will find the
solutions to common problem as well as useful debugging techniques. If everything fails,
feel free to open an issue in our `issue tracker`_

.. _`home directory`: http://en.wikipedia.org/wiki/Home_directory
.. _`issue tracker`: https://github.com/hgrecco/pyvisa/issues
