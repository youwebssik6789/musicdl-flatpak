# Music DL — Flatpak

Unofficial Flatpak packaging for [deltaq471/musicdl](https://github.com/deltaq471/musicdl),
a small Tkinter GUI that downloads audio from YouTube, SoundCloud and Spotify.

The app itself is **not modified**: the upstream source is pinned by commit and
SHA-256 and installed unmodified under `/app`.

## Install a prebuilt bundle

Every push to `main` builds `MusicDL.flatpak` in GitHub Actions:

1. Open the latest green run under **Actions → Flatpak**.
2. Download the `MusicDL.flatpak` artifact.
3. Install it:

```sh
flatpak install --user MusicDL.flatpak
flatpak run io.github.deltaq471.musicdl
```

The runtime `org.freedesktop.Platform//25.08` is fetched from Flathub on first
install.

## Build locally

Prerequisites on Fedora:

```sh
sudo dnf install flatpak flatpak-builder librsvg2-tools
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.freedesktop.Platform//25.08 org.freedesktop.Sdk//25.08
```

On Debian/Ubuntu the packages are `flatpak flatpak-builder librsvg2-bin`.

Then:

```sh
sh scripts/build.sh
```

That is a wrapper around three commands:

```sh
sh scripts/render-icons.sh        # SVG -> 128px/256px PNGs (generated, not committed)
flatpak-builder --force-clean --user --repo=repo --default-branch=master \
  build-dir io.github.deltaq471.musicdl.json
flatpak build-bundle repo MusicDL.flatpak io.github.deltaq471.musicdl master
```

Install your build with:

```sh
flatpak install --user "$PWD/repo" io.github.deltaq471.musicdl//master
```

The first build compiles Tcl 8.6.16 and Tk 8.6.16 from source, so expect
20–30 minutes. Later builds reuse `.flatpak-builder/cache`.

## Automatic updates

`.github/workflows/flatpak.yml` runs daily at 04:17 UTC, on every push to
`main`, and on demand:

1. `scripts/update-upstream.py` asks GitHub for the newest commit on
   `deltaq471/musicdl`'s default branch.
2. If it differs from the pinned commit, the script downloads the tarball,
   computes its SHA-256, rewrites the `url`/`sha256` pair in the manifest, and
   commits as `github-actions[bot]`.
3. The build job then produces a fresh `MusicDL.flatpak` artifact.

Nothing is uploaded anywhere by default — the bundle is an Actions artifact.
Tag pushes (`v*`) also attach it to a GitHub release. Artifact downloads need a
GitHub login, even though the repository is public.

To check upstream immediately instead of waiting for the cron job, open
**Actions → Flatpak → Run workflow** on `main`. That runs the update job first,
and the build job in the same run picks up whatever it pushed.

Manual bump, without CI:

```sh
python3 scripts/update-upstream.py          # rewrite the pin and commit
python3 scripts/update-upstream.py --check  # report only
```

The displayed version in `io.github.deltaq471.musicdl.metainfo.xml` is bumped by
hand on purpose: upstream's only tag is literally `release`, so it cannot be
mapped to a semver automatically.

## Permissions

| Permission | Why |
| --- | --- |
| `--share=network` | downloading from YouTube, SoundCloud and Spotify |
| `--share=ipc`, `--socket=x11` | Tk is an X11 toolkit (runs through XWayland on Wayland) |
| `--filesystem=~/Downloads/Music:create` | the only host path the app can see; `:create` makes Flatpak create it if missing |
| `--talk-name=org.freedesktop.portal.*` | opening finished files/folders in your default handler |

There is **no** `home` access: the rest of `~`, including the rest of
`Downloads`, is invisible to the app. The app's default save folder is
`~/Downloads/Music` and its file chooser is a plain Tk/X11 dialog rather than an
XDG portal picker, which is why the path is granted directly instead of through
a portal.

## Layout

| File | Purpose |
| --- | --- |
| `io.github.deltaq471.musicdl.json` | main manifest |
| `tcl.json`, `tk.json` | Tcl/Tk 8.6.16, built from source |
| `python-tkinter.json` | `_tkinter` extension + `tkinter` package for the runtime's Python 3.13 |
| `yt-dlp.json` | yt-dlp wheel, extracted at build time (no pip) |
| `musicdl.sh` | launcher installed as `/app/bin/musicdl` |
| `*.desktop`, `*.metainfo.xml`, `*.svg` | desktop integration and icon source |
| `scripts/build.sh` | local/CI build entry point |
| `scripts/render-icons.sh` | renders the PNG icons from the SVG |
| `scripts/update-upstream.py` | moves the source pin to upstream HEAD |

## Notes

- The freedesktop runtime ships Python 3.13 and ffmpeg (with libmp3lame,
  libvorbis, flac, aac), but no Tcl/Tk and no `tkinter`, hence the compiled
  modules.
- yt-dlp is vendored from a pinned wheel so builds never need PyPI access, but
  that also means the bundled yt-dlp goes stale until `yt-dlp.json` is bumped.
- Only the SVG icon is committed; the PNGs are rendered during the build.
- Packaging only. Nothing here audits the app: upstream still retries HTTPS
  requests with certificate verification disabled if a certificate error
  occurs, and the sandbox is what limits the damage. Do not open files you did
  not expect to download.
- The bundled app is Apache-2.0, © the upstream author; these packaging files
  are provided as-is.
