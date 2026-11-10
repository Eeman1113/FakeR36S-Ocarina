#!/bin/sh
# Ship of Harkinian (Ocarina of Time) with the GLES2 renderer, the App Installer's app: its first start makes the game's
# assets from the player's ROM (common.sh). Saves and settings in data/. Log: HOME/logs/soh.log; overrides in data/env.
PORT=soh ELF=soh.elf TITLE="Ocarina of Time" O2RS="oot.o2r oot-mq.o2r" CONFIG=shipofharkinian.json
KEEP="shipofharkinian.json imgui.ini Save SoHTimeSplitData.json"
TAKES="N64 1.0 to 1.2 or PAL, GameCube or Master Quest"
. ./common.sh

# Torch's description of the ROM's version, out of assets-yml.zip: all of them would be 20,000 files on the card
prepare() {
    [ -d "$app/assets/$1" ] || unzip -q -o "$app/assets-yml.zip" "$1/*" -d "$app/assets"
}
start
