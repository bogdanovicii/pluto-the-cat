# 2.17.0 cat items: in-game checklist

Build from branch `feat/cat-items` (worktree `../pluto-cat-items`), on top of the 2.16.4 test build. The zip still says
2.16.4 because the version is bumped by whoever cuts the release. Spawn items with the console (`give pluto:<id>`).
Every item logs a `[Pluto]` line; copy those lines into the report.

## Load
- [ ] The BepInEx log has no `step "ball of yarn"/"catnip pouch"/"jingle bell collar"/"hairball item"/"scratching post" failed` lines and no `synergy ... not registered` lines.
- [ ] `give pluto:ball_of_yarn`, `pluto:catnip_pouch`, `pluto:jingle_bell_collar`, `pluto:hairball_item`, `pluto:scratching_post` all work.
- [ ] The Ammonomicon shows each item's icon, name, subtitle and story. Also check the rewritten stories for the Wet Food Can, Coco Blue, Squeaky Toy, Puffed Up and Katana.
- [ ] Play as the Pilot (not Pluto) and the new items turn up in chests and shops over a few runs.

## Ball of Yarn (`ball of yarn: thrown` log)
- [ ] The ball tumbles (2 frames), bounces off walls for about 6 s, then vanishes with a fur puff.
- [ ] It passes through enemies. Each one is stunned for about 1.5 s, then walks slowly. The same enemy isn't re-stunned until that wears off. A boss is only slowed.
- [ ] Walking into the ball sends it toward the aim point.
- [ ] Cat's Cradle (with Coco Blue): the log says `(Cat's Cradle)` and the ball lasts about 12 s.

## Catnip Pouch (`catnip pouch: zoomies` log)
- [ ] Speed and fire rate go up, a green afterimage trail follows, and leaves drift up. The active bar drains over 7 s.
- [ ] Then 2 s of slower walking, then normal speed.
- [ ] Dropping the pouch mid-zoomies or mid-nap puts speed and fire rate back to normal right away.
- [ ] Nip And Tuck (Pluto with Puffed Up): the zoomies start with the puff.

## Jingle Bell Collar
- [ ] A dodge roll through a bullet pattern shows the gold ring and plays the jingle. Bullets within about 2.5 tiles vanish, and nearby small enemies are stunned for about 1 s.
- [ ] Rolling again within 4 s does nothing; after 4 s it jingles again.
- [ ] Dropping the collar stops the jingles.
- [ ] Squeaky Clean (with Squeaky Toy): the ring clears a wider area.

## Hairball (`hairball item: fur cloud` log)
- [ ] It flies like the Wet Food Can and bursts where it stops. Fur puffs mark the cloud for 5 s.
- [ ] Plain enemy bullets crawl inside the cloud and speed back up as they leave.
- [ ] Bullet-pattern bosses (e.g. Gatling Gull, Bullet King): patterns slow down inside the cloud but keep their shape, and nothing stays slow after the cloud ends.
- [ ] Two overlapping clouds: bullets aren't slowed twice and don't speed up early.
- [ ] Hack Attack (with Wet Food Can): enemies in the burst fall in love.
- [ ] The Royal Kibble Sack's empty-reload hairball still works as before.

## Scratching Post (`scratching post: placed` log)
- [ ] The post appears at Pluto's feet, drawn in front of or behind him correctly. Using it again moves it; you get one use per room.
- [ ] Standing next to it shows anger marks and plays a sound, damage goes up, and shots pierce one extra enemy. Walking away ends it.
- [ ] Leaving the room removes the post and the bonus.
- [ ] Whetstone (with Katana): damage goes up more.
