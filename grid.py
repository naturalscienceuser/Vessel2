from settings import symbols

"""
This class is an abstract representation of the contents of the level. Each
cell in the grid represents a block of 16 pixels, and we place symbols
representing objects or collision in these cells. In the case of objects, we
place not only the symbol displayed to the user, but also 8 comma-separated
values representing x and y offset (which allows for pixel perfect positioning)
and the 6 additional properties (size, angle, all that). The cells_to_grid
module loads a level file and converts it into this grid, while the write_out
module takes this grid object and changes the level file to reflect its
contents. It's an intermediate data format, basically
"""

empty_val = symbols["empty space"]

class Grid:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # Represents how far the grid is shifted left or right (happens when
        # the camera moves, basically)
        self.x_offset = 0
        self.y_offset = 0
        self.array = [[empty_val for i in range(self.w)] for i in range(self.h)]

    def set_point(self, x_to_set, y_to_set, val_to_set):
        self.array[y_to_set][x_to_set] = val_to_set

    def get_point(self, x_to_get, y_to_get):
        return self.array[y_to_get][x_to_get]
