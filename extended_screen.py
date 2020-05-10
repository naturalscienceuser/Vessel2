import curses

"""
There are a lot of functions which need access to values which are 
derived from methods of the curses screen object, and which also need access
to other methods of that object. So I made this object to encapsulate the 
curses screen object with those attributes
"""

class ExtendedScreen:
    def __init__(self, cell_top, cell_bottom, empty_val, full_val, oob_val):
        self.scr = curses.initscr()
        self.screen_h, self.screen_w = self.scr.getmaxyx()
        self.cell_top = cell_top
        self.cell_bottom = cell_bottom
        self.cell_w = len(cell_top)
        self.cell_h = 2
        self.full_val = full_val
        self.empty_val = empty_val
        self.oob_val = oob_val
        self.orig_x, self.orig_y = int(self.cell_w / 2), int(self.cell_h / 2)
        self.cells_in_row = int(self.screen_w / self.cell_w) - 1
        self.cells_in_col = int(self.screen_h / self.cell_h) - 1

