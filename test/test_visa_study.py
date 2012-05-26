#_RM = ResourceManager() #liefert Exception in __del__ beim Beenden
#open = _RM.Open
#find_resource = _RM.FindResource

#for faster testing
def testvisa():

    logging.basicConfig(level = logging.DEBUG)
    #log.setLevel(logging.DEBUG) #FIXME

    #open ResourceManager
    RM = ResourceManager()

    #find resources
    resourcelist = RM.find_resource('ASRL?::INSTR')
    print(resourcelist)

    #get some information without opening
    result = RM.parse_resource('ASRL1::INSTR')
    print(result)

    #open
    device = RM.open('ASRL1::INSTR')

    #high level write
    device.write('*IDN?')

    #high level read
    #print(device.read() #don't wan't to wait for timeout...

    #try getting all attributes
    for key in attributes_s.keys():
        try:
            print(device.getattr(key))
        except IOError as value:
            print("Error retrieving Attribute ", key)

    #set some attributes, try different combinations of numeric/string arguments
    device.setattr('VI_ATTR_ASRL_DATA_BITS', 7)
    print(device.getattr(VI_ATTR_ASRL_DATA_BITS))

    #attribute value, string argument
    device.setattr(VI_ATTR_ASRL_STOP_BITS, 'VI_ASRL_STOP_TWO')
    print(device.getattr('VI_ATTR_ASRL_STOP_BITS'))
    print()

    #bitfields
    device.setattr('VI_ATTR_ASRL_FLOW_CNTRL', VI_ASRL_FLOW_XON_XOFF | VI_ASRL_FLOW_RTS_CTS)
    print(device.getattr('VI_ATTR_ASRL_FLOW_CNTRL'))

    #bitfield with string argument
    device.setattr(VI_ATTR_ASRL_FLOW_CNTRL, 'VI_ASRL_FLOW_NONE')
    print(device.getattr('VI_ATTR_ASRL_FLOW_CNTRL'))

    #callback functions

    def event_handler(vi, event_type, context, userhandle):
    #def event_handler(vi, event_type, context): #FIX: should accept four arguments
        sys.stdout.flush()
        print('in event handler')
        print('vi: ', vi)
        print('event_type: ', event_type)
        print('context: ', context)

        print(GetAttribute(context, VI_ATTR_EVENT_TYPE))
        print(GetAttribute(context, VI_ATTR_STATUS))
        print(GetAttribute(context, VI_ATTR_JOB_ID))
        print(GetAttribute(context, VI_ATTR_BUFFER))
        print(GetAttribute(context, VI_ATTR_RET_COUNT))
        print(GetAttribute(context, VI_ATTR_OPER_NAME))
        print('userhandle: ', userhandle)
        print('leaving event handler')

        return VI_SUCCESS

    device.install_handler(VI_EVENT_IO_COMPLETION, ViHndlr(event_handler), 13)

    device.enable_event(VI_EVENT_IO_COMPLETION, VI_HNDLR)

    print('session', device.session)
    jobId = WriteAsync(device.session, 'going to nowhere city')
    print("jobId: ", jobId)

    jobId = ReadAsync(device.session, 10)
    print("jobId: ", jobId)

    device.close()

if __name__ == '__main__':
    testvisa()
