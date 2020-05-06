from conversions import to_double
from settings import double_symbols, symbols

def set_obj_cells(level_file, grid):
    # There are 1000 objects in a stack/at max it seems
    obj_table_offset = level_file.obj_stack_offsets[0]
    obj_stack_end = obj_table_offset + (1000 * 48)  # based on looking, 1000 seems to be right
    coords = []
    for offset in range(obj_table_offset, obj_stack_end, 48):  # putting obj_stack_end may leave us off by 1?
        bytes_text = level_file.mmap_obj[offset:offset+32].decode()
        obj_double = to_double(bytes_text, "little", True)
        try:  # again, use else?
            symbol = double_symbols[obj_double]  # causes KeyError if no object
            offset_from_stack_start = offset - obj_table_offset

            x_stack_offset = level_file.obj_stack_offsets[1] + offset_from_stack_start
            x_pos_bytes = level_file.mmap_obj[x_stack_offset:x_stack_offset+32]
            raw_x_pos = to_double(x_pos_bytes, "little", True)
            x_offset = int(raw_x_pos % 16)
            x_pos = raw_x_pos - x_offset

            y_stack_offset = level_file.obj_stack_offsets[2] + offset_from_stack_start
            y_pos_bytes = level_file.mmap_obj[y_stack_offset:y_stack_offset+32]
            raw_y_pos = to_double(y_pos_bytes, "little", True)
            y_offset = int(raw_y_pos % 16)
            y_pos = raw_y_pos - y_offset

            additional_data_list = []
            for stack_offset in level_file.obj_stack_offsets[3:]:
                data_bytes = level_file.mmap_obj[stack_offset:stack_offset+32]
                data_num = to_double(data_bytes, "little", True)
                additional_data_list.append(int(data_num))
            additional_data_list = [str(data) for data in additional_data_list]
            additional_data = ",".join(additional_data_list)
            cell_contents = f"{symbol},{x_offset},{y_offset},{additional_data}"

            coords.append([int(x_pos/16), int(y_pos/16), cell_contents])

        except KeyError:
            pass
    
    for coordset in coords:
        grid.set_point(coordset[0], coordset[1], coordset[2])


def set_collis_cells(level_file, grid):

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

    ground_coords = []
    for col in range(level_file.w_blocks):
        col_coords = return_col_collis_coords(level_file, col)
        for coordset in col_coords:
            ground_coords.append(coordset)

    for coordset in ground_coords:
        grid.set_point(coordset[0], coordset[1], symbols["collision"])


#def return_spawn_coords(level_file):
#    return [int(level_file.get_option(8)/16), int(level_file.get_option(0)/16)]
#
#def return_goal_coords(level_file):
#    return [int(level_file.get_option(9)/16), int(level_file.get_option(3)/16)]
#
#def return_coin_coords(level_file):
#    return [int(level_file.get_option(6)/16), int(level_file.get_option(12)/16)]

#def set_spawn_coords(level_file, grid):
#    spawn_coords = return_spawn_coords(level_file)
#    grid.set_point(spawn_coords[0], spawn_coords[1], symbols["spawn"])
#
#def set_goal_coords(level_file, grid):
#    goal_coords = [int(level_file.get_option(9)/16), int(level_file.get_option(3)/16)]
#    grid.set_point(goal_coords[0], goal_coords[1], symbols["goal"])
#
#def set_coin_coords(level_file, grid):
#    coin_coords = [int(level_file.get_option(6)/16), int(level_file.get_option(12)/16)]
#    grid.set_point(coin_coords[0], coin_coords[1], symbols["coin"])
