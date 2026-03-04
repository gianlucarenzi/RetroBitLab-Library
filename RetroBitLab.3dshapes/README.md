# Keycap Legend Generator

This tool automates the creation of 3D keycap models with custom engraved legends using FreeCAD. It generates a "Double-Shot" style STEP file containing two separate solids: the **Keycap body** and the **Legend infill**.

## Prerequisites

- **FreeCAD** (0.19 or newer recommended) installed and available in your system path.
- **Gorton Digital Regular** font (or any `.ttf` font) located at `${HOME}/.fonts/GortonDigitalRegular.ttf`.
- A base keycap STEP file (e.g., `DSA 1u.step`) in the working directory.

## Usage

Run the bash script `do_keycap.sh` followed by your desired legend, an optional source keycap file, and an optional font path.

```bash
./do_keycap.sh "LEGEND" [SOURCE_STEP_FILE] [FONT_PATH]
```

### Examples

- **Single character:**
  ```bash
  ./do_keycap.sh "A"
  ```
- **Custom base file:**
  ```bash
  ./do_keycap.sh "TAB" "DSA 1.5u.step"
  ```
- **Custom font:**
  ```bash
  ./do_keycap.sh "A" "DSA 1u.step" "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
  ```

## Advanced Features

The generator supports special formatting tags:

### Multi-line Legends (`\n`)
Use `\n` to split text into multiple lines. The script automatically scales and centers the entire block.
```bash
./do_keycap.sh "SHIFT\nLOCK"
```

### Tabs and Spacing (`\t`)
Use `\t` to insert large horizontal spaces between segments on the same line.
```bash
./do_keycap.sh "Clr\tSet"
```

### Reversed/Inverted Text (`\R`)
Prefix any segment with `\R` to place the text inside a solid rectangular frame (negative text).
```bash
./do_keycap.sh "\RClr\tSet\nCAPS"
```
*In the example above, "Clr" will be inverted inside a box, while "Set" and "CAPS" will be normal.*

## Technical Details

- **Output:** A STEP file named `${BaseName}-${Legend}.step` containing two solids.
- **Alignment:** The legend is automatically centered on the X and Z axes and perfectly flush with the top surface (following any concave curvature).
- **Auto-Scaling:** If the legend is too long for the keycap surface (~12mm), the script automatically shrinks the font size to fit.
- **Headless Mode:** The script runs using `freecad --console` or `freecadcmd`, requiring no GUI.

## Coloring in FreeCAD

Since CLI export of STEP files does not preserve colors, you can easily apply them in the FreeCAD GUI:
1. Open the generated `.step` file.
2. Select the `Keycap` object and change its **Shape Color** in the View tab.
3. Select the `Legend` object and change its **Shape Color** to a contrasting color (e.g., White).
