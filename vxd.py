#!/usr/bin/env python3

import sys
import time
from blessed import Terminal
import functools

echo = functools.partial(print, end='', flush=True)

class vxd():
    def __init__(self, filepath='', filepath2=None, bpl=16, debug_log=False):
        self.debug_log = debug_log
        self.file = filepath
        self.file2 = filepath2
        self.bpl = bpl
        self.statusline = "Opening {}...".format(self.file)
        self.statusline2 = None
        if self.file2:
            self.statusline2 = "Opening {}...".format(self.file2)
        self.term = Terminal()
        self.buf = None
        self.buf2 = None
        self.first_displayed_byte = 0
        self.redraw()

        # TODO: don't read the whole file in; this would be bad on big files
        with open(self.file, 'rb') as f:
            self.buf = f.read()

        if self.file2:
            with open(self.file2, 'rb') as f:
                self.buf2 = f.read()
            self.statusline2 = ''

        if self.buf:
            self.selected_byte = 0

        self.redraw()


    def debug(self, msg):
        if self.debug_log:
            with open('log.txt', 'a') as f:
                f.write("[{}] {}\n".format(time.asctime(), msg))

    def clear(self):
        ''' clear screen '''
        echo(self.term.clear)


    def redraw_status(self):
        ''' redraw both statuslines '''

        self.print_statusline(self.statusline,
                              self.term.height if self.statusline2 is None
                              else self.second_buf_start() - 1, self.file)

        if self.statusline2 is not None:
            self.print_statusline(self.statusline2, self.term.height, self.file2)

    def print_statusline(self, statusline, row, filename=None):
        '''print statusline at specified row.
           prepend filename to statusline if provided
        '''
        if filename:
            statusline = "{}: {}".format(filename, statusline)

        padding = (self.term.width - len(statusline)) * ' '

        with self.term.location(0, row):
             echo(statusline + padding)

    def redraw(self):
        ''' redraw the screen '''
        self.redraw_status()
        self.printbuf(self.buf, self.buf2)
        if self.buf2:
            row_offset = self.second_buf_start()
            self.printbuf(self.buf2, self.buf, row_offset)

    def second_buf_start(self):
        return (self.term.height // 2)

    def last_displayed_byte(self):
        ''' return the index of the last byte displayed onscreen '''
        val = self.first_displayed_byte + self.num_bytes_displayed() - 1
        self.debug("last_displayed_byte = {} + {} - 1 = {:x}".format(self.first_displayed_byte, self.num_bytes_displayed(), val))
        return val

    def last_byte(self):
        ''' return the index of the last byte in the active buffer'''
        return len(self.buf) - 1

    def last_displayed_row(self):
        ''' return the index of the row containing the last displayed byte'''
        val = self.row_of(self.last_displayed_byte())
        self.debug("last_displayed_row: {}".format(val))
        return val

    def num_bytes_displayed(self):
        ''' return the number of bytes displayed from a single buf on the
            screen at one time
        '''
        height = self.term.height - 1
        if self.file2:
            height -= 1 # leave room for a second filename line
            height //= 2 # second file takes half the screen
        val = self.bpl * height
        return val


    def row_of(self, byteidx):
        ''' return the row number containing the byte at specified index '''
        return byteidx // self.bpl


    def printbuf(self, buf, diff=None, row_offset=0):
        ''' Print specified buffer with hex and ascii.
            If row_offset is specified, start at that offset down the screen
            otherwise buffer will be printed starting at the first row of the
            terminal
        '''
        if buf is None:
            return
        bpl = self.bpl
        asc_line = []
        numbytes = self.num_bytes_displayed()
        first_displayed_row = self.row_of(self.first_displayed_byte)
        last_displayed_row = self.last_displayed_row()
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
        self.debug("offset: {}".format(row_offset))
        self.debug("row_offset: {}".format(row_offset))
        with self.term.location(0, row_offset):
            for i, b in enumerate(buf[offset:]):
                if i == numbytes:
                    break
                bnum = i % bpl
                if bnum == 0:
                    echo(t.blue('{:08x} '.format(i + offset)))

                active = (i + offset == self.selected_byte)
                h = '{:02x}'.format(b)
                sep = '  ' if bnum == bpl//2 - 1 else ' '
                char = t.bold(chr(b)) if (b > 0x1f and b < 0x7f) else t.dim('.')
                if diff:
                    if i < len(diff) and b != diff[i]:
                        char = t.red(char)
                        h = t.red(h)
                echo('{}{}'.format(t.standout(h) if active else h, sep))
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
        self.clear()
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
                    self.selected_byte += self.bpl if (self.selected_byte + self.bpl <= self.last_byte()) else 0
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
                    self.statusline2 = self.statusline
                    self.redraw()

        self.clear()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filepath> [<filepath-to-diff>]".format(sys.argv[0]))
        exit(1)

    filepath = sys.argv[1]
    filepath2 = None
    if len(sys.argv) > 2:
        filepath2 = sys.argv[2]

    v = vxd(filepath, filepath2)
    v.bmain()
