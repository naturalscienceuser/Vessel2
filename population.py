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


def set_footer(custom_scr, grid, recording=False, reg="\""):
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
    menu_text = "OBJECT MENU".center(58) + "|\n"
    menu_text += "-"*58 + "|\n"
    # We turn it into a list basically just so we can slice it, such that it
    # only contains keybinds that correspond to object placements
    obj_key_pairs = [[obj_name, key] for obj_name, key in keybinds.items()][20:]
    for i, pair in enumerate(obj_key_pairs):
        justified_obj_name = pair[0].ljust(18)
        justified_keybinds = str(pair[1]).ljust(10)
        menu_text += f"{justified_obj_name.title()} {justified_keybinds}"
        if i % 2 != 0:
            menu_text += "|\n"
    # since it's 2 cols, we need to account for if there are an odd number of obj/key pairs
    if len(obj_key_pairs) % 2 != 0:
        menu_text += "\n"
    menu_text += "="*59 + "\n" + " "*59
    custom_scr.scr.addstr(menu_text)
    custom_scr.scr.move(initial_y, initial_x)

#    menu_text = f"Dash Refresher: {keybinds['dash refresh']} | Checkpoint: {keybinds['checkpoint']}\n"\
#                f"Shine Block: {keybinds['shine block']} | Bomb Block: {keybinds['bomb block']}\n"\
#                f"Metal Block: {keybinds['metal block']} | Fuse: {keybinds['fuse']}\n"\
#                f"Jump Pad: {keybinds['jump pad']} | Ice Block: {keybinds['ice block']}\n"\
#                f"Blue Switch Block: {keybinds['blue switch block']} | Red Switch Block: {keybinds['red switch block']}\n"\
#                f"Dark Block: {keybinds['dark block']}"
