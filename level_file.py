from conversions import to_file_bytes, to_double
import mmap

# NOTE: May be feasible to determine h based off level file size... we at least would need to know the filename though...
class LevelFile:
    def __init__(self, w, h, file_path):
        self.h = h
        self.w = w
        self.h_blocks = int(h / 16)
        self.w_blocks = int(w / 16)
        # How much longer the column is (in chars) compared to minimum size
        self.col_len_from_min = (self.h_blocks - 18) * 24

        raw_offsets = [2880, 50928, 98976, 147024, 195072, 243120, 291168, 339216, 483360]
        # Account for size of 1st 2 cols of collision, which occur before objs
        self.obj_stack_offsets = [offset + (self.col_len_from_min*2) for offset in raw_offsets]

        # s_time and shard time are in frames
        # booleans are 0/1
        # tileset and playerlife actually correspond to vals in-game
        # positions are of course in pixels
        # max_hp is playerlife while starting_hp is startinghp
        # However changing startinghp seems to do nothing at all

#        self.option_offsets = {
#            "spawn_y": 2336, "walljump": 2232,
#            "max_hp": 2000, "goal_y": 1880,
#            "music": 1780, "s_time": 1656,
#            "coin_x": 1556, "tileset": 1456,
#            "spawn_x": 1348, "goal_x": 1244,
#            "dark": 1144, "dash": 1028,
#            "coin_y": 920, "shine": 820,
#            "starting_hp": 708, "shard_time": 588
#        }

        raw_setting_offsets = [
            2336, 2232, 2000, 1880, 1780, 1656, 1556, 1456, 1348, 1244, 1144,
            1028, 920, 820, 708, 588
            ]

        self.setting_offsets = [offset + self.col_len_from_min for offset in raw_setting_offsets]

        self.setting_names = [
            "spawn y", "walljump", "max HP", "goal y", "music", "s time",
            "coin x", "tileset", "spawn x", "goal x", "dark x", "dash",
            "coin y", "shine", "starting hp (unimplemented)", "shard time"
            ]

        with open(file_path, "r+b") as f:
            self.mmap_obj = mmap.mmap(f.fileno(), length=0)

    def clear_stacks(self):
        stack_len = 48000
        for stack_pos in self.obj_stack_offsets:
            stack_start = stack_pos - 16
            for pair_start in range(stack_start, stack_start+stack_len, 48):  # pair of double and type number
                # Weird bytes below represent int 0 plus double -1, so -1 and its type number
                self.mmap_obj[pair_start:pair_start+48] = b"303030303030303030303030303030303030303046304246"
            
    def insert_obj(self, level_obj):
        doubles_to_insert = [level_obj.obj_id, level_obj.x_pixels, level_obj.y_pixels] \
                            + level_obj.additional_data
        stack_pos_offset = 48 * level_obj.obj_num
        offsets = [offset + stack_pos_offset for offset in self.obj_stack_offsets]
        for offset, double_to_insert in zip(offsets, doubles_to_insert):
            bytes_to_insert = to_file_bytes(double_to_insert)
            self.mmap_obj[offset:offset+32] = bytes_to_insert

    # NOTE: Maybe combine this method with remove_obj, since I think it is only used for that
    def return_obj_stack_offset(self, x_pos_to_check, y_pos_to_check):
        """Calculate offset from 1st item in stack"""
        # 48 is derived from size of double + int, since there is a type number before the double
        for x_stack_offset, y_stack_offset in zip(range(self.obj_stack_offsets[1], self.obj_stack_offsets[2], 48), 
                                                  range(self.obj_stack_offsets[2], self.obj_stack_offsets[3], 48)):
            x_hex = self.mmap_obj[x_stack_offset:x_stack_offset+32]
            y_hex = self.mmap_obj[y_stack_offset:y_stack_offset+32]
            x_val_at_offset = to_double(x_hex, inner_table=True)
            y_val_at_offset = to_double(y_hex, inner_table=True)
            if (x_val_at_offset, y_val_at_offset) == (x_pos_to_check, y_pos_to_check):
                # We could have used y stack or whatever to calculate the offset from first item in stack, chose x_stack arbitrarily
                return x_stack_offset - self.obj_stack_offsets[1]
        return None  # In this case there is no object

    def remove_obj(self, stack_offset):
        null_bytes = to_file_bytes(-1.0)
        for offset in self.obj_stack_offsets:
            offset += stack_offset  # account for obj's pos in stack
            self.mmap_obj[offset:offset+32] = null_bytes

    def return_col_offset(self, col_num):
        if col_num == 0:
            return 32
        elif col_num == 1:
            return(2376 + self.col_len_from_min)
        else:
            dist_between_cols = 432 + self.col_len_from_min + 24
            return (531400 + (self.col_len_from_min * 2) + ((col_num - 2) * dist_between_cols))

    # BORKED possibly because of above
    def add_remove_collision(self, xpos, ypos, remove=False):
        if remove:
            bytes_to_add = b"0000000000000000"
        else:
            bytes_to_add = b"000000000000F03F"
        base_offset = self.return_col_offset(xpos)
        offset = (base_offset) + ypos*24
        self.mmap_obj[offset:offset+16] = bytes_to_add

    def set_option(self, option_num, val):
        # If music is selected, we need to turn the song number into the
        # corresponding float. For some reason the levelfile itself doesn't use
        # 0-8 as vals even though songs are displayed that way, but rather
        # these seemingly arbitrary values
        if option_num == 4:
            music_vals = {
                "0": 0, "1": 29, "2": 34, "3": 35, "4": 36, "5": 40, "6": 42,
                "7": 90, "8": 125
                }
            val = music_vals[str(val)]
        offset = self.setting_offsets[option_num]
        val_bytes = to_file_bytes(val)
        self.mmap_obj[offset:offset+32] = val_bytes

