# Fast requested: final three-case results

Status: **complete**. Completed actors: **18/18**; verified scores: **18/18**.

| Task | Stock passed/scored | ADAPT passed/scored | Nov 24 stock | Nov 24 ADAPT |
| --- | ---: | ---: | ---: | ---: |
| Wazero | 1/3 | 2/3 | 0/3 | 1/3 |
| KCP | 0/3 | 2/3 | 0/3 | 1/3 |
| Kombu | 0/3 | 0/3 | 0/3 | 0/3 |
| Total | 1/9 (11.1%) | 4/9 (44.4%) | 0/9 (0.0%) | 2/9 (22.2%) |

Both arms explicitly request Fast through the pinned CLI setting (`fast`, mapped to wire `priority`). The provider tier is recorded separately. Stock HTTP bodies are not captured by its shipped harness, so its actual served tier is unknown. ADAPT outgoing requests are captured; reported response tiers are listed below. A requested tier does not establish acceleration.

| Repeat | Task | Arm | Captured requests | Reported response tiers |
| ---: | --- | --- | ---: | --- |
| 1 | deepswe_wazero-multi-module-snapshots | stock | 0 | unknown (no capture) |
| 1 | deepswe_wazero-multi-module-snapshots | adapt | 14 | {"default": 14} |
| 1 | deepswe_kcp-go-multiplexed-kcp-streams | stock | 0 | unknown (no capture) |
| 1 | deepswe_kcp-go-multiplexed-kcp-streams | adapt | 22 | {"default": 22} |
| 1 | deepswe_kombu-single-active-consumer-priority | stock | 0 | unknown (no capture) |
| 1 | deepswe_kombu-single-active-consumer-priority | adapt | 24 | {"default": 24} |
| 2 | deepswe_wazero-multi-module-snapshots | stock | 0 | unknown (no capture) |
| 2 | deepswe_wazero-multi-module-snapshots | adapt | 16 | {"default": 16} |
| 2 | deepswe_kcp-go-multiplexed-kcp-streams | stock | 0 | unknown (no capture) |
| 2 | deepswe_kcp-go-multiplexed-kcp-streams | adapt | 17 | {"default": 17} |
| 2 | deepswe_kombu-single-active-consumer-priority | stock | 0 | unknown (no capture) |
| 2 | deepswe_kombu-single-active-consumer-priority | adapt | 18 | {"default": 18} |
| 3 | deepswe_wazero-multi-module-snapshots | stock | 0 | unknown (no capture) |
| 3 | deepswe_wazero-multi-module-snapshots | adapt | 20 | {"default": 20} |
| 3 | deepswe_kcp-go-multiplexed-kcp-streams | stock | 0 | unknown (no capture) |
| 3 | deepswe_kcp-go-multiplexed-kcp-streams | adapt | 18 | {"default": 18} |
| 3 | deepswe_kombu-single-active-consumer-priority | stock | 0 | unknown (no capture) |
| 3 | deepswe_kombu-single-active-consumer-priority | adapt | 18 | {"default": 18} |

All coding actors use **GPT-6 Luna / medium**, supplied build **166c433f**, **Codex CLI 0.159.0**, **48K working context**, **45,600 usable input tokens**, **10K tool-output limit**, and **one hour coding allowance per draw**. Stock then ADAPT run for Wazero, KCP and Kombu, repeated three times with independent outputs. The conditional testing instruction and final-question-only continuation policy are unchanged. There is no adaptive maintainer. No prior patch, diagnostic repair or verifier feedback was supplied to fresh actors. Model seed and temperature are unavailable.

Missing grades are excluded; setup failures and outer verifier timeouts without a completed grade are unscored. A test-level timeout inside a completed canonical verifier retains its recorded reward. 0 quota-interrupted generations are preserved separately and excluded from scored denominators; no scored failure was rerolled.

Fresh isolated untouched and positive verifier controls passed. The positive control uses the earlier frozen Wazero stock patch, outside all actor contexts. Project execution and grading use linux/amd64 Docker on Apple ARM macOS; emulation backend is unconfirmed. The supplied build skips data-structure pytest validation on macOS.

The provenance audit passes: source pins, effective settings, frozen patches/source archives, independent outputs and matching task images/prompts. 0/18 completed actors have observed compaction markers. These repetitions alone do not isolate the cause of differences between arms or prove a context-retention benefit. All earlier 18-, 25- and 75-task ledgers remain unchanged. The Nov 24 baseline above is a separate cohort.

[Every draw and configuration](manifest.json) · [Status](status.json) · [Matched-case review](CASE_STUDY.md) · [Frozen passing patches](passing-artifacts/README.md)

Batch wall-clock: **66.5 minutes**, including preflight, controls, coding and grading. Smoke checks and publication are excluded.

The matched-case review flags a compression fallback in both second-repetition Wazero passes; passing the canonical tests does not establish full compressed-data correctness.
