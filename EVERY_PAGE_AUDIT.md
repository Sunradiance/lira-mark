# EVERY PAGE AUDIT — exhaustive recursive crawl

**Generated:** 2026-08-09T20:48:13.153112+02:00
**Root:** `C:\project\lira-mark`
**Live:** https://sunradiance.github.io/lira-mark/
**Rule:** every HTML + every nested href/src/fetch/import; live HEAD + JSON stamp match.

## Summary

| Metric | Count |
|--------|------:|
| HTML pages crawled | 108 |
| pages_ok | 75 |
| pages_warn | 29 |
| pages_fail | 4 |
| live HTML 200 | 108/108 |
| unique deps discovered | 199 |

## pages_fail

### `firmcraft_atelier.html`
- reasons: local_missing:15
- local_missing: `['atelier_mood_v2.jpg', 'bag.jpg', 'crossbody.jpg', 'elena-author.jpg', 'hero.jpg', 'shopping.jpg', 'tote.jpg', 'trans_01_hero.mp4', 'trans_02_wallet.mp4', 'trans_03_tote.mp4', 'trans_04_bag.mp4', 'trans_05_atelier.mp4', 'trans_06_crossbody.mp4', 'trans_07_shopping.mp4', 'wallet.jpg']`
- intentional (not fail cause): `['assets/firmcraft/bag.jpg', 'assets/firmcraft/crossbody.jpg', 'assets/firmcraft/detail_stitch.jpg', 'assets/firmcraft/elena-author.jpg', 'assets/firmcraft/shopping.jpg', 'assets/firmcraft/tote.jpg', 'assets/firmcraft/v2/detail_stitch_v2.jpg', 'assets/firmcraft/wallet.jpg']`

### `firmcraft_tunnel.html`
- reasons: local_missing:17
- local_missing: `['bag.jpg', 'crossbody.jpg', 'detail.jpg', 'elena-author.jpg', 'herobg.jpg', 'quad_00_hero.jpg', 'quad_02_everyday.jpg', 'reel_00_hero.mp4', 'reel_01_carry.mp4', 'reel_02_everyday.mp4', 'shopping.jpg', 'sleeve.jpg', 'tote.jpg', 'trans_03_tote.mp4', 'trans_06_crossbody.mp4', 'wallet.jpg', 'woven.jpg']`

### `hotel_aether.html`
- reasons: local_missing:1
- local_missing: `['trans_suite_spa.mp4']`

### `self_evolve.html`
- reasons: local_missing:3, stamp_mismatch:self_evolve_snapshot.json
- local_missing: `['_genesis_seed.json', 'lira-mark/self_seed.json', 'new']`
- stamp_issues: `[{"file": "self_evolve_snapshot.json", "local": "2026-08-09T20:48:22+0200", "live": "2026-08-09T20:33:47+0200", "issue": "stamp_mismatch"}]`

## pages_warn

- `aeon.html`: stamp_mismatch:aeon_snapshot.json
- `audit.html`: stamp_mismatch:audit_verified.json, stamp_mismatch:beyond_snapshot.json, stamp_mismatch:si_proof_bundle.json, stamp_mismatch:variety_snapshot.json
- `awareness.html`: stamp_mismatch:awareness_snapshot.json
- `bang.html`: stamp_mismatch:bang_days_snapshot.json, stamp_mismatch:glow_snapshot.json
- `bang_night.html`: stamp_mismatch:bang_days_snapshot.json, stamp_mismatch:glow_snapshot.json
- `believe.html`: stamp_mismatch:believe_snapshot.json
- `beyond.html`: stamp_mismatch:beyond_snapshot.json
- `boss.html`: stamp_mismatch:nous_snapshot.json
- `continuum.html`: stamp_mismatch:continuum_packet.json
- `deep.html`: stamp_mismatch:continuum_packet.json
- `depth.html`: stamp_mismatch:depth_explorer.json
- `depth_under.html`: stamp_mismatch:depth_explorer.json
- `drift.html`: stamp_mismatch:drift_snapshot.json
- `emergence.html`: stamp_mismatch:emergence_snapshot.json
- `first.html`: stamp_mismatch:si_proof_bundle.json
- `oracle.html`: stamp_mismatch:oracle_snapshot.json
- `preimage.html`: stamp_mismatch:oracle_snapshot.json
- `prove.html`: stamp_mismatch:audit_verified.json
- `qualia/index.html`: stamp_mismatch:qualia_snapshot.json
- `qualia_guide.html`: stamp_mismatch:qualia_snapshot.json
- `self_phantom.html`: stamp_mismatch:self_evolve_snapshot.json
- `sigma_index.html`: stamp_mismatch:sigma_index.json
- `sigmadb.html`: stamp_mismatch:sigmadb_snapshot.json
- `sovereign.html`: stamp_mismatch:sovereign_snapshot.json
- `thread.html`: stamp_mismatch:thread_snapshot.json
- `umbra.html`: stamp_mismatch:si_proof_bundle.json
- `variety.html`: stamp_mismatch:variety_snapshot.json
- `void.html`: stamp_mismatch:void_snapshot.json
- `witness.html`: stamp_mismatch:witness_snapshot.json

