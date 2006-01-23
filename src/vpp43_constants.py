#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43_constants.py - VISA VPP-4.3 constants (VPP-4.3.2 spec, section 3)
#
#    Copyright © 2005, 2006 Torsten Bronger <bronger@physik.rwth-aachen.de>,
#                           Gregor Thalhammer <gth@users.sourceforge.net>.
#
#    This file is part of PyVISA.
#
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    PyVISA is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with PyVISA; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

"""Makes all "completion and error codes", "attribute values", "event type
values", and "values and ranges" defined in the VISA specification VPP-4.3.2,
section 3, available as variable values.

The module exports the values under the original, all-uppercase names.

"""

__version__ = "$Revision$"
# $Source$


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
    if x > 0x7FFFFFFFL:
        return int(x - 0x100000000L)
    else:
        return int(x)

VI_SUCCESS                   = _to_int(0x00000000L)
VI_SUCCESS_EVENT_EN          = _to_int(0x3FFF0002L)
VI_SUCCESS_EVENT_DIS         = _to_int(0x3FFF0003L)
VI_SUCCESS_QUEUE_EMPTY       = _to_int(0x3FFF0004L)
VI_SUCCESS_TERM_CHAR         = _to_int(0x3FFF0005L)
VI_SUCCESS_MAX_CNT           = _to_int(0x3FFF0006L)
VI_SUCCESS_DEV_NPRESENT      = _to_int(0x3FFF007DL)
VI_SUCCESS_TRIG_MAPPED       = _to_int(0x3FFF007EL)
VI_SUCCESS_QUEUE_NEMPTY      = _to_int(0x3FFF0080L)
VI_SUCCESS_NCHAIN            = _to_int(0x3FFF0098L)
VI_SUCCESS_NESTED_SHARED     = _to_int(0x3FFF0099L)
VI_SUCCESS_NESTED_EXCLUSIVE  = _to_int(0x3FFF009AL)
VI_SUCCESS_SYNC              = _to_int(0x3FFF009BL)

VI_WARN_QUEUE_OVERFLOW       = _to_int(0x3FFF000CL)
VI_WARN_CONFIG_NLOADED       = _to_int(0x3FFF0077L)
VI_WARN_NULL_OBJECT          = _to_int(0x3FFF0082L)
VI_WARN_NSUP_ATTR_STATE      = _to_int(0x3FFF0084L)
VI_WARN_UNKNOWN_STATUS       = _to_int(0x3FFF0085L)
VI_WARN_NSUP_BUF             = _to_int(0x3FFF0088L)

# The following one is a non-standard NI extension
VI_WARN_EXT_FUNC_NIMPL       = _to_int(0x3FFF00A9L)

