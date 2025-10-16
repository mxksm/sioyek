#!/bin/bash

# Define the config directory
SIOYEK_DIR="$CONFIG_DIR/sioyek"
THEMES_DIR="$SIOYEK_DIR/themes"
PREFS_FILE="$SIOYEK_DIR/prefs_user.config"

# Get the input argument for the theme name
THEME_NAME=$1

if [ -z "$THEME_NAME" ]; then
    echo "Please provide a theme name (e.g., ./switch_theme.sh gruvbox_light)"
    exit 1
fi

# Construct the theme file path
SELECTED_THEME_FILE="$THEMES_DIR/$THEME_NAME.config"

# Check if the theme file exists
if [ ! -f "$SELECTED_THEME_FILE" ]; then
    echo "Theme '$THEME_NAME' not found! Please provide a valid theme name."
    exit 1
fi

# Extract the content of the selected theme file
THEME_CONTENT=$(<"$SELECTED_THEME_FILE")

# Use perl to replace the content between the placeholders
perl -0777 -i -pe "
s/# theme placeholder start.*# theme placeholder end/# theme placeholder start\n# (This section will be replaced with the selected theme)\n$THEME_CONTENT\n# theme placeholder end/s
" "$PREFS_FILE"

echo "Switched to theme: $(basename "$SELECTED_THEME_FILE")"

