#!/bin/sh
# 2 Ship 2 Harkinian (Majora's Mask) with the GLES2 renderer, the App Installer's app: its first start makes
# the game's assets from the player's ROM (common.sh). Saves, settings and assets in HOME/.config/2ship (overrides:
# its env); log: HOME/logs/2ship.log.
PORT=2ship ELF=2s2h.elf TITLE="Majora's Mask" O2RS=mm.o2r CONFIG=2ship2harkinian.json
KEEP="2ship2harkinian.json imgui.ini saves presets randomizer"
TAKES="the N64 USA version (1.0) or the GameCube USA one"
. ./common.sh
start
