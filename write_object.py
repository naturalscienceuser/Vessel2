# NOTE: Hopefully this whole file is useless now
import mmap
import struct  # may not need this
import codecs  # may not need this
import binascii  # may not need this
from level_object import LevelObject
from conversions import to_double

#def to_file_bytes(in_double, inner_table=True):
#    """
#    If you want to slap the bytes into an inner table, set inner_table to true. This will return
#    a length 32 string as oppposed to length 16
#    """
#    binary = struct.pack("d", in_double)
#    hex_from_bin = binascii.hexlify(binary)
#    if inner_table:
#        return codecs.encode(hex_from_bin, "hex")
#    else:
#        return hex_from_bin

def insert_obj(mmap_obj, level_object, h):
    doubles_to_insert = [level_object.obj_id, level_object.x_pixels, level_object.y_pixels] \
                        + level_object.additional_data
    stack_offset = 48 * level_object.obj_num
    offsets = [offset + stack_offset for offset in offsets_accounting_for_filesize]
    for offset, double_to_insert in zip(offsets, doubles_to_insert):
        bytes_to_insert = to_file_bytes(double_to_insert)
        mmap_obj[offset:offset+32] = bytes_to_insert

# Object limit appears to be 1000; there should only be 1000 x and y positions in stack to check
def return_obj_stack_offset(mmap_obj, x_pos_to_check, y_pos_to_check):
    """for object number 1 we return 48, for 2 we return 48*2, etc., object 0 returns 0 of course"""
    for x_stack_offset, y_stack_offset in zip(range(50928, 98976, 48), range(98976, 147024, 48)):
        x_hex = mmap_obj[x_stack_offset:x_stack_offset+32]
        y_hex = mmap_obj[y_stack_offset:y_stack_offset+32]
        x_val_at_offset = to_double(x_hex, inner_table=True)
        y_val_at_offset = to_double(y_hex, inner_table=True)
        if (x_val_at_offset, y_val_at_offset) == (x_pos_to_check, y_pos_to_check):
            return x_stack_offset - 50928
    return False  # In this case there is no object

def remove_obj(mmap_obj, stack_offset, h):
    raw_offsets = [2880, 50928, 98976, 147024, 195072, 243120, 291168, 339216, 483360]
    offset_from_minsize = int((432 * ((h - 288) / 288)) * 2)
    offsets_accounting_for_filesize = [raw_offset + offset_from_minsize for raw_offset in raw_offsets]
    offsets = [offset + stack_offset for offset in offsets_accounting_for_filesize]
    null_bytes = to_file_bytes(-1.0)
    for offset in offsets:
        mmap_obj[offset:offset+32] = null_bytes

# Test that removes an object at position 16,16 pixels
if __name__ == "__main__":
    #with open("a_copy.lvl", "r+b") as f:
    #    mm = mmap.mmap(f.fileno(), 0)
    #    stack_offset_1_1 = return_obj_stack_offset(mm, 16.0, 16.0)
    #    remove_obj(mm, stack_offset_1_1)
    with open("a_copy.lvl", "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        test = LevelObject(6.0, 0, 16.0, 16.0)
        insert_obj(mm, test)
