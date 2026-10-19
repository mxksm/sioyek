#!/usr/bin/env bash
# Build the tested source revision from our fork; no source patching.
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SOURCE_REVISION=$(tr -d '[:space:]' < "$SCRIPT_DIR/sioyek-app-revision")
CACHE_DIR="${SIOYEK_BUILD_CACHE:-$HOME/Library/Caches/sioyek-build}"
SOURCE_DIR="$CACHE_DIR/source"
SOURCE_REPO=https://github.com/mxksm/sioyek-app.git
if [[ ! "$SOURCE_REVISION" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Invalid source revision in sioyek-app-revision" >&2
    exit 1
fi
mkdir -p "$CACHE_DIR"
if [ ! -e "$SOURCE_DIR" ]; then
    git clone --no-checkout "$SOURCE_REPO" "$SOURCE_DIR"
fi
if [ "$(git -C "$SOURCE_DIR" remote get-url origin)" != "$SOURCE_REPO" ]; then
    echo "Unexpected repository at $SOURCE_DIR; refusing to change it." >&2
    exit 1
fi
if ! git -C "$SOURCE_DIR" diff --quiet --ignore-submodules=all ||
   ! git -C "$SOURCE_DIR" diff --cached --quiet --ignore-submodules=all; then
    echo "Local source changes exist at $SOURCE_DIR. Commit or save them before updating." >&2
    exit 1
fi
git -C "$SOURCE_DIR" fetch origin "$SOURCE_REVISION"
git -C "$SOURCE_DIR" checkout --detach "$SOURCE_REVISION"
echo "Building sioyek-app at $SOURCE_REVISION"
export SIOYEK_BUILD_CACHE="$CACHE_DIR"
exec bash "$SOURCE_DIR/scripts/build-macos-local.sh"
