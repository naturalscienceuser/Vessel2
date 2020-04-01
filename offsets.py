def return_col_offset(col_num, h):
    offset_from_minsize = int(432 * ((h - 288) / 288))
    h_blocks = int(h / 16)
    dist_between_cols = (h_blocks + 1) * 24  # +1 to account for the extra zero between cols
    if col_num == 0:
        return 32
    elif col_num == 1:
        return (2376 + offset_from_minsize)  # 432 increase for every tick (288 pix) of height added
    else:
        # multiply offset by 2 since it has two cols before it
        return (531400 + (offset_from_minsize * 2) + ((col_num - 2) * dist_between_cols))
