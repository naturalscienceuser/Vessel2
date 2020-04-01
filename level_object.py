class LevelObject:
    def __init__(self, obj_id, obj_num, x_pixels, y_pixels, additional_data=None):
        self.obj_id = obj_id
        self.obj_num = obj_num
        self.stack_offset = obj_num * 48
        self.x_pixels = x_pixels
        self.y_pixels = y_pixels
        self.x_blocks = x_pixels / 16
        self.y_blocks = y_pixels / 16
        if additional_data is None:
            additional_data = [1, 0, 0, 0, 0, 1] 
        self.additional_data = additional_data
