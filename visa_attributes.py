import vpp43 as _constants
from vpp43_types import *

viRO = 'readonly'
viRW = 'readwrite'
viGlobal = 'Global'
viLocal = 'Local'

class viRange:
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
    def __contains__(self, item):
        if item >= self.minimum and item<=self.maximum:
            return True
        else:
            return False
    def __getitem__(self, key):
        if key in self:
            return hex(key)
        else:
            raise IndexError

class viSet:
    def __init__(self, *args):
        self.NameSet = args
        self.dict = {}
        for name in args:
            value = _constants.__dict__[name]
            self.dict[value] = name

    def __repr__(self):
        return repr(self.dict)
    
    def __contains__(self, item):
        return item in self.NameSet

    def __getitem__(self, key):
        return self.dict[key]

class viAttrInfo:
    def __init__(self, access, scope, datatype, values, shortdesc, description):
        self.access = access
        self.scope = scope
        self.datatype = datatype
        self.values = values
        self.description = description

    def __repr__(self):
        #s = repr(self.typecode) + repr(self.values)
        #return s
        return repr(self.__dict__)

#VISA Template Attributes
#Table 3.2.1

attrib = {
    'VI_ATTR_RSRC_IMPL_VERSION': \
    viAttrInfo(
    viRO, viGlobal, ViVersion,
    viRange(0, 0xFFFFFFFF),
    'implementation version',
    "Resource version that uniquely identifies each of the different "\
    "revisions or implementations of a resource."
    ),

    'VI_ATTR_RSRC_LOCK_STATE': \
    viAttrInfo(
    viRO, viGlobal, ViAccessMode,
    viSet('VI_NO_LOCK', 'VI_EXCLUSIVE_LOCK', 'VI_SHARED_LOCK'),
    'lock state',
    "The current locking state of the resource. The resource can be "\
    "unlocked, locked with an exclusive lock, or locked with a shared "\
    "lock."
    ),
    
    'VI_ATTR_RSRC_MANF_ID': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16, viRange(0, 0x3FFF),
    'resource manufacturer ID',
    "A value that corresponds to the VXI manufacturer ID of the "\
    "manufacturer that created the implementation."
    ),
    
    'VI_ATTR_RSRC_MANF_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'resource manufacturer name',
    "A string that corresponds to the VXI manufacturer name of the "\
    "manufacturer that created the implementation."
    ),

    'VI_ATTR_RSRC_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViRsrc, None,
    'resource name',
    "The unique identifier for a resource compliant with the address "\
    "structure presented in Section 4.4.1, Address String."
    ),

    'VI_ATTR_RSRC_SPEC_VERSION': \
    viAttrInfo(
    viRO, viGlobal, ViVersion, None,
    'resource specification version',
    "Resource version that uniquely identifies the version of the VISA "\
    "specification to which the implementation is compliant."
    ),
    
    'VI_ATTR_RSRC_CLASS': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'resource class',
    "Specifies the resource class (for example, INSTR)."
    ),

    #Generic INSTR Resource Attributes
    'VI_ATTR_INTF_NUM': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16, viRange(0, 0xFFFF),
    'interface number',
    "Board number for the given interface."
    ),

    'VI_ATTR_INTF_TYPE': \
    viAttrInfo(
    viRO, viGlobal, ViUInt16,
    viSet('VI_INTF_VXI', 'VI_INTF_GPIB', 'VI_INTF_GPIB_VXI', 'VI_INTF_ASRL',
          'VI_INTF_TCPIP', 'VI_INTF_USB'),
    'interface type',
    "Interface type of the given session."
    ),
    
    'VI_ATTR_INTF_INST_NAME': \
    viAttrInfo(
    viRO, viGlobal, ViString, None,
    'interface name',
    "Human-readable text describing the given interface."
    )
    }

attr = {}
for key, value in attrib.iteritems():
    keyvalue = _constants.__dict__[key]
    attr[keyvalue] = (key, value)

#print attr
    

