from curses import wrapper
from grid import Grid
from write_out import write_out
from os import path
from cells_to_grid import set_obj_cells, set_collis_cells
from display import draw_cell_boundaries, populate_screen_cells, set_footer, menu, prompt
from handle_keystrokes import handle_movement, change_settings, change_obj_offset, change_obj_properties, place_obj_or_collis
from extended_screen import ExtendedScreen
from settings import mappings_to_keys, movement_keys, symbols, obj_symbols_list, obj_names, keys_to_mappings
from level_file import LevelFile
from conversions import to_grid_xy
import sys

def log_var(in_var):
    with open("test.txt", "w") as f:
        print(in_var, file=f)

if len(sys.argv) <= 1:
    print("Please include a path to the file you would like to edit")
    sys.exit()

filepath = sys.argv[1]
if not path.exists(filepath):
    raise IOError("File not found!")
    sys.exit(1)

level_file = LevelFile(filepath)
grid = Grid(level_file.w_blocks, level_file.h_blocks)

# Fill up the grid
set_collis_cells(level_file, grid)
set_obj_cells(level_file, grid)
grid.set_point(level_file.spawn_coords[0], level_file.spawn_coords[1], symbols["spawn"])
grid.set_point(level_file.goal_coords[0], level_file.goal_coords[1], symbols["goal"])
grid.set_point(level_file.coin_coords[0], level_file.coin_coords[1], symbols["coin"])

# Now that we know prior coords, we can clear groups of level file. Previous objects are in grid, so
# They will be written back out anyway. This way the write_out() function does not have to know anything
# about prior objects, it just writes out everything that was in the grid. That makes it easier to code.
level_file.clear_groups()

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

        # If they press an unmapped key, just do nothing
        try:
            mapping = keys_to_mappings[key]
        except KeyError:
            continue

        if mapping == "quit":
            break

        elif mapping == "record":
            recording = not recording
            if recording:
                recorded_keys[register] = []

        if recording and mapping not in ("record", "change register"):
            recorded_keys[register].append(key)

        elif mapping == "playback":
            playing_back = True
            continue  # do we need this? alternatively, should they all have continues?

        if mapping == "change register":
            register = custom_scr.scr.getkey()

        elif key in movement_keys:
            handle_movement(custom_scr, grid, key)

        elif mapping == "settings menu":
            change_settings(custom_scr, grid, level_file)

        elif mapping == "object menu":
            designated_char_index = menu(custom_scr, "OBJECT MENU (q quits)", obj_names)
            if not designated_char_index is None:
                designated_char = obj_symbols_list[designated_char_index]

        elif mapping == "collision mode":
            designated_char = symbols["collision"]

        elif mapping == "rename":
            level_file.new_name = prompt(custom_scr, "Enter a new name: ")

        grid_x, grid_y = to_grid_xy(custom_scr)
        try:
            cell_contents = grid.get_point(grid_x + grid.x_offset, grid_y + grid.y_offset)
        except IndexError:
            cell_contents = symbols["out of bounds"]

        if mapping == "place":
            place_obj_or_collis(custom_scr, grid, designated_char, cell_contents)

        if mapping == "position":
            change_obj_offset(custom_scr, grid, cell_contents)

        elif mapping == "properties":
            change_obj_properties(custom_scr, grid, cell_contents)

        cell_contents = grid.get_point(grid_x + grid.x_offset, grid_y + grid.y_offset)
        set_footer(custom_scr, grid, recording, register, cell_contents[2:])

        if not playing_back:  # Whether or not we have this if here is really a matter of taste
            populate_screen_cells(custom_scr, grid)
            custom_scr.scr.refresh()

wrapper(main)  # putting main in wrapper takes care of reconfiguring stuff if crashes occur
write_out(level_file, grid)
