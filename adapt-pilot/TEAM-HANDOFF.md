# SWE-Interact team handoff

## What we agreed on November 20

Compare the two Codex automation paths and the direct-chat histories on the same small set of tasks. Record the actual initial prompt, follow-up turns, model and effort, workspace, stop condition, frozen patch, and verifier. The meeting raised automation as a hypothesis. The available evidence supports several differences in setup and does not settle which one caused the score gap.

Make failure analysis the priority. Start with **Vitest duration sharding** and **FastAPI deprecation response headers**. Use cattrs as a second example of a shared requirement miss if time permits. Pick one or two trajectories for the demo. Use targeted cross-runs when they resolve a concrete discrepancy.

## Checkpoint for the comparison

| Run | Saved pass rate | Scope |
| --- | ---: | --- |
| Victor P., direct Codex chat, single-turn | 41/75 (54.7%) | DeepSWE 19/25, SWE-bench Pro 11/25, SWE Atlas 11/25 |
| Victor P., Opus multi-turn with adaptive maintainer | 16/70 (22.9%), reported at the sync | Separate setup. Opus 4.7 was reported for the maintainer. Task ledger and transcripts pending. |
| Victor C., stock Codex | 7/38 (18.4%) | Recorded two-week single-turn pairs |
| Victor C., ADAPT | 6/38 (15.8%) | Same recorded pairs |

The matched subset with usable verification has 36 task IDs. Victor P.'s archived direct-chat result is 22/36, stock Codex is 7/36, and ADAPT is 6/36. Flipt CUE validation and Suricata were excluded from this denominator because verification was blocked. The two-week totals replace older results with the newer complete pair on five repeated tasks and span two coding environments. Victor P.'s archive includes native verifier fallbacks and does not independently establish the actor model for every direct-chat run. The 16/70 report is distinct from the Codex stock/ADAPT comparison.

## Where to look

| What | Location |
| --- | --- |
| Current headless stock/ADAPT runner | [Paired campaign guide](WEDNESDAY.md), [runner](run.py), [batch wrapper](run_batch.py), [configured settings](config.json) |
| Prior local runner and FastAPI pilot | [Historical code and inputs](archive/README.md) |
| Two-week analysis and failure labels | [Reproduction instructions](analysis/README.md), [snapshot](analysis/summary-2026-11-20.json) |
| Victor P. direct-chat outcomes and patches | [Results](../results/), [frozen patches](../patches/) |

The AppleScript files mentioned in the meeting still need to be located and exchanged. The published Python continuation wrapper runs the headless CLI. The historical Mac runner is also a CLI runner. Exchange the project-only conversation trajectories privately. The public repository contains code, task-level labels and case summaries.

## First cases to line up

| Case | Victor P. | Victor C. | Evidence to compare |
| --- | --- | --- | --- |
| Vitest duration sharding | Frozen `55dc8aa4` passed 8/8 baseline and 71/71 feature tests. | Latest stock patch was empty. ADAPT passed 70/71 feature tests and used seconds for `recordedAt`. The post-compaction model requests still carried the TTL formula. | Compare the exact timestamp instruction, the development checks, and when each run stopped. |
| FastAPI sunset headers | The archived patch passed the verifier and the known-good control. | Latest stock patch was empty. ADAPT omitted the required `FastAPI.get(sunset=...)` interface. | Compare how each trajectory tracked API coverage and what it tested before stopping. |
| cattrs partial structuring | The passing patch retained successfully structured values on refine. | Both arms overwrote an already structured value and failed the preservation check. | Trace when field preservation became an explicit implementation invariant in each run. |

The shared action is to exchange the exact automation source and two trajectories, then cross-check stop behavior and grader inputs before attributing the gap to context management.
