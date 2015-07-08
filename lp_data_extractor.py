#!/usr/bin/env python

'''
Utility functions to get buffers out of lldb into numpy buffers.
'''

import lldb
import commands
import optparse
import shlex
import matplotlib.pyplot as plt
import numpy as np

lp_debug = False


def idxs_from_arg(arg):
    ''' return key, start, end from:
    key@end
    key
    '''
    key   = arg
    start = 0
    end   = -1
    
    # split on @ to get idxs
    if arg.find( "@" ) >= 0:
        key, end = arg.split("@")
        end = int(end)
    return key, end 
# end idx_from_arg




def lp_get_data(debugger, args, result, internal_dict):
    '''
    extract lldb variables into numpy arrays

    [in] debugger - lldb instance
    [in] args - list of var names conforming to 'var' or 'var@end_idx'
    [in] result - result instance
    [in] internal_dict - not really needed
    '''
    
    if len(args) == 0:
        result.SetError("Please specify something to plot")
        return

    target   = debugger.GetSelectedTarget()
    process  = target.GetProcess()
    thread   = process.GetSelectedThread()
    frame    = thread.GetSelectedFrame()

    names    = []
    ret_data = []

    for arg in args:
        if lp_debug: print (arg)

        #---------------------------------
        # Parse the arg into variable
        #  and end index
        #---------------------------------
        try:
            arg, end = idxs_from_arg(arg)
            names.append(arg)
        except:
            result.SetError("Unable to parse argument: {0}, formats are: var, var@end_idx".format(arg))
            return None, None
        if lp_debug: print ( arg, end )

        #---------------------------------
        # Find the variable in question
        #---------------------------------
        x = frame.FindVariable(arg)
        if not x.is_in_scope:
            result.SetError("{0} not in scope".format(arg))
            return None, None

        # initialize data_type_name and base_type_name
        data_type_name = 'UNKNOWN'
        base_type_name = 'UNKNOWN'

        #---------------------------------------------
        # Figure out the container type and data type
        #   supported containers are:
        #     - stl::vector
        #     - array
        #     - pointer array (must specify end)
        #   supported data types are:
        #     - int
        #     - float
        #     - double
        #---------------------------------------------
        type_name = x.type.name
        if lp_debug: print ("type_name = {0}".format(type_name))
        if type_name.find( 'vector' ) >= 0:
            tmp = x.GetChildAtIndex(0)
            data_type_name = 'vector'
            base_type_name = tmp.type.name
        elif x.type.IsArrayType():
            data_type_name = 'array'
            base_type_name = x.type.GetArrayElementType().name
        elif x.type.IsPointerType():
            data_type_name = 'pointer array'
            base_type_name = x.type.GetPointeeType().name

        if lp_debug: print (data_type_name)
        if lp_debug: print (base_type_name)

        supported = ['double','float','int']
        if base_type_name not in supported:
            result.SetError('{0} type not supported'.format(base_type_name))
            return None, None

        data = None

        #--------------------------------
        # stl::vector data extractor
        #--------------------------------
        if data_type_name == 'vector':
            data = [ 0 for idx in range(x.num_children)]
            for idx in range(x.num_children):
                if base_type_name == 'double':
                    data[idx] = x.GetChildAtIndex(idx).GetData().doubles[0] 
                elif base_type_name == 'float':
                    data[idx] = x.GetChildAtIndex(idx).GetData().floats[0] 
                elif base_type_name == 'int':
                    data[idx] = x.GetChildAtIndex(idx).GetData().sint32s[0] 
                else:
                    result.SetError('{0}: unknown type'.format(base_type_name))
     
        #--------------------------------
        # array data extractor
        #--------------------------------
        elif data_type_name == 'array':
            dd = x.GetData()
            if base_type_name == 'double':
                data = dd.doubles
            elif base_type_name == 'float':
                data = dd.floats
            elif base_type_name == 'int':
                data = dd.ints
            else:
                result.SetError('{0}: unknown type'.format(base_type_name))
                return None, None

        #--------------------------------
        # pointer array data extractor
        #--------------------------------
        elif data_type_name == 'pointer array':
            if end == -1:
                result.SetError('Need end for pointer array, try {0}@end_idx'.format(arg))
                return None, None
            dd = x.GetPointeeData(0,end)
            if base_type_name == 'double':
                data = dd.doubles
            elif base_type_name == 'float':
                data = dd.floats
            elif base_type_name == 'int':
                data = dd.ints
            else:
                result.SetError('{0}: unknown type'.format(base_type_name))
                return None, None
        else:
            result.SetError("{0}: unknown type".format(data_type_name))
            return None, None

        #--------------------------------
        # convert to numpy for return
        #--------------------------------
        data = np.array(data)
        ret_data.append(data)
        # end for each arg
    return ret_data, names

    
# end lp_get_data


# lldb types:
#   'double', 'doubles', 'float', 'floats', 'read_data_helper', 'sint16', 'sint16s', 'sint32', 'sint32s', 'sint64', 'sint64s', 'sint8', 'sint8s', 'size', 'this', 'uint16', 'uint16s', 'uint32', 'uint32s', 'uint64', 'uint64s', 'uint8', 'uint8s'
