#!/usr/bin/env python

#----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import" 
# command
#   (lldb) command script import /path/to/cmdtemplate.py
#----------------------------------------------------------------------

import lldb
import commands
import optparse
import shlex
import matplotlib.pyplot as plt
import numpy as np

def create_plotter_options():
    usage = "usage: %prog [options]"
    description='''
Plotter for lldb.

Handles std::vector, static array, pointer array
'''
    parser = optparse.OptionParser(description=description, prog='plot',usage=usage)
    parser.add_option('--start', action='store', type=int, default=0)
    parser.add_option('--end', action='store', type=int)
    return parser
# end create_framestats_options

def lldb_plot_command(debugger, command, result, internal_dict):
    
    # Use the Shell Lexer to properly parse up command options just like a 
    # shell would
    command_args = shlex.split(command)
    parser = create_plotter_options()

    try:
        (options, args) = parser.parse_args(command_args)
    except:
        # if you don't handle exceptions, passing an incorrect argument to the OptionParser will cause LLDB to exit
        # (courtesy of OptParse dealing with argument errors by throwing SystemExit)
        result.SetError ("option parsing failed")
        return

    if len(args) == 0:
        result.SetError("Please specify something to plot")
        return

    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

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
        x = frame.FindVariable(arg)
        # check for valid var
        if not x.is_in_scope:
            result.SetError("{0} not in scope".format(arg))
            import pdb; pdb.set_trace()
            return

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
            return

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
                return
        elif data_type_name == 'pointer array':
            if not options.end:
                result.SetError('Need end for pointer array')
                return
            dd = x.GetPointeeData(options.start,options.end)
            if base_type_name == 'double':
                data = dd.doubles
            elif base_type_name == 'float':
                data = dd.floats
            elif base_type_name == 'int':
                data = dd.ints
            else:
                result.SetError('{0}: unknown type'.format(base_type_name))
                return
        else:
            result.SetError("{0}: unknown type".format(data_type_name))
            return

        data = np.array(data)
        plt.plot(data)
    plt.show()
    return

    
# end

def __lldb_init_module (debugger, internal_dict):

    # Set up command line
    parser = create_plotter_options()
    lldb_plot_command.__doc__ = parser.format_help()

    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('command script add -f lldbplot.lldb_plot_command plot')
    print 'The "plot" command has been installed, type "help plot" or "plot --help" for detailed help.'
