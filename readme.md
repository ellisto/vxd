VXD (Vim-like heX eDitor)
======================================
VXD is a curses-based console hex viewer with vimlike key bindings.

Eventually, it will have support for editing as well.

Key Bindings
---------------------------------------
Key | function
----|----------
q   | quit
h   | move left
l   | move right
j   | move down
k   | move up
g   | go to beginning of file
G   | go to end of file
n   | goto next diff
N   | goto previous diff


TODO
---------------------------------------
 - Editor capability
 - Fix flickering on some terminals
 - go to specific offset
 - colors
 - open new file from inside vxd (`o`)
 - buffered file reading to handle large files
 - selection of multiple bytes (w/count)
 - searching (hex or ascii)
 - struct/templates!?
 - vertical split diffing
 - specify endianness of value preview
 - additional value preview types
