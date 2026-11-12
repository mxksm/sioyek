#!/bin/bash
# Compatibility entry point; the native picker uses the same local state.
set -eu
SIOYEK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${1:-}"
case "$name" in ""|*[!a-zA-Z0-9_-]*) echo "Provide a theme name from themes/." >&2; exit 1;; esac
if [ ! -f "$SIOYEK_DIR/themes/$name.config" ]; then
    echo "Theme not found: $name" >&2; exit 1
fi
state=$(mktemp "$SIOYEK_DIR/.theme_state.XXXXXX")
trap 'rm -f "$state"' EXIT
printf '%s\n' "$name" > "$state"
mv -f "$state" "$SIOYEK_DIR/theme_state"
