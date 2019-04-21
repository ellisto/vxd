VXD (Vim-like heX Diff)
======================================
VXD is a curses-based console hex viewer and differ with vimlike key bindings.

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
 - value preview (value of a int/uint/etc at the current offset)
 - struct/templates!?
 - vertical split diffing
