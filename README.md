# lldb-plot
Plotting Utilities for LLDB

This is a basic set of commands for plotting from lldb. It also includes the ability to save arbitary buffers to mat files.

For a more mature set of plotting utilities for gdb, see:

https://github.com/flailingsquirrel/gdb-plot

NOTE FOR Mac OS X Users:
=======================

Apple integrates a busted old python.  If you install a newer python version, set your PYTHONHOME environment variable.  Example:

export PYTHONHOME=~/anaconda/

= HOWTO = 

- import the module::

    - plotter:
        command script import lldb_plot.py

    - mat file writer:
        command script import lldb_savemat.py

- plot stuff

    - example cpp provided has several buffers you can plot:

    - raw pointer array (must specify end):
    plot d@1024

    - stl vector
    plot z

    - fixed length array
    plot e

    - plot several:
    plot e z d@1024

- save to mat file

    savemat <matfile> buf1 buf2 buf3...

    example:
        savemat mat_out d@1024 e z

= Known Issues =

- limited type support: int, double, float  (more to come)
- need better synax on command line
- better figures with titles and legends