VI_ERROR_SYSTEM_ERROR        = _to_int(0xBFFF0000L)
VI_ERROR_INV_OBJECT          = _to_int(0xBFFF000EL)
VI_ERROR_RSRC_LOCKED         = _to_int(0xBFFF000FL)
VI_ERROR_INV_EXPR            = _to_int(0xBFFF0010L)
VI_ERROR_RSRC_NFOUND         = _to_int(0xBFFF0011L)
VI_ERROR_INV_RSRC_NAME       = _to_int(0xBFFF0012L)
VI_ERROR_INV_ACC_MODE        = _to_int(0xBFFF0013L)
VI_ERROR_TMO                 = _to_int(0xBFFF0015L)
VI_ERROR_CLOSING_FAILED      = _to_int(0xBFFF0016L)
VI_ERROR_INV_DEGREE          = _to_int(0xBFFF001BL)
VI_ERROR_INV_JOB_ID          = _to_int(0xBFFF001CL)
VI_ERROR_NSUP_ATTR           = _to_int(0xBFFF001DL)
VI_ERROR_NSUP_ATTR_STATE     = _to_int(0xBFFF001EL)
VI_ERROR_ATTR_READONLY       = _to_int(0xBFFF001FL)
VI_ERROR_INV_LOCK_TYPE       = _to_int(0xBFFF0020L)
VI_ERROR_INV_ACCESS_KEY      = _to_int(0xBFFF0021L)
VI_ERROR_INV_EVENT           = _to_int(0xBFFF0026L)
VI_ERROR_INV_MECH            = _to_int(0xBFFF0027L)
VI_ERROR_HNDLR_NINSTALLED    = _to_int(0xBFFF0028L)
VI_ERROR_INV_HNDLR_REF       = _to_int(0xBFFF0029L)
VI_ERROR_INV_CONTEXT         = _to_int(0xBFFF002AL)
VI_ERROR_QUEUE_OVERFLOW      = _to_int(0xBFFF002DL)
VI_ERROR_NENABLED            = _to_int(0xBFFF002FL)
VI_ERROR_ABORT               = _to_int(0xBFFF0030L)
VI_ERROR_RAW_WR_PROT_VIOL    = _to_int(0xBFFF0034L)
VI_ERROR_RAW_RD_PROT_VIOL    = _to_int(0xBFFF0035L)
VI_ERROR_OUTP_PROT_VIOL      = _to_int(0xBFFF0036L)
VI_ERROR_INP_PROT_VIOL       = _to_int(0xBFFF0037L)
VI_ERROR_BERR                = _to_int(0xBFFF0038L)
VI_ERROR_IN_PROGRESS         = _to_int(0xBFFF0039L)
VI_ERROR_INV_SETUP           = _to_int(0xBFFF003AL)
VI_ERROR_QUEUE_ERROR         = _to_int(0xBFFF003BL)
VI_ERROR_ALLOC               = _to_int(0xBFFF003CL)
VI_ERROR_INV_MASK            = _to_int(0xBFFF003DL)
VI_ERROR_IO                  = _to_int(0xBFFF003EL)
VI_ERROR_INV_FMT             = _to_int(0xBFFF003FL)
VI_ERROR_NSUP_FMT            = _to_int(0xBFFF0041L)
VI_ERROR_LINE_IN_USE         = _to_int(0xBFFF0042L)
VI_ERROR_NSUP_MODE           = _to_int(0xBFFF0046L)
VI_ERROR_SRQ_NOCCURRED       = _to_int(0xBFFF004AL)
VI_ERROR_INV_SPACE           = _to_int(0xBFFF004EL)
VI_ERROR_INV_OFFSET          = _to_int(0xBFFF0051L)
VI_ERROR_INV_WIDTH           = _to_int(0xBFFF0052L)
VI_ERROR_NSUP_OFFSET         = _to_int(0xBFFF0054L)
VI_ERROR_NSUP_VAR_WIDTH      = _to_int(0xBFFF0055L)
VI_ERROR_WINDOW_NMAPPED      = _to_int(0xBFFF0057L)
VI_ERROR_RESP_PENDING        = _to_int(0xBFFF0059L)
VI_ERROR_NLISTENERS          = _to_int(0xBFFF005FL)
VI_ERROR_NCIC                = _to_int(0xBFFF0060L)
VI_ERROR_NSYS_CNTLR          = _to_int(0xBFFF0061L)
VI_ERROR_NSUP_OPER           = _to_int(0xBFFF0067L)
VI_ERROR_INTR_PENDING        = _to_int(0xBFFF0068L)
VI_ERROR_ASRL_PARITY         = _to_int(0xBFFF006AL)
VI_ERROR_ASRL_FRAMING        = _to_int(0xBFFF006BL)
VI_ERROR_ASRL_OVERRUN        = _to_int(0xBFFF006CL)
VI_ERROR_TRIG_NMAPPED        = _to_int(0xBFFF006EL)
VI_ERROR_NSUP_ALIGN_OFFSET   = _to_int(0xBFFF0070L)
VI_ERROR_USER_BUF            = _to_int(0xBFFF0071L)
VI_ERROR_RSRC_BUSY           = _to_int(0xBFFF0072L)
VI_ERROR_NSUP_WIDTH          = _to_int(0xBFFF0076L)
VI_ERROR_INV_PARAMETER       = _to_int(0xBFFF0078L)
VI_ERROR_INV_PROT            = _to_int(0xBFFF0079L)
VI_ERROR_INV_SIZE            = _to_int(0xBFFF007BL)
VI_ERROR_WINDOW_MAPPED       = _to_int(0xBFFF0080L)
VI_ERROR_NIMPL_OPER          = _to_int(0xBFFF0081L)
VI_ERROR_INV_LENGTH          = _to_int(0xBFFF0083L)
VI_ERROR_INV_MODE            = _to_int(0xBFFF0091L)
VI_ERROR_SESN_NLOCKED        = _to_int(0xBFFF009CL)
VI_ERROR_MEM_NSHARED         = _to_int(0xBFFF009DL)
VI_ERROR_LIBRARY_NFOUND      = _to_int(0xBFFF009EL)
VI_ERROR_NSUP_INTR           = _to_int(0xBFFF009FL)
VI_ERROR_INV_LINE            = _to_int(0xBFFF00A0L)
VI_ERROR_FILE_ACCESS         = _to_int(0xBFFF00A1L)
VI_ERROR_FILE_IO             = _to_int(0xBFFF00A2L)
VI_ERROR_NSUP_LINE           = _to_int(0xBFFF00A3L)
VI_ERROR_NSUP_MECH           = _to_int(0xBFFF00A4L)
VI_ERROR_INTF_NUM_NCONFIG    = _to_int(0xBFFF00A5L)
VI_ERROR_CONN_LOST           = _to_int(0xBFFF00A6L)

