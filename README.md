# FakeR36S-Ocarina: native Ocarina of Time on a fake R36S

The Legend of Zelda: Ocarina of Time running natively (no emulator) on the fake R36S / GA36-MB handheld (Allwinner A23 or A33, Mali-400) under [FakeR36S-OS](https://github.com/Eeman1113/FakeR36S-OS) or [goodluckOS](https://github.com/CodeZombie/goodluckOS). Majora's Mask builds too.

This is a fork of [glOSports-harbourmasters](https://github.com/alvesmaicon/glOSports-harbourmasters) by **alvesmaicon**, who did the hard part: an OpenGL ES 2 renderer for [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright) on the Mali-400, the 32-bit ARM fixes and the audio fixes. FakeR36S-Ocarina adds a FakeR36S-OS package (it shows up in EmulationStation under **Ports**) and tuning for the dual-core A23.

**No game files are included.** You need your own Ocarina of Time ROM (N64 1.0 to 1.2 or PAL, GameCube, Master Quest). The game builds its assets from it on the first start.

## Install on FakeR36S-OS

1. Download `FakeR36S-ShipOfHarkinian-*.zip` from [Releases](https://github.com/Eeman1113/FakeR36S-Ocarina/releases) (or the latest build under Actions).
2. Unzip it into the root of the card's **HOME** partition. It adds `ports/soh/` and its menu entry.
3. Copy your ROM (`.z64`, `.n64`, `.v64` or a zip of one) to the root of HOME.
4. On the handheld, open **Ports**, then **The Legend of Zelda: Ocarina of Time**. The first start extracts the game from your ROM (a few minutes), then the game starts. Saves and settings live in `HOME/.config/soh`.

On goodluckOS, use the original App Installer zip (`ShipOfHarkinian-*.zip`) as described below.

## Saving

| Buttons | What it does |
|---|---|
| Select + R1 | Save state to the current slot |
| Select + L1 | Load the current slot |
| Select + Right / Left | Next / previous slot (0 to 5) |
| Select + X | Go back to the autosave state (refreshed every 5 seconds of gameplay) |

Save states are on by default and live in memory: they are instant, but they are gone when you quit the game or power off. For progress that survives that, the game's own save is also automatic here: Ship of Harkinian's **Autosave** and **Remember Save Location** are on by default, so the game saves itself every few minutes and on key events, and you continue where you saved. To keep a session paused without quitting, tap the power button: FakeR36S-OS freezes the game with the screen off and resumes it exactly where you were.

## Credits

- **alvesmaicon** for [glOSports-harbourmasters](https://github.com/alvesmaicon/glOSports-harbourmasters): the GLES2 renderer, 32-bit and audio fixes, launcher and build this fork is built on.
- **[HarbourMasters](https://github.com/HarbourMasters)** for Ship of Harkinian and 2 Ship 2 Harkinian.
- **Kenix3 and contributors** for [libultraship](https://github.com/Kenix3/libultraship).
- **The Zelda Reverse Engineering Team** ([zeldaret](https://github.com/zeldaret/oot)) for the decompilation everything starts from.
- **Lywx** for Torch, and the authors of ZAPDTR, OTRExporter and libzip.
- **CodeZombie and contributors** for [goodluckOS](https://github.com/CodeZombie/goodluckOS), the base of FakeR36S-OS.

The Legend of Zelda is Nintendo's. Use your own legally obtained ROM.

---

## Original README (glOSports-harbourmasters)

# Ship of Harkinian and 2 Ship 2 Harkinian for goodluckOS

Ocarina of Time and Majora's Mask, natively on the GA36-MB (Allwinner A33, 32-bit ARM, Mali-400, 512 MB of RAM) under [goodluckOS](https://github.com/CodeZombie/goodluckOS), from HarbourMasters' PC ports: [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright) 9.3.0 and [2 Ship 2 Harkinian](https://github.com/HarbourMasters/2ship2harkinian) 5.0.1. Their renderer needs OpenGL ES 3, which the Mali-400 lacks, so this port brings one written for OpenGL ES 2, a fix for 32-bit builds (the sky, the logo and the text went missing) and audio fixes. Ocarina of Time runs at 480p and 20 FPS, the cartridge's frame rate.

**Nothing of the games is in this repository.** You supply your own ROM: Ocarina of Time in a version Ship of Harkinian supports (N64 1.0 to 1.2 or PAL, or GameCube, Master Quest included), Majora's Mask in its N64 USA version.

Status: work in progress, tested on one GA36-MB (A33) only.

## Installing

Each port is an app for goodluckOS's App Installer (System Settings > System > App Installer).

1. **The port.** Download `ShipOfHarkinian-*.zip` (Ocarina of Time) and/or `2Ship2Harkinian-*.zip` (Majora's Mask) from [Releases](https://github.com/alvesmaicon/glOSports-harbourmasters/releases), copy it to the `apps` folder of the console's HOME and install it in the App Installer. It shows up in the Games tab.
2. **Your ROM.** Copy it to HOME, as a `.z64`, `.n64` or `.v64` file or a zip of one. Ship of Harkinian takes N64 1.0 to 1.2 or PAL, GameCube or Master Quest; 2 Ship 2 Harkinian the N64 USA version (1.0) or the GameCube USA one. The app knows the version by the CRC in the ROM's header (`app/<port>/roms.txt`); the game checks the whole file.
3. **On the console,** open the game. The first time, the launcher finds your ROM in HOME and starts the game with it: the game makes its assets from it by itself, in its ROM Extraction window, then starts. Without a ROM it takes, a screen says what to copy.

Saves, settings and the assets made from the ROM stay in `HOME/.config/soh` and `HOME/.config/2ship`, outside the apps: updates and uninstalls keep them. A port installed by hand before, in `HOME/ports/soh` or `HOME/ports/2ship`, hands its assets, settings and saves to the app on the first start, without the ROM.

## Building

On a PC with Docker (Intel or Apple Silicon; on a Mac, Colima or Docker Desktop). `oot` is the default game, `mm` the other:

```sh
GL_JOBS=3 ./build.sh oot game     # the armhf binary, out/soh/soh.elf (~40 min on an M1)
./build.sh oot assets             # soh.o2r, and oot.o2r from a ROM in out/roms/oot
./build.sh oot libs               # the libraries goodluckOS lacks, into out/soh/libs
./build.sh oot pack               # out/soh.tar, for HOME/ports
```

`./build.sh oot app` makes the App Installer's zip, `out/ShipOfHarkinian-<version>.zip` (`mm`: `2Ship2Harkinian`), from those. GitHub Actions (`.github/workflows/apps.yml`) builds both on every push to `main`; a tag like `v0.1.0` publishes them as that release, with `RELEASE.md` as its notes.

`./build.sh oot shot` runs the binary under qemu-arm on Xvfb and takes screenshots (in its own image, `tools/shot.Dockerfile`); `./build.sh oot native` builds it for the PC, to tell 32-bit bugs from renderer ones.

## Layout

| | |
|---|---|
| `build.sh`, `Dockerfile` | the build, in the `glosports-harbourmasters` image; sources and build trees in the `harbourmasters-work` volume |
| `patches/lus` | libultraship: the OpenGL ES 2 renderer, 32-bit heap pointers |
| `patches/soh`, `patches/2ship` | the ports: Torch's command line, the mixer's NEON on 32-bit ARM, audio, and SoH on to the game after extracting |
| `app/` | `common.sh` (finds the ROM, starts the game with it the first time), and per port its launcher, `app.puppy`, `roms.txt`, first settings (480p, bilinear, the cartridge's look) and own icon (`tools/icons.py`) |
| `native/setup.c` | the first start's screen when there is no ROM to take (SDL2, Pixelify Sans, from glOSports-stardew) |
| `cmake/2ship-deps.cmake` | tinyxml2 and spdlog for 2 Ship 2 Harkinian, built static |
| `tools/` | `perf.sh` (CPU per thread and GPU on the console), `cover.py` (launcher covers from your own art) |

## Credits and licenses

Ship of Harkinian and 2 Ship 2 Harkinian are by [HarbourMasters](https://github.com/HarbourMasters): 2 Ship 2 Harkinian is CC0, and Ship of Harkinian's repository has no license file. Both run on their [libultraship](https://github.com/Kenix3/libultraship) (Kenix3 and contributors, MIT) and build their assets with Torch (Lywx, MIT), ZAPDTR (the Zelda Reverse Engineering Team, MIT) and OTRExporter (HarbourMasters, MIT); [libzip](https://libzip.org/) is BSD-3-Clause. The games are Nintendo's, from your own ROM.

The apps' screen uses [Pixelify Sans](https://github.com/eifetx/Pixelify-Sans) (SIL Open Font License); each zip's `licenses` folder has the licenses of what it carries.

This repository's own code is MIT ([LICENSE](LICENSE)); its patches change the projects above and follow their terms.
