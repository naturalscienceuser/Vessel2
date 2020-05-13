from movement import shift_cursor, move_to_row_pos, move_to_col_pos
from settings import keybinds, symbols
from conversions import to_grid_xy
from population import set_cell, menu, prompt
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

def change_settings(custom_scr, level_file):
    item_num = menu(custom_scr, "SETTINGS", level_file.setting_names)
    val_for_option = int(prompt(custom_scr))
    previous_spawn, previous_goal, previous_coin = \
            level_file.spawn_coords, level_file.goal_coords, level_file.coin_coords
    level_file.set_option(item_num, val_for_option)
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
    x_offset = prompt(custom_scr, prompt_text="Enter x: ").decode()
    y_offset = prompt(custom_scr, prompt_text="Enter y: ").decode()
    icon, properties = cell_contents[0], cell_contents[6:]
    cell_contents = f"{icon},{x_offset},{y_offset},{properties}"
    set_cell(custom_scr, grid, cell_contents) 

