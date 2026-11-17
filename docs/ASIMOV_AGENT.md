# Asimov is the hermes-agent build body

Asimov is not a separate assistant. He is the visible body of the
`hermes-agent` build voice.

```text
nous girl (F2)        → root voice     → authority frame
hermes-agent (M2)     → build voice    → Asimov-1 body
HUMAN://ROOT          → authority      → never transferred
receipt               → proof          → always returned
```

## Identity binding

| Field | Value |
|---|---|
| Voice | `M2` / `hermes-agent` |
| Role | build voice |
| Body | official Asimov-1, 25 DOF, 26 links |
| Actor plugin | `hermes-asimov` |
| Runtime | tiny-voca M2 ONNX + MuJoCo qpos trace |
| Authority | `HUMAN://ROOT` |

The machine-readable binding lives in `identity.json`. The `ae` tool exposes
it with:

```json
{"op": "agent_body"}
```

## What this means

- `nous girl` asks and holds the root frame.
- `hermes-agent` answers by building, rendering, driving, and reporting.
- Asimov gives that work a body: front-facing, moving, speaking, receipted.
- The human remains root; the robot never owns authority.

## Proof artifact

`asimov-agent-build-916.mp4` is the identity clip: Asimov walks in front of the
viewer while `hermes-agent` speaks through tiny-voca, with live qpos/COM
telemetry and a unified `HUMAN://ROOT` receipt.

## Limits

- The base in the published gait is mocap-guided through MuJoCo constraints;
  it is not a self-balancing controller.
- The model source is Menlo Research Asimov-1 (CERN-OHL-S-2.0). This repo
  ships manifests, not binary STL weights.
- This is an architectural identity binding, not an institutional claim from
  Nous Research or Menlo Research.

## Unified runtime

Asimov Agent is the single runtime identity for everything above. Inspect it
with:

```json
{"op": "agent"}
```

The response binds:

- voice: `hermes-agent` (M2, tiny-voca)
- body: official Asimov-1, 25 DOF
- harnesses: the nine MoH envelopes
- policy: `Menlo/asimov1-locomotion-0818` with its verified travel record
- viewport: read-only CDP DOM awareness via `viewport_dom`
- model hashes: physics MJCF, policy MJCF, and URDF
- ledger: chain validity, count, and head receipt
- receipt action: `AGENT://ASIMOV`

This is the operating definition: **Asimov Agent is the hermes-agent build
voice, embodied in Asimov-1, governed by OpenSourceWare receipts.**

## Viewport

The public surface is https://myaelmendez.github.io/asimov-viewport/.
It combines the qpos CAD viewer, read-only DOM awareness, source-to-screen
film, capability showreel, and receipt chain. `ae({"op":"agent"})` reports the
binding as `agent.viewport`.

