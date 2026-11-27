# Three-case repeated comparison — Victor P.

All **18 selected outcomes are scored**: three independent completed draws per task and arm. This is a separate single-turn DeepSWE subset, outside the original 75-task assessment and the earlier 25-task batch.

| Task | Stock passed/scored | ADAPT passed/scored |
| --- | ---: | ---: |
| Wazero multi-module snapshots | 0/3 | 1/3 |
| KCP multiplexed streams | 0/3 | 1/3 |
| Kombu single-active-consumer priority | 0/3 | 0/3 |
| **Total** | **0/9 (0%)** | **2/9 (22.2%)** |

Both arms use **GPT-6 Luna / medium**, supplied build **166c433f**, **Codex CLI 0.159.0**, a **48,000-token working budget**, **45,600 usable input tokens**, a **10,000-token tool-output cap** and a **3,600-second coding allowance per draw**. The controller runs on Apple ARM macOS, with project work and verification in `linux/amd64` Docker containers. The translation backend is unconfirmed. Native compaction was not observed in any of the 18 completed actors.

- [status.json](status.json): completion state, per-task and overall counts, and the separately labeled screenshot reference.
- [manifest.json](manifest.json): all 18 draw records, exact task IDs, settings, source commits, image/prompt hashes and frozen candidate hashes.
- [comparison-CHECKSUMS.json](comparison-CHECKSUMS.json): SHA-256 checksums for the two comparison files.
- [Frozen passing patches and verifier summaries](passing-artifacts/README.md): current ADAPT KCP repeat 1, current ADAPT Wazero repeat 3, and **PREVIOUS RUN — Wazero stock**. The historical stock artifact is not included in the current 18-draw totals.

One earlier generation hit account quota and remains separately unscored. After a supported capacity check succeeded, the remaining outcomes finished. No scored failure was rerolled; all 13 pre-interruption scored records are unchanged. Untouched and known-good verifier controls passed. The old Wazero stock patch was used only for the isolated verifier-positive control, never as a new actor's implementation or input.

The user-provided reference screenshot reports stock **1/9** and ADAPT **2/9**. Its original settings, manifest and per-draw records are unavailable here; those totals are reported reference data, not verified matched-run evidence. Compare the other run's exact task IDs, images, prompts, model/effort, context limits and stopping/testing policy before interpreting the score difference. Three draws per task do not establish a general harness advantage or a context-retention mechanism.

This export contains comparison metadata, exact frozen production patches for the three available verified passes, and summaries of their recorded verifier results. Raw requests, credentials, private binaries, candidate source archives and full traces remain local. Native per-repeat input manifests and the earlier 25/75-task ledgers were not rewritten.
