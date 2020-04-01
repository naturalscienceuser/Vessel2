def preserve_pos(custom_scr, fun):
    def wrapper(*args, **kwargs):
        initial_y, initial_x = scr.getyx()
        ret = fun(*args, **kwargs)
        custom_scr.scr.move(initial_y, initial_x)
        return ret  # return whatever the original function returned
    return wrapper
