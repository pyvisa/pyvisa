# VISA VPP-4.3 data types
#
# (See VPP-4.3.2 specification, section 3)

from ctypes import *

# Part One: Type Assignments for VISA and Instrument Drivers, see spec table
# 3.1.1.
#
# Remark: The pointer and probably also the array variants are of no
# significance in Python because there is no native call-by-reference.
# However, as long as I'm not fully sure about this, they won't hurt.

def _generate_type_dublett(visa_type, ctypes_type):
    return visa_type + "=" + ctypes_type + ";" + \
	"ViP" + visa_type[2:] + "=POINTER(" + visa_type + ")"

def _generate_type_triplett(visa_type, ctypes_type):
    return _generate_type_dublett(visa_type, ctypes_type) + ";" + \
	"ViA" + visa_type[2:] + "=" + "ViP" + visa_type[2:]

exec _generate_type_triplett("ViUInt32",  "c_ulong"  )
exec _generate_type_triplett("ViInt32",   "c_long"   )
exec _generate_type_triplett("ViUInt16",  "c_ushort" )
exec _generate_type_triplett("ViInt16",   "c_short"  )
exec _generate_type_triplett("ViUInt8",   "c_ubyte"  )
exec _generate_type_triplett("ViInt8",    "c_byte"   )
exec _generate_type_triplett("ViAddr",    "c_void_p" )
exec _generate_type_triplett("ViChar",    "c_char"   )
exec _generate_type_triplett("ViByte",    "c_ubyte"  )
exec _generate_type_triplett("ViBoolean", "ViUInt16" )
exec _generate_type_triplett("ViReal32",  "c_float"  )
exec _generate_type_triplett("ViReal64",  "c_double" )

ViBuf         = ViPByte
ViPBuf        = ViPByte
ViABuf        = POINTER(ViBuf)

ViString      = ViPChar
ViPString     = ViPChar
ViAString     = POINTER(ViString)

ViRsrc        = ViString
ViPRsrc       = ViString
ViARsrc       = POINTER(ViRsrc)

exec _generate_type_triplett("ViStatus",  "ViInt32"  )
exec _generate_type_triplett("ViVersion", "ViUInt32" )
exec _generate_type_triplett("ViObject",  "ViUInt32" )
exec _generate_type_triplett("ViSession", "ViObject" )

ViAttr        = ViUInt32
ViConstString = POINTER(ViChar)


# Part Two: Type Assignments for VISA only, see spec table 3.1.2.  The
# difference to the above is of no significance in Python, so I use it here
# only for easier synchronisation with the spec.

exec _generate_type_dublett("ViAccessMode", "ViUInt32" )
exec _generate_type_dublett("ViBusAddress", "ViUInt32" )

ViBusSize     = ViUInt32

exec _generate_type_dublett("ViAttrState",  "ViUInt32" )

# The following is weird, taken from news:zn2ek2w2.fsf@python.net
viVAList      = POINTER(c_char)

exec _generate_type_triplett("ViEventType", "ViUInt32" )

ViPAttr       = POINTER(ViAttr)
ViAAttr       = ViPAttr

ViEventFilter = ViUInt32

exec _generate_type_dublett("ViFindList", "ViObject" )
exec _generate_type_dublett("ViEvent",    "ViObject" )
exec _generate_type_dublett("ViKeyId",    "ViString" )
exec _generate_type_dublett("ViJobId",    "ViUInt32" )

ViHndlr       = CFUNCTYPE(ViSession, ViEventType, ViEvent, ViAddr)
