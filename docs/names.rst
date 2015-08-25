
.. _resource_names:

VISA resource names
===================

If you use the function :func:`open_resource`, you must tell this
function the *VISA resource name* of the instrument you want to
connect to.  Generally, it starts with the bus type, followed by a
double colon ``"::"``, followed by the number within the bus.  For
example,

.. code-block:: none

   GPIB::10

denotes the GPIB instrument with the number 10.  If you have two GPIB
boards and the instrument is connected to board number 1, you must
write

.. code-block:: none

   GPIB1::10

As for the bus, things like ``"GPIB"``, ``"USB"``, ``"ASRL"`` (for
serial/parallel interface) are possible.  So for connecting to an
instrument at COM2, the resource name is

.. code-block:: none

   ASRL2

(Since only one instrument can be connected with one serial interface,
there is no double colon parameter.)  However, most VISA systems allow
aliases such as ``"COM2"`` or ``"LPT1"``.  You may also add your own
aliases.

The resource name is case-insensitive.  It doesn't matter whether you
say ``"ASRL2"`` or ``"asrl2"``.  For further information, I have to refer
you to a comprehensive VISA description like
`<http://www.ni.com/pdf/manuals/370423a.pdf>`_.


VISA Resource Syntax and Examples
---------------------------------

(This is adapted from the VISA manual)

The following table shows the grammar for the address string. Optional string segments are shown in square brackets ([ ]).

=================  ========================================================================================
Interface          Syntax
=================  ========================================================================================
ENET-Serial INSTR  ASRL[0]::host address::serial port::INSTR
-----------------  ----------------------------------------------------------------------------------------
GPIB INSTR         GPIB[board]::primary address[::secondary address][::INSTR]
GPIB INTFC         GPIB[board]::INTFC
-----------------  ----------------------------------------------------------------------------------------
PXI BACKPLANE      PXI[interface]::chassis number::BACKPLANE
PXI INSTR          PXI[bus]::device[::function][::INSTR]
PXI INSTR          PXI[interface]::bus-device[.function][::INSTR]
PXI INSTR          PXI[interface]::CHASSISchassis number::SLOTslot number[::FUNCfunction][::INSTR]
PXI MEMACC         PXI[interface]::MEMACC
-----------------  ----------------------------------------------------------------------------------------
Remote NI-VISA     visa://host address[:server port]/remote resource
-----------------  ----------------------------------------------------------------------------------------
Serial INSTR       ASRLboard[::INSTR]
-----------------  ----------------------------------------------------------------------------------------
TCPIP INSTR        TCPIP[board]::host address[::LAN device name][::INSTR]
TCPIP SOCKET       TCPIP[board]::host address::port::SOCKET
-----------------  ----------------------------------------------------------------------------------------
USB INSTR          USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]
USB RAW            USB[board]::manufacturer ID::model code::serial number[::USB interface number]::RAW
-----------------  ----------------------------------------------------------------------------------------
VXI BACKPLANE      VXI[board][::VXI logical address]::BACKPLANE
VXI INSTR          VXI[board]::VXI logical address[::INSTR]
VXI MEMACC         VXI[board]::MEMACC
VXI SERVANT        VXI[board]::SERVANT
=================  ========================================================================================

Use the GPIB keyword to establish communication with GPIB resources. Use the VXI keyword for VXI resources via embedded, MXIbus, or 1394 controllers. Use the ASRL keyword to establish communication with an asynchronous serial (such as RS-232 or RS-485) device. Use the PXI keyword for PXI and PCI resources. Use the TCPIP keyword for Ethernet communication.

The following table shows the default value for optional string segments.


========================  ==================================
Optional String Segments  Default Value
========================  ==================================
board                     0
GPIB secondary address    none
LAN device name           inst0
PXI bus                   0
PXI function              0
USB interface number      lowest numbered relevant interface
========================  ==================================


The following table shows examples of address strings:

================================  =============================================
Address String 	                  Description
================================  =============================================
ASRL::1.2.3.4::2::INSTR           A serial device attached to port 2 of the
                                  ENET Serial controller at address 1.2.3.4.
--------------------------------  ---------------------------------------------
ASRL1::INSTR                      A serial device attached to interface ASRL1.
--------------------------------  ---------------------------------------------
GPIB::1::0::INSTR                 A GPIB device at primary address 1 and
                                  secondary address 0 in GPIB interface 0.
--------------------------------  ---------------------------------------------
GPIB2::INTFC                      Interface or raw board resource for GPIB
                                  interface 2.
--------------------------------  ---------------------------------------------
PXI::15::INSTR                    PXI device number 15 on bus 0 with implied
                                  function 0.
--------------------------------  ---------------------------------------------
PXI::2::BACKPLANE                 Backplane resource for chassis 2 on the
                                  default PXI system, which is interface 0.
--------------------------------  ---------------------------------------------
PXI::CHASSIS1::SLOT3              PXI device in slot number 3 of the PXI chassis
                                  configured as chassis 1.
--------------------------------  ---------------------------------------------
PXI0::2-12.1::INSTR               PXI bus number 2, device 12 with function 1.
--------------------------------  ---------------------------------------------
PXI0::MEMACC                      PXI MEMACC session.
--------------------------------  ---------------------------------------------
TCPIP::dev.company.com::INSTR     A TCP/IP device using VXI-11 or LXI located at
                                  the specified address. This uses the default
                                  LAN Device Name of inst0.
--------------------------------  ---------------------------------------------
TCPIP0::1.2.3.4::999::SOCKET      Raw TCP/IP access to port 999 at the specified
                                  IP address.
--------------------------------  ---------------------------------------------
USB::0x1234::125::A22-5::INSTR    A USB Test & Measurement class device with
                                  manufacturer ID 0x1234, model code 125, and
                                  serial number A22-5. This uses the device's
                                  first available USBTMC interface. This is
                                  usually number 0.
--------------------------------  ---------------------------------------------
USB::0x5678::0x33::SN999::1::RAW  A raw USB nonclass device with manufacturer
                                  ID 0x5678, model code 0x33, and serial number
                                  SN999. This uses the device's interface number 1.
--------------------------------  ---------------------------------------------
visa://hostname/ASRL1::INSTR      The resource ASRL1::INSTR on the specified
                                  remote system.
--------------------------------  ---------------------------------------------
VXI::1::BACKPLANE                 Mainframe resource for chassis 1 on the default
                                  VXI system, which is interface 0.
--------------------------------  ---------------------------------------------
VXI::MEMACC                       Board-level register access to the VXI interface.
--------------------------------  ---------------------------------------------
VXI0::1::INSTR                    A VXI device at logical address 1 in VXI
                                  interface VXI0.
--------------------------------  ---------------------------------------------
VXI0::SERVANT                     Servant/device-side resource for VXI interface 0.
================================  =============================================

