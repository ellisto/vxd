#!/usr/bin/env python3

import curses
import sys
from blessed import Terminal
import functools

echo = functools.partial(print, end='', flush=True)

class vxd():
    def __init__(self, filepath='', bpl=16):
        self.file = filepath
        self.bpl = bpl
        self.statusline = "Opening {}...".format(self.file)
        self.term = Terminal()
        self.buf = None
        self.redraw()
        with open(self.file, 'rb') as f:
            self.buf = f.read()
        if self.buf is not None:
            self.selected_byte = 0
            self.first_displayed_byte = 0
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


    def last_displayed_byte(self):
        return self.first_displayed_byte + self.num_bytes_displayed() - 1


    def num_bytes_displayed(self):
        height = self.term.height - 1
        return self.bpl * height


    def row_of(self, byteidx):
        return byteidx // self.bpl


    def printbuf(self):
        if self.buf is None:
            return
        bpl = self.bpl
        asc_line = []
        numbytes = self.num_bytes_displayed()
        first_displayed_row = self.row_of(self.first_displayed_byte)
        last_displayed_row = self.row_of(self.last_displayed_byte())
        selected_row = self.row_of(self.selected_byte)
        if selected_row > last_displayed_row:
            rows_to_scroll = selected_row - last_displayed_row
            self.first_displayed_byte += bpl * rows_to_scroll
        elif selected_row < first_displayed_row:
            rows_to_scroll = first_displayed_row - selected_row
            self.first_displayed_byte -= bpl * rows_to_scroll

        offset = self.first_displayed_byte
        bnum = 0
        t = self.term
        with self.term.location(0,0):
            for i, b in enumerate(self.buf[offset:]):
                if i == numbytes:
                    break
                bnum = i % bpl
                if bnum == 0:
                    echo('{:08x} '.format(i + offset))

                active = (i + offset == self.selected_byte) 
                h = '{:02x}'.format(b)
                echo('{} '.format(t.standout(h) if active else h))
                char = t.bold(chr(b)) if (b > 0x1f and b < 0x7f) else t.dim('.')
                asc_line.append(t.standout(char) if active else char) 
                if bnum == bpl - 1: # time for new line
                    echo(' {}'.format(''.join(asc_line)))
                    asc_line.clear()
                    echo('\r\n')
            if len(asc_line) > 0:
                echo(' ' * ((bpl-bnum) * 3 + 1) + ''.join(asc_line))


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
                old_byte = self.selected_byte
                # q quits
                if inp == 'q':
                    break
                elif inp == 'h':
                    self.selected_byte -= 1 if self.selected_byte > 0 else 0
                elif inp == 'l':
                    self.selected_byte += 1 if self.selected_byte < len(self.buf) else 0
                elif inp == 'j':
                    self.selected_byte += self.bpl if (self.selected_byte + self.bpl < len(self.buf)) else 0
                elif inp == 'k':
                    self.selected_byte -= self.bpl if (self.selected_byte - self.bpl >= 0 ) else 0
                elif inp == 'g':
                    self.selected_byte = 0
                elif inp == 'G':
                    self.selected_byte = len(self.buf) - 1

                if self.selected_byte != old_byte:
                    self.statusline = 'byte {b} (0x{b:x}) / {l} (0x{l:x})\t\tdisplayed:({first:x},{last:x})'.format(
                            b=self.selected_byte, l=len(self.buf),
                            first = self.first_displayed_byte,
                            last = self.last_displayed_byte()
                            )

                self.redraw()
        self.clear()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filepath>".format(sys.argv[0]))
        exit(1)

    filepath = sys.argv[1]
    v = vxd(filepath)
    v.bmain()