# testing options changes
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/scratch/a.lvl")
#    test_inst.set_option("starting_hp", 0)

# test clearing stack, seems to work
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/fragmented/a.lvl")
#    test_inst.clear_stack()

# test changing obj type, seems to work
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/fragmented/a.lvl")
#    test_inst.set_obj_type(6, 0, 0)

## test return_num_objs
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/fragmented/a.lvl")
#    test_inst.return_num_objs()

## test defragmenting stack
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/fragmented/a.lvl")

# Removal seems to work now
#if __name__ == "__main__":
#    test_inst = LevelFile(512, 288, "/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/512_288/a.lvl")
#    print(test_inst.return_obj_stack_offset(0, 0))
#    test_inst.remove_obj(0)

#def return_num_objs(self):
#    """Return number of objects in file. Can break if stacks are not defragmented"""
#    num_objs = 0
#    for obj_stack_offset in range(self.obj_stack_offsets[0], self.obj_stack_offsets[1], 48):
#        double = to_double(self.mmap_obj[obj_stack_offset:obj_stack_offset+32], inner_table=True)
#        if double == -1:
#            break
#        num_objs += 1
#    return num_objs

#def defragment_stacks(self):
#    """
#    When an object is deleted, it may leave a "gap" of -1 in the stack in between other objects
#    thus we run this function at initialization to effectively remove those gaps, placing
#    everything at the top of each stack. We do this by splitting the stack into chunks
#    of len 48 (including a double and type num), removing the pairs that are -1, and
#    then adding -1 to that list until it comes out to the same length as before the -1s
#    were removed
#
#    BUT ACTUALLY I think we could have just completely cleared the stack and it would make
#    Absolutely 0 difference--everything just gets overwritten in write_out() anyway
#    """
#    # Type number 0 (int) and double -1
#    null_bytes = b"303030303030303030303030303030303030303046304246"
#    # from start of 1st val in stack to start of last val is 480(48)? chars (pretty sure it's just 48000 after looking at obj and x stack)
#    stack_len = 48000
#    for stack_pos in self.obj_stack_offsets:
#        stack_pos -= 16  # Usually we start after the 5A02 but this time we include it
#        stack = self.mmap_obj[stack_pos:stack_pos+stack_len]
#        doubles_in_stack = stack_len / 48  # 1000
#        # split on every 48 chars, so each type_num + double pair
#        stack_segments = [stack[i:i+48] for i in range(0, len(stack), 48)]
#        segments_not_null = [segment for segment in stack_segments if segment != null_bytes]
#        # append null_bytes until you get the right length
#        segments_not_null.extend([null_bytes]*int((doubles_in_stack-len(segments_not_null))))
#        defragmented_segments = segments_not_null  # Basically just renaming it
#        defragmented_stack = b"".join(defragmented_segments)
#        self.mmap_obj[stack_pos:stack_pos+stack_len] = defragmented_stack
#

#def set_obj_type(self, in_double, x_pix, y_pix):
#    stack_pos_offset = self.return_obj_stack_offset(x_pix, y_pix)
#    stack_pos = self.obj_stack_offsets[0] + stack_pos_offset
#    double_bytes = to_file_bytes(in_double, inner_table = True)
#    self.mmap_obj[stack_pos:stack_pos+32] = double_bytes

