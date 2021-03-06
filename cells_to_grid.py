from conversions import to_double
from settings import double_symbols, symbols

"""
These functions set cells of the Grid object based on preexisting objects and
collision.
"""

def set_obj_cells(level_file, grid):
    """
    I alluded to this in main.py, but when objects are placed on the
    grid we include not only their corresponding symbol, but also 8 numbers
    separated by commas which represent x offset, y offset, and the 6 additional
    properties (size, rotation, all that). So this function determines those
    properties in addition to the cell and type of the object and adds those
    """
    # There are 1000 objects in a group/at max it seems
    obj_table_offset = level_file.obj_group_offsets[0]
    obj_group_end = obj_table_offset + (1000 * 48)  # based on looking, 1000 seems to be right
    coords = []
    for offset in range(obj_table_offset, obj_group_end, 48):  # putting obj_group_end may leave us off by 1?
        bytes_text = level_file.mmap_obj[offset:offset+32].decode()
        obj_double = to_double(bytes_text, "little", True)
        try:  # again, use else?
            symbol = double_symbols[obj_double]  # causes KeyError if no object
        except KeyError:
            pass
        else:
            offset_from_group_start = offset - obj_table_offset

            x_group_offset = level_file.obj_group_offsets[1] + offset_from_group_start
            x_pos_bytes = level_file.mmap_obj[x_group_offset:x_group_offset+32]
            raw_x_pos = to_double(x_pos_bytes, "little", True)
            x_offset = int(raw_x_pos % 16)
            x_pos = raw_x_pos - x_offset

            y_group_offset = level_file.obj_group_offsets[2] + offset_from_group_start
            y_pos_bytes = level_file.mmap_obj[y_group_offset:y_group_offset+32]
            raw_y_pos = to_double(y_pos_bytes, "little", True)
            y_offset = int(raw_y_pos % 16)
            y_pos = raw_y_pos - y_offset

            additional_data_list = []
            for group_offset in level_file.obj_group_offsets[3:]:
                data_bytes = level_file.mmap_obj[group_offset:group_offset+32]
                data_num = to_double(data_bytes, "little", True)
                additional_data_list.append(int(data_num))
            additional_data_list = [str(data) for data in additional_data_list]
            additional_data = ",".join(additional_data_list)
            cell_contents = f"{symbol},{x_offset},{y_offset},{additional_data}"
            coords.append([int(x_pos/16), int(y_pos/16), cell_contents])
    
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
