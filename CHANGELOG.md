## 2.5.0

- Named the two tiny-voca voices: F2 is `nous girl`, M2 is `hermes-agent`.
- Added CLI voice aliases (`nous-girl`, `nous girl`, `hermes-agent`, etc.) and exposed the names through `ae voices`.
- Updated the open-course template and tiny-voca docs to use the new identities.

## 2.4.0

- Promoted tiny-voca to a Hermes TTS primitive: native `tts.provider: tiny-voca` now points at the installed plugin CLI.
- Added `tts_speak`, `tts_voices`, and `tts_receipts` aliases to the single `ae` tool.
- Added `docs/TINY_VOCA.md` documenting the native provider, voice roles, CLI contract, and receipts.

## 2.3.1

- Refreshed sanitized receipt snapshot to the full 45-entry ledger at release time.
- Added a 1.1 MB looping GIF preview of the free-base walk.
- Added a self-contained WebGL qpos viewer with frame scrubbing, play/pause, camera presets, and live base/COM telemetry.
- Added scripts/export_webgl.py to regenerate the viewer from the URDF and runtime trace.

## 2.3.0

- Made core ops self-contained: `speak`, `voices`, `probe`, `witness`, `gallery`, `physics`, and `studio_sync` no longer require legacy plugins.
- Kept `op=call` as an optional bridge to locally installed legacy plugins.
- Added fresh-clone acceptance harness, CI workflow, video index, and sanitized receipt-chain snapshot.

# Changelog

All notable changes to `hermes-ae` are documented here. Version numbers follow
the plugin version in `plugin.yaml`.

## 2.2.0

- Added the bundled `free_walk` local op (Studio v2.2): mocap-guided, free-base
  walk with a ground plane and foot contact spheres. Forward motion and COM
  trajectory are produced by MuJoCo weld constraints, not prescribed.
- New render pipeline `render_free_walk.py` consuming `physics_free_trace.json`
  (`nq=32` including the floating base) and `free_visemes.json`.
- New free-walk physics trace (`asimov_mocap_physics.xml`) and viseme timeline.
- Output video: `asimov-free-walk-916.mp4` (720x1280, 24 fps, 9 s, 216 frames,
  h264/aac) with QC checks and a `VIDEO://ASIMOV_FREE_WALK_916` receipt.
- New env vars: `HERMES_AE_MESHES`, `HERMES_AE_GALLERY` (see `scripts/ae_paths.py`).

## 2.1.0

- Added the bundled `studio_video` local op (Studio v2.1): fixed-base MuJoCo
  physics trace with 25 PD position actuators plus phoneme-driven visemes.
- New physics-only actuated model (`asimov_1_25dof_physics.xml`, `nu=25`, base
  fixed for capture) and renderer `render_studio_v2.py`.
- Output video: `asimov-studio-v2-916.mp4` with a
  `VIDEO://ASIMOV_STUDIO_V2` receipt recording physics, phoneme hashes, and QC.
- Added `studio_v2_frames` generation and cleanup, gallery regeneration, and
  `gh-pages` publish flow.

## 2.0.0

- Consolidated the separate helper plugins behind a single `ae` tool with an
  `op` enum, replacing direct per-plugin tool calls.
- Added shortcut routing (`SHORTCUTS`) to optional legacy local plugins via a
  lightweight `FakeCtx` loader; no heavy imports at registration time.
- Added `op=call` escape hatch for arbitrary installed plugin/tool pairs.
- Introduced the `HUMAN://ROOT` hash-chained receipt ledger with `status`,
  `receipts`, and `verify` ops.

## 1.x

- Early, per-plugin tools for tiny-voca TTS, ffmpeg rendering/VLC control,
  Asimov speech/video, MuJoCo studio, and robot voice — later superseded by the
  unified `ae` tool in 2.0.0.
