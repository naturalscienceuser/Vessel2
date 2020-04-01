from preserve_pos import preserve_pos
from movement import *
from conversions import *
from settings import keybinds
from curses import error

def draw_cell_boundaries(custom_scr):
    initial_y, initial_x = custom_scr.scr.getyx()
    custom_scr.scr.move(0,0)

    def add_row(custom_scr, row_str):
        for i in range(custom_scr.screen_w // len(row_str) - 1):
            custom_scr.scr.addstr(row_str)

    for i in range(int(custom_scr.screen_h / custom_scr.cell_h - 1)):  
        add_row(custom_scr, custom_scr.cell_top)
        shift_cursor(custom_scr, "down")
        move_to_row_pos(custom_scr, "start")
        add_row(custom_scr, custom_scr.cell_bottom)
        shift_cursor(custom_scr, "down")
        move_to_row_pos(custom_scr, "start")

    custom_scr.scr.move(initial_y, initial_x)


def populate_screen_cells(custom_scr, grid):

    def populate_row(custom_scr, grid, in_row_num):
        for col in range(custom_scr.cells_in_row):
            try:
                if col + grid.x_offset < 0 or in_row_num + grid.y_offset < 0:
                    raise IndexError  # Coordinates are negative, ergo oob
                custom_scr.scr.addstr(grid.get_point(col + grid.x_offset, in_row_num + grid.y_offset))
            except IndexError:  # Occurs if coordinates are negative or larger than grid size
                custom_scr.scr.addstr(custom_scr.oob_val)
            shift_cursor(custom_scr, "right", custom_scr.cell_w - 1)

    initial_y, initial_x = custom_scr.scr.getyx()
    custom_scr.scr.move(custom_scr.orig_y, custom_scr.orig_x)
    for row in range(custom_scr.cells_in_col):
        populate_row(custom_scr, grid, row)
        shift_cursor(custom_scr, "down", custom_scr.cell_h)
        move_to_column_1(custom_scr)
    custom_scr.scr.move(initial_y, initial_x)


# NOTE: we probably don't want the menu param at all, I think it is better to make the menu in another func
def set_footer(custom_scr, grid, recording=False, reg="\"", menu=False):
    initial_y, initial_x = custom_scr.scr.getyx()
    grid_x, grid_y = to_grid_xy(custom_scr)
    display_x = grid_x + grid.x_offset
    display_y = grid_y + grid.y_offset
    # if not menu
    display_str = f"({display_x}, {display_y})".ljust(10)
    display_str += f" reg: {reg} "
    if recording:
        display_str += "recording"
    else:
        display_str += " " * len("recording")
    custom_scr.scr.addstr(custom_scr.screen_h - 3, 0, display_str)
    custom_scr.scr.move(initial_y, initial_x)


def set_cell(custom_scr, grid, in_val, cell_x=None, cell_y=None):
    initial_y, initial_x = custom_scr.scr.getyx()
    if cell_x is None and cell_y is None:
        screen_y, screen_x = custom_scr.scr.getyx()
    else:
        screen_x, screen_y = to_screen_xy(custom_scr, cell_x, cell_y) 
    custom_scr.scr.addstr(screen_y, screen_x, in_val) 
    grid_x, grid_y = to_grid_xy(custom_scr, screen_x, screen_y)
    grid_x += grid.x_offset
    grid_y += grid.y_offset
    grid.set_point(grid_x, grid_y, in_val)
    custom_scr.scr.move(initial_y, initial_x)


def display_menu(custom_scr):
    initial_y, initial_x = custom_scr.scr.getyx()
    custom_scr.scr.move(0,0)
    custom_scr.scr.addstr("MEOW MEOW QUACK")
    custom_scr.scr.move(initial_y, initial_x)
