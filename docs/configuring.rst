.. _configuring:


Configuring PyVISA
==================

In most cases PyVISA will be able to find the location of the shared visa library.
If this does not work or you want to use another one, you need to provide the library
path to the `VisaLibrary` or `ResourceManager` constructor::

    >>> visalib = VisaLibrary('/path/to/library')

or::

    >>> rm = ResourceManager('Path to library')


You can make this library the default for all PyVISA applications by using
a configuration file called :file:`.pyvisarc` (mind the leading dot).

For Windows, place it in your "Documents and Settings" folder, [#]_
e.g. :file:`C:\\Documents and Settings\\smith\\.pyvisarc` if "smith" is the
name of your login account. For Linux or Mac, put it in your home directory.

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
:file:`c:\\Python24\\share\\pyvisa\\.pyvisarc`.

