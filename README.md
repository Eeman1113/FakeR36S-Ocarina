# Ship of Harkinian and 2 Ship 2 Harkinian for goodluckOS

Ocarina of Time and Majora's Mask, natively on the GA36-MB (Allwinner A33, 32-bit ARM, Mali-400, 512 MB of RAM) under [goodluckOS](https://github.com/CodeZombie/goodluckOS), from HarbourMasters' PC ports: [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright) 9.3.0 and [2 Ship 2 Harkinian](https://github.com/HarbourMasters/2ship2harkinian) 5.0.1. Their renderer needs OpenGL ES 3, which the Mali-400 lacks, so this port brings one written for OpenGL ES 2, a fix for 32-bit builds (the sky, the logo and the text went missing) and audio fixes. Ocarina of Time runs at 480p and 20 FPS, the cartridge's frame rate.

**Nothing of the games is in this repository.** You supply your own ROM: Ocarina of Time in a version Ship of Harkinian supports (N64 1.0 to 1.2 or PAL, or GameCube, Master Quest included), Majora's Mask in its N64 USA version.

Status: work in progress, tested on one GA36-MB (A33) only. Next: an App Installer app for each game that extracts your ROM on the console at its first start.

## Building

On a PC with Docker (Intel or Apple Silicon; on a Mac, Colima or Docker Desktop). `oot` is the default game, `mm` the other:

```sh
GL_JOBS=3 ./build.sh oot game     # the armhf binary, out/soh/soh.elf (~40 min on an M1)
./build.sh oot assets             # soh.o2r, and oot.o2r from a ROM in out/roms/oot
./build.sh oot libs               # the libraries goodluckOS lacks, into out/soh/libs
./build.sh oot pack               # out/soh.tar, for HOME/ports
```

`./build.sh oot shot` runs the binary under qemu-arm on Xvfb and takes screenshots (in its own image, `tools/shot.Dockerfile`); `./build.sh oot native` builds it for the PC, to tell 32-bit bugs from renderer ones.

## Layout

| | |
|---|---|
| `build.sh`, `Dockerfile` | the build, in the `glosports-harbourmasters` image; sources and build trees in the `harbourmasters-work` volume |
| `patches/lus` | libultraship: the OpenGL ES 2 renderer, 32-bit heap pointers |
| `patches/soh`, `patches/2ship` | the ports: Torch's command line, the mixer's NEON on 32-bit ARM, audio |
| `app/` | each port's launcher and first settings (480p, bilinear, the cartridge's look) |
| `cmake/2ship-deps.cmake` | tinyxml2 and spdlog for 2 Ship 2 Harkinian, built static |
| `tools/` | `perf.sh` (CPU per thread and GPU on the console), `cover.py` (launcher covers from your own art) |

## Credits and licenses

Ship of Harkinian and 2 Ship 2 Harkinian are by [HarbourMasters](https://github.com/HarbourMasters): 2 Ship 2 Harkinian is CC0, and Ship of Harkinian's repository has no license file. Both run on their [libultraship](https://github.com/Kenix3/libultraship) (Kenix3 and contributors, MIT) and build their assets with Torch (Lywx, MIT), ZAPDTR (the Zelda Reverse Engineering Team, MIT) and OTRExporter (HarbourMasters, MIT); [libzip](https://libzip.org/) is BSD-3-Clause. The games are Nintendo's, from your own ROM.

This repository's own code is MIT ([LICENSE](LICENSE)); its patches change the projects above and follow their terms.
