import sys

with open("keybinds.txt", "r") as f, open("env.txt", "r") as e:
    keybind_file_lines = [line.rstrip("\n") for line in f.readlines()]
    symbol_file_lines = [line.rstrip("\n") for line in e.readlines()]

symbols = {}
symbols_list = []
for i in range(0, len(symbol_file_lines), 3):
    symbol_name = symbol_file_lines[i].lower()
    value = symbol_file_lines[i+1]
    symbols[symbol_name] = value
    symbols_list.append(value)

# So to add symbols, it would appear that we would need to add the double to the end of the list, and then add the symbol to the end of env file
symbol_doubles_list = [1.0, 50.0, 4.0, 5.0, 6.0, 10.0, 9.0, 12.0, 211.0, 210.0, 22.0]
obj_symbols_list = symbols_list[3:]
symbol_doubles = {symbol:double for symbol, double in zip(obj_symbols_list, symbol_doubles_list)}
double_symbols = {double:symbol for symbol, double in symbol_doubles.items()}

keybinds = {}
movement_keys = []
placement_keys = []
placement_key_symbols = {}  # keyboardkey:icon
# Well, if I figure this out... names_of_obj_corresponding_to_key = {}
symbols_list_index = 3  # we only want placement symbols which is why we start at 3
for loop_count, i in enumerate(range(0, len(keybind_file_lines), 3)):
    key_name = keybind_file_lines[i].lower()
    values = keybind_file_lines[i+1].split(",")
    keybinds[key_name] = values
    if loop_count < 14:
        for value in values:
            movement_keys.append(value)
    elif loop_count > 22:  # If we add something between placement keys and movement keys, increment this by 3
        for value in values:
            placement_keys.append(value)
            placement_key_symbols[value] = symbols_list[symbols_list_index]
        symbols_list_index += 1


if __name__ == "__main__":
    print(str(obj_symbols_list))
