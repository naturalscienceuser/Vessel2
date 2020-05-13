from curses import wrapper
from grid import Grid
from write_out import write_out
from os import path
from cells_to_grid import set_obj_cells, set_collis_cells#, return_spawn_coords, return_goal_coords, return_coin_coords
from display import draw_cell_boundaries, populate_screen_cells, set_footer, menu, prompt, set_cell
from handle_keystrokes import handle_movement, change_settings, change_obj_offset, change_obj_properties, place_obj_or_collis
from extended_screen import ExtendedScreen
from settings import keybinds, movement_keys, symbols, obj_symbols_list, obj_names
from level_file import LevelFile
from conversions import to_grid_xy
import sys

def log_var(in_var):
    with open("test.txt", "w") as f:
        print(in_var, file=f)

filepath = sys.argv[1]  # 0st item is name of script, so index 1 is the first actual argument
if not path.exists(filepath):
    raise IOError("File not found!")

level_file = LevelFile(filepath)
grid = Grid(level_file.w_blocks, level_file.h_blocks)

# Fill up the grid
set_collis_cells(level_file, grid)
set_obj_cells(level_file, grid)
grid.set_point(level_file.spawn_coords[0], level_file.spawn_coords[1], symbols["spawn"])
grid.set_point(level_file.goal_coords[0], level_file.goal_coords[1], symbols["goal"])
grid.set_point(level_file.coin_coords[0], level_file.coin_coords[1], symbols["coin"])

# Now that we know prior coords, we can clear stacks of level file. Previous objects are in grid, so
# They will be written back out anyway. This way the write_out() function does not have to know anything
# about prior objects, it just writes out everything that was in the grid. That makes it easier to code.
level_file.clear_stacks()

cell_top_str = "+---"
cell_bottom_str = "| " + symbols["empty space"] + " "

custom_scr = ExtendedScreen(
        cell_top_str, cell_bottom_str, symbols["empty space"], 
        symbols["collision"], symbols["out of bounds"]
        )

def main(screen):
    draw_cell_boundaries(custom_scr)
    custom_scr.scr.move(custom_scr.orig_y, custom_scr.orig_x)
    recording = False
    playing_back = False
    recorded_keys = {}
    register = "\""
    key_index = 0
    designated_char = symbols["collision"]
    populate_screen_cells(custom_scr, grid)
    while True:
        if not playing_back:
            key = custom_scr.scr.getkey()
        else:
            try:
                key = recorded_keys[register][key_index]
            # We are out of keys to playback (IndexError) or user
            # never recorded any to that register (KeyError)
            except (IndexError, KeyError):
                playing_back = False
                key_index = 0
                continue
            key_index += 1

        if key in keybinds["quit"]:
            break

        elif key in keybinds["record"]:
            recording = not recording
            if recording:
                recorded_keys[register] = []

        if(recording and key not in keybinds["record"] 
        and key not in keybinds["change register"]):
            recorded_keys[register].append(key)

        elif key in keybinds["playback"]:
            playing_back = True
            continue  # do we need this? alternatively, should they all have continues?

        if key in keybinds["change register"]:
            register = custom_scr.scr.getkey()

        elif key in movement_keys:
            handle_movement(custom_scr, grid, key)

        elif key in keybinds["settings menu"]:
            change_settings(custom_scr, level_file)

        elif key in keybinds["object menu"]:
            designated_char_index = menu(custom_scr, "OBJECT MENU", obj_names)
            designated_char = obj_symbols_list[designated_char_index]

        elif key in keybinds["collision mode"]:
            designated_char = symbols["collision"]

        grid_x, grid_y = to_grid_xy(custom_scr)
        try:
            cell_contents = grid.get_point(grid_x + grid.x_offset, grid_y + grid.y_offset)
        except IndexError:
            cell_contents = symbols["out of bounds"]

        if key in keybinds["place"]:
            place_obj_or_collis(custom_scr, grid, designated_char, cell_contents)

        if key in keybinds["position"]:
            change_obj_offset(custom_scr, grid, cell_contents)

        elif key in keybinds["properties"]:
            change_obj_properties(custom_scr, grid, cell_contents)

        set_footer(custom_scr, grid, recording, register, cell_contents[2:])

        if not playing_back:  # Whether or not we have this if here is really a matter of taste
            populate_screen_cells(custom_scr, grid)
            custom_scr.scr.refresh()

wrapper(main)  # putting main in wrapper takes care of reconfiguring stuff if crashes occur
write_out(level_file, grid)
