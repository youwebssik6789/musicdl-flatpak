#!/bin/sh
# Build MusicDL.flatpak from source. See README.md for prerequisites.
set -eu

cd "$(dirname "$0")/.."

app_id=io.github.deltaq471.musicdl
branch=master

sh scripts/render-icons.sh

# shellcheck disable=SC2086
flatpak-builder --force-clean --user ${FLATPAK_BUILDER_ARGS:-} \
    --repo=repo --default-branch="$branch" \
    build-dir "$app_id.json"

flatpak build-bundle repo MusicDL.flatpak "$app_id" "$branch"

echo "built $(pwd)/MusicDL.flatpak"
