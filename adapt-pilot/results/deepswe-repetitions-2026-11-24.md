# Three paired DeepSWE repetitions per task

Completed November 24, 2026 on Victor C.’s machine. Each selected task received three fresh stock/ADAPT pairs. All 18 coding attempts were scored.

| Task | Stock passes | ADAPT passes | Repetition scores (stock / ADAPT) |
| --- | ---: | ---: | --- |
| Wazero | 0/3 | 1/3 | 0/0, 0/0, 0/1 |
| KCP | 1/3 | 1/3 | 0/1, 0/0, 1/0 |
| Kombu | 0/3 | 0/3 | 0/0, 0/0, 0/0 |
| **Total** | **1/9** | **2/9** | |

1 means the existing and feature test suites both passed. Wazero’s third ADAPT attempt passed. KCP passed once in each arm, in different repetitions. All Kombu attempts scored zero; the first stock patch passed all 94 feature tests and failed five existing tests.

Each slot used GPT-6 Luna medium, Codex 0.159.0, a 48K context, a 10K tool output cap, and a 60-minute coding budget. Both arms used the same full prompt with conditional `continue` and the same pinned Linux image for each task. Arm order alternated. Untouched checkouts scored 0 and supplied solutions scored 1 in all three verifier controls.

See the [repetition runner instructions](../README.md#wazero-kcp-and-kombu-repetitions) and the [JSON results](deepswe-repetitions-2026-11-24.json) for per-arm scores, verifier exit codes, usage, image IDs, and patch hashes.
