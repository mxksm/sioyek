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
brew install --quiet freeglut mesa harfbuzz

log "Cloning source code"
git clone --quiet -b development --recurse-submodules -j8 https://github.com/ahrm/sioyek.git .

TARGET=$(sw_vers -productVersion | cut -d. -f1)
log "macOS target: $TARGET"
log "Modifying build script to use new target"
sed -Ei '' "s/QMAKE_MACOSX_DEPLOYMENT_TARGET.=.[0-9]+/QMAKE_MACOSX_DEPLOYMENT_TARGET = $TARGET/" pdf_viewer_build_config.pro

log "Making python virtual environment in directory venv"
python3 -m venv venv
source venv/bin/activate

log "Installing aqtinstall"
pip install aqtinstall

log "Installing qt 6.8.1 with all modules"
aqt install-qt mac desktop 6.8.1 clang_64 -m all

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

log "Extracting build artifact into /tmp/sioyek.app"
mv build/sioyek.app /tmp/sioyek.app
log "Signing app package"
sudo codesign --force --sign - --deep /tmp/sioyek.app

log "Remove all source code and intermediary objects"
cd /tmp
rm -rf $WD

log "Moving app to /Applications"
mv /tmp/sioyek.app /Applications/
ln -s /Applications/sioyek.app/Contents/MacOS/sioyek /usr/local/bin/sioyek
