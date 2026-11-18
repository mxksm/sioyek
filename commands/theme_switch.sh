#!/bin/bash
# Switch palettes from scripts using the same state as the native picker.
set -eu
SIOYEK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${1:-}"
case "$name" in ""|*[!a-zA-Z0-9_-]*) echo "Provide a theme name from themes/." >&2; exit 1;; esac
if [ ! -f "$SIOYEK_DIR/themes/$name.config" ]; then
    echo "Theme not found: $name" >&2; exit 1
fi
state=$(mktemp "$SIOYEK_DIR/.prefs_local.XXXXXX")
trap 'rm -f "$state"' EXIT
if [ -f "$SIOYEK_DIR/prefs_local.config" ]; then
    awk '$1 != "theme"' "$SIOYEK_DIR/prefs_local.config" > "$state"
fi
printf 'theme %s\n' "$name" >> "$state"
mv -f "$state" "$SIOYEK_DIR/prefs_local.config"
rm -f "$SIOYEK_DIR/theme_state"
