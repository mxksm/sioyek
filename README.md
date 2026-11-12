# Custom Sioyek Configuration

macOS configuration, keyboard shortcuts, themes, and a build launcher for the
[mxksm/sioyek-app](https://github.com/mxksm/sioyek-app) fork of
[Sioyek](https://github.com/ahrm/sioyek). The fork adds PDF tabs, split view,
drawing tools, a temporary laser pointer, and searchable floating document pickers.
See the [app README](https://github.com/mxksm/sioyek-app#readme) for the fork's
features and instructions for building directly from source.

## Configuration

- [keys_user.config](keys_user.config): keyboard shortcuts.
- [prefs_user.config](prefs_user.config): colors, startup commands, pen settings,
  laser duration, and search preferences.
- [commands/](commands/): file-navigation scripts and a theme-switch compatibility helper.
- [sioyek-app-revision](sioyek-app-revision): the app commit used by the build launcher.

Keep machine-specific settings in **`prefs_local.config`**, beside
`prefs_user.config`. It is loaded last and ignored by Git, so pulls do not replace
it or conflict with changes to the public defaults. The build launcher creates
an empty file when needed; it never overwrites an existing one.

For example, create/edit `~/.config/sioyek/prefs_local.config` with:

```conf
pdf_library_path ~/Documents/university
```

Leave `pdf_library_path ~/Documents` in the tracked `prefs_user.config`. Other
preferences can go in the local file too. Restart Sioyek after editing the local
file; no rebuild is needed. For an existing installation, create the local file
before opening Sioyek with this configuration.

## Themes and file navigation

- **Theme picker** — `Space th` opens a floating, searchable list of 26 palettes.
  Start in normal mode: `j`/`k`, `gg`/`G` navigate; `i` or `/` starts searching;
  Enter applies a theme. Escape returns to normal mode, then closes the picker.
- **Favorite themes** — Option+1–5, Option+8–9, and Option+0 keep their original
  themes. The picker shows assigned shortcuts and the current theme.
  Slots 6 and 7 are available for personal favorites.
- **File Navigation** — Open the previous PDF with Shift+D or the next with Shift+L, sorted alphanumerically within the current directory.
- **Current Folder** — Browse the current PDF's directory with Space F D.

> Keep this configuration at `$CONFIG_DIR/sioyek`, or `~/.config/sioyek` when `$CONFIG_DIR` is unset.

In **Space T H**, move with `j`/`k` or the arrow keys to preview themes across
the app. **Enter** saves the selected theme; **Esc** closes the picker and restores
the original theme. When editing the search, the first Esc returns to normal mode.
Previews do not change the saved selection.

Themes live in `themes/<name>.config`, with one palette per file. `source_theme
catppuccin_latte` in `prefs_user.config` supplies the fresh-install default. The
chosen theme is saved separately in **`theme_state`**, which Git ignores.
Switching themes never rewrites `prefs_user.config`; pulling updates therefore
preserves the local selection. `prefs_local.config` loads after the palette,
so personal color overrides and favorite assignments take precedence.

For example, in `prefs_local.config`:

```conf
theme_slot_1 nord
theme_slot_6 rose_pine
theme_slot_7 paper_sepia
```

These assign Option+1, Option+6, and Option+7. Use the palette filename without `.config` as the identifier. Friendly display
names come from metadata in each palette file. Any slot
0–9 can be reassigned. The key bindings themselves remain in `keys_user.config`.
You can also run `set_theme(nord)` in a macro.

The original favorites now have these display names:

| Shortcut | Display name | Palette identifier |
| --- | --- | --- |
| Option+1 | Flexoki Dark | `flexoki_dark` |
| Option+2 | Monokai Midnight | `monokai_midnight` |
| Option+3 | Slate | `slate` |
| Option+4 | Tokyo Dracula | `tokyo_dracula` |
| Option+5 | Cocoa | `cocoa` |
| Option+8 | Gruvbox Light | `gruvbox_light` |
| Option+9 | Catppuccin Latte | `catppuccin_latte` |
| Option+0 | Paper White | `paper_white` |

Other renamed palettes are Sandstone (`sandstone`), Parchment (`parchment`),
Catppuccin Graphite (`catppuccin_graphite`), and Violet Charcoal (`violet_charcoal`).

To make a personal palette, copy an existing file to `themes/local-my-theme.config`
and edit its colors. Files named `local-*.config` are ignored by Git and appear
in the picker automatically the next time it opens. Keep the palette's complete
set of color settings so switching from another theme gives consistent results.
Set `# name: My Theme` and `# description: Dark · muted colors` at the top of a
palette to choose its picker label and description. Themes are sorted by their
display names. Editing the active palette reloads it immediately. The shell helper
`commands/theme_switch.sh <name>` updates the same local state for scripts.

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

Press `t` for the wide floating table of contents. Use `j`/`k` or `gg`/`G`
to select sections, `i` to search, and Enter to jump. Esc returns to normal mode
or closes the panel; left/right arrows collapse/expand chapters in normal mode.

Press `p`, type a page number, then Enter to jump to that page (for example, `p12` then Enter).

## Floating menus and compact status

Bookmarks, highlights, marks, portals, the older document/window lists, and
configuration-file and custom-option menus use the same wide floating picker.
They start in normal mode: `j`/`k`, `gg`/`G`, `i` to search, and Enter to select.
Existing delete/edit actions remain available; Cmd+Delete removes the selected
entry even while the search field contains a query.

`sb` toggles a compact, square status panel at the bottom-right of each PDF pane.
It normally shows only the page count. Active tools add a short label; the pen
also shows its width and ink color. Search shows the current match, and zoom
appears for 1.5 seconds after changing it. No full-width strip is reserved.

The tabs use the same theme colors in a centered floating strip, with square
edges and space around it. It fits the tab labels and scrolls horizontally when
needed; `st` still shows or hides it.

Errors (including missing contents or SyncTeX data) appear inside the Sioyek
window. Dismiss them with **Enter**, **Esc**, or the Dismiss button.

Workspace-save confirmations, ink copy/cut/paste feedback, and text-selection
notices disappear after three seconds. Active input prompts remain until completed
or cancelled.

Pending key sequences show **Awaiting key** and a compact list of continuations.
For example, **Space** lists the file shortcuts; **Space f** narrows them to
**f**, **l**, **w**, and **d**. Complete the shortcut or press **Esc** to cancel.
To hide the continuation panel, set `show_command_hints 0` in `prefs_local.config`;
the pending-key status remains available.

Optional settings in `prefs_local.config`:

```conf
# Include the current chapter in the compact status panel.
status_bar_show_chapter 1
# Restore the legacy strip and status_bar_format customization if preferred.
# compact_status_bar 0
```

## Annotation shortcuts

- `x`: toggle freehand drawing; the filled cursor shows the current pen color.
- Cmd+R / Cmd+G / Cmd+B: select red / green / blue ink. Option+W changes pen width.
- Hold the right mouse button while drawing to erase; release to return to the pen.
- C (unshifted): toggle circular eraser (removes only touched portions of strokes); Escape exits.
- Shift+P: rectangle eraser.
- Option+V: lasso ink. Draw around strokes, drag inside the selection to move, or
  drag a corner to scale. Escape cancels an active drag or exits the lasso.
  In lasso mode, `y` copies, `d` cuts, and `p` pastes at the center of the pane;
  the pasted group stays selected for moving/scaling. `x` returns to the pen.
  Named registers work with `"ay`, `"ad`, and `"ap` (letters a–z), shared across
  PDFs and windows until the app quits. The ink clipboard uses at most 32 MiB.
  Moves, scaling, cuts and pastes support Cmd+Z / Cmd+Shift+Z and save automatically.
  The lasso edits ink on unrotated PDFs, including the blank canvas.
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

## Shortcuts and commands

Press `:` for a wide floating list of commands and their keyboard shortcuts.
It starts in normal mode: `j`/`k` move through results, `gg`/`G` jump to the ends,
and `i` enters the search field. Search filters the list as you type. Enter runs
the selected command; `yy` copies its name. Escape returns to normal mode, then
closes the picker. The selected command's description appears below the list.
`?` is intentionally unbound.

## Finding documents

- Space F L: search library PDF filenames and titles, including files never opened before.
- Space F W: search text across every page of library PDFs.
- Space F F: search recent documents.
- Space F D: browse and search the current PDF's directory.
- Press each key in sequence. These replace the old Shift+O, Cmd+Shift+O,
  Ctrl+Shift+O, Cmd+Shift+F, and Space F A aliases. Apostrophe is “go to mark.”
- Each document picker has a PDF preview on the right. Ctrl+L / Ctrl+D browse
  preview pages (Ctrl+U also goes back). Content search lists each file once,
  highlights its matches, and lets you use [ / ] in normal mode to jump between
  matching pages. Enter opens the previewed page. Nearby results are preloaded
  and cached to avoid a loading flash while moving through the list.
- Filename search matches filename, PDF metadata title, or text on the first page. Words can be
  entered in any order; capitalization and accents do not matter. Small typos are
  tolerated with `fuzzy_searching 1` in `prefs_user.config`.
- Use the arrow keys and Enter to choose a result.
  The selected file opens in the pane that launched the picker.
- Long lists expand to the available window height. Scroll to see further results;
  arrow keys stay within the picker at either end of the list.
- Cmd+Delete removes the selected entry from recents, including while searching.
  The search text stays intact, and the PDF remains on disk.
- In the folder picker, Enter opens a folder. Backspace in an empty search field,
  or Option+Up, goes to its parent. Pasting a file or folder path also works.

The public `prefs_user.config` defaults to:

```conf
pdf_library_path ~/Documents
```

Set a different location in the ignored `prefs_local.config` described above.
Use semicolons for multiple folders, for example:

```conf
pdf_library_path ~/Documents; ~/Downloads; ~/Books
```

Results combine every folder and its subfolders; overlapping files appear only
once. An unavailable folder does not block the others. Spaces need no quotes;
semicolons are separators. `~` means your home folder. Reopen the picker after
changing the setting. Library
results show their containing folders; folder names are searchable too. Scans run
in the background, use a session cache, and refresh on opening and every 30
seconds while the picker is visible. Hidden folders and symlinks are skipped.
Scanning leaves recents untouched; Enter opens the selected PDF.

Content search matches a case-insensitive phrase with normalized whitespace.
It extracts text in the background and caches it on disk, refreshing changed PDFs.
Results arrive progressively, one per PDF, up to 2,000 PDFs per query.
Unreadable or encrypted PDFs are skipped; scanned images require an OCR text layer.

Titles are indexed locally in the background and cached for the running session.
Image-only scans need searchable text or title metadata to match by title.

All document pickers start in **normal mode**. Press `i` to type a search, then Escape to
return to normal mode. Escape in normal mode closes the picker; Ctrl+C closes
immediately. The heading shows the mode.
In normal mode, `j` / `k` navigate results, `gg` / `G` select the first / last
result in the current search, and `i` / `a` resume typing. Use
`h` / `l`, `w` / `b` / `e`, and `0` / `$` to move through the query; `v` starts
visual selection and `x` deletes it. `~` swaps uppercase/lowercase in the
selection and returns to normal mode. In normal mode, `~` toggles the character
under the cursor (`3~` toggles three characters). `s` replaces the selection or
current character and enters insert mode (`3s` replaces three characters).
These work in all Vim-enabled
text fields, including prompts and annotations. `yy` copies the selected file or folder's full
path (using aliases and shell quoting) to the system clipboard; visual-mode `y` copies search text (`Vy` copies the
whole query). `p` pastes, and `u` / Ctrl+R undo / redo search edits. `dd`, `dw`, and
`cw` delete or change text. Escape leaves visual mode before closing the picker.
See the [full editing shortcuts](https://github.com/mxksm/sioyek-app#vim-style-search-editing)
for the supported motions and commands.

PDF text search (`/`) opens in insert mode so you can type immediately. Escape
returns to normal mode for Vim editing; Enter submits from either mode. Document
and command pickers keep their normal-mode default. All text-only prompts
(including text annotations, rename, and workspace names) start in insert mode.
To reopen a text annotation from the keyboard, press `sa`, then type its label.
The editor opens with the existing text ready to edit; Enter saves it.

Regular PDF search highlights all visible matches (`should_highlight_unselected_search 1`
in `prefs_user.config`), with a separate color for the active match. Library content
previews also highlight every occurrence on the previewed page. `n` / Shift+N
step through matches; when the active match scrolls offscreen, the visible match
nearest the center becomes active. On a page with no visible matches, stepping
resumes from your current position.

`render_cache_size_mb 256` limits retained page images across windows. Visible
images stay protected; this is not a cap on total Sioyek memory. It allows unused
large images from fullscreen/zooming to be released after a short grace period.

## Tabs and split view

- Cmd+T: open the persistent blank canvas; Cmd+W: close the current tab (the last tab returns to the canvas).
- Cmd+Shift+T: reopen the last closed tab with its reading position. Repeat to restore earlier closed tabs.
- Cmd+1–8: select a numbered tab in the focused pane. Cmd+9 selects the last tab.
- Shift+E / Shift+R: select the tab to the left / right, wrapping at either end.
- Option+R / Option+Shift+R: rotate clockwise / counterclockwise.
- Shift+, (`<`) / Shift+. (`>`): move the focused PDF's tab one place left / right.
  Tabs stop at either end without wrapping; both split panes keep their views.
- Ctrl+Tab: cycle through tabs in most-recently-used order. Keep Ctrl held to
  display the switcher; release Ctrl to open the selection. Shift reverses direction.
  A quick tap switches without showing the panel; the PDF stays unchanged while
  choosing from the open switcher.
- Cmd+Backslash: toggle side-by-side PDF panes sharing the same tabs.
- Cmd+Shift+Backslash: toggle top-and-bottom panes. Switching between the two
  layouts preserves both PDFs and their reading positions. Repeating the current
  layout's shortcut collapses it; there are always at most two panes.
- Ctrl+K / Ctrl+J: focus the top / bottom pane.
- Cmd+L: link navigation in both panes (opens a split if needed). Both indicators
  light up. Movement, page jumps, zoom, fitting and rotation apply to both,
  including navigation macros. Tab selection, annotations and mouse-wheel
  scrolling stay independent. Closing the split disables linking.
- Ctrl+H / Ctrl+L: focus the left / right pane; Cmd+Option+W switches sides.
- Drag the divider to resize the panes. The top line marks the focused pane;
  both lines follow the theme. Each pane keeps its own position and zoom.
- Ctrl+T: open a separate window; Ctrl+W: close the entire window.
- `st` / `sb`: show or hide the tab bar / status bar.

Collapsing a split keeps the focused PDF. Tabs are restored at startup, but the
split layout starts with one pane.

Custom script paths use `$CONFIG_DIR`, falling back to `$HOME/.config`.

## Named workspaces

- **Cmd+Shift+S** (`save_workspace`): name and save the current window's layout.
  Saving the same name updates it; the last name is prefilled.
- **Cmd+Shift+P** (`open_workspace`): search saved workspaces and press Enter to
  restore one in the current window. Other windows stay as they are.

Workspaces save tab order, the selected PDF in each pane, each tab's zoom and
position, split orientation and proportions, and keyboard focus. They can include the hidden scratch
canvas, which remains shared across every workspace. Saved layouts are snapshots:
save again when you want to update one.

The floating picker uses the same Vim controls as document search: `i` to search,
Escape to return to normal mode, `j`/`k` and `gg`/`G` to navigate, Enter to open.
**Previous session (automatic)** restores the layout you had immediately before
the last workspace switch, including an unnamed set of tabs. Missing PDFs leave
the current layout intact and show their path.

In the workspace picker, **Cmd+Delete** removes the selected saved layout, including
while searching or editing the search. It selects the next result and leaves the
open PDFs and annotations untouched. The automatic Previous session entry can
also be removed; switching workspaces creates a new recovery entry.

Layouts are stored in `workspaces.json` in Sioyek's application-data directory
(on macOS, `~/Library/Application Support/sioyek/`). This file contains paths and
view settings, not copies of PDFs or drawings.

### Blank canvas

Cmd+T opens one persistent **100-page** blank PDF, shared across windows and panes. It has no
number or label in the tab bar and stays out of recents, the library and Ctrl+Tab.
Repeated Cmd+T reuses it. Closing the last PDF with Cmd+W returns to the canvas;
Cmd+W on the canvas leaves it open. Use the document pickers to open real PDFs.

Use the usual page navigation (`d`/`l`, `gg`/`G`) to move around the canvas.
Existing one-page canvases expand automatically, preserving page-one drawings and
keeping the original PDF as `blank.pdf.before-expansion`.

Draw with the usual pen and eraser shortcuts. Finished strokes, undo and redo
are saved automatically. The PDF and its drawing sidecar live in the `canvas`
folder inside Sioyek's application-data directory (on macOS,
`~/Library/Application Support/sioyek/canvas/`). Back up the whole folder: the
strokes are in `blank.pdf.sioyek.drawings`, separate from `blank.pdf`. Rebuilds
do not replace these files. An existing personal PDF named `blank.pdf` is untouched.

## Select PDF text with Vim motions

Press **`v`** to select text directly in the PDF with a visible caret and live highlighting.
Use **`h/j/k/l`**, **`w/b/e`**, **`0/^/$`**, and **`gg/G`**; counts such as **`3w`** work too.
**`iw/aw`** select the current word without/with whitespace, and **`o`** switches the moving endpoint.
Press **`v`** again to move just the caret, then **`v`** to start a new selection there.
**`y`** or **Cmd+C** copies and exits; **Escape/Enter** leaves the selection available for highlighting.
It starts from existing selected text, text under the mouse, or the center of the focused pane.
This works across pages and in either split pane. The command is `visual_select`.

## Jump from a PDF to LaTeX source

On macOS, **Cmd+click** the PDF text to open the corresponding source location.
Alternatively, press **`sd`** (`synctex_select_line`) to label the visible text
lines, then type a label to jump to its source. Escape cancels the labels.
Both work in either split pane; Cmd+click also works while drawing without
leaving ink. The existing SyncTeX right-click mode remains available.

Compile with SyncTeX enabled (`-synctex=1`) and keep the `.synctex.gz` file
beside the PDF. VimTeX enables this in its default latexmk configuration:
open the PDF using `:VimtexView` so it supplies the callback to the existing
editor. For another editor, configure `inverse_search_command`, using `%1`
for the source path, `%2` for its line and `%3` for its column. Quote `%1`
when it is a separate command argument. A rotated PDF must be rotated back
before inverse search.

### Friendly paths

`path_aliases` lists preferred folder paths, separated by semicolons. Put it in
`~/.config/sioyek/prefs_local.config`, since these folders belong to the local
computer. For example:

```
path_aliases ~/Documents/university; ~/Books
```

When a folder is a symlink, document pickers and the recent-tab switcher show
that friendly path instead of its resolved target (such as an iCloud directory).
The most specific matching target wins; missing folders are ignored. Canonical
paths remain in use internally for history, tabs and annotations.

In document pickers, `yy` copies the friendly absolute path. On macOS/Linux,
paths containing spaces or shell metacharacters are quoted automatically for
pasting into a terminal. Workspace and command names are copied unchanged.
This setting is intentionally absent from the shared `prefs_user.config`.
`prefs_local.config` is ignored by Git and must be configured separately on each Mac.
