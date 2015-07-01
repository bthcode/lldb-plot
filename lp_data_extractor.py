#!/usr/bin/env python

'''
Script to plot data from lldb

Requires: numpy + matplotlib

USAGE: plot var1 var2 var3@1024

    - NOTE: var3@1024 = plot first 1024 elements
            -- this syntax is required for pointer arrays

License:
    - Do whatever you want with this and don't blame me

TODO:
    - modularize 
        - make a 'get data for variable' library
        - plot should call that and then plot
        - add save to mat file
    - formalize type support
        - right now only double, float int
        - add the rest of the basic types
        - should we allow the caller to specify the cast to python type?
        - support complex data
'''


import lldb
import commands
import optparse
import shlex
import matplotlib.pyplot as plt
import numpy as np

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
    
    if len(args) == 0:
        result.SetError("Please specify something to plot")
        return

    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    names = []
    legend = []
    ret_data = []

    for arg in args:
    #--------------------------
    # Now, guess the type
    #  Supported are:
    #    static array
    #    pointer array (end required)
    #    std::vector
    #  Types supported are:
    #   'double', 'doubles', 'float', 'floats', 'read_data_helper', 'sint16', 'sint16s', 'sint32', 'sint32s', 'sint64', 'sint64s', 'sint8', 'sint8s', 'size', 'this', 'uint16', 'uint16s', 'uint32', 'uint32s', 'uint64', 'uint64s', 'uint8', 'uint8s'
    #--------------------------
        print (arg)
        try:
            arg, end = idxs_from_arg(arg)
            names.append(arg)
        except:
            result.SetError("Unable to parse argument: {0}, formats are: var, var@end_idx".format(arg))
            return None, None
        print ( arg, end )
        x = frame.FindVariable(arg)
        # check for valid var
        if not x.is_in_scope:
            result.SetError("{0} not in scope".format(arg))
            import pdb; pdb.set_trace()
            return None, None

        # initialize data_type_name and base_type_name
        data_type_name = 'UNKNOWN'
        base_type_name = 'UNKNOWN'

        # Figure out the type
        type_name = x.type.name
        print ("type_name = {0}".format(type_name))
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

        print data_type_name
        print base_type_name

        # check types
        supported = ['double','float','int']
        if base_type_name not in supported:
            result.SetError('{0} type not supported'.format(base_type_name))
            return None, None

        data = None
        # get data
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

        data = np.array(data)
        ret_data.append(data)
        # end for each arg
    return ret_data, names

    
# end
