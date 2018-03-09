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
        padding = (self.term.width - len(self.statusline)) * ' '
        with self.term.location(0, self.term.height):
             echo(self.statusline + padding)
             

    def redraw(self):
        self.redraw_status()
        self.printbuf()


    def last_displayed_byte(self):
        return self.first_displayed_byte + self.num_bytes_displayed() - 1

    def last_byte(self):
        return len(self.buf) - 1


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
                    echo(t.blue('{:08x} '.format(i + offset)))

                active = (i + offset == self.selected_byte) 
                h = '{:02x}'.format(b)
                sep = '  ' if bnum == bpl//2 - 1 else ' '
                echo('{}{}'.format(t.standout(h) if active else h, sep))
                char = t.bold(chr(b)) if (b > 0x1f and b < 0x7f) else t.dim('.')
                asc_line.append(t.standout(char) if active else char) 
                if bnum == bpl - 1: # time for new line
                    echo(' {}'.format(''.join(asc_line)))
                    asc_line.clear()
                    echo('\r\n')
            if len(asc_line) > 0:
                asc_padding =  ' ' * (bpl - len(asc_line))
                hex_padding = ' ' * ((bpl-bnum) * 3 + 1)
                echo(hex_padding + ''.join(asc_line) + asc_padding)


    def bmain(self):
        self.redraw()
        t = self.term
        with t.hidden_cursor(), \
                t.location(), \
                t.fullscreen(), \
                t.cbreak(), \
                t.keypad():
            inp = None
            while True:
                inp = t.inkey()
                self.statusline = ''
                old_byte = self.selected_byte
                # q quits
                if inp == 'q':
                    break
                # hjkl or arrow keys move cursor
                elif inp == 'h' or inp.code == t.KEY_LEFT:
                    self.selected_byte -= 1 if self.selected_byte > 0 else 0
                elif inp == 'l' or inp.code  == t.KEY_RIGHT:
                    self.selected_byte += 1 if self.selected_byte < self.last_byte() else 0
                elif inp == 'j' or inp.code  == t.KEY_DOWN:
                    self.selected_byte += self.bpl if (self.selected_byte + self.bpl < self.last_byte()) else 0
                elif inp == 'k' or inp.code  == t.KEY_UP:
                    self.selected_byte -= self.bpl if (self.selected_byte - self.bpl >= 0 ) else 0
                # g or home go to beginning 
                elif inp == 'g' or inp.code  == t.KEY_HOME:
                    self.selected_byte = 0
                # G or end go to end
                elif inp == 'G' or inp.code  == t.KEY_END:
                    self.selected_byte = self.last_byte()

                if self.selected_byte != old_byte:
                    self.statusline = 'byte {b} (0x{b:x}) / {l} (0x{l:x})'.format(
                            b=self.selected_byte, l=self.last_byte())
                    self.redraw()

        self.clear()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filepath>".format(sys.argv[0]))
        exit(1)

    filepath = sys.argv[1]
    v = vxd(filepath)
    v.bmain()
