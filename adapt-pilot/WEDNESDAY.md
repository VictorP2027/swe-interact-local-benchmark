# Wednesday paired runs

Use the committed [assignment plan](assignments/wednesday.json): Victor C. owns 38 tasks and Victor P. owns 37. Each owner has 12 or 13 tasks from each family. All 75 task IDs are assigned once. Run both stock and ADAPT for every assigned task on the same machine.

Keep the pinned checkout and assignment plan fixed throughout the batch. Use the same profile as Tuesday: GPT-6 Luna, medium effort, Codex 0.159.0, ADAPT `166c433f`, 48K context, 10K tool-output cap and a one-hour coding budget per arm. Model sampling seed and temperature are unavailable. Task order uses seed 224. Every task starts with its full single-turn specification and receives `continue` only for a clarification question.

Both arms run headlessly through the supplied CLI and reuse its existing local sign-in. Run the synthetic judge smoke once per output; reuse its saved proof when resuming. The controller requires an Apple silicon Mac; project commands and grading run in Linux Docker. Set `SWE_ADAPT_RELEASE` to the pinned private release and `SWE_INTERACT_DATASET` if the dataset is not next to this repository. Check the sign-in with `"$SWE_ADAPT_RELEASE/codex/bin/codex" login status`. Use `login --device-auth` on a headless machine that needs a sign-in. Each person signs in on their own machine; credentials are not part of the repository or result packets.

## Victor C.

The first shared task is Vitest duration sharding, which is also the planned manual-review case. Prepare and run just that pair before starting the rest:

```sh
cd adapt-pilot
python3 campaign.py prepare --owner victor-c --output output-wednesday-victor-c
python3 campaign.py judge-smoke --owner victor-c --output output-wednesday-victor-c
caffeinate -i python3 run_batch.py --owner victor-c --output output-wednesday-victor-c \
  --task deepswe_vitest-duration-sharding
python3 review_evidence.py --output output-wednesday-victor-c \
  --task deepswe_vitest-duration-sharding
```

Resume all remaining assigned pairs with:

```sh
caffeinate -i python3 run_batch.py --owner victor-c --output output-wednesday-victor-c
```

## Victor P.

Run the same Vitest smoke pair in a separate calibration output. It checks the second machine and stays outside the primary 75-task comparison; the primary Vitest task belongs to Victor C.

```sh
cd adapt-pilot
python3 campaign.py prepare --owner victor-p --calibration --output output-wednesday-victor-p-smoke
python3 campaign.py judge-smoke --owner victor-p --calibration --output output-wednesday-victor-p-smoke
caffeinate -i python3 run_batch.py --owner victor-p --calibration --output output-wednesday-victor-p-smoke
python3 review_evidence.py --output output-wednesday-victor-p-smoke
```

Prepare a separate primary output, then run the 37 assigned pairs:

```sh
python3 campaign.py prepare --owner victor-p --output output-wednesday-victor-p
caffeinate -i python3 run_batch.py --owner victor-p --output output-wednesday-victor-p
```

The wrapper releases a control-only image when it is not needed for the selected primary task. SWE-bench Pro builds the upstream Dockerfile wrapper around its supplied base image. DeepSWE and SWE Atlas pull the task's prebuilt image. Missing `allow_internet` follows Harbor's legacy default of true; explicit false disables it. See the [Harbor task reference](https://github.com/harbor-framework/skills/blob/main/skills/harbor-task-creator/references/task-toml-reference.md).

## Checkpoints and handoff

Keep the same output directory when resuming. The wrapper records an opaque machine ID and rejects a different machine, owner, plan or calibration mode. It checks ownership and runs both arms on that machine. Launch it with `caffeinate -i` to prevent idle sleep. Run one campaign at a time per machine.

The runner saves each result, frozen patch and tracked source archive before removing its coding container. Partial work stays unscored. The batch skips completed scores and can resume grading from a frozen patch. Exit 75 means account quota stopped the run. Resume the same command after quota is available. The batch records unresolved cases in `batch-status.json` and continues to the remaining tasks.

Both coding arms use the requested task CPU count up to Docker's available capacity. Each attempt records the effective limit. When a grading patch collides with preexisting image files, the adapter verifies the saved candidate tree and rebuilds its diff against the full starting image tree. FastAPI uses its upstream test script's warning policy when the old override names a class absent from the image.

Keep the current image until both arms finish. Upstream prebuilt image digests are recorded so a removed image can be restored for grading. Dockerfile-built images stay cached across an unfinished pair. The one-hour budget covers coding; builds and the upstream verifier have separate time limits.

```sh
python3 campaign.py status --output output-wednesday-victor-c
python3 campaign.py export --output output-wednesday-victor-c --destination results/wednesday-victor-c
```

Use the corresponding output paths for Victor P. Share `HANDOFF.md`, `handoff.json`, the assignment plan and frozen patches. Keep raw logs, request archives, sign-in files and the compiled prototype local. The export includes settings, source hashes, opaque machine IDs, scores, tokens, timings and paired checks.

Combine the two primary packets after copying their shareable folders into the repository. The collector rejects calibration packets, duplicate owners, changed settings and pairs from different machines:

```sh
python3 collect_results.py --input results/wednesday-victor-c/handoff.json \
  --input results/wednesday-victor-p/handoff.json --output results/wednesday-combined.json
```

Add `--require-complete` when all 75 pairs should be scored. Partial collections report the missing and unscored tasks.

Use `run_overflow.py` to queue a backup on Victor C.'s Mac after all 38 primary pairs have scores. It reuses the matching verifier validation and writes the backup separately.

```sh
caffeinate -i python3 run_overflow.py --primary output-wednesday-victor-c \
  --output output-wednesday-victor-c-backup
```

Use the backup packet only if Victor P.'s primary packet is unavailable. Pass `--allow-backup` to the collector to substitute it. The combined report records the backup's actual machine and operator.

## Manual review

Build the full private packet with `review_evidence.py`, then open `output-wednesday-*/manual-review/deepswe_vitest-duration-sharding/README.md`. Request-body views need Python 3.14+ or the `zstd` command; the rest of the harness supports Python 3.11+. Each private packet includes the specification, supplied tests, frozen implementations, source archives, actor test commands and outputs, grading results, final answers, context data and full tool traces. Filtered session events and context-history Git bundles preserve context before and after compaction. ADAPT request-body views exclude HTTP headers. Add `--historical-output /path/to/older/output` to include a separate historical reference. `CHECKSUMS.json` identifies the saved evidence, and `NOTES.md` has a comparison template that survives rebuilding the packet.

Compare the implementations and failed checks first. Then locate the evidence each agent saw before compaction, what survived in ADAPT's data structures, and what was read again afterward. Decide whether missing earlier evidence caused a failure and whether the task actually stressed context. Keep setup failures and implementation mistakes separate from context loss.

The supplied Mac controller skips data-structure pytest checks. The Linux task terminal is a shared tool adaptation. Record these limits when comparing with the paper. A smoke task can fail its feature tests while still confirming that authentication, execution, checkpointing and grading work.