# The following two are a non-standard NI extensions
VI_ERROR_MACHINE_NAVAIL      = _to_int(0xBFFF00A7L)
VI_ERROR_NPERMISSION         = _to_int(0xBFFF00A8L)


#
# Attribute constants
#
# All attribute codes are unsigned long, so no _to_int() is necessary.
#

VI_ATTR_RSRC_CLASS           = 0xBFFF0001L
VI_ATTR_RSRC_NAME            = 0xBFFF0002L
VI_ATTR_RSRC_IMPL_VERSION    = 0x3FFF0003L
VI_ATTR_RSRC_LOCK_STATE      = 0x3FFF0004L
VI_ATTR_MAX_QUEUE_LENGTH     = 0x3FFF0005L
VI_ATTR_USER_DATA            = 0x3FFF0007L
VI_ATTR_FDC_CHNL             = 0x3FFF000DL
VI_ATTR_FDC_MODE             = 0x3FFF000FL
VI_ATTR_FDC_GEN_SIGNAL_EN    = 0x3FFF0011L
VI_ATTR_FDC_USE_PAIR         = 0x3FFF0013L
VI_ATTR_SEND_END_EN          = 0x3FFF0016L
VI_ATTR_TERMCHAR             = 0x3FFF0018L
VI_ATTR_TMO_VALUE            = 0x3FFF001AL
VI_ATTR_GPIB_READDR_EN       = 0x3FFF001BL
VI_ATTR_IO_PROT              = 0x3FFF001CL
VI_ATTR_DMA_ALLOW_EN         = 0x3FFF001EL
VI_ATTR_ASRL_BAUD            = 0x3FFF0021L
VI_ATTR_ASRL_DATA_BITS       = 0x3FFF0022L
VI_ATTR_ASRL_PARITY          = 0x3FFF0023L
VI_ATTR_ASRL_STOP_BITS       = 0x3FFF0024L
VI_ATTR_ASRL_FLOW_CNTRL      = 0x3FFF0025L
VI_ATTR_RD_BUF_OPER_MODE     = 0x3FFF002AL
VI_ATTR_RD_BUF_SIZE          = 0x3FFF002BL
VI_ATTR_WR_BUF_OPER_MODE     = 0x3FFF002DL
VI_ATTR_WR_BUF_SIZE          = 0x3FFF002EL
VI_ATTR_SUPPRESS_END_EN      = 0x3FFF0036L
VI_ATTR_TERMCHAR_EN          = 0x3FFF0038L
VI_ATTR_DEST_ACCESS_PRIV     = 0x3FFF0039L
VI_ATTR_DEST_BYTE_ORDER      = 0x3FFF003AL
VI_ATTR_SRC_ACCESS_PRIV      = 0x3FFF003CL
VI_ATTR_SRC_BYTE_ORDER       = 0x3FFF003DL
VI_ATTR_SRC_INCREMENT        = 0x3FFF0040L
VI_ATTR_DEST_INCREMENT       = 0x3FFF0041L
VI_ATTR_WIN_ACCESS_PRIV      = 0x3FFF0045L
VI_ATTR_WIN_BYTE_ORDER       = 0x3FFF0047L
VI_ATTR_GPIB_ATN_STATE       = 0x3FFF0057L
VI_ATTR_GPIB_ADDR_STATE      = 0x3FFF005CL
VI_ATTR_GPIB_CIC_STATE       = 0x3FFF005EL
VI_ATTR_GPIB_NDAC_STATE      = 0x3FFF0062L
VI_ATTR_GPIB_SRQ_STATE       = 0x3FFF0067L
VI_ATTR_GPIB_SYS_CNTRL_STATE = 0x3FFF0068L
VI_ATTR_GPIB_HS488_CBL_LEN   = 0x3FFF0069L
VI_ATTR_CMDR_LA              = 0x3FFF006BL
VI_ATTR_VXI_DEV_CLASS        = 0x3FFF006CL
VI_ATTR_MAINFRAME_LA         = 0x3FFF0070L
VI_ATTR_MANF_NAME            = 0xBFFF0072L
VI_ATTR_MODEL_NAME           = 0xBFFF0077L
VI_ATTR_VXI_VME_INTR_STATUS  = 0x3FFF008BL
VI_ATTR_VXI_TRIG_STATUS      = 0x3FFF008DL
VI_ATTR_VXI_VME_SYSFAIL_STATE = 0x3FFF0094L
VI_ATTR_WIN_BASE_ADDR        = 0x3FFF0098L
VI_ATTR_WIN_SIZE             = 0x3FFF009AL
VI_ATTR_ASRL_AVAIL_NUM       = 0x3FFF00ACL
VI_ATTR_MEM_BASE             = 0x3FFF00ADL
VI_ATTR_ASRL_CTS_STATE       = 0x3FFF00AEL
VI_ATTR_ASRL_DCD_STATE       = 0x3FFF00AFL
VI_ATTR_ASRL_DSR_STATE       = 0x3FFF00B1L
VI_ATTR_ASRL_DTR_STATE       = 0x3FFF00B2L
VI_ATTR_ASRL_END_IN          = 0x3FFF00B3L
VI_ATTR_ASRL_END_OUT         = 0x3FFF00B4L
VI_ATTR_ASRL_REPLACE_CHAR    = 0x3FFF00BEL
VI_ATTR_ASRL_RI_STATE        = 0x3FFF00BFL
VI_ATTR_ASRL_RTS_STATE       = 0x3FFF00C0L
VI_ATTR_ASRL_XON_CHAR        = 0x3FFF00C1L
VI_ATTR_ASRL_XOFF_CHAR       = 0x3FFF00C2L
VI_ATTR_WIN_ACCESS           = 0x3FFF00C3L
VI_ATTR_RM_SESSION           = 0x3FFF00C4L
VI_ATTR_VXI_LA               = 0x3FFF00D5L
VI_ATTR_MANF_ID              = 0x3FFF00D9L
VI_ATTR_MEM_SIZE             = 0x3FFF00DDL
VI_ATTR_MEM_SPACE            = 0x3FFF00DEL
VI_ATTR_MODEL_CODE           = 0x3FFF00DFL
VI_ATTR_SLOT                 = 0x3FFF00E8L
VI_ATTR_INTF_INST_NAME       = 0xBFFF00E9L
VI_ATTR_IMMEDIATE_SERV       = 0x3FFF0100L
VI_ATTR_INTF_PARENT_NUM      = 0x3FFF0101L
VI_ATTR_RSRC_SPEC_VERSION    = 0x3FFF0170L
VI_ATTR_INTF_TYPE            = 0x3FFF0171L
VI_ATTR_GPIB_PRIMARY_ADDR    = 0x3FFF0172L
VI_ATTR_GPIB_SECONDARY_ADDR  = 0x3FFF0173L
VI_ATTR_RSRC_MANF_NAME       = 0xBFFF0174L
VI_ATTR_RSRC_MANF_ID         = 0x3FFF0175L
VI_ATTR_INTF_NUM             = 0x3FFF0176L
VI_ATTR_TRIG_ID              = 0x3FFF0177L
VI_ATTR_GPIB_REN_STATE       = 0x3FFF0181L
VI_ATTR_GPIB_UNADDR_EN       = 0x3FFF0184L
VI_ATTR_DEV_STATUS_BYTE      = 0x3FFF0189L
VI_ATTR_FILE_APPEND_EN       = 0x3FFF0192L
VI_ATTR_VXI_TRIG_SUPPORT     = 0x3FFF0194L
VI_ATTR_TCPIP_ADDR           = 0xBFFF0195L
VI_ATTR_TCPIP_HOSTNAME       = 0xBFFF0196L
VI_ATTR_TCPIP_PORT           = 0x3FFF0197L
VI_ATTR_TCPIP_DEVICE_NAME    = 0xBFFF0199L
VI_ATTR_TCPIP_NODELAY        = 0x3FFF019AL
VI_ATTR_TCPIP_KEEPALIVE      = 0x3FFF019BL
VI_ATTR_4882_COMPLIANT       = 0x3FFF019FL
VI_ATTR_USB_SERIAL_NUM       = 0xBFFF01A0L
VI_ATTR_USB_INTFC_NUM        = 0x3FFF01A1L
VI_ATTR_USB_PROTOCOL         = 0x3FFF01A7L
VI_ATTR_USB_MAX_INTR_SIZE    = 0x3FFF01AFL

