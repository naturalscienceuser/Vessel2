# NOTE: This file should be useless now, moved functionality to cells_to_grid
import mmap
from settings import symbols
from conversions import to_double
from settings import double_symbols

# TODO: x and y stack offsets (we really probably should have a level file class for this)
def return_obj_coords():
    # There are 1001 objects in a stack/at max it seems
    offset_from_minsize = int((432 * ((h - 288) / 288)) * 2)
    obj_table_offset = 2880 + offset_from_minsize
    obj_stack_end = 1000 * 48  # based on looking, 1000 seems to be right
    for offset in range(obj_table_offset, obj_stack_end, 48):  # putting obj_stack_end may leave us off by 1?
        bytes_text = mmap_obj[offset:offset+32].decode()
        obj_double = to_double(bytes_text, "little", True)
        try:
            symbol = double_symbols[obj_double]
        except KeyError:
            pass

if __name__ == "__main__":
    with open("a.lvl", "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        return_obj_coords(mm, 288)
