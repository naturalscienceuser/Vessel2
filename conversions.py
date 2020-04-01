import codecs
import binascii
import struct

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

def to_file_bytes(in_double, inner_table=True):
    """
    If you want to slap the bytes into an inner table, set inner_table to true. This will return
    a length 32 string as oppposed to length 16
    """
    binary = struct.pack("d", in_double)
    hex_from_bin = binascii.hexlify(binary)
    if inner_table:
        return codecs.encode(hex_from_bin, "hex")
    else:
        return hex_from_bin
