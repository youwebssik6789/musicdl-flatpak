#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Flatpak launcher for Music DL.
export PYTHONPATH=/app/lib/python3.13/site-packages${PYTHONPATH:+:$PYTHONPATH}

# $HOME inside the sandbox is a temporary mount, so upstream's dotfiles would
# be discarded when the app exits. Point them at the app's persistent config
# directory instead, so settings and the cached SoundCloud client ID survive.
state=${XDG_CONFIG_HOME:-$HOME/.var/app/io.github.deltaq471.musicdl/config}/musicdl
mkdir -p "$state"
for name in .sc_dl.json .sc_cid; do
    if [ ! -e "$HOME/$name" ] && [ ! -L "$HOME/$name" ]; then
        ln -s "$state/${name#.}" "$HOME/$name" 2>/dev/null || true
    fi
done

exec python3 /app/share/musicdl/downloader_gui.py "$@"
