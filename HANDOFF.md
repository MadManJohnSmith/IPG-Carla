# Handoff — IPG-Carla

Date: 2026-11-07. Read this first; it assumes no prior session context.

## What this repo is

An asynchronous SIL/HIL bridge between IPG CarMaker and CARLA. The implemented
Mode A sends driver inputs CarMaker → CARLA over UDP using the `!I3f` binary
packet (`seq`, `steer`, `gas`, `brake`). Mode B — CarMaker owns vehicle
dynamics and CARLA is a kinematic/visual puppet — is designed but not
implemented; see `docs/mode-b.md`.

## Current state

- Mode A works. `bash bridge/run_test.sh` passes without CARLA (standard library
  only): the receiver runs with `--test` and the stress test exercises bursts,
  reordering, gaps and timeouts. Last run: 1578 ticks, 1856 packets, 76.3 Hz.
- Protocol and steer normalization are documented in `README.md` §8. Do not
  re-derive them: `!I3f`, `steer / STEER_MAX_RAD` clamped to `[-1, 1]`.
- `bridge/extractor_carmaker.py` has not been validated against a real CarMaker
  installation in this repo's current state.
- Lab evidence (NotebookLM sources, rig photos, Gemini chats) lives OUTSIDE this
  repo under `~/Documents/research/ipg-carla-lab/` and
  `~/Documents/research/gemini-chats/`. It is sensitive and must never be
  committed. A private backup is in `MadManJoohnSmith/ipg-carla-lab-evidence`
  (ask Alan for access). See `docs/lab-evidence.md`.

## Environment

- Not installed: this machine is scheduled for a factory restore. Do not
  download or install CARLA before that.
- Planned Linux host: Python 3.10 + `carla==0.9.15` in a venv (README §4).
  CARLA 0.9.15 publishes wheels for `cp37`-`cp310`; Python 3.11+ will not install
  it. `carla==0.9.16` ships `cp310`-`cp312`, but the bridge is validated against
  0.9.15.
- Reference GPU: GTX 1050 Ti, 4 GB VRAM. CARLA will run at Low quality; useful
  for functional tests, not for realistic sensor simulation.
- CarMaker 14.1.1 is Windows-only and not available locally. For Mode B, prefer
  remote access to the lab PC or the CarMaker project folder (`.ipg`, data
  dictionary, Vehicle Data Set) over shipping the VHDX: the image may be
  BitLocker-encrypted and the licence is likely node-locked.

## Next steps

1. After the machine rebuild: install Python 3.10 and CARLA 0.9.15, then run
   `bash bridge/run_test.sh` to confirm the baseline.
2. Read `docs/mode-b.md` and decide the Mode B scope: extend the UDP bridge or
   adopt the ROS2/RSDS architecture described in the notes.
3. Obtain lab access or the CarMaker project; validate real UAQs and the
   assumptions in `extractor_carmaker.py`.
4. Implement Mode B in small steps; keep Mode A as a regression.
5. Before publishing any lab capture: redact and confirm with Alan.

## Do not

- Do not commit `~/Documents/research/` or any lab capture to this public repo.
- Do not install CARLA before the factory restore.
- Do not re-derive the protocol, the steer normalization, or the NotebookLM
  extraction method; the docs and evidence indexes record them.

## Suggested skills

- `handoff` — update this file at the end of a session.
- `browser-use:control-browser` — only if the NotebookLM sources must be
  re-extracted; use `docs/extraction-method.md` and do not improvise selectors.
- `writing-for-agents` — when editing this handoff or `docs/`.

## Ownership

Alan (MadManJohnSmith). Public repo: <https://github.com/MadManJohnSmith/IPG-Carla>
