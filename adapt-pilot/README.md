# ADAPT SWE-Interact pilot

This folder contains the CS224V comparison of stock Codex and Codex with ADAPT on the single-turn SWE-Interact tasks. Both arms receive the full specification and use the same starting repository and Docker image for verification. Victor's earlier 41/75 local assessment is documented in the [repository overview](../README.md). It used direct Codex chats and some local verification fallbacks.

Both arms use GPT-6 Luna at medium reasoning effort, Codex CLI 0.159.0, a 48,000-token working context, a 10,000-token tool-output cap, and one hour for coding. If an agent ends with a clarification question, the wrapper resumes the same session with the literal message `continue`. The last-line question detector and eight-continuation cap are local choices. Seed 224 fixes the task order, with FastAPI first. Model sampling and temperature are managed by the underlying service.

The coding agents run on macOS. The supplied SWE-Interact verifiers score frozen patches in Linux Docker. A reward of 1 is a pass. Setup errors and other unscored attempts appear in the attempt history. SWE Atlas additionally uses a rubric judge. DeepSWE and SWE-bench Pro provide the primary comparison with test-based scores.

## Setup and run

Requires Python 3.11+, Git, Docker Desktop, an Apple silicon Mac, and a ChatGPT account with Codex access. Check out the upstream dataset next to this repository, or set `SWE_INTERACT_DATASET` to its checkout path.

```sh
git clone https://github.com/scaleapi/SWE-Interact.git ../SWE-Interact
git -C ../SWE-Interact checkout b32f98c3b8f76ca65e84341d1f30e5af7135f85d
cd adapt-pilot
export SWE_ADAPT_RELEASE=/absolute/path/to/authorized/adapt-release
python3 run.py preflight
python3 run.py run --cycle-images --task deepswe_fastapi-deprecation-response-headers
python3 run.py run --cycle-images
```

Obtain the pinned ADAPT release from the project team. The runner checks its version and bundled binary checksums. The historical FastAPI pair used an image from the original pilot and a Starlette warning filter. The portable config builds the upstream image and keeps the same filter. The historical image ID remains in [the snapshot manifest](results/manifest.json). Image IDs can differ when upstream tags or unpinned packages change.

On SWE Atlas, the default rubric model is Claude Opus 4.5 via a gateway configured with `OPENAI_API_KEY` and `OPENAI_API_BASE`. To run with the existing Codex login, pass `--local-rubric` on the first invocation. Both arms then use GPT-6 Luna at medium effort for the rubric, with the upstream tests and rubric prompts. The manifest records the judge and bridge version. Compare SWE Atlas results with the judge identified.

The runner saves each attempt and refreshes the report. With `--cycle-images`, it removes the dedicated build cache after loading the task image and removes the image after both scores are saved. If a run stops, rerun the same command. The runner skips scored arms and can reuse a frozen patch for an interrupted verifier. Three tasks are held out of the pilot.

## Results and limitations

[Snapshot report](results/REPORT.md) · [Manifest](results/manifest.json) · [Attempt records](results/attempts.json)

The snapshot covers the pilot through the recorded checkpoint. The manifest captures the settings used for that snapshot. The adjacent `config.json` is the configuration for a fresh run. The published records contain scores, token counts, trace counts, timestamps, and hashes. Access to the original workspaces, raw traces, preprint, and compiled release is managed separately by the project team.

This pilot applies the paper's agent settings to a new benchmark and compares the two harnesses exposed by the supplied release. It records aggregate token use including cached input. To assess the context-management mechanism directly, use the saved traces to locate compaction and determine whether evidence from earlier in the task was recovered when needed.
