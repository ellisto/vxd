#!/usr/bin/env python3

import curses
import sys
from blessed import Terminal
import functools

echo = functools.partial(print, end='', flush=True)

class vxd():
    def __init__(self, file=''):
        self.file = file
        self.statusline = "Opening {}...".format(self.file)
        self.term = Terminal()
        self.buf = None
        self.redraw()
        with open(file, 'rb') as f:
            self.buf = f.read()
            self.statusline += 'read {} bytes'.format(len(self.buf))
        if self.buf is not None:
            self.selected_byte = 0
        self.redraw()

    def clear(self):
        echo(self.term.clear)

    def redraw_status(self):
         with self.term.location(0, self.term.height):
             echo(self.statusline)

    def redraw(self):
        self.clear()
        self.redraw_status()
        self.printbuf()

    def printbuf(self):
        if self.buf is None:
            return
        bpl = 16
        height = self.term.height - 1
        numbytes = bpl * height
        asc_line = []
        bnum = 0
        with self.term.location(0,0):
            for i, b in enumerate(self.buf):
                if i == numbytes:
                    #bnum = i % bpl
                    #if bnum > 0:
                    #    echo(' ' * ((bpl-bnum) * 3 + 1) + ''.join(asc_line))
                    break
                bnum = i % bpl
                if bnum == 0:
                    echo('{:08x} '.format(i))
                echo('{:02x} '.format(b))
                #todo make nonprintables distinct from a literal '.' (maybe dim formatting?)
                asc_line.append(chr(b) if (b > 0x1f and b < 0x7f) else '.') 
                if bnum == bpl - 1: # time for new line
                    echo(' {}'.format(''.join(asc_line)))
                    asc_line.clear()
                    echo('\r\n')
            if len(asc_line) > 0:
                echo(' ' * ((bpl-bnum) * 3 + 1) + ''.join(asc_line))

            #echo(hexdump(self.buf[:400], 'return'))
        

    def bmain(self):
        self.redraw()
        term = self.term
        with term.hidden_cursor(), \
                term.location(), \
                term.fullscreen(), \
                term.cbreak(), \
                term.keypad():
            inp = None
            while True:
                inp = term.inkey()
                self.statusline = ''
                self.redraw()
                # q quits
                if inp == 'q':
                    break
        self.clear()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filepath>".format(sys.argv[0]))
        exit(1)
    #v = vxd('/home/tje/test.bin')
    filepath = sys.argv[1]
    v = vxd(filepath)
    v.bmain()
