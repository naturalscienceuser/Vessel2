## Summary
Vessel is a command-line level editor for Waveland custom level files. It supports adding/removing collision and objects and changing level settings, and input recording and playback. A demo can be found at https://streamable.com/c0tx0e

## Usage
```
python3 main.py path/to/level/file
```
The editor takes 1 argument, which is the path to the level file you want to edit. Vessel does not have the ability to create new level files from scratch; it can only edit existing ones. Keybinds can be found in the keybinds.txt file, and a brief explanation will be provided here:

* Up, Down, Left, and Right move the cursor 1 cell in a given direction
* Shift Left, Shift Right, Shift Up, and Shift Down move the camera 1 cell in a given direction
* Row Start, Row Middle, and Row End put the cursor at the start, middle, or end of the current row
* Column Start, Column Middle, and Column End put the cursor at the start, middle, or end of the current column
* Place places a block of collision (if in collision mode) or an object (if in object mode)
* Quit saves all changes and quits
* Record toggles recording. If recording, inputs will be saved to the current register.
* Playback plays back the inputs that are saved to the current register.
* Change Register can be used to switch the register to record/playback to. After pressing the Change Register key, press any other key to switch to that register. You can have as many registers as there are valid keys.
* Object Menu brings up the object menu, allowing you to select an object using the numbers 0-9. You will then be put in object mode, and pressing the Place key will place the object you have selected.
* Settings menu brings up the settings menu, allowing you to select a setting to change
* Collision Mode puts you in collision mode, so that when the Place key is pressed, it will insert collision rather than an object. Note that the editor starts in collision mode by default.
* Position prompts you to fine-tune the position of the object under the cursor. The object will be shifted right and down by however many pixels you input for the x and y offset.
* Properties prompts you to change the properties of an object. Property 1 corresponds to the object's size, property 2 corresponds to rotation, Property 5 seems to be unused, and other properties are not fully understood.
* Rename prompts you to rename the level. This will not rename the file itself, but will change the name that shows up in the in-game editor.

If you wish to customize the keybindings, just change the values in keybinds.txt under the corresponding mapping. To map a function to multiple keys, input those keys separated by commas.

Each object has a unique symbol, which can be changed through the symbols.txt file. The author hopes that the format of said file is self-evident.

Each cell in the level file represents 16x16 pixels, or the size of 1 block of collision
