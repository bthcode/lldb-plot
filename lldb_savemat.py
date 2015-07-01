#!/usr/bin/env python

'''
Script to save buffers to mat files

USAGE: savemat matfile var1 var2 var3@1024

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
import string
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from lp_data_extractor import *


def lldb_savemat_command(debugger, command, result, internal_dict):
    
    command_args = shlex.split(command)

    args = shlex.split(command)
    if args < 2:
        result.SetError( "USAGE: savemat matfile buffer1 buffer2 ...." )
        return

    matfile = args[0]
    buffs = args[1:]

    if len(buffs) == 0:
        result.SetError("Please specify something to plot")
        return

    try:
        data, names = lp_get_data(debugger,buffs,result,internal_dict)
    except Exception as err:
        result.SetError("Failed to get data, error = {0}".format(err))
        return

    d = {}
    for idx in range(len(data)):
        d[names[idx]] = data[idx]

    sio.savemat(matfile, d)

    return
# end lldb_savemat_command

def __lldb_init_module (debugger, internal_dict):

    # Set up command line
    lldb_savemat_command.__doc__ = '''savemat matfile var1 var2@1024, var3

  - var2@1024 - plot 1024 elements from var2 (note - this is required for pointer arrays)
'''

    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('command script add -f lldb_savemat.lldb_savemat_command savemat')
    print 'The "savemat" command has been installed, type "help savemat" or "savemat --help" for detailed help.'
# end __lldb_init_module
