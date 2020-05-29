from conversions import to_file_bytes, to_double, to_int
import mmap

class LevelFile:
    def __init__(self, file_path):
        with open(file_path, "r+b") as f:
            self.mmap_obj = mmap.mmap(f.fileno(), length=0)

        self.file_path = file_path
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

        self.new_name = None
        self.setting_str_len_num_location = 464 + self.col_len_from_min

        raw_offsets = [
                2880, 50928, 98976, 147024, 195072, 243120, 291168, 339216,
                483360
                ]
        # Account for size of 1st 2 cols of collision, which occur before objs
        obj_group_offsets_1_char_name = [
                offset + (self.col_len_from_min*2) for offset in raw_offsets
                ]
        # Account for len of filename
        self.obj_group_offsets = [
                offset + self.len_from_1_char
                for offset in obj_group_offsets_1_char_name
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

    def clear_groups(self):
        group_len = 48000
        for group_pos in self.obj_group_offsets:
            group_start = group_pos - 16
            for pair_start in range(group_start, group_start+group_len, 48):  # pair of double and type number
                # Weird bytes below represent int 0 plus double -1, so -1 and its type number
                self.mmap_obj[pair_start:pair_start+48] = b"303030303030303030303030303030303030303046304246"

    def insert_obj(self, level_obj):
        doubles_to_insert = [level_obj.obj_id, level_obj.x_pixels, level_obj.y_pixels] \
                            + level_obj.additional_data
        group_pos_offset = 48 * level_obj.obj_num
        offsets = [offset + group_pos_offset for offset in self.obj_group_offsets]
        for offset, double_to_insert in zip(offsets, doubles_to_insert):
            bytes_to_insert = to_file_bytes(double_to_insert)
            self.mmap_obj[offset:offset+32] = bytes_to_insert

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
        self.mmap_obj[offset:offset+16] = bytes_to_add

    def update_name_len(self):
        # Update len of setting string
        num_letters = len(self.new_name)
        # The len number means len after it's decode, so it's 2 not 4
        new_settings_len = ((num_letters * 2) - 2) + 948
        new_settings_len_bytes = to_file_bytes(new_settings_len, inner_table=False, num_type="i")
        self.mmap_obj[self.setting_str_len_num_location:self.setting_str_len_num_location+8] = new_settings_len_bytes
        # Update len of name string
        num_letters_bytes = to_file_bytes(num_letters, inner_table=True, num_type="i")
        name_len_location = 2120 + self.col_len_from_min
        self.mmap_obj[name_len_location:name_len_location+16] = num_letters_bytes

    def set_setting(self, setting_num, val):
        # If music is selected, we need to turn the song number into the
        # corresponding float. For some reason the levelfile itself doesn't use
        # 0-8 as vals even though songs are displayed that way, but rather
        # these seemingly arbitrary values
        if setting_num == 4:
            music_vals = {
                "0": 0, "1": 29, "2": 34, "3": 35, "4": 36, "5": 40, "6": 42,
                "7": 90, "8": 125
                }
            val = music_vals[str(int(val))]
        offset = self.setting_offsets[setting_num]
        val_bytes = to_file_bytes(val)
        self.mmap_obj[offset:offset+32] = val_bytes

        if setting_num in (0, 8):
            self.spawn_coords = self.return_spawn_coords()
        elif setting_num in (3, 9):
            self.goal_coords = self.return_goal_coords()
        elif setting_num in (6, 12):
            self.coin_coords = self.return_coin_coords()


    def get_setting(self, setting_num):
        offset = self.setting_offsets[setting_num]
        val_bytes = self.mmap_obj[offset:offset+32]
        val = to_double(val_bytes, inner_table=True)
        return val

    def return_spawn_coords(self):
        return [int(self.get_setting(8)/16), int(self.get_setting(0)/16)]

    def return_goal_coords(self):
        return [int(self.get_setting(9)/16), int(self.get_setting(3)/16)]

    def return_coin_coords(self):
        return [int(self.get_setting(6)/16), int(self.get_setting(12)/16)]


if __name__ == "__main__":
    test_inst = LevelFile("/Users/Joesaccount/Documents/coding_for_fun/WL_curses/object_branch_levelfile/512_288/a.lvl")
    print(f"{test_inst.setting_str_len_num_location=}")
