#!/bin/sh
# Render the PNG icons the manifest installs from the committed SVG.
# The PNGs are generated, not committed, so this must run before flatpak-builder.
set -eu

cd "$(dirname "$0")/.."

if ! command -v rsvg-convert >/dev/null 2>&1; then
    echo "error: rsvg-convert not found" >&2
    echo "  Fedora:        sudo dnf install librsvg2-tools" >&2
    echo "  Debian/Ubuntu: sudo apt install librsvg2-bin" >&2
    exit 1
fi

svg=io.github.deltaq471.musicdl.svg
rsvg-convert -w 128 -h 128 "$svg" -o io.github.deltaq471.musicdl.png
rsvg-convert -w 256 -h 256 "$svg" -o io.github.deltaq471.musicdl-256.png
echo "rendered 128x128 and 256x256 icons"
