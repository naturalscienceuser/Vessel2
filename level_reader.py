"""
So okay, the reason the byte order is flipped for the level file is because it stores numbers with little endian 
byte order, which means that the most significant bytes (largest) are last and least significant are first
so if we uncode the bytes in their original state, we must do binascii.unhexlify(bytestring) and then 
struct.unpack("<d", bytestring) to specify little endian. When we flip the bytes, we convert it to big 
endian, so to correctly unpack that we would so struct.unpack(">d", bytestring) after unhexlifying

For reference, ints = 8 bytes, doubles = 16 bytes, strings can vary

Okay, so here's the thing. If we convert one of our strings into ascii assuming base 16
(https://onlineasciitools.com/convert-bytes-to-ascii) then we get what seems to be hexadecimal.
running codecs.decode(that_hexadecimal, "hex") gets us stuff that actually makes sense

So do codecs.decode(original, "hex") on hex gets us some sensible stuff

In the case of a table within a table, decode it as hex one time and then you can treat it like a
 normal table

Also converting 53 from hex to decimal then using chr() gets us "S". The bytes are hex that correspond
to ascii, apparently
"""
import binascii
import struct
import sys
import codecs

folder = "obj_limit"  # only change this from now on, okay?
level_file = folder + "/a.lvl"
test_file = folder + ".txt"

class Global:
    def __init__(self):
        self.offset = 0

def flip_bytes(in_str):
    sbytes = [in_str[i]+in_str[i+1] for i in range(0, len(in_str), 2)]
    sbytes.reverse()
    return "".join(sbytes)

def to_int(in_str, byte_order="little"):
    """Use for converting w/h and type numbers"""
    if byte_order == "little":
        in_str = flip_bytes(in_str)
    return int(in_str, 16)

def to_double(in_str, byte_order="little"):
    if byte_order == "big":
        format = ">d"
    elif byte_order == "little":
        format = "<d"
    binary = binascii.unhexlify(in_str)
    return struct.unpack(format, binary)

def to_file_bytes(in_double, inner_table=False):
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

def overwrite_str(offset, target_str, overwrite_str):
    part_before = target_str[:offset]
    part_after = target_str[offset+len(overwrite_str):]
    return part_before + overwrite_str + part_after

def write_out(in_input, out_file=test_file):
    with open(out_file, "a") as f:
        f.write(str(in_input))
        f.write("\n")

globals = Global()

def read_table(text, amt_to_chop=24, inner_table=False):  # True offset is number of chars from start of file
    if inner_table:
        offset_multiplier = 2
    else:
        offset_multiplier = 1
    full_table = text
    text = text[amt_to_chop:]
    globals.offset += amt_to_chop * offset_multiplier
    text_length = len(text)
    # We decode inner table bytes into hex, which cuts the length in half. So to make sure the offset
    # relative to the start of the file remains accurate, we must multiply changes by 2. I think.
    ptr = 0
    while True:
        type_num_str = text[ptr:ptr+8]
        ptr += 8
        globals.offset += 8 * offset_multiplier
        if ptr >= text_length:
            print("End of table")
            write_out("End of table")
            input()
            return
        type_num = to_int(type_num_str)
        if type_num == 0:  # double
            to_print = f"Double {to_double(text[ptr:ptr+16])} (chars from start: {globals.offset})"
            print(to_print)
            write_out(to_print)
            ptr += 16
            globals.offset += 16 * offset_multiplier
        elif type_num == 1:  # string
            str_len = to_int(text[ptr:ptr+8])
            ptr += 8
            globals.offset += 8 * offset_multiplier  # maybe this broke it?
            write_out(f"Found string (length {str_len} bytes)")
            amt_to_slice = str_len * 2  # since a byte is 2 chars
            str_sbytes = text[ptr:ptr+amt_to_slice]
            # codecs.decode() turns bytes into... hex in this case
            str_hex = codecs.decode(str_sbytes, "hex")  # str_hex is a bytestring
            # increase ptr here but not offset, because this ptr goes right past the inner table, 
            # but the offset must increase as we go through that table
            ptr += amt_to_slice
            # ...Unless the string is not a table, in which case, yeah, we can just move past
            if not str_hex.startswith(b"5A02"):
                globals.offset += amt_to_slice * offset_multiplier
                converted_str = codecs.decode(str_hex, "hex")
                write_out(f"Found string: {converted_str}")
                input()
            else:
                write_out("Table within table!")
                print("Table within table!")
                #with open("scratch_metal.txt", "w") as target:
                #    target.write(str_hex.decode())
                print(f"ptr is at: {ptr - amt_to_slice}, with offset that is {ptr - amt_to_slice + 24}")
                write_out(str_hex.decode())
                input()
                read_table(str_hex.decode(), inner_table=True)
        else:
            print("Now this is getting interesting")
            print(f"pointer is: {ptr}, account for offset that is {ptr+24}")
            print(f"Type num is {type_num}")
            input()
            break

if __name__ == "__main__":
    with open(test_file, "w") as f:
        f.write("")
    
    with open(level_file, "r") as f:
        full_text = f.read()
        write_out(f"Full length {str(len(full_text))}")
        read_table(full_text)
