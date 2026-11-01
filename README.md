# Custom Sioyek Configuration

macOS configuration, keyboard shortcuts, themes, and a build launcher for the
[mxksm/sioyek-app](https://github.com/mxksm/sioyek-app) fork of
[Sioyek](https://github.com/ahrm/sioyek). The fork adds PDF tabs, split view,
drawing tools, and a temporary laser pointer.

## Features

- **Theme Switching** — Switch themes with Option+1–5, Option+8–9, or Option+0.
- **File Navigation** — Open the previous PDF with Shift+D or the next with Shift+L, sorted alphanumerically within the current directory.
- **Directory Switching** — Open the current PDF's directory with Shift+U.

> Keep this configuration at `$CONFIG_DIR/sioyek`, or `~/.config/sioyek` when `$CONFIG_DIR` is unset.

## Installation

Requires macOS 14+, Homebrew, Python 3, and Xcode command-line tools.
If a Sioyek configuration already exists at the destination, back it up before
installing this configuration.

```sh
mkdir -p "${CONFIG_DIR:-$HOME/.config}"
git clone https://github.com/mxksm/sioyek.git "${CONFIG_DIR:-$HOME/.config}/sioyek"
cd "${CONFIG_DIR:-$HOME/.config}/sioyek"
bash build-sioyek.sh
```

The launcher downloads and builds the exact source commit listed in
`sioyek-app-revision`. A separate source checkout or GitHub token is not required.
Source and Qt are cached under `~/Library/Caches/sioyek-build` for subsequent
builds. The build does not modify the user configuration.

Quit Sioyek and reopen the installed app afterward. The build prints its path:
`/Applications/sioyek.app`, or `~/Applications/sioyek.app` if `/Applications`
is not writable. It keeps a backup of the previously installed app. Open the
printed path explicitly if both locations contain an installation.

Source development and upstream merge instructions are in the fork's
[FORK.md](https://github.com/mxksm/sioyek-app/blob/development/FORK.md).

## Annotation shortcuts

- `p` or `x`: toggle freehand drawing; the filled cursor shows the current pen color.
- Hold the right mouse button while drawing to erase; release to return to the pen.
- Shift+E: toggle circular eraser (removes only touched portions of strokes); Escape exits.
- Shift+P: rectangle eraser.
- Shift+C: toggle a glowing red laser trail. Hold the left mouse button to draw;
  release to fade from the beginning. Escape clears it.
  Laser marks are temporary and never saved.
- Cmd+Z / Ctrl+Z: undo drawing; Cmd+Shift+Z: redo drawing. Erasing is not undoable.
- Shift+A: create a text box; `w`, then `a`: delete a visible annotation.

Set the laser's lifetime after release in `prefs_user.config`:

```conf
laser_pointer_duration_ms 1450
```

Values are milliseconds, from 100 to 60000. Smaller values fade faster;
larger values fade slower. Changes apply to the next released stroke.

## Tabs and split view

- Cmd+T: open a PDF in a tab; Cmd+W: close the current tab.
- Cmd+1–9: select a tab in the focused pane.
- Shift+, (`<`) / Shift+. (`>`): move the focused PDF's tab one place left / right.
  Tabs stop at either end without wrapping; both split panes keep their views.
- Ctrl+Tab: cycle through tabs in most-recently-used order. Keep Ctrl held to
  display the switcher; release Ctrl to open the selection. Shift reverses direction.
- Cmd+Backslash: toggle two PDF panes sharing the same tabs.
- Ctrl+H / Ctrl+L: focus the left / right pane; Cmd+Option+W switches sides.
- Drag the divider to resize the panes. The top line marks the focused pane;
  both lines follow the theme. Each pane keeps its own position and zoom.
- Ctrl+T: open a separate window; Ctrl+W: close the entire window.

Collapsing a split keeps the focused PDF. Tabs are restored at startup, but the
split layout starts with one pane.

Custom script paths use `$CONFIG_DIR`, falling back to `$HOME/.config`.
