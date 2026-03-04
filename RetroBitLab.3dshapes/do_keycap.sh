#!/bin/bash

# Disable history expansion to handle special characters like '!'
set +H

if [ -z "$1" ]; then
    echo "Usage: $0 \"LEGEND\" [SOURCE_STEP_FILE] [FONT_PATH]"
    echo "Example: $0 \"A\" \"DSA 1u.step\" \"/path/to/font.ttf\""
    echo "Default font: /home/gianluca/.fonts/GortonDigitalRegular.ttf"
    exit 1
fi

# Input file management
IN_FILE="${2:-DSA 1u.step}"
if [ ! -f "$IN_FILE" ]; then
    echo "ERROR: File '$IN_FILE' not found in current directory."
    exit 1
fi

# Font management - Make path absolute
DEFAULT_FONT="/home/gianluca/.fonts/GortonDigitalRegular.ttf"
FONT_ARG="${3:-$DEFAULT_FONT}"

if [[ "$FONT_ARG" = /* ]]; then
    IN_FONT="$FONT_ARG"
else
    IN_FONT="$(pwd)/$FONT_ARG"
fi

if [ ! -f "$IN_FONT" ]; then
    echo "ERROR: Font file '$IN_FONT' not found."
    exit 1
fi

export IN_STEP="$(pwd)/$IN_FILE"
export IN_FONT="$IN_FONT"
export IN_TEXT="$1"

# Output filename cleanup (ASCII only, no special characters)
BASE_NAME=$(basename "$IN_FILE" .step | tr ' ' '_')
CLEAN_TEXT=$(echo "$1" | sed 's/\\R//g' | sed 's/\\n/_/g' | sed 's/\\t/_/g' | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//')

[ -z "$CLEAN_TEXT" ] && CLEAN_TEXT="legend"

export OUT_STEP="$(pwd)/${BASE_NAME}-${CLEAN_TEXT}.step"

# Execution
if command -v freecad >/dev/null 2>&1; then
    freecad --console "$(pwd)/keycap_script.py"
else
    freecadcmd "$(pwd)/keycap_script.py"
fi

echo "---"
if [ -f "$OUT_STEP" ]; then
    echo "SUCCESS: Geometry generated at $OUT_STEP"
else
    echo "ERROR: File was not generated."
fi

set -H
