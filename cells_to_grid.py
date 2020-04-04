import mmap
from offsets import return_col_offset
from conversions import to_double
from settings import double_symbols

# TODO: Finish writing this function (It's done?)
def return_obj_coords(level_file):
    # There are 1000 objects in a stack/at max it seems
    obj_table_offset = level_file.obj_stack_offsets[0]
    obj_stack_end = obj_table_offset + (1000 * 48)  # based on looking, 1000 seems to be right
    coords = []
    for offset in range(obj_table_offset, obj_stack_end, 48):  # putting obj_stack_end may leave us off by 1?
        bytes_text = level_file.mmap_obj[offset:offset+32].decode()
        obj_double = to_double(bytes_text, "little", True)
        try:
            symbol = double_symbols[obj_double]  # causes KeyError if no object
            offset_from_stack_start = offset - obj_table_offset
            x_stack_offset = level_file.obj_stack_offsets[1] + offset_from_stack_start
            x_pos_bytes = level_file.mmap_obj[x_stack_offset:x_stack_offset+32]
            x_pos = to_double(x_pos_bytes, "little", True)
            y_stack_offset = level_file.obj_stack_offsets[2] + offset_from_stack_start
            y_pos_bytes = level_file.mmap_obj[y_stack_offset:y_stack_offset+32]
            y_pos = to_double(y_pos_bytes, "little", True)
            coords.append([int(x_pos/16), int(y_pos/16), symbol])
        except KeyError:
            pass
    return coords

def return_col_collis_coords(level_file, col_num):
    offset = level_file.return_col_offset(col_num)
    col_end = offset + (24 * level_file.h_blocks)
    coords = []
    cell_y = 0
    for i in range(offset, col_end, 24):
        if level_file.mmap_obj[i:i+16] == b"000000000000F03F":
            coords.append([col_num, cell_y])
        cell_y += 1
    return coords

def return_all_collis_coords(level_file):
    ground_coords = []
    for col in range(level_file.w_blocks):
        col_coords = return_col_collis_coords(level_file, col)
        for coordset in col_coords:
            ground_coords.append(coordset)
    return ground_coords

if __name__ == "__main__":
    from level_file import LevelFile
    level_file = LevelFile(512, 288, "a.lvl")
    print(return_obj_coords(level_file))
