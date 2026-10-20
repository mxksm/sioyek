# Custom Sioyek Configuration

This configuration extends the default Sioyek setup with several useful features for efficient PDF navigation and theming.

## Features

- **Theme Switching** — Instantly toggle between whole themes using <kbd>⌥ Option</kbd> + <kbd>1–9</kbd>.  
- **File Navigation** — Move left with <kbd>D</kbd> or right with <kbd>L</kbd> between PDF files in the current directory sorted alphanumerically for quick browsing.  
- **Directory Switching** — Jump to the directory of the currently opened file with <kbd>u</kbd>, making it easy to access related PDFs.

> Keep this configuration at `$CONFIG_DIR/sioyek`, or `~/.config/sioyek` when `$CONFIG_DIR` is unset.

## Build or update the app

The application source now lives in [mxksm/sioyek-app](https://github.com/mxksm/sioyek-app).
This repository keeps the configs, shortcuts, and a build launcher. There are no
source-injection scripts: application changes are ordinary commits in the fork.

On either Mac, from this configuration repository:

```sh
git pull --ff-only
bash build-sioyek.sh
```

Quit Sioyek and reopen the installed app afterward. The build prints its path
(`/Applications/sioyek.app`, or `~/Applications/sioyek.app` if `/Applications`
is not writable). It keeps a backup of the previously installed app.

You do not need to clone the source fork separately. The launcher fetches the
exact tested commit listed in `sioyek-app-revision`. It caches the source and Qt
under `~/Library/Caches/sioyek-build` for subsequent builds. No source-repo write
token is needed on the other laptop to download and build this public fork.

If Git refuses to pull because you edited `prefs_user.config`, stash that file
first, pull, then restore the stash. Only pop a stash if the first command reports
that it saved changes:

```sh
git stash push -m laptop-preferences -- prefs_user.config
git pull --ff-only
git stash pop
```

If restoring the stash reports a conflict, resolve it before building: keep your
chosen theme and machine preferences, and retain the updated portable commands.
The build itself does not modify your user config.

The first build needs Homebrew, Python 3, Xcode command-line tools and macOS 14+.
Source development and upstream merge instructions are in the fork's
[FORK.md](https://github.com/mxksm/sioyek-app/blob/development/FORK.md).

## Annotation shortcuts

- `p`: toggle freehand drawing; the filled cursor shows the current pen color.
- Shift+E: toggle circular eraser (removes only touched portions of strokes); Escape exits.
- Shift+P: rectangle eraser.
- Cmd+Z / Ctrl+Z: undo drawing; Cmd+Shift+Z: redo drawing. Erasing is not undoable.
- Shift+A: create a text box; `w`, then `a`: delete a visible annotation.

## Tabs and split view

- Cmd+T: open a PDF in a tab; Cmd+W: close the current tab.
- Cmd+1–9: select a tab in the focused pane.
- Cmd+Backslash: toggle two PDF panes sharing the same tabs.
- Ctrl+H / Ctrl+L: focus the left / right pane; Cmd+Option+W switches sides.
- Drag the divider to resize the panes. The top line marks the focused pane;
  both lines follow the theme. Each pane keeps its own position and zoom.
- Ctrl+T: open a separate window; Ctrl+W: close the entire window.

Collapsing a split keeps the focused PDF. Tabs are restored at startup, but the
split layout starts with one pane.

Custom script paths use `$CONFIG_DIR`, falling back to `$HOME/.config`.
