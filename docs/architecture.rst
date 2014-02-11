.. _architecture:

Architecture
============

PyVISA implements convenient and Pythonic programming in three layers:

 1. Low-level: A wrapper around the shared visa library.

    The wrapper define the argument types and response types of each function,
    as well as the conversions between Python objects and foreign types.

    You will normally not need to access these functions directly. If you do,
    it probably means that we need to improve layer 2.

 2. Middle-level: A wrapping Python function for each function the shared visa library.

    These functions call the low-level functions, adding some code to deal with
    types conversion for functions that returns values by reference.
    These functions also have comprehensive and Python friendly documentation.

    You only need to access these layer if you want to control certain specific
    aspects of the VISA library such as memory moving.

 3. High-level: An object-oriented layer.

    It exposes all functionality using three main clases: `VisaLibrary`,
    `ResourceManager` and `Instrument`.


It is important to notice that you do not need to import functions form levels 1 and 2,
but you can call them directly from the the `VisaLibrary` object. Indeed, all level 1
functions are static methods of `VisaLibrary`. All level 2 functions are bound methos of
`VisaLibrary`.

Levels 1 and 2are implemented in the same package called `ctwrapper` (which stands for
ctypes wrapper). The higher level uses `ctwrapper` but in principle can use any package.
This will allow us to create other wrappers.

We have two wrappers planned:
- a Mock module that allows you to test a PyVISA program even if you do not have
  VISA installed.
- a CFFI based wrapper. CFFI is new python package that allows easier and more
  robust wrapping of foreign libraries. It might be part of Python in the future.
