from movement import shift_cursor, move_to_row_pos, move_to_col_pos
from settings import keybinds, placement_keys, placement_key_symbols, symbols
from conversions import to_grid_xy
from population import set_cell
import sys

def log_var(in_var):
    with open("test.txt", "w") as f:
        print(in_var, file=f)

def handle_movement(custom_scr, grid, in_key):
    initial_y, initial_x = custom_scr.scr.getyx()
    if in_key in keybinds["column start"]:
        move_to_col_pos(custom_scr, "first cell")
    elif in_key in keybinds["column middle"]:
        move_to_col_pos(custom_scr, "mid")
    elif in_key in keybinds["column end"]:
        move_to_col_pos(custom_scr, "end")
    elif in_key in keybinds["row start"]:
        move_to_row_pos(custom_scr, "first cell")
    elif in_key in keybinds["row middle"]:
        move_to_row_pos(custom_scr, "mid")
    elif in_key in keybinds["row end"]:
        move_to_row_pos(custom_scr, "end")
    if in_key in keybinds["shift up"]:
        grid.y_offset -= 1
    elif in_key in keybinds["shift left"]:
        grid.x_offset -= 1
    elif in_key in keybinds["shift right"]:
        grid.x_offset += 1
    elif in_key in keybinds["shift down"]:
        grid.y_offset += 1
    try:
        if in_key in keybinds["up"]:
            shift_cursor(custom_scr, "up", custom_scr.cell_h)
        elif in_key in keybinds["down"]:
            shift_cursor(custom_scr, "down", custom_scr.cell_h)
        elif in_key in keybinds["left"]:
            shift_cursor(custom_scr, "left", custom_scr.cell_w)
        elif in_key in keybinds["right"]:
            shift_cursor(custom_scr, "right", custom_scr.cell_w)
    except:  # moving cursor to negative coordinates
        if in_key in keybinds["up"] and grid.y_offset > 0:
            grid.y_offset -= 1
        elif in_key in keybinds["left"] and grid.x_offset > 0:
            grid.x_offset -= 1
        custom_scr.scr.move(initial_y, initial_x)
        return

    grid_x, grid_y = to_grid_xy(custom_scr)
    if grid_x > custom_scr.cells_in_row - 1:  # moving cursor past end of screen row
        grid.x_offset += 1
        custom_scr.scr.move(initial_y, initial_x)
    elif grid_y > custom_scr.cells_in_col - 1:  # moving cursor past end of screen col
        grid.y_offset += 1
        custom_scr.scr.move(initial_y, initial_x)

def toggle_cell_contents(custom_scr, grid, in_char):
    initial_y, initial_x = custom_scr.scr.getyx()
    grid_x, grid_y = to_grid_xy(custom_scr, initial_x, initial_y)
    try:
        symbol_at_pt = grid.get_point(grid_x + grid.x_offset, grid_y + grid.y_offset)[0]
        if symbol_at_pt == in_char[0]:
            set_cell(custom_scr, grid, symbols["empty space"])
        # Can't place over coin, goal, or spawn
        elif symbol_at_pt not in (symbols["spawn"], symbols["goal"], symbols["coin"]):
            set_cell(custom_scr, grid, in_char)
    except IndexError:  # Tried to place terrain out of bounds
        pass
