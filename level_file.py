from conversions import to_file_bytes, to_double
import mmap

# NOTE: May be feasible to determine h based off level file size... we at least would need to know the filename though...
class LevelFile:
    def __init__(self, w, h, file_path):
        self.col_len_from_min = int(432 * ((h - 288) / 288)) 
        self.h = h
        self.w = w
        self.h_blocks = int(h / 16)
        self.w_blocks = int(w / 16)
        raw_offsets = [2880, 50928, 98976, 147024, 195072, 243120, 291168, 339216, 483360]
        self.obj_stack_offsets = [raw_offset + self.col_len_from_min for raw_offset in raw_offsets]
        with open(file_path, "r+b") as f:
            self.mmap_obj = mmap.mmap(f.fileno(), length=0)

    def insert_obj(self, level_obj):
        doubles_to_insert = [level_obj.obj_id, level_obj.x_pixels, level_obj.y_pixels] \
                            + level_obj.additional_data
        stack_pos_offset = 48 * level_obj.obj_num
        offsets = [offset + stack_pos_offset for offset in self.obj_stack_offsets]
        for offset, double_to_insert in zip(offsets, doubles_to_insert):
            bytes_to_insert = to_file_bytes(double_to_insert)
            self.mmap_obj[offset:offset+32] = bytes_to_insert

    def return_obj_stack_offset(self, x_pos_to_check, y_pos_to_check):
        for x_stack_offset, y_stack_offset in zip(range(self.obj_stack_offsets[1], self.obj_stack_offsets[2], 48), 
                                                  range(self.obj_stack_offsets[2], self.obj_stack_offsets[3], 48)):
            x_hex = self.mmap_obj[x_stack_offset:x_stack_offset+32]
            y_hex = self.mmap_obj[y_stack_offset:y_stack_offset+32]
            x_val_at_offset = to_double(x_hex, inner_table=True)
            y_val_at_offset = to_double(y_hex, inner_table=True)
            if (x_val_at_offset, y_val_at_offset) == (x_pos_to_check, y_pos_to_check):
                # We could have used y stack or whatever to calculate the offset from first item in stack, chose x_stack arbitrarily
                return x_stack_offset - self.obj_stack_offsets[1]
            return False  # In this case there is no object

    def remove_obj(self, stack_offset):
        null_bytes = to_file_bytes(-1.0)
        for offset in self.obj_stack_offsets:
            mmap_obj[offset:offset+32] = null_bytes

    def return_col_offset(self, col_num):  # used in add_remove_collision
        if col_num == 0:
            return 32
        elif col_num == 1:
            return(2376 + self.col_len_from_min)
        else:
            dist_between_cols = (self.h_blocks + 1) * 24  # +1 to account for the extra zero between cols
            return (531400 + (self.col_len_from_min * 2) + ((col_num - 2) * dist_between_cols))

    def add_remove_collision(self, xpos, ypos, remove=False):
        if remove:
            bytes_to_add = b"0000000000000000"
        else:
            bytes_to_add = b"000000000000F03F"
        base_offset = self.return_col_offset(xpos)
        offset = (base_offset) + ypos*24
        self.mmap_obj[offset:offset+16] = bytes_to_add
