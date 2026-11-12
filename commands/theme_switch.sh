#!/bin/bash
# Compatibility entry point; the native picker uses the same local state.
set -eu
SIOYEK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${1:-}"
case "$name" in ""|*[!a-zA-Z0-9_-]*) echo "Provide a theme name from themes/." >&2; exit 1;; esac
if [ ! -f "$SIOYEK_DIR/themes/$name.config" ]; then
    case "$name" in
        ash_gray) name=slate;;
        flexoki) name=flexoki_dark;;
        gray_5) name=cocoa;;
        gray_6) name=sandstone;;
        monokai) name=monokai_midnight;;
        new) name=catppuccin_graphite;;
        warm_7) name=parchment;;
        wezterm) name=tokyo_dracula;;
        white_background) name=paper_white;;
        terminal_theme) name=violet_charcoal;;
    esac
fi
if [ ! -f "$SIOYEK_DIR/themes/$name.config" ]; then
    echo "Theme not found: $name" >&2; exit 1
fi
state=$(mktemp "$SIOYEK_DIR/.theme_state.XXXXXX")
trap 'rm -f "$state"' EXIT
printf '%s\n' "$name" > "$state"
mv -f "$state" "$SIOYEK_DIR/theme_state"
