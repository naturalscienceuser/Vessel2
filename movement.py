from settings import mappings_to_keys
from conversions import *

def shift_cursor(custom_scr, dir_to_move, amt=1):
    current_y, current_x = custom_scr.scr.getyx()
    if dir_to_move in mappings_to_keys["up"]:
        custom_scr.scr.move(current_y - amt, current_x)
    elif dir_to_move in mappings_to_keys["down"]:
        custom_scr.scr.move(current_y + amt, current_x)
    elif dir_to_move in mappings_to_keys["left"]:
        custom_scr.scr.move(current_y, current_x - amt)
    elif dir_to_move in mappings_to_keys["right"]:
        custom_scr.scr.move(current_y, current_x + amt)

def move_to_row_pos(custom_scr, in_pos="start"):
    current_y, current_x = custom_scr.scr.getyx()
    if in_pos == "start":
        custom_scr.scr.move(current_y, 0)
    elif in_pos == "first cell":
        custom_scr.scr.move(current_y, custom_scr.cell_w // 2)
    elif in_pos == "mid":
        target_x, _ = to_screen_xy(custom_scr, custom_scr.cells_in_row // 2, current_y)
        custom_scr.scr.move(current_y, target_x)
    elif in_pos == "end":
        custom_scr.scr.move(current_y, custom_scr.cells_in_row * custom_scr.cell_w - int(custom_scr.cell_w / 2))

def move_to_col_pos(custom_scr, in_pos="mid"):
    current_y, current_x = custom_scr.scr.getyx()
    if in_pos == "first cell":
        custom_scr.scr.move(custom_scr.cell_h // 2, current_x)
    elif in_pos == "mid":
        _, target_y = to_screen_xy(custom_scr, current_x, custom_scr.cells_in_col // 2)
        custom_scr.scr.move(target_y, current_x)
    elif in_pos == "end":
        custom_scr.scr.move(custom_scr.cells_in_col * custom_scr.cell_h - int(custom_scr.cell_h / 2), current_x)

def move_to_column_1(custom_scr):
    current_y, current_x = custom_scr.scr.getyx()
    new_x = int(custom_scr.cell_w / 2)
    custom_scr.scr.move(current_y, new_x)
