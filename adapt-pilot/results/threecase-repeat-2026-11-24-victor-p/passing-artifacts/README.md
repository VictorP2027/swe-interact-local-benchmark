# Frozen patches and verifier summaries for passing runs

These are exact copies of frozen production patches, with SHA-256 checks and summaries of their recorded Linux verifier results. No diagnostic repairs or new regrading are included.

| Label | Batch | Patch | Verifier summary |
| --- | --- | --- | --- |
| current-kcp-adapt-repeat-1 | swe-threecase-repeat-20261124 | [patch](current-kcp-adapt-repeat-1/implementation.patch) | [summary](current-kcp-adapt-repeat-1/verifier-summary.json) |
| current-wazero-adapt-repeat-3 | swe-threecase-repeat-20261124 | [patch](current-wazero-adapt-repeat-3/implementation.patch) | [summary](current-wazero-adapt-repeat-3/verifier-summary.json) |
| **PREVIOUS RUN — Wazero stock** | swe-adapt-deepswe25-20261120 | [patch](previous-run-wazero-stock/implementation.patch) | [summary](previous-run-wazero-stock/verifier-summary.json) |

The current 18-draw result remains **stock 0/9, ADAPT 2/9**. The older Wazero stock pass is outside that denominator; its patch was used only as a verifier-positive control for this batch. Both Wazero passes have 2 named baseline passes and 78 named feature passes. KCP logs report successful package/stage exits without individual test counts, so its summary leaves those counts null.

[Machine-readable index](index.json) · [Artifact checksums](CHECKSUMS.json) · [Current status](../status.json) · [Manifest](../manifest.json)
