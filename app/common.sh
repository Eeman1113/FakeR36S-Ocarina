# common.sh: what both apps' launchers share, sourced in the app's folder once they set PORT (soh, 2ship), ELF, TITLE,
# O2RS (the archives a ROM makes), CONFIG (the port's settings file) and KEEP (what of an older HOME/ports/<port> is
# the player's). The game makes its assets from the player's ROM by itself, in its ROM Extraction window, when it is
# started with the ROM: this finds the ROM in HOME first (by the CRC in its header, the version the port reads), or the
# assets of an install from before the App Installer. Saves, settings and assets live in HOME/.config/<port>, outside
# the app, as Luanti's worlds and Stardew Valley's saves do: an uninstall keeps them, and a new install needs no ROM.
app=$(pwd)
data=$HOME/.config/$PORT
log=$HOME/logs/$PORT.log
export SHIP_HOME=$data
export LD_LIBRARY_PATH=$app/libs${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
# where the first test builds kept them
[ ! -d "$app/data" ] || [ -e "$data" ] || { mkdir -p "${data%/*}" && mv "$app/data" "$data"; }
mkdir -p "$data" "$HOME/logs"

# TAKES: the ROMs the port takes, in a few words (translated below)
# the Portuguese is here, not in goodluckOS's pt-BR.lang, so that the app brings its messages' translation
LANGUAGE=$(sed -n 's/^language=//p' "$HOME/.config/puppy/settings" 2>/dev/null | tail -n 1)
translate() {
    [ "$LANGUAGE" = pt-BR ] || return 0
    awk -v key="$1" 'index($0, key " = ") == 1 { print substr($0, length(key) + 4); exit }' <<'LANG'
Getting your game ready = Preparando o seu jogo
No %s ROM in HOME. Copy yours to HOME, as a .z64, .n64 or .v64 file or a zip of one, and open the game again. It takes: %s = Nenhuma ROM de %s na HOME. Copie a sua para a HOME, como arquivo .z64, .n64 ou .v64 ou um zip dele, e abra o jogo de novo. Ele aceita: %s
The ROM in %s could not be unpacked: is the zip whole? = Não deu para descompactar a ROM de %s: o zip está inteiro?
Press any button to go back = Aperte qualquer botão para voltar
the N64 USA version (1.0) or the GameCube USA one = a versão de N64 americana (1.0) ou a de GameCube americana
N64 1.0 to 1.2 or PAL, GameCube or Master Quest = N64 1.0 a 1.2 ou PAL, GameCube ou Master Quest
LANG
}

text() {
    _t=$(translate "$1")
    printf '%s' "${_t:-$1}"
}

# say <kind> "English text with %s" [args]: translated as Puppy is, a line for the setup screen
say() {
    _kind=$1
    _fmt=$(translate "$2")
    [ -n "$_fmt" ] || _fmt=$2
    shift 2
    printf '%s %s\n' "$_kind" "$(printf "$_fmt" "$@")"
}

# the setup screen with one error and its prompt, then back to the launcher
fail() {
    {
        printf 'T %s\n' "$TITLE"
        say U "Getting your game ready"
        say E "$@"
        say W "Press any button to go back"
    } | tee -a "$log" | "$app/setup" "$app/fonts/PixelifySans.ttf" > /dev/null
    exit 1
}

ready() {
    for _o in $O2RS; do [ -f "$data/$_o" ] && return 0; done
    return 1
}

# the roms.txt line of the ROM whose first bytes come on stdin: its byte order from the first word (z64 big-endian,
# v64 byte-swapped, n64 little-endian), the CRC from the word at 0x10
rom_line() {
    _h=$(head -c 20 | od -An -tx1 | tr -d ' \n')
    _c=$(echo "$_h" | cut -c33-40)
    case $(echo "$_h" | cut -c1-8) in
        80371240) ;;
        37804012) _c=$(echo "$_c" | sed 's/\(..\)\(..\)\(..\)\(..\)/\2\1\4\3/') ;;
        40123780) _c=$(echo "$_c" | sed 's/\(..\)\(..\)\(..\)\(..\)/\4\3\2\1/') ;;
        *) return 1 ;;
    esac
    grep -i "^$_c " "$app/roms.txt"
}

