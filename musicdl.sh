#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Flatpak launcher for Music DL.
export PYTHONPATH=/app/lib/python3.13/site-packages${PYTHONPATH:+:$PYTHONPATH}
exec python3 /app/share/musicdl/downloader_gui.py "$@"
