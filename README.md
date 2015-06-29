# lldb-plot
Plotting Utilities for LLDB

This is a basic set of commands for plotting from lldb. 

For a more mature set of plotting utilities for gdb, see:

https://github.com/flailingsquirrel/gdb-plot

= HOWTO = 

- import the module::

    command script import ../lldbplot.py

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

= Known Issues =

- limited type support: int, double, float  (more to come)
- need better synax on command line
- better figures with titles and legends
