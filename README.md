# Music DL — Flatpak

Unofficial Flatpak packaging for [deltaq471/musicdl](https://github.com/deltaq471/musicdl),
a small Tkinter GUI that downloads audio from YouTube, SoundCloud and Spotify.

The app itself is **not modified**: the upstream source is pinned by commit and
SHA-256 and installed unmodified under `/app`.

## Install a prebuilt bundle

Every successful build is published to a rolling
[**latest release**](https://github.com/youwebssik6789/musicdl-flatpak/releases/latest),
so the download URL never changes:

```sh
curl -LO https://github.com/youwebssik6789/musicdl-flatpak/releases/download/latest/MusicDL.flatpak
flatpak install --user MusicDL.flatpak
flatpak run io.github.deltaq471.musicdl
```

Or download `MusicDL.flatpak` by hand from the release page. The release notes
list the upstream commit it was built from, the build timestamp and the bundle's
SHA-256, so you can check what you are installing.

The runtime `org.freedesktop.Platform//25.08` is fetched from Flathub on first
install.

The same bundle is also attached to each Actions run as an artifact for 30 days,
which is handy for going back to an older build. Artifact downloads need a
GitHub login even though the repository is public.

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
3. The build job then produces a fresh `MusicDL.flatpak` and republishes the
   `latest` release with it.

The release is a single rolling one: the `latest` tag is force-moved to the
commit each bundle was built from, and the `MusicDL.flatpak` asset is replaced
in place, so there is always exactly one download link and no pile of old
releases. Each Actions run also keeps its own `MusicDL.flatpak` artifact for 30
days if you want an older build. Artifact downloads need a GitHub login, even
though the repository is public.

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
| `LICENSE`, `NOTICE` | Apache-2.0 license text and attribution |

## Notes

- The freedesktop runtime ships Python 3.13 and ffmpeg (with libmp3lame,
  libvorbis, flac, aac), but no Tcl/Tk and no `tkinter`, hence the compiled
  modules.
- yt-dlp is vendored from a pinned wheel so builds never need PyPI access, but
  that also means the bundled yt-dlp goes stale until `yt-dlp.json` is bumped.
- Only the SVG icon is committed; the PNGs are rendered during the build.
- The `latest` release is rolled over, not appended to: its asset is replaced on
  every successful build and its tag is force-moved to the commit that produced
  the bundle. Old builds remain available as per-run Actions artifacts.
- Packaging only. Nothing here audits the app: upstream still retries HTTPS
  requests with certificate verification disabled if a certificate error
  occurs, and the sandbox is what limits the damage. Do not open files you did
  not expect to download.

## License

The packaging in this repository — manifest, module definitions, build and
update scripts, desktop integration and icon source — is licensed under the
[Apache License 2.0](LICENSE). Each script carries an
`SPDX-License-Identifier: Apache-2.0` tag, and [NOTICE](NOTICE) holds the
attribution.

The application itself is [deltaq471/musicdl](https://github.com/deltaq471/musicdl),
also Apache-2.0, © its author. It is built from an unmodified upstream tarball.

Because the bundle redistributes code written by others, it carries every
license text it owes, all under `/app/share/licenses`:

| Path | Component | License |
| --- | --- | --- |
| `io.github.deltaq471.musicdl/LICENSE` | musicdl itself | Apache-2.0 |
| `tcl/license.terms` | Tcl 8.6.16 | BSD-style |
| `tk/license.terms` | Tk 8.6.16 | BSD-style |
| `zlib/LICENSE` | zlib, vendored in Tcl | zlib |
| `libtommath/LICENSE` | libtommath, vendored in Tcl | public domain |
| `python/LICENSE` | CPython `tkinter` + `_tkinter` | PSF-2.0 |
| `.../yt_dlp-*.dist-info/licenses/LICENSE` | yt-dlp | Unlicense |

The CI smoke test checks each of these files after installing the bundle, so a
missing license fails the build instead of shipping quietly.
