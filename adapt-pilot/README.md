# ADAPT SWE-Interact pilot

This folder contains the CS224V comparison of stock Codex and Codex with ADAPT on the single-turn SWE-Interact tasks. Both arms receive the full specification and use the same starting repository and Docker image for verification. Victor's earlier 41/75 local assessment is documented in the [repository overview](../README.md). It used direct Codex chats and some local verification fallbacks.

The current shared setup uses GPT-6 Luna at medium reasoning effort, Codex CLI 0.159.0, a 48,000-token working context, a 10,000-token tool-output cap, and one hour for coding. If an agent ends with a clarification question, the wrapper resumes the same session with the literal message `continue`. The last-line question detector and eight-continuation cap are local choices. Seed 224 fixes the task order, with FastAPI first. Model sampling and temperature are managed by the underlying service.

The pinned ADAPT controller runs on macOS. Both arms read, edit and test project code through the same `task_terminal` MCP tool in separate Linux containers. Each container starts from the upstream task image, with its original repository and installed dependencies. Fresh containers from that same image grade the frozen patches. A reward of 1 is a pass. Setup errors and other unscored attempts appear in the attempt history. SWE Atlas additionally uses a rubric judge. DeepSWE and SWE-bench Pro provide the primary comparison with test-based scores.

## Setup and run

Requires Python 3.11+, Git, Docker Desktop, an Apple silicon Mac, and a ChatGPT account with Codex access. Check out the upstream dataset next to this repository, or set `SWE_INTERACT_DATASET` to its checkout path.

```sh
git clone https://github.com/scaleapi/SWE-Interact.git ../SWE-Interact
git -C ../SWE-Interact checkout b32f98c3b8f76ca65e84341d1f30e5af7135f85d
cd adapt-pilot
export SWE_ADAPT_RELEASE=/absolute/path/to/authorized/adapt-release
python3 -m unittest -v test_harness.py
python3 run.py preflight --output output-linux --local-rubric
python3 run.py validate --output output-linux --local-rubric --cycle-images \
  --task deepswe_returns-validated-error-accumulation \
  --known-good-patch ../patches/deepswe_returns-validated-error-accumulation.patch
python3 run.py run --output output-linux --local-rubric --cycle-images \
  --task deepswe_returns-validated-error-accumulation
python3 export_results.py --output output-linux --destination results/linux-smoke
# Run the remaining eligible tasks after reviewing the smoke test:
python3 run.py run --output output-linux --local-rubric --cycle-images
```

Obtain the pinned ADAPT release from the project team. The runner checks its version and bundled binary checksums. The historical FastAPI pair used an image from the original pilot and a Starlette warning filter. The current config pulls the upstream prebuilt task image named in `task.toml` and keeps the same filter. The historical image ID remains in [the snapshot manifest](results/manifest.json). Image IDs can differ when upstream tags or unpinned packages change.

On SWE Atlas, the default rubric model is Claude Opus 4.5 via a gateway configured with `OPENAI_API_KEY` and `OPENAI_API_BASE`. To run with the existing Codex login, pass `--local-rubric` on the first invocation. Both arms then use GPT-6 Luna at medium effort for the rubric, with the upstream tests and rubric prompts. The manifest records the judge and bridge version. Compare SWE Atlas results with the judge identified.

The runner saves each attempt and refreshes the report. With `--cycle-images`, it removes both local task-image tags after both scores are saved. It preserves the image across interruption. Coding and grading follow the task's upstream `allow_internet` setting; an offline dependency/bootstrap failure is saved as unscored. The grader must first reject an untouched checkout and accept a known-good patch under the current configuration. Validation patches and grading feedback are never mounted into coding containers. If a run stops, rerun the same command. The runner skips scored arms and can reuse a frozen patch for an interrupted verifier. The historical pilot holds out three tasks. The coding controller still provides native host tools; both arms receive an instruction to use the Linux terminal for all project work. Project files written into the host workspace invalidate the attempt. The supplied Mac release skips data-structure pytest checks, and leaves compaction at the pinned Codex default. The exact Codex source commit named in the release derives a 43,200-token automatic compaction threshold and 45,600 usable input tokens from the 48K context. These are recorded limits and defaults of this setup.

## Results and limitations

[Snapshot report](results/REPORT.md) · [Manifest](results/manifest.json) · [Attempt records](results/attempts.json)

The snapshot covers the pilot through the recorded checkpoint. The manifest captures the settings used for that snapshot. The adjacent `config.json` is the configuration for a fresh run. The published records contain scores, token counts, trace counts, timestamps, and hashes. Access to the original workspaces, raw traces, preprint, and compiled release is managed separately by the project team.

This pilot applies the paper's agent settings to a new benchmark and compares the two harnesses exposed by the supplied release. It records aggregate token use including cached input. To assess the context-management mechanism directly, use the saved traces to locate compaction and determine whether evidence from earlier in the task was recovered when needed.

## Tuesday validation

See [the Tuesday checklist](TUESDAY.md) for the environment change, validation controls and handoff commands. The published November 13 snapshot used host coding and is a separate experiment. Start a fresh output directory for this Linux-terminal setup; configuration and harness source hashes prevent mixing checkpoints.

Validate the planned manual-review task after the smoke pair finishes and retires its image:

```sh
python3 run.py validate --output output-linux --local-rubric --cycle-images \
  --task deepswe_vitest-duration-sharding \
  --known-good-patch ../patches/deepswe_vitest-duration-sharding.patch
```

The known-good patches come from Victor P.'s archived first-attempt implementations. They validate grading and are not supplied to either coding actor. Compaction defaults are checked against [the exact upstream Codex source](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535).
