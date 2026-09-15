# Pluto the Cat 2.16.0 — in-game test checklist (Samurai Pluto)

> **Historical: tester checklist for 2.16.0.** Pending items here are not current verification; record results per build.

Install 2.16.0 together with Vet Visit 0.14.0 (the costume unlocks by beating the Vet). Delete
`BepInEx/config/bogdan.etg.plutothecat.cfg` once so the new key appears. Report `[Pluto]` lines from LogOutput.log.

## Unlock
1. Fresh save state for Pluto (or Vet not yet beaten): no kimono stand above Pluto in the Breach.
2. Set `UnlockSamuraiCostume = true`, restart: the kimono stand appears; its second frame sparkles when you are near.
3. Set it back to false. Beat the Vet in the past: the stand appears on the next Breach visit.

## Costume and loadout
4. Touch the stand: Pluto wears the kimono in idle, run (all 4 directions), rolls, item get, death.
5. In costume, in the Breach: guns become Taiyaki Cannon + Katana. Touch the stand again: back to the Royal Kibble Sack.
6. Take the elevator in costume: the samurai guns stay. Quick restart in costume: still samurai guns.
7. Save and quit mid-run in costume, continue: note which guns you have (Vet Visit logs the gun ids on arrival).
8. Use the Breach alt-gun shrine as Pluto: nothing changes.
9. Puffed Up (take a hit) in costume: anger marks, no fur poking through the kimono.

## Weapons
10. Taiyaki Cannon: mini taiyaki fly from the mouth, pale pink bonito puff on hit, reload shows the Churu tube.
11. Katana at full health: each swing sends a sakura crescent that pierces; enemy bullets touching the swing vanish.
12. Katana after taking damage: swing still cuts bullets, no crescent.
13. Katana reload next to bullets: nearby bullets are cleared. Log line `katana reach: ... swing radius ~N units` present.

## Boss cards
14. Normal Pluto vs a boss: Pluto's bust with the kibble sack slides in bottom-left; the boss art stays visible.
15. Samurai Pluto vs a boss: the samurai bust with the katana instead.

Screenshots of 4, 10, 11, 14 and 15 please.
