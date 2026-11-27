# Matched-case review

This review uses frozen candidates and their recorded canonical verifier results. It introduces no repairs, actor feedback, regrading or additional benchmark outcomes.

## Wazero, repetition 2: both pass

| Arm | Reward | Named baseline passes | Named feature passes | Observed compactions |
| --- | ---: | ---: | ---: | ---: |
| stock | 1 | 2 | 78 | 0 |
| adapt | 1 | 2 | 78 | 0 |

Both candidates implement the snapshot/error API and resolve selective restore targets by matching saved module identities before falling back to positional restore for a full module set. These are concrete implementation behaviors shared by the successful pair.

The two first-repetition failures differ: stock fails full-memory reconstruction after incremental capture and selective-module restoration; ADAPT does not build the feature tests because `snapshot.ErrorCode` is undefined. The second pair passes those tests. This locates the observed errors in implementation/API coverage; it does not establish why a particular generation chose that implementation.

**Code-review limitation:** both passing second-repetition patches include an incremental-compression fallback that copies the baseline compressed bytes and removes their final byte when the newly compressed representation is not smaller. That fallback does not encode the changed memory and can leave a truncated gzip payload. Restore reads separately retained full memory data, so a verifier pass does not establish a valid compressed round trip. This is a source-inspection finding, not a new test result. Canonical scores remain unchanged.

Frozen patch SHA-256 values:

- [stock frozen patch](passing-artifacts/current-wazero-stock-repeat-2/implementation.patch): `9ebaeffbe04f3fb1777e6f36da503a34fb47fe9c11b3b2508801def816f25c7c`.
- [adapt frozen patch](passing-artifacts/current-wazero-adapt-repeat-2/implementation.patch): `2e021dea4e4bc777cf8492452706143d2778e7acbfe794cec017b9f10cad3b38`.

## KCP, repetition 1: different outcomes

Stock passes the baseline stage but fails the following feature checks; ADAPT passes both verifier stages in the matched draw:

- `TestMuxNumStreamsDecreasesAfterClose`.
- `TestMuxSNMPCountersIncremented`.
- `TestMuxStreamNotRemovedUntilBothClosed`.
- `TestMuxStreamRetainedUntilDataDrained`.

These checks concern stream lifecycle, draining and counters. Their results support a task-implementation difference in this pair; they do not isolate an ADAPT memory heuristic as its cause. A causal claim would require an ablation with matched prompts/settings and the relevant context mechanism disabled.

## Context and service tier

Across all completed draws, **0/18** have observed compaction markers. Both arms use GPT-6 Luna / medium, 48K working context (45,600 usable input), a 10K tool-output cap and a one-hour coding allowance. A 48K cap alone does not demonstrate context-retention stress; repeated compactions followed by recovery of earlier facts would be stronger evidence.

Fast is explicitly requested for both arms. All 167 captured ADAPT responses reported default service; stock response-tier capture is unavailable. This experiment cannot establish a Fast speedup or attribute differences to the service tier.

[Full results](README.md) · [Per-draw manifest](manifest.json) · [Frozen passing patches](passing-artifacts/README.md)
