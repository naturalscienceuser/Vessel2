from movement import shift_cursor, move_to_row_pos, move_to_col_pos
from settings import mappings_to_keys, symbols, keys_to_mappings
from conversions import to_grid_xy
from display import set_cell, menu, prompt
import sys
from functools import partial
from curses import error

def handle_movement(custom_scr, grid, in_key):
    initial_y, initial_x = custom_scr.scr.getyx()
    mapping = keys_to_mappings[in_key]
    mappings_to_actions = {
            "column start": partial(move_to_col_pos, custom_scr, "first cell"),
            "column middle": partial(move_to_col_pos, custom_scr, "mid"),
            "column end": partial(move_to_col_pos, custom_scr, "end"),
            "row start": partial(move_to_row_pos, custom_scr, "first cell"),
            "row middle": partial(move_to_row_pos, custom_scr, "mid"),
            "row end": partial(move_to_row_pos, custom_scr, "end"),
            "shift up": partial(grid.change_y_offset, -1),
            "shift left": partial(grid.change_x_offset, -1),
            "shift right": partial(grid.change_x_offset, 1),
            "shift down": partial(grid.change_y_offset, 1),
            "up": partial(shift_cursor, custom_scr, "up", custom_scr.cell_h),
            "down": partial(shift_cursor, custom_scr, "down", custom_scr.cell_h),
            "left": partial(shift_cursor, custom_scr, "left", custom_scr.cell_w),
            "right": partial(shift_cursor, custom_scr, "right", custom_scr.cell_w),
            }
    try:
        mappings_to_actions[mapping]()
    except error:  # move cursor to negative coordinates
        if in_key in mappings_to_keys["up"] and grid.y_offset > 0:
            grid.y_offset -= 1
        elif in_key in mappings_to_keys["left"] and grid.x_offset > 0:
            grid.x_offset -= 1
        custom_scr.scr.move(initial_y, initial_x)
        return

    grid_x, grid_y = to_grid_xy(custom_scr)
    # moving cursor past end of screen row
    if grid_x > custom_scr.cells_in_row - 1:
        grid.x_offset += 1
        custom_scr.scr.move(initial_y, initial_x)
    # moving cursor past end of screen col
    elif grid_y > custom_scr.cells_in_col - 1:
        grid.y_offset += 1
        custom_scr.scr.move(initial_y, initial_x)


def change_settings(custom_scr, grid, level_file):
    item_num = menu(custom_scr, "SETTINGS (q quits)", level_file.setting_names)
    if item_num is None:
        return
    val_for_setting = float(prompt(custom_scr))
    previous_spawn, previous_goal, previous_coin = \
            level_file.spawn_coords, level_file.goal_coords, level_file.coin_coords
    level_file.set_setting(item_num, val_for_setting)
    if item_num in (0, 8):
        grid.set_point(previous_spawn[0], previous_spawn[1], symbols["empty space"])
        grid.set_point(level_file.spawn_coords[0], level_file.spawn_coords[1], symbols["spawn"])
    elif item_num in (3, 9):
        grid.set_point(previous_goal[0], previous_goal[1], symbols["empty space"])
        grid.set_point(level_file.goal_coords[0], level_file.goal_coords[1], symbols["goal"])
    elif item_num in (6, 12):
        grid.set_point(previous_coin[0], previous_coin[1], symbols["empty space"])
        grid.set_point(level_file.coin_coords[0], level_file.coin_coords[1], symbols["coin"])


def change_obj_offset(custom_scr, grid, cell_contents):
    # cell_contents is literally the contents of the cell in the grid object
    # under the cursor, eg. m,0,0,1,0,0,0,0,1
    x_offset = prompt(custom_scr, prompt_text="Enter x: ").decode()
    y_offset = prompt(custom_scr, prompt_text="Enter y: ").decode()
    icon, properties = cell_contents[0], cell_contents[6:]
    cell_contents = f"{icon},{x_offset},{y_offset},{properties}"
    set_cell(custom_scr, grid, cell_contents) 


def change_obj_properties(custom_scr, grid, cell_contents):
    # cell_contents is literally the contents of the cell in the grid object
    # under the cursor, eg. m,0,0,1,0,0,0,0,1
    icon, offsets = cell_contents[0], cell_contents[2:5]
    properties = []
    for i in range(1, 7):
        property_val = prompt(custom_scr, prompt_text=f"Enter property {str(i)}: ").decode()
        properties.append(property_val)
    properties_str = ",".join(properties)
    cell_contents = f"{icon},{offsets},{properties_str}"
    set_cell(custom_scr, grid, cell_contents)


def place_obj_or_collis(custom_scr, grid, designated_char, cell_contents):
    data = ""
    # If placing an object, add these numbers to represent x and y
    # offset followed by its 6 additional properties
    if designated_char not in symbols["collision"]:
        data = ",0,0,1,0,0,0,0,1"

    def is_changeable(in_char):
        return in_char not in (
                symbols["spawn"], symbols["goal"], 
                symbols["coin"], symbols["out of bounds"]
                )

    try:
        if cell_contents[0] == designated_char:
            set_cell(custom_scr, grid, symbols["empty space"])
        elif is_changeable(cell_contents[0]):
            set_cell(custom_scr, grid, designated_char + data)
    except IndexError:  # Tried to place terrain out of bounds
        pass

