# DeepSWE verifier and trace audit · November 24, 2026

This audit follows the [25-task DeepSWE comparison](deepswe-2026-11-24.md). It examines whether the verifier reproduces verdicts on saved candidates and what the Vitest traces show about the remaining failure.

## Method

Each regrade applies the saved patch in a fresh Linux container and uses the benchmark's supplied tests. The audit checks the saved patch hash, Docker image ID, starting commit, and test file hashes. It runs untouched and supplied-solution controls, then regrades each Kombu and KCP candidate twice, reversing candidate order for the second repeat. The actor runs and their original grades are preserved. These replays use the same Docker host as the active stock campaign, so host load can vary.

## Vitest duration sharding

| Run | Coding behavior | Existing tests | Feature tests | Reward |
| --- | --- | ---: | ---: | ---: |
| Stock Codex, paired | Ran 14 read-only terminal commands over 48 seconds and ended with an empty patch | 8/8 | 15/71 | 0 |
| ADAPT, paired | Used 25 terminal commands over 268 seconds, implemented the feature, and ran `git diff --check` | 8/8 | 70/71 | 0 |
| Victor P., direct chat | Froze commit `55dc8aa4` and verified it in the supplied Linux image | 8/8 | 71/71 | 1 |

The paired arms started from Vitest commit `647e6ade` on the same task image with the same full specification. The supplied test expects `recordedAt` in milliseconds. The specification includes a ten-digit timestamp example alongside a TTL formula that subtracts from the millisecond clock `Date.now()`.

1. **16:42:42 UTC.** ADAPT recorded a compaction event. The TTL formula appeared in all 35 captured ADAPT request bodies, including those after this event.
2. **16:43:16 UTC.** ADAPT first wrote a timestamp in seconds.
3. **16:44:35 UTC.** ADAPT explicitly chose to align with the seconds example. It then changed the TTL cutoff to use seconds and stopped after checking the patch for whitespace errors.
4. **Verification.** The existing suite passed. The new recency check failed because the recorded timestamp used seconds. The trace supports a choice between conflicting cues followed by insufficient validation as the immediate cause.

The [direct-chat patch](../../patches/deepswe_vitest-duration-sharding.patch) uses `Date.now()` and adds focused tests. The project checkpoint also records build, source lint, type checking, and focused development tests before the patch was frozen. Its bytes match the saved known-good control, which scored 1 on the paired image while the untouched control scored 0. The [direct-chat result](../../results/tasks/deepswe_vitest-duration-sharding.json) records the frozen commit and verifier. The full first prompt and any follow-ups, the actor model and context settings, and the stopping conditions still require session evidence before attributing the workflow gap.

## Kombu single active consumer priority

The untouched control scored 0 and the supplied solution scored 1.

| Frozen stock patch | Replay rewards | Existing tests, both replays | Feature tests, both replays |
| --- | --- | --- | --- |
| Original paired run | 0, 0 | 1,408 passed, 4 failed | 94/94 |
| Fresh stock run | 1, 1 | 1,412 passed, 0 failed | 94/94 |

The original candidate reproduced the same four mailbox regressions on both regrades. Both stock patches passed the entire new suite. In the original patch, transport initialization clears all shared broker state, including existing bindings and exchanges. The later patch clears only the three new consumer state collections at initialization in the affected transports. The diff and test failures are consistent with the narrower reset preserving mailbox behavior.

## KCP multiplexed streams

The untouched control scored 0 and the supplied solution scored 1.

| Frozen patch | Replay rewards | Existing suite | Feature suite |
| --- | --- | --- | --- |
| Stock Codex | 0, 0 | Passed both times | Failed both times |
| ADAPT | 1, 1 | Passed both times | Passed both times |

The original stock grade and both replays reported that the stream count stayed above zero after both sides closed. All three hit Go's two-minute timeout on the read deadline test. The stock implementation marks streams closed without removing them from the session map and sets the deadline without a timer to wake a blocked reader. The ADAPT patch implements both cleanup and a deadline timer. Both stock replays also reported a counter assertion absent from the original log. The task-level verdict reproduced, with some variation in the reported failures.

## FastAPI backup case

The original paired stock run ended with an empty patch. Its ADAPT counterpart failed a feature check because `FastAPI.get()` did not accept the new `sunset` argument. The fresh stock repeat produced a nonempty patch and initially hit a patch application collision with files already in the image. After preserving the exact candidate and normalizing the patch, its next grade exited before tests because the legacy pytest warning filter referred to a class missing from the supplied Starlette version.

Today's replay used the pinned grader's compatibility check to remove that filter. The untouched control scored 0 and the supplied solution scored 1. The same saved stock candidate then scored 0 with **3,134 existing tests and 2 of 3 feature tests passing**. The remaining feature test failed because `FastAPI.get(sunset=...)` was unsupported, the same missing interface observed in the original ADAPT patch. The corrected grade gives the earlier zero a valid test basis.

## Comparing across machines

Compare the two machines' records by task ID and arm. Verify the prompt hash, actor model, reasoning effort, working context, starting image, and verifier policy before pooling verdicts. The historical direct-chat archive supplies useful passing patches and cases to inspect. The full archive includes verifier fallbacks and lacks independently verified actor settings.

Victor P.'s archive lists passing direct-chat results for [Kombu](../../results/tasks/deepswe_kombu-single-active-consumer-priority.json), [KCP](../../results/tasks/deepswe_kcp-go-multiplexed-kcp-streams.json), and [FastAPI](../../results/tasks/deepswe_fastapi-deprecation-response-headers.json), as well as the Vitest patch above. These records provide candidate-level comparisons for the workflow audit. The paired experiment's rates use only its pinned stock and ADAPT runs.

[Machine-readable replay scores, patch and image hashes, and verifier settings](frozen-patch-audit-2026-11-24.json)
