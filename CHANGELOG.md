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
