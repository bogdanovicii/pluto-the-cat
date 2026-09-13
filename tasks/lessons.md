# Lessons

## 2026-09-13 — Alexandria CharacterAPI altGuns
- Alexandria 0.5.10 `HandleLoadout` iterates `altGun` without a null check; the list only exists when characterdata.txt has an `<altGuns>` block. Always include it, even with no alt skin.
- `Loader.BuildCharacter` catches its own exceptions and returns null. Check the return value before logging success; never print "ready" unconditionally.
- Static validation caught none of this. Runtime API contracts (what a loader tolerates) need a real in-game run; keep the remote Steam-machine test loop as the final gate.

## 2026-09-13 — vanilla item ids
- Never guess a vanilla console id. Every id must be looked up in `docs/research/gungeon_items_idmap.txt` (Cardboard Box is `box`, the cheese is `partially_eaten_cheese`). `tools/validate.py` now enforces this for synergy ids.
- Optional features (synergies) register last and each in its own try/catch, so one bad id costs a synergy, not the character.