# the first ROM in HOME the port takes, as "<roms.txt line>|<file>|<entry in the zip, or nothing>": loose ROMs
# anywhere but apps and the hidden folders, zips in HOME itself and in any n64 folder; a zipped one is unpacked into
# the data folder for the game, and removed once it is done
find_rom() {
    _r=$(find "$HOME" -maxdepth 5 \( -path "$HOME/.*" -o -path "$HOME/apps" \) -prune -o -type f \( -name '*.z64' -o \
            -name '*.Z64' -o -name '*.n64' -o -name '*.N64' -o -name '*.v64' -o -name '*.V64' \) -print 2>/dev/null |
        while IFS= read -r _f; do
            _l=$(rom_line < "$_f") && { echo "$_l|$_f|"; break; }
        done)
    [ -z "$_r" ] || { echo "$_r"; return 0; }
    for _z in "$HOME"/*.zip "$HOME"/*.ZIP "$HOME"/*/n64/*.zip "$HOME"/*/N64/*.zip "$HOME"/n64/*.zip; do
        [ -f "$_z" ] || continue
        _r=$(unzip -l "$_z" 2>/dev/null | awk '{ $1 = $2 = $3 = ""; sub(/^ +/, ""); print }' |
            grep -i -E '\.(z64|n64|v64)$' | while IFS= read -r _e; do
                _l=$(unzip -p "$_z" "$_e" 2>/dev/null | rom_line) && { echo "$_l|$_z|$_e"; break; }
            done)
        [ -z "$_r" ] || { echo "$_r"; return 0; }
    done
    return 1
}

# the game, its output in the log; arguments go to it (a ROM to extract)
play() {
    [ -f "$data/$CONFIG" ] || cp "$app/defaults.json" "$data/$CONFIG"
    [ -f "$data/env" ] && { set -a; . "$data/env"; set +a; }
    {
        date
        grep -E "MemTotal|MemAvailable|SwapFree|Shmem:" /proc/meminfo
        cd "$app" && "./$ELF" "$@"
        echo "exit $?"
        grep -E "MemAvailable|SwapFree" /proc/meminfo
    } > "$log" 2>&1
}

start() {
    # an install from before the App Installer: its assets, settings and saves
    _old=$HOME/ports/$PORT
    if ! ready && [ -d "$_old" ]; then
        for _k in $O2RS $KEEP; do
            [ -e "$_old/$_k" ] && [ ! -e "$data/$_k" ] && cp -r "$_old/$_k" "$data/"
        done
    fi
    ready && { play; return; }

    _found=$(find_rom) || fail "No %s ROM in HOME. Copy yours to HOME, as a .z64, .n64 or .v64 file or a zip of one, and open the game again. It takes: %s" "$TITLE" "$(text "$TAKES")"
    _line=${_found%%|*}
    _rest=${_found#*|}
    _file=${_rest%%|*}
    _entry=${_rest#*|}
    _rom=$_file
    if [ -n "$_entry" ]; then
        _rom=$data/rom.${_entry##*.}
        unzip -p "$_file" "$_entry" > "$_rom" || { rm -f "$_rom"; fail "The ROM in %s could not be unpacked: is the zip whole?" "${_file##*/}"; }
    fi
    # the port's own part of the extraction, for this ROM's version (soh: Torch's yml, one folder of many)
    command -v prepare > /dev/null && prepare "$(echo "$_line" | cut -d ' ' -f 2)"
    echo "$(date '+%F %T') extracting $_file ${_entry:+($_entry) }: $_line" >> "$HOME/logs/$PORT-import.log"
    play "$_rom"
    rm -f "$data"/rom.*
}
