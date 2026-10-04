#!/usr/bin/env bash

cd ~/

set -e

COLOR='\033[1;32m'
NC='\033[0m' # No Color

log() {
  echo -e "${COLOR}#" $@ "${NC}"
}

WD=$(mktemp -d)
log "Working in: $WD"
cd $WD

log "Install dependencies"
for dependency in freeglut mesa harfbuzz; do
  if [ ! -d "$(brew --prefix)/opt/$dependency" ]; then
    brew install --quiet "$dependency"
  fi
done

log "Cloning source code"
git clone --quiet -b development --recurse-submodules -j8 https://github.com/ahrm/sioyek.git .

log "Fixing live status bar theme refresh"
python3 - <<'PY'
from pathlib import Path

path = Path('pdf_viewer/main_widget.cpp')
source = path.read_text()
anchor = 'void MainWidget::on_config_file_changed(ConfigManager* new_config) {'
assert source.count(anchor) == 1, 'Upstream config reload handler changed; review patch'
start = source.index(anchor)
end = source.index('\n}', start)
handler = source[start:end]
for label in ('status_label_left', 'status_label_right'):
    statement = f'{label}->setStyleSheet(get_status_stylesheet());'
    if statement not in handler:
        handler += '\n    ' + statement
source = source[:start] + handler + source[end:]
anchor = 'void MainWidget::on_configs_changed(std::vector<std::string>* config_names) {'
assert source.count(anchor) == 1, 'Upstream config notification handler changed; review patch'
call = '\n    on_config_file_changed(config_manager);'
if anchor + call not in source:
    source = source.replace(anchor, anchor + call, 1)
path.write_text(source)
PY

# Qt 6.8.1's macOS binaries are built with macOS 14 as their deployment
# target. The deployment target is the oldest supported macOS release, not
# the version currently running on this machine.
TARGET=14
log "macOS deployment target: $TARGET"
log "Modifying build configuration to use compatible target"
sed -Ei '' "s/QMAKE_MACOSX_DEPLOYMENT_TARGET.=.[0-9]+/QMAKE_MACOSX_DEPLOYMENT_TARGET = $TARGET/" pdf_viewer_build_config.pro
# Qt 6.8.1 needs ARM ACLE declarations with current Apple Clang.
echo 'QMAKE_CXXFLAGS += -include arm_acle.h' >> pdf_viewer_build_config.pro
# Upstream build_mac.sh rewrites this value again; pin that rewrite too.
sed -Ei '' 's/\$\(sw_vers -productVersion \| cut -d\. -f1\)/14/' build_mac.sh

log "Making python virtual environment in directory venv"
python3 -m venv venv
source venv/bin/activate

log "Installing aqtinstall"
pip install aqtinstall

log "Installing qt 6.8.1 with all modules"
aqt install-qt mac desktop 6.8.1 clang_64 -m all

# AGL was removed from current macOS SDKs, but Qt 6.8.1 still lists it in
# its qmake metadata. Modern Qt OpenGL uses the OpenGL framework directly.
find 6.8.1/macos -type f \( \
  -name '*.prl' -o -name '*.pri' -o -name '*.conf' -o -name '*.pc' \
\) -exec sed -Ei '' 's/-framework AGL//g' {} +

log "Deactivating venv"
deactivate

log "Defining QT-related environment variables"
export Qt6_DIR=$PWD/6.8.1/macos/
export QT_PLUGIN_PATH=$PWD/6.8.1/macos/plugins
export PKG_CONFIG_PATH=$PWD/6.8.1/macos/lib/pkgconfig
export QML2_IMPORT_PATH=$PWD/6.8.1/macos/qml
export PATH="$PWD/6.8.1/macos/bin:$PATH"

THREADS=$(sysctl -n hw.ncpu)
log "Starting the building process with $THREADS parallel threads"
env MAKE_PARALLEL=$THREADS ./build_mac.sh

log "Verifying app package signature"
codesign --verify --deep --strict build/sioyek.app

INSTALL_DIR=/Applications
BIN_DIR=/opt/homebrew/bin
if [ ! -w "$INSTALL_DIR" ]; then
  INSTALL_DIR="$HOME/Applications"
fi
if [ ! -w "$BIN_DIR" ]; then
  BIN_DIR="$HOME/.local/bin"
fi
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
if [ -e "$INSTALL_DIR/sioyek.app" ]; then
  BACKUP="$INSTALL_DIR/sioyek-backup-$(date +%Y%m%d-%H%M%S).app"
  log "Preserving installed app at $BACKUP"
  mv "$INSTALL_DIR/sioyek.app" "$BACKUP"
fi
log "Moving app to $INSTALL_DIR"
mv build/sioyek.app "$INSTALL_DIR/sioyek.app"
ln -sf "$INSTALL_DIR/sioyek.app/Contents/MacOS/sioyek" "$BIN_DIR/sioyek"

log "Remove all source code and intermediary objects"
cd /tmp
rm -rf "$WD"
