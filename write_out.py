from settings import symbols, symbol_doubles
from level_object import LevelObject

full_val = symbols["collision"]
empty_val = symbols["empty space"]

def write_out(level_file, in_grid):
    """Assumes stacks have been cleared i.e. no preexisting objs"""

    def write_row(level_file, in_grid, row_num, in_obj_num=0):
        row = in_grid.array[row_num]
        obj_num = in_obj_num
        for i, cell_val in enumerate(row):
            try:
                cell_symbol, cell_data = cell_val[0], cell_val[2:].split(",")

                # KeyError if no obj symbol in grid, in which case we don't insert object
                # The below lines could maybe be in except else clause (see docs)
                obj_double = symbol_doubles[cell_symbol]

                x_offset, y_offset = int(cell_data[0]), int(cell_data[1])
                additional_data = [int(data) for data in cell_data[2:]]

                level_obj = LevelObject(obj_double, obj_num, (i*16) + x_offset, (row_num*16) + y_offset, additional_data)
                level_file.insert_obj(level_obj)
                obj_num += 1

            except KeyError:
                if cell_symbol == full_val:
                    remove = False
                elif cell_symbol == empty_val:
                    remove = True
                level_file.add_remove_collision(i, row_num, remove)
                obj_stack_offset = level_file.return_obj_stack_offset(i*16, row_num*16)
                # If there was no object there to begin with, why bother removing?
                if obj_stack_offset is None:  # No obj present
                    continue
                level_file.remove_obj(obj_stack_offset)
        return obj_num

    total_obj_num = 0
    for i in range(len(in_grid.array)):
        total_obj_num = write_row(level_file, in_grid, i, total_obj_num)
