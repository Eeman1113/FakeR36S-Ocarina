#!/usr/bin/env python3
"""Move an Ocarina of Time playthrough from an N64 emulator into Ship of Harkinian.

Reads a RetroArch Mupen64Plus / ParaLLEl N64 save file (.srm), a raw N64 SRAM dump (.sra),
or a ParaLLEl N64 / Mupen64Plus save state (.state, RetroArch RZIP or plain), and writes
oot_save.sav: Ship of Harkinian's old ("unversioned") save format, which the game converts
into its own save files on its next start. Put it in SoH's folder (HOME/.config/soh on
FakeR36S-OS) next to shipofharkinian.json; the game renames it to oot_save.bak once done.

  python3 n64save2soh.py "Zelda - Ocarina of Time.srm" oot_save.sav
  python3 n64save2soh.py --state "Zelda - Ocarina of Time.state" --slot 1 oot_save.sav
  python3 n64save2soh.py --info "Zelda - Ocarina of Time.srm"

With --state, the live game in the state's memory is written as if you had saved at that
moment: same items, quest progress and flags, and you start where the game would put you
after a save there (as with a normal in-game save).

Layout: zeldaret/oot's SaveContext / Sram (N64, big-endian) and Ship of Harkinian's
SaveContext_v0 (same offsets, little-endian), SaveManager::ConvertFromUnversioned.
"""
import argparse, struct, sys, zlib

SRAM_SIZE = 0x8000
HEADER = 0x20                 # SRAM header, then the slots (N64 and SoH v0 agree)
SLOT = 0x1450                 # sizeof(SaveContext_v0) + 0x28
SAVE_INFO = 0x1354            # the part of SaveContext the game writes to SRAM
MAGIC = b"\x98\x09\x10\x21ZELDA"
DEBUG_NAME = bytes.fromhex("b6b3b8b5dfdfdfdf")   # "LINK" in the game's font

# (offset, size) of every 16- and 32-bit field in the first 0x1354 bytes of SaveContext
FIELDS = [(0x00, 4), (0x04, 4), (0x08, 4), (0x0C, 2), (0x10, 4), (0x14, 4), (0x18, 4),
          (0x22, 2), (0x2C, 2), (0x2E, 2), (0x30, 2), (0x34, 2), (0x36, 2), (0x38, 2),
          (0x48, 2), (0x52, 2), (0x54, 4), (0x66, 2), (0x70, 2),
          (0x9C, 2), (0xA0, 4), (0xA4, 4), (0xD0, 2)]
FIELDS += [(0xD4 + 4 * i, 4) for i in range(124 * 7)]          # sceneFlags
FIELDS += [(0xE64 + 4 * i, 4) for i in range(10)]              # Farore's Wind
FIELDS += [(0xE9C + 4 * i, 4) for i in range(6)]               # gsFlags
FIELDS += [(0xEB8 + 4 * i, 4) for i in range(7)]               # highScores
FIELDS += [(0xED4 + 2 * i, 2) for i in range(14 + 4 + 30)]     # eventChkInf, itemGetInf, infTable
FIELDS += [(0xF38, 4)]                                          # worldMapAreaData
FIELDS += [(0x1348 + 2 * i, 2) for i in range(5)]               # horseData
FIELDS += [(0x1352, 2)]                                         # checksum


def word_swap(b):
    return b"".join(b[i:i + 4][::-1] for i in range(0, len(b) - len(b) % 4, 4))


def to_little(save_be):
    """One slot's SaveInfo, N64 big-endian -> SoH v0 little-endian."""
    out = bytearray(save_be)
    for off, size in FIELDS:
        out[off:off + size] = save_be[off:off + size][::-1]
    return bytes(out)


