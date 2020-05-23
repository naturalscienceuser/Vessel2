from settings import symbols, symbol_doubles
from level_object import LevelObject
from codecs import decode

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
                if cell_symbol in (symbols["coin"], symbols["goal"], symbols["spawn"]):
                    continue
                # KeyError if no obj symbol in grid, in which case we don't insert object
                obj_double = symbol_doubles[cell_symbol]
            except KeyError:
                if cell_symbol == full_val:
                    remove = False
                elif cell_symbol == empty_val:
                    remove = True
                level_file.add_remove_collision(i, row_num, remove)
                #level_file.remove_obj(i*16, row_num*16)
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

    # Change name last if necessary, since that means we don't have to
    # recalculate all the offsets. Since the length may change, I opt to read
    # the file in as a string, manipulate it, then write it all back. I do not
    # know how to insert into/remove bytes from a file any more nicely
    if level_file.new_name is None:
        return

    def delete_from_str(in_str, start, end):
        return in_str[:start] + in_str[end:]

    def insert_into_str(in_str, text_to_insert, location):
        before, after = in_str[:location], in_str[location:]
        return before + text_to_insert + after

    def file_bytes_to_str(in_bytes):
        hex_as_hex = decode(in_bytes, "hex")
        return decode(hex_as_hex, "hex")

    def str_to_file_bytes(in_str):
        # This .upper() was a doozy
        str_as_hex = "".join("{:02x}".format(ord(char)) for char in in_str).upper()
        return "".join("{:02x}".format(ord(char)) for char in str_as_hex)

    level_file.update_name_len()
    level_file.mmap_obj.close()
    with open(level_file.file_path, "r") as f:
        text = f.read()
    with open(level_file.file_path, "w") as f:
        len_of_old_name = level_file.len_from_1_char + 4
        text_no_name = delete_from_str(text, 2136, 2136+len_of_old_name)
        new_name_bytes = str_to_file_bytes(level_file.new_name.decode())
        text_w_new_name = insert_into_str(text_no_name, new_name_bytes, 2136)
        f.write(text_w_new_name)

##    Trying to do it without creating a new file object, not sure there's a point
#    level_file.update_name_len()
#    text = level_file.mmap_obj.read()
#    len_of_old_name = level_file.len_from_1_char + 4
#    text_no_name = delete_from_str(text, 2136, 2136+len_of_old_name)
#    new_name_bytes = str_to_file_bytes(level_file.new_name.decode())
#    text_w_new_name = insert_into_str(text_no_name, new_name_bytes, 2136)
#    f.write(text_w_new_name)

