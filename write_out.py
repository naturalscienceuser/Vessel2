from settings import symbols, symbol_doubles
from level_object import LevelObject

full_val = symbols["collision"]
empty_val = symbols["empty space"]

def write_out(level_file, in_grid):
    """
    Write contents of grid to the actual level file.
    Assumes groups have been cleared i.e. no preexisting objs
    """

    def write_row(level_file, in_grid, row_num, in_obj_num=0):
        row = in_grid.array[row_num]
        obj_num = in_obj_num
        for i, cell_val in enumerate(row):
            try:
                cell_symbol, cell_data = cell_val[0], cell_val[2:].split(",")
                # KeyError if no obj symbol in grid, in which case we don't insert object
                obj_double = symbol_doubles[cell_symbol]
            except KeyError:
                if cell_symbol == full_val:
                    remove = False
                elif cell_symbol == empty_val:
                    remove = True
                level_file.add_remove_collision(i, row_num, remove)
                obj_group_offset = level_file.return_obj_group_offset(i*16, row_num*16)
                # If there was no object there to begin with, why bother removing?
                if obj_group_offset is None:  # No obj present
                    continue
                level_file.remove_obj(obj_group_offset)
            else:
                x_offset, y_offset = int(cell_data[0]), int(cell_data[1])
                additional_data = [int(data) for data in cell_data[2:]]
                level_obj = LevelObject(obj_double, obj_num, (i*16) + x_offset, (row_num*16) + y_offset, additional_data)
                level_file.insert_obj(level_obj)
                obj_num += 1
        return obj_num

    total_obj_num = 0
    for i in range(len(in_grid.array)):
        total_obj_num = write_row(level_file, in_grid, i, total_obj_num)

# TODO: This doesn't work, no idea why not
#    # Change name last if necessary, since that means we don't have to 
#    # recalculate all the offsets
#    if level_file.new_name is None:
#        return
#
#    def delete_from_str(in_str, start, end):
#        return in_str[:start] + in_str[end:]
#
#    def insert_into_str(in_str, text_to_insert, location):
#        before, after = in_str[:location], in_str[location:]
#        return before + text_to_insert + after
#
#    def file_bytes_to_str(in_bytes):
#        hex_as_hex = decode(in_bytes, "hex")
#        return decode(hex_as_hex, "hex")
#
#    def str_to_file_bytes(in_str):
#        str_as_hex = "".join("{:02x}".format(ord(char)) for char in in_str)
#        return "".join("{:02x}".format(ord(char)) for char in str_as_hex)
#
#    file_text = level_file.mmap_obj.read()
#    level_file.mmap_obj.close()
#    with open(level_file.file_path, "r") as f:
#        text = f.read()
#    with open(level_file.file_path, "w") as f:
#        len_of_name = level_file.len_from_1_char + 4
#        print(len_of_name)
#        text = delete_from_str(text, 2136, 2136+len_of_name)
#        new_name_bytes = str_to_file_bytes(level_file.new_name.decode())
#        print(new_name_bytes)
#        text = insert_into_str(text, new_name_bytes, 2136)
#        f.write(text)