def checksum(save_be):
    return sum(struct.unpack(">%dH" % (SAVE_INFO // 2), save_be[:SAVE_INFO])) & 0xFFFF


def sram_from_srm(data):
    """N64 SRAM (big-endian bytes) out of an .srm/.sra in whatever byte order it was dumped."""
    if len(data) == 0x48800:                   # RetroArch mupen64plus/parallel: eeprom, 4 mempaks, sram, flash
        data = data[0x800 + 4 * 0x8000:0x800 + 4 * 0x8000 + SRAM_SIZE]
    data = data[:SRAM_SIZE]
    for cand in (data, word_swap(data)):
        if cand[3:12] == MAGIC:
            return cand
    raise SystemExit("no Ocarina of Time SRAM header found (is this an OoT save?)")


def unrzip(data):
    if data[:8] != b"#RZIPv\x01#":
        return data
    total = struct.unpack_from("<Q", data, 12)[0]
    out, pos = bytearray(), 20
    while pos < len(data) and len(out) < total:
        n = struct.unpack_from("<I", data, pos)[0]
        out += zlib.decompress(data[pos + 4:pos + 4 + n])
        pos += 4 + n
    return bytes(out)


def saves_from_state(data):
    """Every SaveContext-looking block in a save state's RDRAM, big-endian."""
    data = unrzip(data)
    found = []
    for view in (data, word_swap(data)):
        start = 0
        while True:
            i = view.find(b"ZELDAZ", start)
            if i < 0:
                break
            base = i - 0x1C
            if base >= 0 and base + SAVE_INFO <= len(view):
                found.append(view[base:base + SAVE_INFO])
            start = i + 1
    return found


def summary(s):
    u16 = lambda o: struct.unpack_from(">H", s, o)[0]
    s16 = lambda o: struct.unpack_from(">h", s, o)[0]
    u32 = lambda o: struct.unpack_from(">I", s, o)[0]
    name = bytes(s[0x24:0x2C])
    events = sum(bin(u16(0xED4 + 2 * i)).count("1") for i in range(14))
    items = sum(1 for b in s[0x74:0x74 + 24] if b != 0xFF)
    return {"name": name.hex(), "deaths": u16(0x22), "hearts": s16(0x2E) // 16, "health": s16(0x30),
            "rupees": s16(0x34), "items": items, "quest": "%08x" % u32(0xA4), "events": events,
            "gs_tokens": s16(0xD0), "age": "child" if struct.unpack_from(">i", s, 4)[0] else "adult",
            "scene": s16(0x66)}


def build(slots_be, header):
    out = bytearray(SRAM_SIZE)
    out[0:HEADER] = header
    for n, s in enumerate(slots_be):
        if s is not None:
            out[HEADER + n * SLOT:HEADER + n * SLOT + SAVE_INFO] = to_little(s)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--state", action="store_true", help="src is a save state: take the live game from its memory")
    ap.add_argument("--slot", type=int, default=1, help="with --state: which SoH file (1-3) to write it to")
    ap.add_argument("--info", action="store_true", help="only show what is in src")
    a = ap.parse_args()
    data = open(a.src, "rb").read()

    if a.state:
        cands = saves_from_state(data)
        if not cands:
            raise SystemExit("no Ocarina of Time game found in this state's memory")
        # skip the game's built-in debug save ("LINK", full inventory), which sits in its code in memory;
        # of the rest, gSaveContext is the live game: take the copy with the most progress (the SRAM buffer can be stale)
        real = [c for c in cands if bytes(c[0x24:0x2C]) != DEBUG_NAME] or cands
        best = max(real, key=lambda s: (summary(s)["events"], summary(s)["items"], summary(s)["rupees"], summary(s)["health"]))
        for c in cands:
            print("state:", summary(c), "<- used" if c is best else "")
        if a.info or not a.out:
            return
        best = bytearray(best)
        struct.pack_into(">H", best, 0x1352, checksum(best[:0x1352] + b"\0\0"))
        header = bytearray(HEADER)
        header[1] = 0                       # z-target: switch
        header[2] = 1                       # language: English (NTSC)
        header[3:12] = MAGIC
        slots = [None, None, None]
        slots[a.slot - 1] = bytes(best)
        open(a.out, "wb").write(build(slots, bytes(header)))
    else:
        sram = sram_from_srm(data)
        slots = []
        for n in range(3):
            s = sram[HEADER + n * SLOT:HEADER + n * SLOT + SAVE_INFO]
            ok = s[0x1C:0x22] == b"ZELDAZ"
            print("file %d:" % (n + 1), summary(s) if ok else "empty",
                  "" if not ok or checksum(s[:0x1352] + b"\0\0") == struct.unpack_from(">H", s, 0x1352)[0]
                  else "(checksum mismatch)")
            slots.append(s if ok else None)
        if a.info or not a.out:
            return
        open(a.out, "wb").write(build(slots, sram[:HEADER]))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
