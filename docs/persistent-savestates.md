# Save states that survive a power off

Ship of Harkinian's save states are a copy of the game's memory: the 4 MB system heap (every actor,
the scene, the camera...), the 3.5 MB audio heap, `gSaveContext` and the static data of about forty
files and overlays. Restoring one is a `memcpy` back. That works inside one run of the game, but not
after a restart, because that memory is full of **pointers**, and pointers are only valid in the
process that wrote them. This is the plan to make them portable, so a state written to the card can
be loaded after the console was off.

## Where the pointers in a state point

| Into | Example | Plan |
|---|---|---|
| The system and audio heaps | an actor's `parent`, `gPlayState` | allocate both heaps at **fixed addresses** (`mmap` with `MAP_FIXED_NOREPLACE` at a constant address, falling back to today's `memalign`): the same on every run |
| The game's own code and static data | actor `update`/`draw` functions, tables | build `soh.elf` **non-PIE** (`-no-pie`): the executable always loads at the same address |
| Assets loaded from the `.o2r` | Link's skeleton, animations, collision meshes, room data | **relocate** (below) |
| Anything else (other malloc'd memory) | should be rare | counted when saving; a state that has any is refused instead of risking a crash |

The audio heap's sequence-script pointers are already saved as offsets by SoH (`BackupSeqScriptState`),
which is the same idea.

## Relocating asset pointers

Every asset goes through one call, `ResourceLoader::LoadResource` (inside
`ResourceManager::LoadResourceProcess`), on one thread at a time. The patch:

1. **Track.** A thread-local "loading asset X" tag is set around that call, and a global
   `operator new`/`delete` in the executable records every block allocated while it is set:
   `(base, size) -> (asset path, block number)`. Loading the same asset from the same `.o2r` runs the
   same code, so its blocks come out in the same order: block N of asset X is always the same thing.
2. **Save to the card.** The state is scanned word by word (aligned 32-bit words: about 2 million, a
   fraction of a second on the A23). A word that falls inside a tracked block becomes a fixup:
   `(where in the state, asset path, block number, offset in the block)`. Words pointing into the
   heaps or the executable need nothing. The file holds a header (format version, a hash of
   `soh.elf`, the fixed heap addresses), the state and the fixup table, compressed.
3. **Load from the card.** Refuse if the `soh.elf` hash differs (an update changes code addresses).
   Otherwise load every asset named in the fixups (synchronously, recording their blocks), patch each
   fixup to the new block address plus offset, and hand the result to SoH's normal `Load()`.

A word that is really an integer but happens to look like an asset address would be "relocated" by
mistake. On a 32-bit system those addresses sit in high, mmap'd ranges that game integers rarely
reach, and the fixup count per state is logged to find out how often it would matter.

## On the console

- Manual slots (Select+R1 / Select+L1) are written to `HOME/.config/soh/states/slot<N>.state`.
- The rolling autosave stays in memory every 5 s and is written to the card every 30 s and when you
  quit (Select+Start), in a background thread, so the game doesn't stutter.
- After a restart: load your save file, then Select+X (autosave) or Select+L1 (slot) brings you back
  to the exact moment.

## Milestones

1. Fixed-address heaps and a non-PIE `soh.elf`; check on the console that addresses repeat across runs.
2. Asset tracking; log the fixup count and any untracked pointers of a real state.
3. Disk format, save and load in the same run (round trip).
4. Load after a restart; then the autosave to disk.
