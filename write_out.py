import mmap
#from pathlib import Path
from settings import symbols, symbol_doubles
from level_object import LevelObject
from add_remove_collision import add_remove_collision

full_val = symbols["collision"]
empty_val = symbols["empty space"]

# before I had called this write_rows, but I think we can just make this write_out
def write_out(level_file, in_grid):

    def write_row(level_file, in_grid, row_num, in_obj_num=0):
        row = in_grid.array[row_num]
        obj_num = in_obj_num
        for i, cell in enumerate(row):
            try:
                # KeyError if no obj symbol in grid, in which case we don't insert object
                obj_double = symbol_doubles[cell]
                level_obj = LevelObject(obj_double, obj_num, i*16, row_num*16)
                level_file.insert_obj(level_obj)
                obj_num += 1
            except KeyError:
                if cell == full_val:
                    remove = False
                elif cell == empty_val:
                    remove = True
                level_file.add_remove_collision(i, row_num, remove)
                obj_stack_offset = level_file.return_obj_stack_offset(i, row_num)
                # If there was no object there to begin with, why bother removing?
                if not obj_stack_offset:  
                    continue
                level_file.remove_obj(obj_stack_offset)
        return obj_num

    total_obj_num = 0
    for i in range(len(in_grid.array)):
        objects_added = write_row(level_file, in_grid, i, total_obj_num)
        total_obj_num += objects_added

#def write_out(level_file, in_grid):
#    write_rows(level_file, in_grid)