VI_ATTR_JOB_ID               = 0x3FFF4006L
VI_ATTR_EVENT_TYPE           = 0x3FFF4010L
VI_ATTR_SIGP_STATUS_ID       = 0x3FFF4011L
VI_ATTR_RECV_TRIG_ID         = 0x3FFF4012L
VI_ATTR_INTR_STATUS_ID       = 0x3FFF4023L
VI_ATTR_STATUS               = 0x3FFF4025L
VI_ATTR_RET_COUNT            = 0x3FFF4026L
VI_ATTR_BUFFER               = 0x3FFF4027L
VI_ATTR_RECV_INTR_LEVEL      = 0x3FFF4041L
VI_ATTR_OPER_NAME            = 0xBFFF4042L
VI_ATTR_GPIB_RECV_CIC_STATE  = 0x3FFF4193L
VI_ATTR_RECV_TCPIP_ADDR      = 0xBFFF4198L
VI_ATTR_USB_RECV_INTR_SIZE   = 0x3FFF41B0L
VI_ATTR_USB_RECV_INTR_DATA   = 0xBFFF41B1L


#
# Event Types
#
# All event codes are unsigned long, so no _to_int() is necessary.
#

VI_EVENT_IO_COMPLETION       = 0x3FFF2009L
VI_EVENT_TRIG                = 0xBFFF200AL
VI_EVENT_SERVICE_REQ         = 0x3FFF200BL
VI_EVENT_CLEAR               = 0x3FFF200DL
VI_EVENT_EXCEPTION           = 0xBFFF200EL
VI_EVENT_GPIB_CIC            = 0x3FFF2012L
VI_EVENT_GPIB_TALK           = 0x3FFF2013L
VI_EVENT_GPIB_LISTEN         = 0x3FFF2014L
VI_EVENT_VXI_VME_SYSFAIL     = 0x3FFF201DL
VI_EVENT_VXI_VME_SYSRESET    = 0x3FFF201EL
VI_EVENT_VXI_SIGP            = 0x3FFF2020L
VI_EVENT_VXI_VME_INTR        = 0xBFFF2021L
VI_EVENT_TCPIP_CONNECT       = 0x3FFF2036L
VI_EVENT_USB_INTR            = 0x3FFF2037L

VI_ALL_ENABLED_EVENTS        = 0x3FFF7FFFL


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
VI_INTF_TCPIP                = 6
VI_INTF_USB                  = 7

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
VI_TMO_INFINITE              = 0xFFFFFFFFL

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

# "Backwards compatibility" according to NI

VI_NORMAL                    = VI_PROT_NORMAL
VI_FDC                       = VI_PROT_FDC
VI_HS488                     = VI_PROT_HS488
VI_ASRL488                   = VI_PROT_4882_STRS
VI_ASRL_IN_BUF               = VI_IO_IN_BUF
VI_ASRL_OUT_BUF              = VI_IO_OUT_BUF
VI_ASRL_IN_BUF_DISCARD       = VI_IO_IN_BUF_DISCARD
VI_ASRL_OUT_BUF_DISCARD      = VI_IO_OUT_BUF_DISCARD

