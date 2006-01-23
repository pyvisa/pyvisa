#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43_attributes.py - VISA VPP-4.3.2 attributes data
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


__version__ = "$Revision$"
# \$Source${}$\$

from vpp43_constants import *
from vpp43_types import *

attributes = {
    VI_ATTR_4882_COMPLIANT      : ViBoolean,
    # VI_ATTR_ASRL_ALLOW_TRANSMIT
    VI_ATTR_ASRL_AVAIL_NUM      : ViUInt32,
    VI_ATTR_ASRL_BAUD           : ViUInt32,
    # VI_ATTR_ASRL_BREAK_LEN
    # VI_ATTR_ASRL_BREAK_STATE
    VI_ATTR_ASRL_CTS_STATE      : ViInt16,
    VI_ATTR_ASRL_DATA_BITS      : ViUInt16,
    VI_ATTR_ASRL_DCD_STATE      : ViInt16,
    # VI_ATTR_ASRL_DISCARD_NULL
    VI_ATTR_ASRL_DSR_STATE      : ViInt16,
    VI_ATTR_ASRL_DTR_STATE      : ViInt16,
    VI_ATTR_ASRL_END_IN         : ViUInt16,
    VI_ATTR_ASRL_END_OUT        : ViUInt16,
    VI_ATTR_ASRL_FLOW_CNTRL     : ViUInt16,
    VI_ATTR_ASRL_PARITY         : ViUInt16,
    VI_ATTR_ASRL_REPLACE_CHAR   : ViUInt8,
    VI_ATTR_ASRL_RI_STATE       : ViInt16,
    VI_ATTR_ASRL_RTS_STATE      : ViInt16,
    VI_ATTR_ASRL_STOP_BITS      : ViUInt16,
    # VI_ATTR_ASRL_WIRE_MODE
    VI_ATTR_ASRL_XOFF_CHAR      : ViUInt8,
    VI_ATTR_ASRL_XON_CHAR       : ViUInt8,
    VI_ATTR_BUFFER              : ViBuf,
    VI_ATTR_CMDR_LA             : ViInt16,
    VI_ATTR_DEST_ACCESS_PRIV    : ViUInt16,
    VI_ATTR_DEST_BYTE_ORDER     : ViUInt16,
    VI_ATTR_DEST_INCREMENT      : ViInt32,
    VI_ATTR_DEV_STATUS_BYTE     : ViUInt8,
    VI_ATTR_DMA_ALLOW_EN        : ViBoolean,
    VI_ATTR_EVENT_TYPE          : ViEventType,
    VI_ATTR_FDC_CHNL            : ViUInt16,
    VI_ATTR_FDC_GEN_SIGNAL_EN   : None,
    VI_ATTR_FDC_MODE            : ViUInt16,
    VI_ATTR_FDC_USE_PAIR        : ViBoolean,
    VI_ATTR_FILE_APPEND_EN      : ViBoolean,
    VI_ATTR_GPIB_ADDR_STATE     : ViInt16,
    VI_ATTR_GPIB_ATN_STATE      : ViInt16,
    VI_ATTR_GPIB_CIC_STATE      : ViBoolean,
    VI_ATTR_GPIB_HS488_CBL_LEN  : ViInt16,
    VI_ATTR_GPIB_NDAC_STATE     : ViInt16,
    VI_ATTR_GPIB_PRIMARY_ADDR   : ViUInt16,
    VI_ATTR_GPIB_READDR_EN      : ViBoolean,
    VI_ATTR_GPIB_RECV_CIC_STATE : ViBoolean,
    VI_ATTR_GPIB_REN_STATE      : ViInt16,
    VI_ATTR_GPIB_SECONDARY_ADDR : ViUInt16,
    VI_ATTR_GPIB_SRQ_STATE      : ViInt16,
    VI_ATTR_GPIB_SYS_CNTRL_STATE : ViBoolean,
    VI_ATTR_GPIB_UNADDR_EN      : ViBoolean,
    VI_ATTR_IMMEDIATE_SERV      : ViBoolean,
    VI_ATTR_INTF_INST_NAME      : ViString,
    VI_ATTR_INTF_NUM            : ViUInt16,
    VI_ATTR_INTF_PARENT_NUM     : ViUInt16,
    VI_ATTR_INTF_TYPE           : ViUInt16,
    VI_ATTR_INTR_STATUS_ID      : ViUInt32,
    VI_ATTR_IO_PROT             : ViUInt16,
    VI_ATTR_JOB_ID              : ViJobId,
    VI_ATTR_MAINFRAME_LA        : ViInt16,
    VI_ATTR_MANF_ID             : ViUInt16,
    VI_ATTR_MANF_NAME           : ViString,
    VI_ATTR_MAX_QUEUE_LENGTH    : ViUInt32,
    VI_ATTR_MEM_BASE            : ViBusAddress,
    VI_ATTR_MEM_SIZE            : ViBusSize,
    VI_ATTR_MEM_SPACE           : ViUInt16,
    VI_ATTR_MODEL_CODE          : ViUInt16,
    VI_ATTR_MODEL_NAME          : ViString,
    VI_ATTR_OPER_NAME           : ViString,
    # Many "PXI" attributes
    VI_ATTR_RD_BUF_OPER_MODE    : ViUInt16,
    VI_ATTR_RD_BUF_SIZE         : ViUInt32,
    VI_ATTR_RECV_INTR_LEVEL     : ViInt16,
    VI_ATTR_RECV_TCPIP_ADDR     : None,
    VI_ATTR_RECV_TRIG_ID        : ViInt16,
    VI_ATTR_RET_COUNT           : ViUInt32,
    VI_ATTR_RM_SESSION          : ViSession,
    VI_ATTR_RSRC_CLASS          : ViString,
    VI_ATTR_RSRC_IMPL_VERSION   : ViVersion,
    VI_ATTR_RSRC_LOCK_STATE     : ViAccessMode,
    VI_ATTR_RSRC_MANF_ID        : ViUInt16,
    VI_ATTR_RSRC_MANF_NAME      : ViString,
    VI_ATTR_RSRC_NAME           : ViRsrc,
    VI_ATTR_RSRC_SPEC_VERSION   : ViVersion,
    VI_ATTR_SEND_END_EN         : ViBoolean,
    VI_ATTR_SIGP_STATUS_ID      : ViUInt16,
    VI_ATTR_SLOT                : ViInt16,
    VI_ATTR_SRC_ACCESS_PRIV     : ViUInt16,
    VI_ATTR_SRC_BYTE_ORDER      : ViUInt16,
    VI_ATTR_SRC_INCREMENT       : ViInt32,
    VI_ATTR_STATUS              : ViStatus,
    VI_ATTR_SUPPRESS_END_EN     : ViBoolean,
    VI_ATTR_TCPIP_ADDR          : ViString,
    VI_ATTR_TCPIP_DEVICE_NAME   : ViString,
    VI_ATTR_TCPIP_HOSTNAME      : ViString,
    VI_ATTR_TCPIP_KEEPALIVE     : ViBoolean,
    VI_ATTR_TCPIP_NODELAY       : ViBoolean,
    VI_ATTR_TCPIP_PORT          : ViUInt16,
    VI_ATTR_TERMCHAR            : ViUInt8,
    VI_ATTR_TERMCHAR_EN         : ViBoolean,
    VI_ATTR_TMO_VALUE           : ViUInt32,
    VI_ATTR_TRIG_ID             : ViInt16,
    # VI_ATTR_USB_ALT_SETTING
    # VI_ATTR_USB_BULK_IN_PIPE
    # VI_ATTR_USB_BULK_IN_STATUS
    # VI_ATTR_USB_BULK_OUT_PIPE
    # VI_ATTR_USB_BULK_OUT_STATUS
    # VI_ATTR_USB_CLASS
    VI_ATTR_USB_INTFC_NUM       : ViInt16,
    # VI_ATTR_USB_INTR_IN_PIPE
    # VI_ATTR_USB_INTR_IN_STATUS
    VI_ATTR_USB_MAX_INTR_SIZE   : ViUInt16,
    # VI_ATTR_USB_NUM_INTFCS
    # VI_ATTR_USB_NUM_PIPES
    VI_ATTR_USB_PROTOCOL        : ViInt16,
    VI_ATTR_USB_RECV_INTR_DATA  : ViAUInt8,
    VI_ATTR_USB_RECV_INTR_SIZE  : ViUInt16,
    VI_ATTR_USB_SERIAL_NUM      : ViString,
    # VI_ATTR_USB_SUBCLASS
    VI_ATTR_USER_DATA           : ViAddr,
    VI_ATTR_VXI_DEV_CLASS       : ViUInt16,
    VI_ATTR_VXI_LA              : ViInt16,
    VI_ATTR_VXI_TRIG_STATUS     : ViUInt32,
    VI_ATTR_VXI_TRIG_SUPPORT    : ViUInt32,
    VI_ATTR_VXI_VME_INTR_STATUS : ViUInt16,
    VI_ATTR_VXI_VME_SYSFAIL_STATE : ViInt16,
    VI_ATTR_WIN_ACCESS          : ViUInt16,
    VI_ATTR_WIN_ACCESS_PRIV     : ViUInt16,
    VI_ATTR_WIN_BASE_ADDR       : ViBusAddress,
    VI_ATTR_WIN_BYTE_ORDER      : ViUInt16,
    VI_ATTR_WIN_SIZE            : ViBusSize,
    VI_ATTR_WR_BUF_OPER_MODE    : ViUInt16,
    VI_ATTR_WR_BUF_SIZE         : ViUInt32
}
