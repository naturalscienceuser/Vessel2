import curses
from curses import wrapper
import mmap
from grid import Grid
from write_out import write_out
from os import path
from cells_to_grid import return_all_collis_coords, return_obj_coords
from population import draw_cell_boundaries, populate_screen_cells, set_footer, menu, prompt
from handle_keystrokes import handle_movement, place_char
from extended_screen import ExtendedScreen
from level_object import LevelObject
from settings import keybinds, movement_keys, symbols, obj_symbols_list
from level_file import LevelFile
import sys

def log_var(in_var):
    with open("test.txt", "w") as f:
        print(in_var, file=f)

filepath = sys.argv[1]  # 0st item is name of script, so index 1 is the first actual argument
if not path.exists(filepath):
    raise IOError("File not found!")

w_pix = int(sys.argv[2])
h_pix = int(sys.argv[3])
w_blocks = int(w_pix / 16)
h_blocks = int(h_pix / 16)

grid = Grid(w_blocks, h_blocks)
level_file = LevelFile(w_pix, h_pix, filepath)
with open(filepath, "r+b") as f:
    mm = mmap.mmap(f.fileno(), length=0)
    prior_collis_coordinates = return_all_collis_coords(level_file)
    prior_obj_coords = return_obj_coords(level_file)  # [[xpos, ypos, symbol], [xpos, ypos, symbol], ...]
    # Now that we know prior coords, we can clear stacks of level file. Previous objects are in grid, so
    # They will be written back out anyway. This way the write_out() function does not have to know anything
    # about prior objects, it just writes out everything that was in the grid. That makes it easier to code.
    level_file.clear_stacks()
for collis_coordpair in prior_collis_coordinates:
    grid.set_point(int(collis_coordpair[0]), int(collis_coordpair[1]), symbols["collision"])
for obj_coordset in prior_obj_coords:
    grid.set_point(obj_coordset[0], obj_coordset[1], obj_coordset[2])

cell_top_str = "+---"
cell_bottom_str = "| " + symbols["empty space"] + " "

custom_scr = ExtendedScreen(cell_top_str, cell_bottom_str, symbols["empty space"], symbols["collision"], symbols["out of bounds"])

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
            item_num = menu(custom_scr, "SETTINGS", level_file.setting_names)  # maybe make the menu function figure out the labels based on title?
            val_for_option = int(prompt(custom_scr))
            level_file.set_option(item_num, val_for_option)

        elif key in keybinds["object menu"]:
            obj_names = [symbol_name for symbol_name in symbols.keys()][3:]
            designated_char_index = menu(custom_scr, "OBJECT MENU", obj_names)
            designated_char = obj_symbols_list[designated_char_index]

        elif key in keybinds["place"]:
            place_char(custom_scr, grid, designated_char)

        set_footer(custom_scr, grid, recording, register)
        if not playing_back:  # Whether or not we have this if here is really a matter of taste
            populate_screen_cells(custom_scr, grid)
            custom_scr.scr.refresh()

wrapper(main)  # putting main in wrapper takes care of reconfiguring stuff if crashes occur
write_out(level_file, grid)
