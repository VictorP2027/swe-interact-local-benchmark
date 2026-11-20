# ADAPT SWE-Interact comparison

Start with the [November 20 team handoff](TEAM-HANDOFF.md) for the shared conclusions, code inventory, and two cases to compare. The [analysis folder](analysis/) reproduces the aggregate from the saved trial artifacts.

Use [WEDNESDAY.md](WEDNESDAY.md) to run the shared campaign. The committed [assignment plan](assignments/wednesday.json) gives Victor C. 38 tasks and Victor P. 37. Run both stock Codex and ADAPT for every assigned task on the same machine. All 75 tasks are included.

Both arms receive the full single-turn specification and use GPT-6 Luna, medium reasoning, Codex 0.159.0, ADAPT commit `166c433f`, a 48K context, a 10K tool-output cap and a one-hour coding budget. The wrapper replies `continue` to a clarification question within that same budget, with a local eight-continuation cap. Seed 224 fixes assignment order. The supplied runner does not expose model seed or temperature.

## Setup

Requires Python 3.11+, Git, Docker Desktop, an Apple silicon Mac, the authorized pinned ADAPT release and an existing Codex sign-in. Obtain the private release from the project team. The compiled release stays outside this repository.

```sh
git clone https://github.com/scaleapi/SWE-Interact.git ../SWE-Interact
git -C ../SWE-Interact checkout b32f98c3b8f76ca65e84341d1f30e5af7135f85d
cd adapt-pilot
export SWE_ADAPT_RELEASE=/absolute/path/to/authorized/adapt-release
python3 -m unittest -v test_harness.py test_campaign.py test_collection.py
```

Set `SWE_INTERACT_DATASET` if the dataset is elsewhere. Check the existing login with `"$SWE_ADAPT_RELEASE/codex/bin/codex" login status`. The CLI runs headlessly using that sign-in; an OpenAI API key is unnecessary for this configuration.

Follow the owner-specific commands in [WEDNESDAY.md](WEDNESDAY.md). Use `campaign.py` for the split run. It checks task ownership, binds the output to one machine, invokes both arms, prevents idle sleep on Mac and preserves completed results on resume. Keep the pinned checkout and plan fixed throughout the batch.

## Execution and saved evidence

The ADAPT controller runs on macOS. Both arms read, edit and test project code through the same `task_terminal` MCP tool in separate Linux containers. Fresh containers from the same image grade their frozen patches. DeepSWE and SWE Atlas use upstream prebuilt images; SWE-bench Pro builds its upstream Dockerfile wrapper. Missing `allow_internet` follows Harbor's default of true.

The runner validates the grader with untouched and known-good controls before coding. It checks the generated model settings after each arm. Frozen patches, tracked source archives and partial work are saved before coding containers are removed. Completed scores are skipped; interrupted grading resumes from the saved candidate. Active task images cycle after both arms are scored.

Use `review_evidence.py` for private manual-review packets and `campaign.py export` for a shareable `HANDOFF.md`. Keep raw traces, sign-in files, request archives and the private release local. Use `collect_results.py` to combine the two primary packets. Calibration and historical results stay separate.

## Limits and reference results

The shared Linux terminal is a tool adaptation. Native host tools remain available for context data; project edits in the host workspace invalidate an attempt. The supplied Mac controller skips data-structure pytest validation. The [pinned Codex source](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535) derives a 43,200-token automatic compaction threshold from the 48K context.

SWE Atlas uses GPT-6 Luna medium through the local headless judge bridge in place of the upstream Claude Opus default. Both arms use the same substitute judge, recorded in the manifest. DeepSWE and SWE-bench Pro use test-based scores. A task passes only when its supplied verifier returns reward 1.

[Wednesday preparation and smoke results](results/wednesday-prep-2026-11-20/HANDOFF.md) · [Tuesday validation](results/tuesday-2026-11-20/HANDOFF.md) · [Earlier pilot snapshot](results/REPORT.md)

The earlier snapshot used host coding. Victor P.'s [41/75 direct-chat archive](../README.md) used a different protocol. Those records are references outside the new paired campaign.
