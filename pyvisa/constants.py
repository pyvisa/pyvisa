# -*- coding: utf-8 -*-
"""
    pyvisa.constants
    ~~~~~~~~~~~~~~~~

    VISA VPP-4.3 constants (VPP-4.3.2 spec, section 3).

    Makes all "completion and error codes", "attribute values", "event type
    values", and "values and ranges" defined in the VISA specification VPP-4.3.2,
    section 3, available as variable values.

    The module exports the values under the original, all-uppercase names.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import enum

from .compat import PYTHON3

if PYTHON3:
    LongEnum = enum.IntEnum
else:
    class LongEnum(long, enum.Enum):
        pass

# _to_int() is necessary because the VISA specification is flawed: It defines
# the VISA codes, which have a value less than zero, in their internal 32-bit
# signed integer representation.  However, this is positive.  ctypes doesn't
# care about that and (correctly) returns the negative value, which is left as
# such by Python.
#


def _to_int(x):
    """Converts a completion and error code as it is listed in 32-bit notation
    in the VPP-4.3.2 specification to the actual integer value.
    """
    if x > 0x7FFFFFFF:
        return int(x - 0x100000000)
    else:
        return int(x)

VI_SUCCESS                   = _to_int(0x00000000)
VI_SUCCESS_EVENT_EN          = _to_int(0x3FFF0002)
VI_SUCCESS_EVENT_DIS         = _to_int(0x3FFF0003)
VI_SUCCESS_QUEUE_EMPTY       = _to_int(0x3FFF0004)
VI_SUCCESS_TERM_CHAR         = _to_int(0x3FFF0005)
VI_SUCCESS_MAX_CNT           = _to_int(0x3FFF0006)
VI_SUCCESS_DEV_NPRESENT      = _to_int(0x3FFF007D)
VI_SUCCESS_TRIG_MAPPED       = _to_int(0x3FFF007E)
VI_SUCCESS_QUEUE_NEMPTY      = _to_int(0x3FFF0080)
VI_SUCCESS_NCHAIN            = _to_int(0x3FFF0098)
VI_SUCCESS_NESTED_SHARED     = _to_int(0x3FFF0099)
VI_SUCCESS_NESTED_EXCLUSIVE  = _to_int(0x3FFF009A)
VI_SUCCESS_SYNC              = _to_int(0x3FFF009B)

VI_WARN_QUEUE_OVERFLOW       = _to_int(0x3FFF000C)
VI_WARN_CONFIG_NLOADED       = _to_int(0x3FFF0077)
VI_WARN_NULL_OBJECT          = _to_int(0x3FFF0082)
VI_WARN_NSUP_ATTR_STATE      = _to_int(0x3FFF0084)
VI_WARN_UNKNOWN_STATUS       = _to_int(0x3FFF0085)
VI_WARN_NSUP_BUF             = _to_int(0x3FFF0088)

# The following one is a non-standard NI extension
VI_WARN_EXT_FUNC_NIMPL       = _to_int(0x3FFF00A9)

VI_ERROR_SYSTEM_ERROR        = _to_int(0xBFFF0000)
VI_ERROR_INV_OBJECT          = _to_int(0xBFFF000E)
VI_ERROR_RSRC_LOCKED         = _to_int(0xBFFF000F)
VI_ERROR_INV_EXPR            = _to_int(0xBFFF0010)
VI_ERROR_RSRC_NFOUND         = _to_int(0xBFFF0011)
VI_ERROR_INV_RSRC_NAME       = _to_int(0xBFFF0012)
VI_ERROR_INV_ACC_MODE        = _to_int(0xBFFF0013)
VI_ERROR_TMO                 = _to_int(0xBFFF0015)
VI_ERROR_CLOSING_FAILED      = _to_int(0xBFFF0016)
VI_ERROR_INV_DEGREE          = _to_int(0xBFFF001B)
VI_ERROR_INV_JOB_ID          = _to_int(0xBFFF001C)
VI_ERROR_NSUP_ATTR           = _to_int(0xBFFF001D)
VI_ERROR_NSUP_ATTR_STATE     = _to_int(0xBFFF001E)
VI_ERROR_ATTR_READONLY       = _to_int(0xBFFF001F)
VI_ERROR_INV_LOCK_TYPE       = _to_int(0xBFFF0020)
VI_ERROR_INV_ACCESS_KEY      = _to_int(0xBFFF0021)
VI_ERROR_INV_EVENT           = _to_int(0xBFFF0026)
VI_ERROR_INV_MECH            = _to_int(0xBFFF0027)
VI_ERROR_HNDLR_NINSTALLED    = _to_int(0xBFFF0028)
VI_ERROR_INV_HNDLR_REF       = _to_int(0xBFFF0029)
VI_ERROR_INV_CONTEXT         = _to_int(0xBFFF002A)
VI_ERROR_QUEUE_OVERFLOW      = _to_int(0xBFFF002D)
VI_ERROR_NENABLED            = _to_int(0xBFFF002F)
VI_ERROR_ABORT               = _to_int(0xBFFF0030)
VI_ERROR_RAW_WR_PROT_VIOL    = _to_int(0xBFFF0034)
VI_ERROR_RAW_RD_PROT_VIOL    = _to_int(0xBFFF0035)
VI_ERROR_OUTP_PROT_VIOL      = _to_int(0xBFFF0036)
VI_ERROR_INP_PROT_VIOL       = _to_int(0xBFFF0037)
VI_ERROR_BERR                = _to_int(0xBFFF0038)
VI_ERROR_IN_PROGRESS         = _to_int(0xBFFF0039)
VI_ERROR_INV_SETUP           = _to_int(0xBFFF003A)
VI_ERROR_QUEUE_ERROR         = _to_int(0xBFFF003B)
VI_ERROR_ALLOC               = _to_int(0xBFFF003C)
VI_ERROR_INV_MASK            = _to_int(0xBFFF003D)
VI_ERROR_IO                  = _to_int(0xBFFF003E)
VI_ERROR_INV_FMT             = _to_int(0xBFFF003F)
VI_ERROR_NSUP_FMT            = _to_int(0xBFFF0041)
VI_ERROR_LINE_IN_USE         = _to_int(0xBFFF0042)
VI_ERROR_NSUP_MODE           = _to_int(0xBFFF0046)
VI_ERROR_SRQ_NOCCURRED       = _to_int(0xBFFF004A)
VI_ERROR_INV_SPACE           = _to_int(0xBFFF004E)
VI_ERROR_INV_OFFSET          = _to_int(0xBFFF0051)
VI_ERROR_INV_WIDTH           = _to_int(0xBFFF0052)
VI_ERROR_NSUP_OFFSET         = _to_int(0xBFFF0054)
VI_ERROR_NSUP_VAR_WIDTH      = _to_int(0xBFFF0055)
VI_ERROR_WINDOW_NMAPPED      = _to_int(0xBFFF0057)
VI_ERROR_RESP_PENDING        = _to_int(0xBFFF0059)
VI_ERROR_NLISTENERS          = _to_int(0xBFFF005F)
VI_ERROR_NCIC                = _to_int(0xBFFF0060)
VI_ERROR_NSYS_CNTLR          = _to_int(0xBFFF0061)
VI_ERROR_NSUP_OPER           = _to_int(0xBFFF0067)
VI_ERROR_INTR_PENDING        = _to_int(0xBFFF0068)
VI_ERROR_ASRL_PARITY         = _to_int(0xBFFF006A)
VI_ERROR_ASRL_FRAMING        = _to_int(0xBFFF006B)
VI_ERROR_ASRL_OVERRUN        = _to_int(0xBFFF006C)
VI_ERROR_TRIG_NMAPPED        = _to_int(0xBFFF006E)
VI_ERROR_NSUP_ALIGN_OFFSET   = _to_int(0xBFFF0070)
VI_ERROR_USER_BUF            = _to_int(0xBFFF0071)
VI_ERROR_RSRC_BUSY           = _to_int(0xBFFF0072)
VI_ERROR_NSUP_WIDTH          = _to_int(0xBFFF0076)
VI_ERROR_INV_PARAMETER       = _to_int(0xBFFF0078)
VI_ERROR_INV_PROT            = _to_int(0xBFFF0079)
VI_ERROR_INV_SIZE            = _to_int(0xBFFF007B)
VI_ERROR_WINDOW_MAPPED       = _to_int(0xBFFF0080)
VI_ERROR_NIMPL_OPER          = _to_int(0xBFFF0081)
VI_ERROR_INV_LENGTH          = _to_int(0xBFFF0083)
VI_ERROR_INV_MODE            = _to_int(0xBFFF0091)
VI_ERROR_SESN_NLOCKED        = _to_int(0xBFFF009C)
VI_ERROR_MEM_NSHARED         = _to_int(0xBFFF009D)
VI_ERROR_LIBRARY_NFOUND      = _to_int(0xBFFF009E)
VI_ERROR_NSUP_INTR           = _to_int(0xBFFF009F)
VI_ERROR_INV_LINE            = _to_int(0xBFFF00A0)
VI_ERROR_FILE_ACCESS         = _to_int(0xBFFF00A1)
VI_ERROR_FILE_IO             = _to_int(0xBFFF00A2)
VI_ERROR_NSUP_LINE           = _to_int(0xBFFF00A3)
VI_ERROR_NSUP_MECH           = _to_int(0xBFFF00A4)
VI_ERROR_INTF_NUM_NCONFIG    = _to_int(0xBFFF00A5)
VI_ERROR_CONN_LOST           = _to_int(0xBFFF00A6)

# The following two are a non-standard NI extensions
VI_ERROR_MACHINE_NAVAIL      = _to_int(0xBFFF00A7)
VI_ERROR_NPERMISSION         = _to_int(0xBFFF00A8)


#
# Attribute constants
#
# All attribute codes are unsigned long, so no _to_int() is necessary.
#

VI_ATTR_RSRC_CLASS           = 0xBFFF0001
VI_ATTR_RSRC_NAME            = 0xBFFF0002
VI_ATTR_RSRC_IMPL_VERSION    = 0x3FFF0003
VI_ATTR_RSRC_LOCK_STATE      = 0x3FFF0004
VI_ATTR_MAX_QUEUE_LENGTH     = 0x3FFF0005
VI_ATTR_USER_DATA            = 0x3FFF0007
VI_ATTR_FDC_CHNL             = 0x3FFF000D
VI_ATTR_FDC_MODE             = 0x3FFF000F
VI_ATTR_FDC_GEN_SIGNAL_EN    = 0x3FFF0011
VI_ATTR_FDC_USE_PAIR         = 0x3FFF0013
VI_ATTR_SEND_END_EN          = 0x3FFF0016
VI_ATTR_TERMCHAR             = 0x3FFF0018
VI_ATTR_TMO_VALUE            = 0x3FFF001A
VI_ATTR_GPIB_READDR_EN       = 0x3FFF001B
VI_ATTR_IO_PROT              = 0x3FFF001C
VI_ATTR_DMA_ALLOW_EN         = 0x3FFF001E
VI_ATTR_ASRL_BAUD            = 0x3FFF0021
VI_ATTR_ASRL_DATA_BITS       = 0x3FFF0022
VI_ATTR_ASRL_PARITY          = 0x3FFF0023
VI_ATTR_ASRL_STOP_BITS       = 0x3FFF0024
VI_ATTR_ASRL_FLOW_CNTRL      = 0x3FFF0025

VI_ATTR_ASRL_DISCARD_NULL    = 0x3FFF00B0
VI_ATTR_ASRL_CONNECTED       = 0x3FFF01BB
VI_ATTR_ASRL_BREAK_STATE     = 0x3FFF01BC
VI_ATTR_ASRL_BREAK_LEN       = 0x3FFF01BD
VI_ATTR_ASRL_ALLOW_TRANSMIT  = 0x3FFF01BE
VI_ATTR_ASRL_WIRE_MODE       = 0x3FFF01BF

VI_ATTR_RD_BUF_OPER_MODE     = 0x3FFF002A
VI_ATTR_RD_BUF_SIZE          = 0x3FFF002B
VI_ATTR_WR_BUF_OPER_MODE     = 0x3FFF002D
VI_ATTR_WR_BUF_SIZE          = 0x3FFF002E
VI_ATTR_SUPPRESS_END_EN      = 0x3FFF0036
VI_ATTR_TERMCHAR_EN          = 0x3FFF0038
VI_ATTR_DEST_ACCESS_PRIV     = 0x3FFF0039
VI_ATTR_DEST_BYTE_ORDER      = 0x3FFF003A
VI_ATTR_SRC_ACCESS_PRIV      = 0x3FFF003C
VI_ATTR_SRC_BYTE_ORDER       = 0x3FFF003D
VI_ATTR_SRC_INCREMENT        = 0x3FFF0040
VI_ATTR_DEST_INCREMENT       = 0x3FFF0041
VI_ATTR_WIN_ACCESS_PRIV      = 0x3FFF0045
VI_ATTR_WIN_BYTE_ORDER       = 0x3FFF0047
VI_ATTR_GPIB_ATN_STATE       = 0x3FFF0057
VI_ATTR_GPIB_ADDR_STATE      = 0x3FFF005C
VI_ATTR_GPIB_CIC_STATE       = 0x3FFF005E
VI_ATTR_GPIB_NDAC_STATE      = 0x3FFF0062
VI_ATTR_GPIB_SRQ_STATE       = 0x3FFF0067
VI_ATTR_GPIB_SYS_CNTRL_STATE = 0x3FFF0068
VI_ATTR_GPIB_HS488_CBL_LEN   = 0x3FFF0069
VI_ATTR_CMDR_LA              = 0x3FFF006B
VI_ATTR_VXI_DEV_CLASS        = 0x3FFF006C
VI_ATTR_MAINFRAME_LA         = 0x3FFF0070
VI_ATTR_MANF_NAME            = 0xBFFF0072
VI_ATTR_MODEL_NAME           = 0xBFFF0077
VI_ATTR_VXI_VME_INTR_STATUS  = 0x3FFF008B
VI_ATTR_VXI_TRIG_STATUS      = 0x3FFF008D
VI_ATTR_VXI_VME_SYSFAIL_STATE = 0x3FFF0094

VI_ATTR_WIN_BASE_ADDR        = 0x3FFF0098
VI_ATTR_WIN_SIZE             = 0x3FFF009A
VI_ATTR_ASRL_AVAIL_NUM       = 0x3FFF00AC
VI_ATTR_MEM_BASE             = 0x3FFF00AD
VI_ATTR_ASRL_CTS_STATE       = 0x3FFF00AE
VI_ATTR_ASRL_DCD_STATE       = 0x3FFF00AF
VI_ATTR_ASRL_DSR_STATE       = 0x3FFF00B1
VI_ATTR_ASRL_DTR_STATE       = 0x3FFF00B2
VI_ATTR_ASRL_END_IN          = 0x3FFF00B3
VI_ATTR_ASRL_END_OUT         = 0x3FFF00B4
VI_ATTR_ASRL_REPLACE_CHAR    = 0x3FFF00BE
VI_ATTR_ASRL_RI_STATE        = 0x3FFF00BF
VI_ATTR_ASRL_RTS_STATE       = 0x3FFF00C0
VI_ATTR_ASRL_XON_CHAR        = 0x3FFF00C1
VI_ATTR_ASRL_XOFF_CHAR       = 0x3FFF00C2
VI_ATTR_WIN_ACCESS           = 0x3FFF00C3
VI_ATTR_RM_SESSION           = 0x3FFF00C4
VI_ATTR_VXI_LA               = 0x3FFF00D5
VI_ATTR_MANF_ID              = 0x3FFF00D9
VI_ATTR_MEM_SIZE             = 0x3FFF00DD
VI_ATTR_MEM_SPACE            = 0x3FFF00DE
VI_ATTR_MODEL_CODE           = 0x3FFF00DF
VI_ATTR_SLOT                 = 0x3FFF00E8
VI_ATTR_INTF_INST_NAME       = 0xBFFF00E9
VI_ATTR_IMMEDIATE_SERV       = 0x3FFF0100
VI_ATTR_INTF_PARENT_NUM      = 0x3FFF0101
VI_ATTR_RSRC_SPEC_VERSION    = 0x3FFF0170
VI_ATTR_INTF_TYPE            = 0x3FFF0171
VI_ATTR_GPIB_PRIMARY_ADDR    = 0x3FFF0172
VI_ATTR_GPIB_SECONDARY_ADDR  = 0x3FFF0173
VI_ATTR_RSRC_MANF_NAME       = 0xBFFF0174
VI_ATTR_RSRC_MANF_ID         = 0x3FFF0175
VI_ATTR_INTF_NUM             = 0x3FFF0176
VI_ATTR_TRIG_ID              = 0x3FFF0177
VI_ATTR_GPIB_REN_STATE       = 0x3FFF0181
VI_ATTR_GPIB_UNADDR_EN       = 0x3FFF0184
VI_ATTR_DEV_STATUS_BYTE      = 0x3FFF0189
VI_ATTR_FILE_APPEND_EN       = 0x3FFF0192
VI_ATTR_VXI_TRIG_SUPPORT     = 0x3FFF0194
VI_ATTR_TCPIP_ADDR           = 0xBFFF0195
VI_ATTR_TCPIP_HOSTNAME       = 0xBFFF0196
VI_ATTR_TCPIP_PORT           = 0x3FFF0197
VI_ATTR_TCPIP_DEVICE_NAME    = 0xBFFF0199
VI_ATTR_TCPIP_NODELAY        = 0x3FFF019A
VI_ATTR_TCPIP_KEEPALIVE      = 0x3FFF019B
VI_ATTR_4882_COMPLIANT       = 0x3FFF019F
VI_ATTR_USB_SERIAL_NUM       = 0xBFFF01A0
VI_ATTR_USB_INTFC_NUM        = 0x3FFF01A1
VI_ATTR_USB_PROTOCOL         = 0x3FFF01A7
VI_ATTR_USB_MAX_INTR_SIZE    = 0x3FFF01AF

VI_ATTR_JOB_ID               = 0x3FFF4006
VI_ATTR_EVENT_TYPE           = 0x3FFF4010
VI_ATTR_SIGP_STATUS_ID       = 0x3FFF4011
VI_ATTR_RECV_TRIG_ID         = 0x3FFF4012
VI_ATTR_INTR_STATUS_ID       = 0x3FFF4023
VI_ATTR_STATUS               = 0x3FFF4025
VI_ATTR_RET_COUNT            = 0x3FFF4026
VI_ATTR_BUFFER               = 0x3FFF4027
VI_ATTR_RECV_INTR_LEVEL      = 0x3FFF4041
VI_ATTR_OPER_NAME            = 0xBFFF4042
VI_ATTR_GPIB_RECV_CIC_STATE  = 0x3FFF4193
VI_ATTR_RECV_TCPIP_ADDR      = 0xBFFF4198
VI_ATTR_USB_RECV_INTR_SIZE   = 0x3FFF41B0
VI_ATTR_USB_RECV_INTR_DATA   = 0xBFFF41B1


VI_ATTR_VXI_TRIG_DIR        = _to_int(0x3FFF4044)
VI_ATTR_VXI_TRIG_LINES_EN   = _to_int(0x3FFF4043)

#
# Event Types
#
# All event codes are unsigned long, so no _to_int() is necessary.
#

VI_EVENT_IO_COMPLETION       = 0x3FFF2009
VI_EVENT_TRIG                = 0xBFFF200A
VI_EVENT_SERVICE_REQ         = 0x3FFF200B
VI_EVENT_CLEAR               = 0x3FFF200D
VI_EVENT_EXCEPTION           = 0xBFFF200E
VI_EVENT_GPIB_CIC            = 0x3FFF2012
VI_EVENT_GPIB_TALK           = 0x3FFF2013
VI_EVENT_GPIB_LISTEN         = 0x3FFF2014
VI_EVENT_VXI_VME_SYSFAIL     = 0x3FFF201D
VI_EVENT_VXI_VME_SYSRESET    = 0x3FFF201E
VI_EVENT_VXI_SIGP            = 0x3FFF2020
VI_EVENT_VXI_VME_INTR        = 0xBFFF2021
VI_EVENT_PXI_INTR            = 0x3FFF2022
VI_EVENT_TCPIP_CONNECT       = 0x3FFF2036
VI_EVENT_USB_INTR            = 0x3FFF2037

VI_ALL_ENABLED_EVENTS        = 0x3FFF7FFF


#
# Values and Ranges
#

VI_FIND_BUFLEN               = 256
VI_NULL                      = 0

VI_TRUE                      = 1
VI_FALSE                     = 0

VI_INTF_GPIB                 = 1
VI_INTF_VXI                  = 2
VI_INTF_GPIB_VXI             = 3
VI_INTF_ASRL                 = 4
VI_INTF_PXI                  = 5
VI_INTF_TCPIP                = 6
VI_INTF_USB                  = 7
VI_INTF_RIO                  = 8
VI_INTF_FIREWIRE             = 9

VI_PROT_NORMAL               = 1
VI_PROT_FDC                  = 2
VI_PROT_HS488                = 3
VI_PROT_4882_STRS            = 4
VI_PROT_USBTMC_VENDOR        = 5

VI_FDC_NORMAL                = 1
VI_FDC_STREAM                = 2

VI_LOCAL_SPACE               = 0
VI_A16_SPACE                 = 1
VI_A24_SPACE                 = 2
VI_A32_SPACE                 = 3
VI_OPAQUE_SPACE              = 0xFFFF

VI_UNKNOWN_LA                = -1
VI_UNKNOWN_SLOT              = -1
VI_UNKNOWN_LEVEL             = -1

VI_QUEUE                     = 1
VI_HNDLR                     = 2
VI_SUSPEND_HNDLR             = 4
VI_ALL_MECH                  = 0xFFFF

VI_ANY_HNDLR                 = 0

VI_TRIG_ALL                  = -2
VI_TRIG_SW                   = -1
VI_TRIG_TTL0                 = 0
VI_TRIG_TTL1                 = 1
VI_TRIG_TTL2                 = 2
VI_TRIG_TTL3                 = 3
VI_TRIG_TTL4                 = 4
VI_TRIG_TTL5                 = 5
VI_TRIG_TTL6                 = 6
VI_TRIG_TTL7                 = 7
VI_TRIG_ECL0                 = 8
VI_TRIG_ECL1                 = 9
VI_TRIG_PANEL_IN             = 27
VI_TRIG_PANEL_OUT            = 28

VI_TRIG_PROT_DEFAULT         = 0
VI_TRIG_PROT_ON              = 1
VI_TRIG_PROT_OFF             = 2
VI_TRIG_PROT_SYNC            = 5

VI_READ_BUF                  = 1
VI_WRITE_BUF                 = 2
VI_READ_BUF_DISCARD          = 4
VI_WRITE_BUF_DISCARD         = 8
VI_IO_IN_BUF                 = 16
VI_IO_OUT_BUF                = 32
VI_IO_IN_BUF_DISCARD         = 64
VI_IO_OUT_BUF_DISCARD        = 128

VI_FLUSH_ON_ACCESS           = 1
VI_FLUSH_WHEN_FULL           = 2
VI_FLUSH_DISABLE             = 3

VI_NMAPPED                   = 1
VI_USE_OPERS                 = 2
VI_DEREF_ADDR                = 3

VI_TMO_IMMEDIATE             = 0
# Attention! The following is *really* positive!  (unsigned long)
VI_TMO_INFINITE              = 0xFFFFFFFF

VI_NO_LOCK                   = 0
VI_EXCLUSIVE_LOCK            = 1
VI_SHARED_LOCK               = 2
VI_LOAD_CONFIG               = 4

VI_NO_SEC_ADDR               = 0xFFFF

VI_ASRL_PAR_NONE             = 0
VI_ASRL_PAR_ODD              = 1
VI_ASRL_PAR_EVEN             = 2
VI_ASRL_PAR_MARK             = 3
VI_ASRL_PAR_SPACE            = 4

VI_ASRL_STOP_ONE             = 10
VI_ASRL_STOP_ONE5            = 15
VI_ASRL_STOP_TWO             = 20

VI_ASRL_FLOW_NONE            = 0
VI_ASRL_FLOW_XON_XOFF        = 1
VI_ASRL_FLOW_RTS_CTS         = 2
VI_ASRL_FLOW_DTR_DSR         = 4

VI_ASRL_END_NONE             = 0
VI_ASRL_END_LAST_BIT         = 1
VI_ASRL_END_TERMCHAR         = 2
VI_ASRL_END_BREAK            = 3

VI_STATE_ASSERTED            = 1
VI_STATE_UNASSERTED          = 0
VI_STATE_UNKNOWN             = -1

VI_BIG_ENDIAN                = 0
VI_LITTLE_ENDIAN             = 1

VI_DATA_PRIV                 = 0
VI_DATA_NPRIV                = 1
VI_PROG_PRIV                 = 2
VI_PROG_NPRIV                = 3
VI_BLCK_PRIV                 = 4
VI_BLCK_NPRIV                = 5
VI_D64_PRIV                  = 6
VI_D64_NPRIV                 = 7

VI_WIDTH_8                   = 1
VI_WIDTH_16                  = 2
VI_WIDTH_32                  = 4

VI_GPIB_REN_DEASSERT         = 0
VI_GPIB_REN_ASSERT           = 1
VI_GPIB_REN_DEASSERT_GTL     = 2
VI_GPIB_REN_ASSERT_ADDRESS   = 3
VI_GPIB_REN_ASSERT_LLO       = 4
VI_GPIB_REN_ASSERT_ADDRESS_LLO = 5
VI_GPIB_REN_ADDRESS_GTL      = 6

VI_GPIB_ATN_DEASSERT         = 0
VI_GPIB_ATN_ASSERT           = 1
VI_GPIB_ATN_DEASSERT_HANDSHAKE = 2
VI_GPIB_ATN_ASSERT_IMMEDIATE = 3

VI_GPIB_HS488_DISABLED       = 0
VI_GPIB_HS488_NIMPL          = -1

VI_GPIB_UNADDRESSED          = 0
VI_GPIB_TALKER               = 1
VI_GPIB_LISTENER             = 2

VI_VXI_CMD16                 = 0x0200
VI_VXI_CMD16_RESP16          = 0x0202
VI_VXI_RESP16                = 0x0002
VI_VXI_CMD32                 = 0x0400
VI_VXI_CMD32_RESP16          = 0x0402
VI_VXI_CMD32_RESP32          = 0x0404
VI_VXI_RESP32                = 0x0004

VI_ASSERT_SIGNAL             = -1
VI_ASSERT_USE_ASSIGNED       = 0
VI_ASSERT_IRQ1               = 1
VI_ASSERT_IRQ2               = 2
VI_ASSERT_IRQ3               = 3
VI_ASSERT_IRQ4               = 4
VI_ASSERT_IRQ5               = 5
VI_ASSERT_IRQ6               = 6
VI_ASSERT_IRQ7               = 7

VI_UTIL_ASSERT_SYSRESET      = 1
VI_UTIL_ASSERT_SYSFAIL       = 2
VI_UTIL_DEASSERT_SYSFAIL     = 3

VI_VXI_CLASS_MEMORY          = 0
VI_VXI_CLASS_EXTENDED        = 1
VI_VXI_CLASS_MESSAGE         = 2
VI_VXI_CLASS_REGISTER        = 3
VI_VXI_CLASS_OTHER           = 4

VI_PXI_LBUS_UNKNOWN = -1
VI_PXI_LBUS_NONE    =  0
VI_PXI_LBUS_STAR_TRIG_BUS_0 = 1000
VI_PXI_LBUS_STAR_TRIG_BUS_1 = 1001
VI_PXI_LBUS_STAR_TRIG_BUS_2 = 1002
VI_PXI_LBUS_STAR_TRIG_BUS_3 = 1003
VI_PXI_LBUS_STAR_TRIG_BUS_4 = 1004
VI_PXI_LBUS_STAR_TRIG_BUS_5 = 1005
VI_PXI_LBUS_STAR_TRIG_BUS_6 = 1006
VI_PXI_LBUS_STAR_TRIG_BUS_7 = 1007
VI_PXI_LBUS_STAR_TRIG_BUS_8 = 1008
VI_PXI_LBUS_STAR_TRIG_BUS_9 = 1009
VI_PXI_STAR_TRIG_CONTROLLER = 1413
VI_PXI_LBUS_SCXI = 2000

VI_ATTR_PXI_DEV_NUM         = _to_int(0x3FFF0201)
VI_ATTR_PXI_FUNC_NUM        = _to_int(0x3FFF0202)
VI_ATTR_PXI_BUS_NUM         = _to_int(0x3FFF0205)
VI_ATTR_PXI_CHASSIS         = _to_int(0x3FFF0206)
VI_ATTR_PXI_SLOTPATH        = _to_int(0xBFFF0207)
VI_ATTR_PXI_SLOT_LBUS_LEFT  = _to_int(0x3FFF0208)
VI_ATTR_PXI_SLOT_LBUS_RIGHT = _to_int(0x3FFF0209)
VI_ATTR_PXI_TRIG_BUS        = _to_int(0x3FFF020A)
VI_ATTR_PXI_STAR_TRIG_BUS   = _to_int(0x3FFF020B)
VI_ATTR_PXI_STAR_TRIG_LINE  = _to_int(0x3FFF020C)

VI_ATTR_PXI_MEM_TYPE_BAR0   = _to_int(0x3FFF0211)
VI_ATTR_PXI_MEM_TYPE_BAR1   = _to_int(0x3FFF0212)
VI_ATTR_PXI_MEM_TYPE_BAR2   = _to_int(0x3FFF0213)
VI_ATTR_PXI_MEM_TYPE_BAR3   = _to_int(0x3FFF0214)
VI_ATTR_PXI_MEM_TYPE_BAR4   = _to_int(0x3FFF0215)
VI_ATTR_PXI_MEM_TYPE_BAR5   = _to_int(0x3FFF0216)
VI_ATTR_PXI_MEM_BASE_BAR0   = _to_int(0x3FFF0221)
VI_ATTR_PXI_MEM_BASE_BAR1   = _to_int(0x3FFF0222)
VI_ATTR_PXI_MEM_BASE_BAR2   = _to_int(0x3FFF0223)
VI_ATTR_PXI_MEM_BASE_BAR3   = _to_int(0x3FFF0224)
VI_ATTR_PXI_MEM_BASE_BAR4   = _to_int(0x3FFF0225)
VI_ATTR_PXI_MEM_BASE_BAR5   = _to_int(0x3FFF0226)
VI_ATTR_PXI_MEM_SIZE_BAR0   = _to_int(0x3FFF0231)
VI_ATTR_PXI_MEM_SIZE_BAR1   = _to_int(0x3FFF0232)
VI_ATTR_PXI_MEM_SIZE_BAR2   = _to_int(0x3FFF0233)
VI_ATTR_PXI_MEM_SIZE_BAR3   = _to_int(0x3FFF0234)
VI_ATTR_PXI_MEM_SIZE_BAR4   = _to_int(0x3FFF0235)
VI_ATTR_PXI_MEM_SIZE_BAR5   = _to_int(0x3FFF0236)
VI_ATTR_PXI_IS_EXPRESS      = _to_int(0x3FFF0240)
VI_ATTR_PXI_SLOT_LWIDTH     = _to_int(0x3FFF0241)
VI_ATTR_PXI_MAX_LWIDTH      = _to_int(0x3FFF0242)
VI_ATTR_PXI_ACTUAL_LWIDTH   = _to_int(0x3FFF0243)
VI_ATTR_PXI_DSTAR_BUS       = _to_int(0x3FFF0244)
VI_ATTR_PXI_DSTAR_SET       = _to_int(0x3FFF0245)

VI_ATTR_PXI_SRC_TRIG_BUS    = _to_int(0x3FFF020D)
VI_ATTR_PXI_DEST_TRIG_BUS   = _to_int(0x3FFF020E)

VI_ATTR_PXI_RECV_INTR_SEQ   = _to_int(0x3FFF4240)
VI_ATTR_PXI_RECV_INTR_DATA  = _to_int(0x3FFF4241)

# TODO: What is the value
VI_ATTR_PXI_MEM_BASE_BARX = None
VI_ATTR_PXI_MEM_SIZE_BARX = None
VI_ATTR_PXI_MEM_TYPE_BARX = None


VI_ATTR_USB_BULK_OUT_PIPE = _to_int(0x3FFF01A2)
VI_ATTR_USB_BULK_IN_PIPE = _to_int(0x3FFF01A3)
VI_ATTR_USB_INTR_IN_PIPE = _to_int(0x3FFF01A4)
VI_ATTR_USB_CLASS = _to_int(0x3FFF01A5)
VI_ATTR_USB_SUBCLASS = _to_int(0x3FFF01A6)
VI_ATTR_USB_ALT_SETTING = _to_int(0x3FFF01A8)
VI_ATTR_USB_END_IN = _to_int(0x3FFF01A9)
VI_ATTR_USB_NUM_INTFCS = _to_int(0x3FFF01AA)
VI_ATTR_USB_NUM_PIPES = _to_int(0x3FFF01AB)
VI_ATTR_USB_BULK_OUT_STATUS = _to_int(0x3FFF01AC)
VI_ATTR_USB_BULK_IN_STATUS = _to_int(0x3FFF01AD)
VI_ATTR_USB_INTR_IN_STATUS = _to_int(0x3FFF01AE)
VI_ATTR_USB_CTRL_PIPE = _to_int(0x3FFF01B0)
VI_USB_PIPE_STATE_UNKNOWN = -1
VI_USB_PIPE_READY = 0
VI_USB_PIPE_STALLED = 1


# From VI_ATTR_USB_END_IN
VI_USB_END_NONE             = 0
VI_USB_END_SHORT            = 4
VI_USB_END_SHORT_OR_COUNT   = 5

# "Backwards compatibility" according to NI

VI_NORMAL                    = VI_PROT_NORMAL
VI_FDC                       = VI_PROT_FDC
VI_HS488                     = VI_PROT_HS488
VI_ASRL488                   = VI_PROT_4882_STRS
VI_ASRL_IN_BUF               = VI_IO_IN_BUF
VI_ASRL_OUT_BUF              = VI_IO_OUT_BUF
VI_ASRL_IN_BUF_DISCARD       = VI_IO_IN_BUF_DISCARD
VI_ASRL_OUT_BUF_DISCARD      = VI_IO_OUT_BUF_DISCARD


# Enums

@enum.unique
class AccessModes(enum.IntEnum):

    #: Does not obtain any lock on the VISA resource.
    no_lock = 0

    #: Obtains a exclusive lock on the VISA resource.
    exclusive_lock = 1

    #: Obtains a lock on the VISA resouce which may be shared
    #: between multiple VISA sessions.
    shared_lock = 2


@enum.unique
class StopBits(enum.IntEnum):
    """The number of stop bits that indicate the end of a frame.
    """
    one = VI_ASRL_STOP_ONE
    one_and_a_half = VI_ASRL_STOP_ONE5
    two = VI_ASRL_STOP_TWO


@enum.unique
class Parity(enum.IntEnum):
    """The parity types to use with every frame transmitted and received on a serial session.
    """
    none = VI_ASRL_PAR_NONE
    odd = VI_ASRL_PAR_ODD
    even = VI_ASRL_PAR_EVEN
    mark = VI_ASRL_PAR_MARK
    space = VI_ASRL_PAR_SPACE


@enum.unique
class SerialTermination(enum.IntEnum):
    """The available methods for terminating a serial transfer.
    """

    #: The transfer terminates when all requested data is transferred
    #: or when an error occurs.
    none = VI_ASRL_END_NONE

    #: The transfer occurs with the last bit not set until the last
    #: character is sent.
    last_bit = VI_ASRL_END_LAST_BIT

    #: The transfer terminate by searching for "/"
    #: appending the termination character.
    termination_char = VI_ASRL_END_TERMCHAR

    #: The write transmits a break after all the characters for the
    #: write are sent.
    termination_break = VI_ASRL_END_BREAK


@enum.unique
class InterfaceType(enum.IntEnum):
    """The hardware interface
    """

    # Used for unknown interface type strings.
    unknown = -1

    #: GPIB Interface.
    gpib = VI_INTF_GPIB

    #: VXI (VME eXtensions for Instrumentation), VME, MXI (Multisystem eXtension Interface).
    vxi = VI_INTF_VXI

    #: GPIB VXI (VME eXtensions for Instrumentation).
    gpib_vxi = VI_INTF_GPIB_VXI

    #: Serial devices connected to either an RS-232 or RS-485 controller.
    asrl = VI_INTF_ASRL

    #: PXI device.
    pxi = VI_INTF_PXI

    #: TCPIP device.
    tcpip = VI_INTF_TCPIP

    #: Universal Serial Bus (USB) hardware bus.
    usb = VI_INTF_USB

    #: Rio device.
    rio = VI_INTF_RIO

    #: Firewire device.
    firewire = VI_INTF_FIREWIRE

    #: Rohde and Schwarz Device via Passport
    rsnrp = 33024


@enum.unique
class AddressState(enum.IntEnum):

    unaddressed = VI_GPIB_UNADDRESSED
    talker = VI_GPIB_TALKER
    listenr = VI_GPIB_LISTENER


@enum.unique
class IOProtocol(enum.IntEnum):

    normal = VI_PROT_NORMAL

    #: Fast data channel (FDC) protocol for VXI
    fdc = VI_PROT_FDC

    #: High speed 488 transfer for GPIB
    hs488 = VI_PROT_HS488

    #: 488 style transfer for serial
    protocol4882_strs = VI_PROT_4882_STRS

    #: Test measurement class vendor specific for USB
    usbtmc_vendor = VI_PROT_USBTMC_VENDOR


@enum.unique
class LineState(enum.IntEnum):

    asserted = VI_STATE_ASSERTED
    unasserted = VI_STATE_UNASSERTED
    unknown = VI_STATE_UNKNOWN


@enum.unique
class EventMechanism(enum.IntEnum):
    """The available event mechanisms for event handling.
    """

    queue = VI_QUEUE
    handler = VI_HNDLR

    #: events queued but handler not called
    suspend_handler = VI_SUSPEND_HNDLR

    all = VI_ALL_MECH


# Note that enum.IntEnum fails here for python2:
#  OverflowError: Python int too large to convert to C long
# so use LongEnum instead (some values are too large, and ViEventType is unsigned)
@enum.unique
class EventType(LongEnum):
    """The available event types for event handling.
    """

    io_completion = VI_EVENT_IO_COMPLETION
    trig = VI_EVENT_TRIG
    service_request = VI_EVENT_SERVICE_REQ
    clear = VI_EVENT_CLEAR
    exception = VI_EVENT_EXCEPTION
    gpib_controller_in_charge = VI_EVENT_GPIB_CIC
    gpib_talk = VI_EVENT_GPIB_TALK
    gpib_listen = VI_EVENT_GPIB_LISTEN
    vxi_vme_sysfail = VI_EVENT_VXI_VME_SYSFAIL
    vxi_vme_sysreset = VI_EVENT_VXI_VME_SYSRESET
    vxi_signal_interrupt = VI_EVENT_VXI_SIGP
    vxi_vme_interrupt = VI_EVENT_VXI_VME_INTR
    pxi_interrupt = VI_EVENT_PXI_INTR
    tcpip_connect = VI_EVENT_TCPIP_CONNECT
    usb_interrupt = VI_EVENT_USB_INTR
    all_enabled = VI_ALL_ENABLED_EVENTS


@enum.unique
class StatusCode(enum.IntEnum):
    """Specifies the status codes that NI-VISA driver-level operations can return.
    """

    #: The operation was aborted.
    error_abort = VI_ERROR_ABORT

    #: Insufficient system resources to perform necessary memory allocation.
    error_allocation = VI_ERROR_ALLOC

    #: The specified attribute is read-only.
    error_attribute_read_only = VI_ERROR_ATTR_READONLY

    #: Bus error occurred during transfer.
    error_bus_error = VI_ERROR_BERR

    #: Unable to deallocate the previously allocated data structures corresponding to this session or object reference.
    error_closing_failed = VI_ERROR_CLOSING_FAILED

    #: The connection for the specified session has been lost.
    error_connection_lost = VI_ERROR_CONN_LOST

    #: An error occurred while trying to open the specified file. Possible causes include an invalid path or lack of access rights.
    error_file_access = VI_ERROR_FILE_ACCESS

    #: An error occurred while performing I/O on the specified file.
    error_file_i_o = VI_ERROR_FILE_IO

    #: A handler is not currently installed for the specified event.
    error_handler_not_installed = VI_ERROR_HNDLR_NINSTALLED

    #: Unable to queue the asynchronous operation because there is already an operation in progress.
    error_in_progress = VI_ERROR_IN_PROGRESS

    #: Device reported an input protocol error during transfer.
    error_input_protocol_violation = VI_ERROR_INP_PROT_VIOL

    #: The interface type is valid but the specified interface number is not configured.
    error_interface_number_not_configured = VI_ERROR_INTF_NUM_NCONFIG

    #: An interrupt is still pending from a previous call.
    error_interrupt_pending = VI_ERROR_INTR_PENDING

    #: The access key to the resource associated with this session is invalid.
    error_invalid_access_key = VI_ERROR_INV_ACCESS_KEY

    #: Invalid access mode.
    error_invalid_access_mode = VI_ERROR_INV_ACC_MODE

    #: Invalid address space specified.
    error_invalid_address_space = VI_ERROR_INV_SPACE

    #: Specified event context is invalid.
    error_invalid_context = VI_ERROR_INV_CONTEXT

    #: Specified degree is invalid.
    error_invalid_degree = VI_ERROR_INV_DEGREE

    #: Specified event type is not supported by the resource.
    error_invalid_event = VI_ERROR_INV_EVENT

    #: Invalid expression specified for search.
    error_invalid_expression = VI_ERROR_INV_EXPR

    #: A format specifier in the format string is invalid.
    error_invalid_format = VI_ERROR_INV_FMT

    #: The specified handler reference is invalid.
    error_invalid_handler_reference = VI_ERROR_INV_HNDLR_REF

    #: Specified job identifier is invalid.
    error_invalid_job_i_d = VI_ERROR_INV_JOB_ID

    #: Invalid length specified.
    error_invalid_length = VI_ERROR_INV_LENGTH

    #: The value specified by the line parameter is invalid.
    error_invalid_line = VI_ERROR_INV_LINE

    #: The specified type of lock is not supported by this resource.
    error_invalid_lock_type = VI_ERROR_INV_LOCK_TYPE

    #: Invalid buffer mask specified.
    error_invalid_mask = VI_ERROR_INV_MASK

    #: Invalid mechanism specified.
    error_invalid_mechanism = VI_ERROR_INV_MECH

    #: The specified mode is invalid.
    error_invalid_mode = VI_ERROR_INV_MODE

    #: The specified session or object reference is invalid.
    error_invalid_object = VI_ERROR_INV_OBJECT

    #: Invalid offset specified.
    error_invalid_offset = VI_ERROR_INV_OFFSET

    #: The value of an unknown parameter is invalid.
    error_invalid_parameter = VI_ERROR_INV_PARAMETER

    #: The protocol specified is invalid.
    error_invalid_protocol = VI_ERROR_INV_PROT

    #: Invalid resource reference specified. Parsing error.
    error_invalid_resource_name = VI_ERROR_INV_RSRC_NAME

    #: Unable to start operation because setup is invalid due to inconsistent state of properties.
    error_invalid_setup = VI_ERROR_INV_SETUP

    #: Invalid size of window specified.
    error_invalid_size = VI_ERROR_INV_SIZE

    #: Invalid source or destination width specified.
    error_invalid_width = VI_ERROR_INV_WIDTH

    #: Could not perform operation because of I/O error.
    error_io = VI_ERROR_IO

    #: A code library required by VISA could not be located or loaded.
    error_library_not_found = VI_ERROR_LIBRARY_NFOUND

    #: The specified trigger line is currently in use.
    error_line_in_use = VI_ERROR_LINE_IN_USE

    #: The remote machine does not exist or is not accepting any connections.
    error_machine_not_available = VI_ERROR_MACHINE_NAVAIL

    #: The device does not export any memory.
    error_memory_not_shared = VI_ERROR_MEM_NSHARED

    #: No listeners condition is detected (both NRFD and NDAC are deasserted).
    error_no_listeners = VI_ERROR_NLISTENERS

    #: The specified operation is unimplemented.
    error_nonimplemented_operation = VI_ERROR_NIMPL_OPER

    #: The specified attribute is not defined or supported by the referenced session, event, or find list.
    error_nonsupported_attribute = VI_ERROR_NSUP_ATTR

    #: The specified state of the attribute is not valid or is not supported as defined by the session, event, or find list.
    error_nonsupported_attribute_state = VI_ERROR_NSUP_ATTR_STATE

    #: A format specifier in the format string is not supported.
    error_nonsupported_format = VI_ERROR_NSUP_FMT

    #: The interface cannot generate an interrupt on the requested level or with the requested statusID value.
    error_nonsupported_interrupt = VI_ERROR_NSUP_INTR

    #: The specified trigger source line (trigSrc) or destination line (trigDest) is not supported by this VISA implementation, or the combination of lines is not a valid mapping.
    error_nonsupported_line = VI_ERROR_NSUP_LINE

    #: The specified mechanism is not supported for the specified event type.
    error_nonsupported_mechanism = VI_ERROR_NSUP_MECH

    #: The specified mode is not supported by this VISA implementation.
    error_nonsupported_mode = VI_ERROR_NSUP_MODE

    #: Specified offset is not accessible from this hardware.
    error_nonsupported_offset = VI_ERROR_NSUP_OFFSET

    #: The specified offset is not properly aligned for the access width of the operation.
    error_nonsupported_offset_alignment = VI_ERROR_NSUP_ALIGN_OFFSET

    #: The session or object reference does not support this operation.
    error_nonsupported_operation = VI_ERROR_NSUP_OPER

    #: Cannot support source and destination widths that are different.
    error_nonsupported_varying_widths = VI_ERROR_NSUP_VAR_WIDTH

    #: Specified width is not supported by this hardware.
    error_nonsupported_width = VI_ERROR_NSUP_WIDTH

    #: Access to the remote machine is denied.
    error_no_permission = VI_ERROR_NPERMISSION

    #: The interface associated with this session is not currently the Controller-in-Charge.
    error_not_cic = VI_ERROR_NCIC

    #: The session must be enabled for events of the specified type in order to receive them.
    error_not_enabled = VI_ERROR_NENABLED

    #: The interface associated with this session is not the system controller.
    error_not_system_controller = VI_ERROR_NSYS_CNTLR

    #: Device reported an output protocol error during transfer.
    error_output_protocol_violation = VI_ERROR_OUTP_PROT_VIOL

    #: Unable to queue asynchronous operation.
    error_queue_error = VI_ERROR_QUEUE_ERROR

    #: The event queue for the specified type has overflowed, usually due to not closing previous events.
    error_queue_overflow = VI_ERROR_QUEUE_OVERFLOW

    #: Violation of raw read protocol occurred during transfer.
    error_raw_read_protocol_violation = VI_ERROR_RAW_RD_PROT_VIOL

    #: Violation of raw write protocol occurred during transfer.
    error_raw_write_protocol_violation = VI_ERROR_RAW_WR_PROT_VIOL

    #: The resource is valid, but VISA cannot currently access it.
    error_resource_busy = VI_ERROR_RSRC_BUSY

    #: Specified type of lock cannot be obtained or specified operation cannot be performed because the resource is locked.
    error_resource_locked = VI_ERROR_RSRC_LOCKED

    #: Insufficient location information, or the device or resource is not present in the system.
    error_resource_not_found = VI_ERROR_RSRC_NFOUND

    #: A previous response is still pending, causing a multiple query error.
    error_response_pending = VI_ERROR_RESP_PENDING

    #: A framing error occurred during transfer.
    error_serial_framing = VI_ERROR_ASRL_FRAMING

    #: An overrun error occurred during transfer. A character was not read from the hardware before the next character arrived.
    error_serial_overrun = VI_ERROR_ASRL_OVERRUN

    #: A parity error occurred during transfer.
    error_serial_parity = VI_ERROR_ASRL_PARITY

    #: The current session did not have any lock on the resource.
    error_session_not_locked = VI_ERROR_SESN_NLOCKED

    #: Service request has not been received for the session.
    error_srq_not_occurred = VI_ERROR_SRQ_NOCCURRED

    #: Unknown system error.
    error_system_error = VI_ERROR_SYSTEM_ERROR

    #: Timeout expired before operation completed.
    error_timeout = VI_ERROR_TMO

    #: The path from the trigger source line (trigSrc) to the destination line (trigDest) is not currently mapped.
    error_trigger_not_mapped = VI_ERROR_TRIG_NMAPPED

    #: A specified user buffer is not valid or cannot be accessed for the required size.
    error_user_buffer = VI_ERROR_USER_BUF

    #: The specified session currently contains a mapped window.
    error_window_already_mapped = VI_ERROR_WINDOW_MAPPED

    #: The specified session is currently unmapped.
    error_window_not_mapped = VI_ERROR_WINDOW_NMAPPED

    #: Operation completed successfully.
    success = VI_SUCCESS

    #: Session opened successfully, but the device at the specified address is not responding.
    success_device_not_present = VI_SUCCESS_DEV_NPRESENT

    #: Specified event is already disabled for at least one of the specified mechanisms.
    success_event_already_disabled = VI_SUCCESS_EVENT_DIS

    #: Specified event is already enabled for at least one of the specified mechanisms.
    success_event_already_enabled = VI_SUCCESS_EVENT_EN

    #: The number of bytes read is equal to the input count.
    success_max_count_read = VI_SUCCESS_MAX_CNT

    #: Operation completed successfully, and this session has nested exclusive locks.
    success_nested_exclusive = VI_SUCCESS_NESTED_EXCLUSIVE

    #: Operation completed successfully, and this session has nested shared locks.
    success_nested_shared = VI_SUCCESS_NESTED_SHARED

    #: Event handled successfully. Do not invoke any other handlers on this session for this event.
    success_no_more_handler_calls_in_chain = VI_SUCCESS_NCHAIN

    #: Operation completed successfully, but the queue was already empty.
    success_queue_already_empty = VI_SUCCESS_QUEUE_EMPTY

    #: Wait terminated successfully on receipt of an event notification. There is still at least one more event occurrence of the requested type(s) available for this session.
    success_queue_not_empty = VI_SUCCESS_QUEUE_NEMPTY

    #: Asynchronous operation request was performed synchronously.
    success_syncronous = VI_SUCCESS_SYNC

    #: The specified termination character was read.
    success_termination_character_read = VI_SUCCESS_TERM_CHAR

    #: The path from the trigger source line (trigSrc) to the destination line (trigDest) is already mapped.
    success_trigger_already_mapped = VI_SUCCESS_TRIG_MAPPED

    #: The specified configuration either does not exist or could not be loaded. The VISA-specified defaults are used.
    warning_configuration_not_loaded = VI_WARN_CONFIG_NLOADED

    #: The operation succeeded, but a lower level driver did not implement the extended functionality.
    warning_ext_function_not_implemented = VI_WARN_EXT_FUNC_NIMPL

    #: Although the specified state of the attribute is valid, it is not supported by this resource implementation.
    warning_nonsupported_attribute_state = VI_WARN_NSUP_ATTR_STATE

    #: The specified buffer is not supported.
    warning_nonsupported_buffer = VI_WARN_NSUP_BUF

    #: The specified object reference is uninitialized.
    warning_null_object = VI_WARN_NULL_OBJECT

    #: VISA received more event information of the specified type than the configured queue size could hold.
    warning_queue_overflow = VI_WARN_QUEUE_OVERFLOW

    #: The status code passed to the operation could not be interpreted.
    warning_unknown_status = VI_WARN_UNKNOWN_STATUS
