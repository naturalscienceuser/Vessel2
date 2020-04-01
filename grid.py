from settings import symbols
empty_val = symbols["empty space"]

class Grid:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x_offset = 0
        self.y_offset = 0
        self.array = [[empty_val for i in range(self.w)] for i in range(self.h)]

    def set_point(self, x_to_set, y_to_set, val_to_set):
        self.array[y_to_set][x_to_set] = val_to_set

    def get_point(self, x_to_get, y_to_get):
        return self.array[y_to_get][x_to_get]
