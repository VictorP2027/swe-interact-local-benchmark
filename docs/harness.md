# Harness notes

Python 3.11+ is required for `tomllib`. Docker, Git and each task's original runtime/dependencies are needed for evaluation. Rubric grading additionally requires the supported Codex CLI, its existing sign-in, the requested model, and dependencies used by the upstream rubric evaluator. No credentials are stored here.

`verify-direct.py` handles non-RF supplied test scripts. `verify-rf.py` handles supplied RF test/rubric scripts through `codex_rubric_bridge.py`. `grade-rf-frozen-patch.py` grades a frozen patch without rerunning its tests. The bridge uses GPT-6 Luna at medium reasoning, forbids model tool use, and records requests, responses and usage. Its output-token budget is an instruction, not a hard CLI token limit.

These scripts were extracted from an existing workspace. They expect a clone at `$SWE_INTERACT_WORKSPACE/SWE-Interact`, clean task repositories with recorded implementation commits, task-owned prepared containers, and the original run ledger at `$SWE_INTERACT_WORKSPACE/outputs/swe-interact-direct/progress.json`. The published `results/summary.json` is an export, not a replacement for that live ledger. Do not point a rerun at the completed original ledger.

Workspace root defaults to the current directory and can be set with `SWE_INTERACT_WORKSPACE`. Set `CODEX_CLI` if the Codex executable is not on PATH. `verify-direct.py` requires `--docker-host`; `verify-rf.py` requires `DOCKER_HOST`. Select the socket for a task-owned environment explicitly. The scripts can reset/clean and stop the selected task-owned containers, so use prepared benchmark containers only.

For argument documentation without executing a benchmark:

```sh
python3 harness/verify-direct.py --help
python3 harness/verify-rf.py --help
python3 harness/grade-rf-frozen-patch.py --help
```

This export only changes workspace/executable/socket configuration in the historical harness. It has not been used to rerun the 75-task assessment. Task-specific native fallbacks and reconciliation steps are described in the result records; the four scripts alone do not reproduce every recovery.
