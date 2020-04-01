import mmap
from offsets import return_col_offset

def add_remove_collision(mmap_obj, xpos, ypos, h, remove=False):
    if remove:
        bytes_to_add = b"0000000000000000"
    else:
        bytes_to_add = b"000000000000F03F"
    base_offset = return_col_offset(xpos, h)
    offset = (base_offset) + ypos*24
    mmap_obj[offset:offset+16] = bytes_to_add

if __name__ == "__main__":
    with open("collis_row0/a.lvl", "r+b") as f:
        mm = mmap.mmap(f.fileno(), length=0)
        add_remove_collision(mm, 1, 1)

