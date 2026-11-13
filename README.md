# SWE-Interact local benchmark

**Local adapted first-attempt pass rate: 54.7% — 41 of 75 tasks passed.**

| Outcome | Tasks |
| --- | ---: |
| Passed | 41 |
| Failed | 34 |
| Ungraded | 0 |

These implementations were authored directly in a Codex chat from SWE-Interact's single-turn specifications. GPT-6 Luna with medium reasoning was used for rubric grading, replacing the upstream default grader. **54.7% is not an official GPT-6 Luna coding-agent benchmark score.** The actor model was not independently established by these records.

The assessment includes documented native-runtime fallbacks, recovered artifacts and source-failure assessments whose full canonical evaluations did not finish. It does not represent 75 identical canonical invocations. Twenty failed tasks later received passing feedback-assisted grades; those corrections never replace the initial outcomes.

## Contents

- [All 75 task outcomes](results/README.md) and [machine-readable summary](results/summary.json).
- [First-attempt implementation patches](patches/): all 75, including Arcane reconstructed from its recorded commits.
- [Sanitized per-task result records](results/tasks/), [provenance and hashes](results/provenance.json).
- [Original final assessment and limitations](docs/original-final-results.md).
- [Original harness scripts with minimal portability edits](harness/), and [usage notes](docs/harness.md).

The code and result records allow inspection of the local work. Raw execution/model logs, credentials, environment files, build caches and full upstream checkouts are retained locally and are not bundled. References starting with `LOCAL_WORKSPACE` identify those omitted local artifacts. This export is not a self-contained replay of the original chat or the full evaluation environment.

## Separate context-loss pilot

A later six-call Bandit pilot compared original requirements with one short summary. Both conditions had zero task passes; three calls returned no edits. It did not establish that context loss caused earlier failures. The pilot does not contribute to the 41/75 score.

## Upstream

Benchmark: [scaleapi/SWE-Interact](https://github.com/scaleapi/SWE-Interact). The exact checkout commit and original artifact hashes are recorded in provenance. Upstream benchmark files and dependencies are not vendored. Patches target the upstream projects identified by each task; their applicable licenses remain relevant.
