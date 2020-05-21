import codecs
import binascii
import struct

def flip_bytes(in_str):
    sbytes = [in_str[i]+in_str[i+1] for i in range(0, len(in_str), 2)]
    sbytes.reverse()
    return "".join(sbytes)


def to_int(in_str, byte_order="little", inner_table=False):
    if type(in_str) == type(b""):
        in_str = in_str.decode()

    if inner_table:
        in_str = codecs.decode(in_str.encode(), "hex").decode()

    if byte_order == "little":
        in_str = flip_bytes(in_str)

    return int(in_str, 16)


def to_screen_xy(custom_scr, cell_x_to_convert, cell_y_to_convert):
    new_x = cell_x_to_convert * custom_scr.cell_w + (custom_scr.cell_w / 2)
    new_y = cell_y_to_convert * custom_scr.cell_h + 1
    new_x = int(new_x)
    new_y = int(new_y)
    return new_x, new_y


def to_grid_xy(custom_scr, screen_x_to_convert=None, screen_y_to_convert=None):
    if screen_x_to_convert is None and screen_y_to_convert is None:
        screen_y_to_convert, screen_x_to_convert = custom_scr.scr.getyx()
    new_x = (screen_x_to_convert - (custom_scr.cell_w / 2)) / custom_scr.cell_w
    new_y = (screen_y_to_convert - 1) / custom_scr.cell_h
    new_x = int(new_x)
    new_y = int(new_y)
    return new_x, new_y


def to_double(in_str, byte_order="little", inner_table=False):
    if byte_order == "big":
        format = ">d"
    elif byte_order == "little":
        format = "<d"
    if inner_table:
        in_str = codecs.decode(in_str, "hex")
    binary = binascii.unhexlify(in_str)
    return struct.unpack(format, binary)[0]  # we use [0] b/c it returns a tuple


def to_file_bytes(in_num, inner_table=True, num_type="d"):
    """
    If you want to slap the bytes into an inner table, set inner_table to true.
    This will return a length 32 string as oppposed to length 16, also, see
    https://docs.python.org/2/library/struct.html for possible formats
    """
    binary = struct.pack(num_type, in_num)
    hex_from_bin = binascii.hexlify(binary).upper()  # hope .upper() doesn't break anything
    if inner_table:
        return codecs.encode(hex_from_bin, "hex")
    else:
        return hex_from_bin

if __name__ == "__main__":
    test_bytes = to_file_bytes(4, inner_table=True, num_type="i")
    print(test_bytes)
