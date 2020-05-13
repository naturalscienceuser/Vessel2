from conversions import to_file_bytes, to_double, to_int
import mmap

class LevelFile:
    def __init__(self, file_path):
        with open(file_path, "r+b") as f:
            self.mmap_obj = mmap.mmap(f.fileno(), length=0)

        w_bytes = self.mmap_obj[8:16]
        h_bytes = self.mmap_obj[16:24]
        self.w_blocks = to_int(w_bytes)
        # I don't know why, but the file always says height is 1 larger than
        # the game does (is it that mystery zero again?)
        self.h_blocks = to_int(h_bytes) - 1
        self.w = self.w_blocks * 16
        self.h = self.h_blocks * 16

        # The amount of file length contributed by collision (+1 is for the
        # mysterious extra 0 at the end of every row)
        collis_space = self.w_blocks * (self.h_blocks+1) * 24
        len_1_char_name = collis_space + 530480  # file len w 1 char name
        self.len_from_1_char = len(self.mmap_obj) - len_1_char_name

        # How much longer the column is (in chars) compared to minimum size
        self.col_len_from_min = (self.h_blocks - 18) * 24

        raw_offsets = [
                2880, 50928, 98976, 147024, 195072, 243120, 291168, 339216,
                483360
                ]
        # Account for size of 1st 2 cols of collision, which occur before objs
        obj_stack_offsets_1_char_name = [
                offset + (self.col_len_from_min*2) for offset in raw_offsets
                ]
        # Account for len of filename
        self.obj_stack_offsets = [
                offset + self.len_from_1_char 
                for offset in obj_stack_offsets_1_char_name
                ]

        # s_time and shard time are in frames
        # booleans are 0/1
        # tileset and playerlife actually correspond to vals in-game
        # positions are of course in pixels
        # max_hp is playerlife while starting_hp is startinghp
        # However changing startinghp seems to do nothing at all

        raw_setting_offsets = [
            2336, 2232, 2000, 1880, 1780, 1656, 1556, 1456, 1348, 1244, 1144,
            1028, 920, 820, 708, 588
            ]

        # Account for offset caused by col len (since 1 collision col is above)
        setting_offsets_1_char_name = [
                offset + self.col_len_from_min
                for offset in raw_setting_offsets
                ]

        # Account for offset caused by name len
        setting_offsets_1_char_name[0] += self.len_from_1_char
        setting_offsets_1_char_name[1] += self.len_from_1_char
        self.setting_offsets = setting_offsets_1_char_name

        self.setting_names = [
            "spawn y", "walljump", "max HP", "goal y", "music", "s time",
            "coin x", "tileset", "spawn x", "goal x", "dark x", "dash",
            "coin y", "shine", "starting hp (unimplemented)", "shard time"
            ]

        self.spawn_coords = self.return_spawn_coords()
        self.goal_coords = self.return_goal_coords()
        self.coin_coords = self.return_coin_coords()

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

    # Could this be an inner function somewhere too?
    def return_col_offset(self, col_num):
        if col_num == 0:
            return 32
        elif col_num == 1:
            return(2376 + self.col_len_from_min) + self.len_from_1_char
        else:
            dist_between_cols = (432 + self.col_len_from_min + 24)
            return (531400 + (self.col_len_from_min * 2) + ((col_num - 2) * dist_between_cols)) + self.len_from_1_char

    def add_remove_collision(self, xpos, ypos, remove=False):
        if remove:
            bytes_to_add = b"0000000000000000"
        else:
            bytes_to_add = b"000000000000F03F"
        base_offset = self.return_col_offset(xpos)
        offset = (base_offset) + ypos*24
        print(f"{xpos=} {ypos=} {offset=}")
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

        if option_num in (0, 8):
            self.spawn_coords = self.return_spawn_coords()
        elif option_num in (3, 9):
            self.goal_coords = self.return_goal_coords()
        elif option_num in (6, 12):
            self.coin_coords = self.return_coin_coords()


    def get_option(self, option_num):
        offset = self.setting_offsets[option_num]
        val_bytes = self.mmap_obj[offset:offset+32]
        val = to_double(val_bytes, inner_table=True)
        return val

    def return_spawn_coords(self):
        return [int(self.get_option(8)/16), int(self.get_option(0)/16)]

    def return_goal_coords(self):
        return [int(self.get_option(9)/16), int(self.get_option(3)/16)]

    def return_coin_coords(self):
        return [int(self.get_option(6)/16), int(self.get_option(12)/16)]


if __name__ == "__main__":
    test_inst = LevelFile("/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/bb/bb.lvl")
    print(test_inst.return_col_offset(2))

