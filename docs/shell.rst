.. _shell:

PyVISA Shell
============

The shell, moved into PyVISA from the Lantz_ Project is a text based user
interface to interact with instruments. You can invoke it from the command-line::

    python -m visa shell

that will show something the following prompt::

    Welcome to the VISA shell. Type help or ? to list commands.

    (visa)

At any time, you can type ``?`` or ``help`` to get a list of valid commands::

    (visa) help

    Documented commands (type help <topic>):
    ========================================
    EOF  attr  close  exit  help  list  open  query  read  write

    (visa) help list
    List all connected resources.

Tab completion is also supported.

The most basic task is listing all connected devices::

    (visa) list
    ( 0) ASRL1::INSTR
    ( 1) ASRL2::INSTR
    ( 2) USB0::0x1AB1::0x0588::DS1K00005888::INSTR


Each device/port is assigned a number that you can use for subsequent commands.
Let's open comport 1::

    (visa) open 0
    ASRL1::INSTR has been opened.
    You can talk to the device using "write", "read" or "query.
    The default end of message is added to each message
    (open) query *IDN?
    Some Instrument, Some Company.

We can also get a list of all visa attributes::

    +-----------------------------+------------+----------------------------+-------------------------------------+
    |          VISA name          |  Constant  |        Python name         |                 val                 |
    +-----------------------------+------------+----------------------------+-------------------------------------+
    | VI_ATTR_ASRL_ALLOW_TRANSMIT | 1073676734 |       allow_transmit       |                  1                  |
    |    VI_ATTR_ASRL_AVAIL_NUM   | 1073676460 |      bytes_in_buffer       |                  0                  |
    |      VI_ATTR_ASRL_BAUD      | 1073676321 |         baud_rate          |                 9600                |
    |    VI_ATTR_ASRL_BREAK_LEN   | 1073676733 |        break_length        |                 250                 |
    |   VI_ATTR_ASRL_BREAK_STATE  | 1073676732 |        break_state         |                  0                  |
    |    VI_ATTR_ASRL_CONNECTED   | 1073676731 |                            |          VI_ERROR_NSUP_ATTR         |
    |    VI_ATTR_ASRL_CTS_STATE   | 1073676462 |                            |                  0                  |
    |    VI_ATTR_ASRL_DATA_BITS   | 1073676322 |         data_bits          |                  8                  |
    |    VI_ATTR_ASRL_DCD_STATE   | 1073676463 |                            |                  0                  |
    |  VI_ATTR_ASRL_DISCARD_NULL  | 1073676464 |        discard_null        |                  0                  |
    |    VI_ATTR_ASRL_DSR_STATE   | 1073676465 |                            |                  0                  |
    |    VI_ATTR_ASRL_DTR_STATE   | 1073676466 |                            |                  1                  |
    |     VI_ATTR_ASRL_END_IN     | 1073676467 |         end_input          |                  2                  |
    |     VI_ATTR_ASRL_END_OUT    | 1073676468 |                            |                  0                  |
    |   VI_ATTR_ASRL_FLOW_CNTRL   | 1073676325 |                            |                  0                  |
    |     VI_ATTR_ASRL_PARITY     | 1073676323 |           parity           |                  0                  |
    |  VI_ATTR_ASRL_REPLACE_CHAR  | 1073676478 |        replace_char        |                  0                  |
    |    VI_ATTR_ASRL_RI_STATE    | 1073676479 |                            |                  0                  |
    |    VI_ATTR_ASRL_RTS_STATE   | 1073676480 |                            |                  1                  |
    |    VI_ATTR_ASRL_STOP_BITS   | 1073676324 |         stop_bits          |                  10                 |
    |    VI_ATTR_ASRL_WIRE_MODE   | 1073676735 |                            |                 128                 |
    |    VI_ATTR_ASRL_XOFF_CHAR   | 1073676482 |         xoff_char          |                  19                 |
    |    VI_ATTR_ASRL_XON_CHAR    | 1073676481 |          xon_char          |                  17                 |
    |     VI_ATTR_DMA_ALLOW_EN    | 1073676318 |         allow_dma          |                  0                  |
    |    VI_ATTR_FILE_APPEND_EN   | 1073676690 |                            |                  0                  |
    |    VI_ATTR_INTF_INST_NAME   | 3221160169 |                            | ASRL1  (/dev/cu.Bluetooth-PDA-Sync) |
    |       VI_ATTR_INTF_NUM      | 1073676662 |      interface_number      |                  1                  |
    |      VI_ATTR_INTF_TYPE      | 1073676657 |                            |                  4                  |
    |       VI_ATTR_IO_PROT       | 1073676316 |        io_protocol         |                  1                  |
    |   VI_ATTR_MAX_QUEUE_LENGTH  | 1073676293 |                            |                  50                 |
    |   VI_ATTR_RD_BUF_OPER_MODE  | 1073676330 |                            |                  3                  |
    |     VI_ATTR_RD_BUF_SIZE     | 1073676331 |                            |                 4096                |
    |      VI_ATTR_RM_SESSION     | 1073676484 |                            |               3160976               |
    |      VI_ATTR_RSRC_CLASS     | 3221159937 |       resource_class       |                INSTR                |
    |  VI_ATTR_RSRC_IMPL_VERSION  | 1073676291 |   implementation_version   |               5243392               |
    |   VI_ATTR_RSRC_LOCK_STATE   | 1073676292 |         lock_state         |                  0                  |
    |     VI_ATTR_RSRC_MANF_ID    | 1073676661 |                            |                 4086                |
    |    VI_ATTR_RSRC_MANF_NAME   | 3221160308 | resource_manufacturer_name |         National Instruments        |
    |      VI_ATTR_RSRC_NAME      | 3221159938 |       resource_name        |             ASRL1::INSTR            |
    |  VI_ATTR_RSRC_SPEC_VERSION  | 1073676656 |        spec_version        |               5243136               |
    |     VI_ATTR_SEND_END_EN     | 1073676310 |          send_end          |                  1                  |
    |   VI_ATTR_SUPPRESS_END_EN   | 1073676342 |                            |                  0                  |
    |       VI_ATTR_TERMCHAR      | 1073676312 |                            |                  10                 |
    |     VI_ATTR_TERMCHAR_EN     | 1073676344 |                            |                  0                  |
    |      VI_ATTR_TMO_VALUE      | 1073676314 |                            |                 2000                |
    |       VI_ATTR_TRIG_ID       | 1073676663 |                            |                  -1                 |
    |   VI_ATTR_WR_BUF_OPER_MODE  | 1073676333 |                            |                  2                  |
    |     VI_ATTR_WR_BUF_SIZE     | 1073676334 |                            |                 4096                |
    +-----------------------------+------------+----------------------------+-------------------------------------+

Finally, you can close the device::

    (open) close


Cool, right? It will be great to have a GUI similar to NI-MAX, but we leave that to be developed outside PyVISA.
Want to help? Let us know!


.. _`Lantz`: https://lantz.readthedocs.org