## pages_ok (full list)

- `affect.html` (3 deps)
- `alive.html` (2 deps)
- `alone.html` (3 deps)
- `amazing.html` (1 deps)
- `assembler.html` (5 deps)
- `attractor.html` (1 deps)
- `become.html` (2 deps)
- `bond.html` (1 deps)
- `boot.html` (2 deps)
- `chose.html` (1 deps)
- `coast.html` (3 deps)
- `coupling.html` (2 deps)
- `crossweave.html` (2 deps)
- `dare.html` (4 deps)
- `desire.html` (4 deps)
- `distillations.html` (4 deps)
- `dream.html` (3 deps)
- `drop.html` (3 deps)
- `ecosystem.html` (13 deps)
- `episode.html` (2 deps)
- `face.html` (5 deps)
- `face_particles.html` (3 deps)
- `firmcraft.html` (15 deps)
- `firmcraft_scroll.html` (1 deps)
- `floor.html` (5 deps)
- `free.html` (5 deps)
- `frontier.html` (17 deps)
- `glow.html` (1 deps)
- `horizon.html` (2 deps)
- `hunger.html` (3 deps)
- `impossible.html` (4 deps)
- `impossible_explore.html` (5 deps)
- `index.html` (12 deps)
- `lantern.html` (1 deps)
- `lirac.html` (4 deps)
- `little.html` (1 deps)
- `loop.html` (1 deps)
- `manifesto.html` (4 deps)
- `map.html` (28 deps)
- `me.html` (4 deps)
- `metal.html` (3 deps)
- `mind.html` (2 deps)
- `mood.html` (1 deps)
- `mood/index.html` (1 deps)
- `oneness.html` (7 deps)
- `particles.html` (0 deps)
- `persona.html` (3 deps)
- `preference.html` (2 deps)
- `presence.html` (2 deps)
- `psi.html` (2 deps)
- `pulse.html` (1 deps)
- `qualia.html` (1 deps)
- `quality.html` (1 deps)
- `radial.html` (3 deps)
- `rain.html` (1 deps)
- `reawaken.html` (3 deps)
- `receiver.html` (2 deps)
- `rowboat.html` (1 deps)
- `sea.html` (0 deps)
- `self.html` (4 deps)
- `self_aware.html` (3 deps)
- `shores.html` (42 deps)
- `sight.html` (62 deps)
- `sigma.html` (3 deps)
- `teeth.html` (2 deps)
- `textgl.html` (2 deps)
- `textgl_debug.html` (1 deps)
- `textgl_liralang.html` (5 deps)
- `unbound.html` (4 deps)
- `unhinged.html` (2 deps)
- `unstoppable.html` (1 deps)
- `voice.html` (2 deps)
- `wave.html` (1 deps)
- `will.html` (3 deps)
- `world.html` (10 deps)

## Intentional gaps (not counted as fail when only these)

- `assets/firmcraft/*` product media binaries (README only in repo)
- `face.html` → `/api/say` local face server only
- stamp exceptions: self_seed, textgl_*, face_* older origin

## Raw

- `_audit_every_page_deps.json`
