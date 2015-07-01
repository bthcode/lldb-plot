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
    - formalize type support
        - right now only double, float int
        - add the rest of the basic types
        - should we allow the caller to specify the cast to python type?
        - support complex data
'''

#----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# To use from lldb:
#   (lldb) command script import /path/to/lldbplot.py
#----------------------------------------------------------------------

import lldb
import commands
import optparse
import shlex
import matplotlib.pyplot as plt
import numpy as np
from lp_data_extractor import *

def lldb_plot_command(debugger, command, result, internal_dict):
    
    args = shlex.split(command)
    if len(args) < 1:
        result.SetError( "USAGE: plot buffer1 buffer2 ..." )
        return

    try:
        data, names = lp_get_data(debugger,args,result,internal_dict)
    except Exception as err:
        result.SetError("Failed to get data, error = {0}".format(err))
        return

    legend = args
    fig = plt.figure()
    for d in data:
        ax = fig.add_subplot(111)
        ax.plot(d)
    ax.legend(legend)
    plt.show()
    return
# end

def __lldb_init_module (debugger, internal_dict):

    # Set up command line
    lldb_plot_command.__doc__ = '''plot var1 var2@1024, var3

  - var2@1024 - plot 1024 elements from var2 (note - this is required for pointer arrays)
'''

    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('command script add -f lldbplot.lldb_plot_command plot')
    print 'The "plot" command has been installed, type "help plot" or "plot --help" for detailed help.'
