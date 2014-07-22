.. _architecture:

Architecture
============

PyVISA implements convenient and Pythonic programming in three layers:

 1. Low-level: A wrapper around the shared visa library.

    The wrapper defines the argument types and response types of each function,
    as well as the conversions between Python objects and foreign types.

    You will normally not need to access these functions directly. If you do,
    it probably means that we need to improve layer 2.

 2. Middle-level: A wrapping Python function for each function of the shared visa library.

    These functions call the low-level functions, adding some code to deal with
    type conversions for functions that return values by reference.
    These functions also have comprehensive and Python friendly documentation.

    You only need to access this layer if you want to control certain specific
    aspects of the VISA library which are not implemented by the corresponding
    resource class.

 3. High-level: An object-oriented layer.

    It exposes all functionality using three main clases: `VisaLibrary`,
    `ResourceManager` and `Resource` (and derived classes).


Most of the time you will only need to instantiate a `ResourceManager`. For a given resource,
you will use the `open_resource` method to obtain the apropriate object. If needed, you will
be able to access the `VisaLibrary` object directly using the `visalib` attribute.

It is important to notice that you do not need to import functions from levels 1 and 2,
but you can call them directly from the the `VisaLibrary` object. Indeed, all level 1
functions are **static methods** of `VisaLibrary`. All level 2 functions are **bound methods**
of `VisaLibrary`.

Levels 1 and 2 are implemented in the same package called `ctwrapper` (which stands for
ctypes wrapper). The higher level uses `ctwrapper` but in principle can use any package.
This will allow us to create other wrappers.

We have two wrappers planned:

- a Mock module that allows you to test a PyVISA program even if you do not have
  VISA installed.

- a CFFI based wrapper. CFFI is new python package that allows easier and more
  robust wrapping of foreign libraries. It might be part of Python in the future.
