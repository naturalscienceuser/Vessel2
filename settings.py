import sys
"""
Get the symbols and keybinds and arrange them in dicts so we can look them up
as needed in other files. Making a list of movement keys is also helpful to 
know if we should send the keystroke to handle_movement() (see main.py)
"""

with open("keybinds.txt", "r") as f, open("symbols.txt", "r") as e:
    keybind_file_lines = [line.rstrip("\n") for line in f.readlines()]
    symbol_file_lines = [line.rstrip("\n") for line in e.readlines()]

symbols = {}  # {"Collision": "X", "Empty Space": " ", ...}
symbols_list = []  # ["X", " ", "#", "S", ...]
for i in range(0, len(symbol_file_lines), 3):
    symbol_name = symbol_file_lines[i].lower()
    value = symbol_file_lines[i+1]
    symbols[symbol_name] = value
    symbols_list.append(value)

for symbol in symbols_list:
    if symbols_list.count(symbol) > 1:
        print("Duplicate symbol {symbol} in symbols.txt; exiting")
        sys.exit()

# So to add symbols, it would appear that we would need to add the double to the end of the list, and then add the symbol to the end of symbols file
symbol_doubles_list = [
    1.0, 50.0, 4.0, 5.0, 6.0, 10.0, 9.0, 12.0, 211.0, 210.0, 22.0, 0.0, 2.0,
    3.0, 7.0, 8.0, 11.0, 21.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 201.0,
    202.0, 203.0, 204.0, 209.0, 212.0, 205.0, 206.0, 207.0, 208.0, 213.0, 214.0
    ]

objs_start = 6
obj_symbols_list = symbols_list[objs_start:]
obj_names = [symbol_name for symbol_name in symbols.keys()][objs_start:]
symbol_doubles = {symbol:double for symbol, double in zip(obj_symbols_list, symbol_doubles_list)}
double_symbols = {double:symbol for symbol, double in symbol_doubles.items()}

mappings_to_keys = {}
keys_to_mappings = {}  # {"c": "place", "m": "object menu", ...} hopefully
movement_keys = []
for loop_count, i in enumerate(range(0, len(keybind_file_lines), 3)):
    key_name = keybind_file_lines[i].lower()
    values = keybind_file_lines[i+1].split(",")
    mappings_to_keys[key_name] = values
    for value in values:
        keys_to_mappings[value] = key_name
    if loop_count < 14:
        for value in values:
            movement_keys.append(value)


if __name__ == "__main__":
    print(mappings_to_keys)
