#!/usr/bin/env python3

import curses
import sys
from hexdump import hexdump
from blessed import Terminal
import functools

echo = functools.partial(print, end='', flush=True)

class vxd():
    def __init__(self, file=''):
        self.file = file
        self.statusline = "Opening {}...".format(self.file)
        self.term = Terminal()
        with open(file, 'rb') as f:
            self.buf = f.read(400)

    def clear(self):
        echo(self.term.clear)

    def redraw_status(self):
         with self.term.location(0, self.term.height):
             self.term.clear_eos()
             print(self.statusline)


    def redraw(self):
        self.clear()
        self.redraw_status()
        self.printbuf()

    def printbuf(self):
        with self.term.location(0,0):
            print(hexdump(self.buf, 'return'))
        

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
                # q quits
                if inp == 'q':
                    break
                elif inp == 'r':
                    self.redraw()
        self.clear()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filepath>".format(sys.argv[0]))
        exit(1)
    #v = vxd('/home/tje/test.bin')
    filepath = sys.argv[1]
    v = vxd(filepath)
    v.bmain()
