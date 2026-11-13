# CS224V SWE-Interact evaluation

Snapshot generated 2026-11-13T19:40:11+00:00.

The same 75 task IDs are available in single-turn and multi-turn form.
Both arms use the single-turn SWE-Interact task and receive the same full specification upfront.
If the final reply ends with a question, resume the same session with the literal message continue.
The detector checks the last nonempty prose line, skipping fenced code and Markdown blockquotes.
This follows the ADAPT paper's clarification policy. The detector and continuation cap are local choices.
A future experiment can use SWE-Interact's multi-turn protocol with a live simulated maintainer.
The agent uses the pinned Codex release and GPT-6 Luna on the ChatGPT subscription.
The 48K context and 10K tool output cap follow ADAPT §3.3. All continuations share the one-hour coding budget.
The fixed seed controls task order. The compiled runner exposes no model seed or temperature.
A trial counts as resolved when the upstream verifier returns reward 1.
Only scored attempts enter the denominators. Interrupted and unscored attempts stay in the history.
Token totals include cached input. A context window is a per-call budget.
The local adapter runs the coding agent on macOS and upstream verification in Linux Docker.
The upstream single-turn verifier runs on the frozen candidate.
Attempts using image cycling share a task image across both arms and retire it after both scores are saved.
Prior local stock attempts are reused only after checking their prompt, model settings, release,
patch hash and final reply. Every reused attempt already satisfied the continue rule.
The previous Terra pilot and Victor's historical 41/75 single-turn result are separate from this experiment.
The local stock harness serves as the baseline. Historical results are not a third matched arm.
3 tasks are held because they involve security scanning or exploit tooling.

## Results

| Arm | Resolved | Scored | Eligible |
| --- | ---: | ---: | ---: |
| stock | 5 | 27 | 72 |
| adapt | 3 | 26 | 72 |

Matched stock/ADAPT tasks scored: 26.

Dataset coverage: 26/75 matched pairs; 72 tasks in scope, 25 currently deferred for grader setup.
- In progress: `swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171` (adapt, grading).

Current blockers

- SWE Atlas grading requires OPENAI_API_KEY and OPENAI_API_BASE.

On these tasks, stock resolved 4/26 and ADAPT resolved 3/26.

| Matched task | Stock reward | ADAPT reward | Stock tokens | ADAPT tokens |
| --- | ---: | ---: | ---: | ---: |
| deepswe_fastapi-deprecation-response-headers | 0 | 0 | 238,626 | 180,268 |
| deepswe_kombu-single-active-consumer-priority | 0 | 1 | 183,386 | 638,902 |
| deepswe_awilix-async-container-initialization | 0 | 0 | 185,591 | 220,781 |
| swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d | 0 | 0 | 527,592 | 269,569 |
| deepswe_wazero-multi-module-snapshots | 1 | 0 | 152,244 | 165,020 |
| deepswe_cattrs-partial-structuring-recovery | 0 | 0 | 155,006 | 223,293 |
| swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367 | 1 | 1 | 103,151 | 226,735 |
| swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26 | 1 | 0 | 466,106 | 80,947 |
| deepswe_tomlkit-toml-table-converters | 0 | 0 | 264,637 | 377,741 |
| deepswe_sqlite-utils-safe-import-checkpoints | 0 | 0 | 184,430 | 1,055,271 |
| deepswe_etree-xml-diff-patch | 0 | 0 | 67,133 | 210,070 |
| swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan | 0 | 0 | 181,024 | 253,284 |
| deepswe_arcane-drift-detection-baselines | 0 | 0 | 908,257 | 2,180,436 |
| deepswe_testem-bail-on-test-failure | 0 | 0 | 318,747 | 105,654 |
| deepswe_httpx-streaming-json-iteration | 0 | 0 | 181,890 | 338,481 |
| swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c | 0 | 0 | 151,247 | 276,708 |
| swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e | 0 | 0 | 138,826 | 262,980 |
| deepswe_mobly-grouped-test-barriers | 0 | 0 | 199,473 | 208,565 |
| swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86 | 0 | 0 | 156,788 | 177,367 |
| swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818 | 0 | 0 | 366,786 | 253,061 |
| swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | 0 | 0 | 139,530 | 307,113 |
| swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26 | 0 | 0 | 235,196 | 820,249 |
| deepswe_clack-async-autocomplete-options | 0 | 0 | 139,888 | 139,585 |
| swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86 | 0 | 0 | 149,110 | 211,945 |
| swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4 | 1 | 1 | 159,207 | 523,933 |
| deepswe_httpx-deterministic-cookie-store | 0 | 0 | 126,240 | 155,936 |

Paired resource use

Token and time summaries include only matched tasks where both arms reported the corresponding value.
Elapsed time is measured from attempt start to saved score; it can include image preparation, verifier time, and pauses before resuming.
The subscription runs do not expose a per-trial dollar charge. Token counts are recorded separately from account usage.

| Arm | Token pairs | Total tokens | Median tokens | Min–max tokens | At least 544K | Time pairs | Median elapsed (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stock | 26 | 6,080,111 | 181,457 | 67,133–908,257 | 1 | 26 | 166 |
| adapt | 26 | 9,863,894 | 239,898 | 80,947–2,180,436 | 4 | 26 | 138 |

| Task family | Stock resolved / scored | ADAPT resolved / scored |
| --- | ---: | ---: |
| DeepSWE | 1 / 14 | 1 / 14 |
| SWE-bench Pro | 4 / 13 | 2 / 12 |
| SWE Atlas Refactoring | 0 / 0 | 0 / 0 |

## Configuration

```json
{
  "arms": {
    "adapt": "codex",
    "stock": "codex-shipped"
  },
  "configuration": {
    "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
    "codex_version": "0.159.0",
    "context_window": 48000,
    "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
    "first_task": "deepswe_fastapi-deprecation-response-headers",
    "image_overrides": {
      "deepswe_fastapi-deprecation-response-headers": "sha256:9b51fac6b334a94a4057d941ac9b9d4a47dc68abccaabd5270f8223764287047"
    },
    "lane": "subscription",
    "max_continuations": 8,
    "model": "gpt-6-luna",
    "model_seed": null,
    "platform": "linux/amd64",
    "protocol": "singleturn-with-conditional-continue",
    "reasoning_effort": "medium",
    "rubric_model": "anthropic/claude-opus-4-5-20251101",
    "task_order_seed": 224,
    "temperature": null,
    "tool_output_limit": 10000,
    "trial_wall_clock_s": 3600,
    "verifier_pytest_addopts": {
      "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
    }
  },
  "model_catalog_sha256": "a5e25107506f0934cb62144c093c72bf8c7fa5de1436f4aa02fe54769d789618",
  "runner_sha256": "96fb6d40ce455c428280639ca82e426f3f6a34454acd55bc30f360e516464373"
}
```

## Per-task results in scheduled order

| # | Task | Family | Stock | ADAPT |
| ---: | --- | --- | --- | --- |
| 1 | deepswe_fastapi-deprecation-response-headers | DeepSWE | fail (0) | fail (0) |
| 2 | deepswe_kombu-single-active-consumer-priority | DeepSWE | fail (0) | pass (1) |
| 3 | deepswe_awilix-async-container-initialization | DeepSWE | fail (0) | fail (0) |
| 4 | rf_task-69b7c2a04b6f8ff9ed98813b | SWE Atlas Refactoring | deferred | deferred |
| 5 | swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d | SWE-bench Pro | fail (0) | fail (0) |
| 6 | rf_task-69d196f015a150488265afb7 | SWE Atlas Refactoring | deferred | deferred |
| 7 | deepswe_wazero-multi-module-snapshots | DeepSWE | pass (1) | fail (0) |
| 8 | deepswe_cattrs-partial-structuring-recovery | DeepSWE | fail (0) | fail (0) |
| 9 | swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367 | SWE-bench Pro | pass (1) | pass (1) |
| 10 | rf_task-69b7c2a04b6f8ff9ed988137 | SWE Atlas Refactoring | deferred | deferred |
| 11 | swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26 | SWE-bench Pro | pass (1) | fail (0) |
| 12 | rf_task-69b7c2a04b6f8ff9ed98812f | SWE Atlas Refactoring | deferred | deferred |
| 13 | rf_task-696719205599a51110d4b436 | SWE Atlas Refactoring | deferred | deferred |
| 14 | rf_task-694b4b99829f00e24fd11891 | SWE Atlas Refactoring | deferred | deferred |
| 15 | deepswe_tomlkit-toml-table-converters | DeepSWE | fail (0) | fail (0) |
| 16 | rf_task-696719205599a51110d4b458 | SWE Atlas Refactoring | deferred | deferred |
| 17 | deepswe_sqlite-utils-safe-import-checkpoints | DeepSWE | fail (0) | fail (0) |
| 18 | deepswe_etree-xml-diff-patch | DeepSWE | fail (0) | fail (0) |
| 19 | swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan | SWE-bench Pro | fail (0) | fail (0) |
| 20 | deepswe_arcane-drift-detection-baselines | DeepSWE | fail (0) | fail (0) |
| 21 | deepswe_testem-bail-on-test-failure | DeepSWE | fail (0) | fail (0) |
| 22 | rf_task-696719205599a51110d4b428 | SWE Atlas Refactoring | deferred | deferred |
| 23 | deepswe_httpx-streaming-json-iteration | DeepSWE | fail (0) | fail (0) |
| 24 | rf_task-694b4b99829f00e24fd11889 | SWE Atlas Refactoring | deferred | deferred |
| 25 | rf_task-696719205599a51110d4b40c | SWE Atlas Refactoring | deferred | deferred |
| 26 | swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c | SWE-bench Pro | fail (0) | fail (0) |
| 27 | rf_task-696719205599a51110d4b451 | SWE Atlas Refactoring | deferred | deferred |
| 28 | swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e | SWE-bench Pro | fail (0) | fail (0) |
| 29 | deepswe_mobly-grouped-test-barriers | DeepSWE | fail (0) | fail (0) |
| 30 | swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86 | SWE-bench Pro | fail (0) | fail (0) |
| 31 | rf_task-696719205599a51110d4b447 | SWE Atlas Refactoring | deferred | deferred |
| 32 | deepswe_bandit-structured-nosec-directives | DeepSWE | held | held |
| 33 | deepswe_pwntools-tube-multiplexing | DeepSWE | held | held |
| 34 | swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818 | SWE-bench Pro | fail (0) | fail (0) |
| 35 | swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | SWE-bench Pro | fail (0) | fail (0) |
| 36 | rf_task-696719205599a51110d4b441 | SWE Atlas Refactoring | deferred | deferred |
| 37 | rf_task-696719205599a51110d4b446 | SWE Atlas Refactoring | deferred | deferred |
| 38 | swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26 | SWE-bench Pro | fail (0) | fail (0) |
| 39 | deepswe_clack-async-autocomplete-options | DeepSWE | fail (0) | fail (0) |
| 40 | rf_task-69d196f015a150488265afb9 | SWE Atlas Refactoring | deferred | deferred |
| 41 | rf_task-696719205599a51110d4b434 | SWE Atlas Refactoring | deferred | deferred |
| 42 | rf_task-696719205599a51110d4b455 | SWE Atlas Refactoring | deferred | deferred |
| 43 | swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86 | SWE-bench Pro | fail (0) | fail (0) |
| 44 | swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4 | SWE-bench Pro | pass (1) | pass (1) |
| 45 | swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e | SWE-bench Pro | held | held |
| 46 | deepswe_httpx-deterministic-cookie-store | DeepSWE | fail (0) | fail (0) |
| 47 | swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | SWE-bench Pro | pass (1) | grading |
| 48 | rf_task-69b7c2a04b6f8ff9ed98813d | SWE Atlas Refactoring | deferred | deferred |
| 49 | deepswe_returns-validated-error-accumulation | DeepSWE | pending | pending |
| 50 | rf_task-69391d8d1ce51c407be1e533 | SWE Atlas Refactoring | deferred | deferred |
| 51 | swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d | SWE-bench Pro | pending | pending |
| 52 | swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb | SWE-bench Pro | pending | pending |
| 53 | rf_task-69d196f015a150488265afc1 | SWE Atlas Refactoring | deferred | deferred |
| 54 | swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125 | SWE-bench Pro | pending | pending |
| 55 | swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan | SWE-bench Pro | pending | pending |
| 56 | deepswe_vitest-duration-sharding | DeepSWE | pending | pending |
| 57 | rf_task-694b4b99829f00e24fd11885 | SWE Atlas Refactoring | deferred | deferred |
| 58 | swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86 | SWE-bench Pro | pending | pending |
| 59 | swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan | SWE-bench Pro | pending | pending |
| 60 | swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566 | SWE-bench Pro | pending | pending |
| 61 | deepswe_drizzle-orm-window-function-builders | DeepSWE | pending | pending |
| 62 | deepswe_ofetch-per-origin-circuit-breaker | DeepSWE | pending | pending |
| 63 | rf_task-696719205599a51110d4b440 | SWE Atlas Refactoring | deferred | deferred |
| 64 | swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288 | SWE-bench Pro | pending | pending |
| 65 | rf_task-696719205599a51110d4b476 | SWE Atlas Refactoring | deferred | deferred |
| 66 | deepswe_boa-hierarchical-evaluation-cancellation | DeepSWE | pending | pending |
| 67 | deepswe_participle-grammar-conflict-analysis | DeepSWE | pending | pending |
| 68 | swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f | SWE-bench Pro | pending | pending |
| 69 | deepswe_kcp-go-multiplexed-kcp-streams | DeepSWE | pending | pending |
| 70 | rf_task-694b4b99829f00e24fd118a1 | SWE Atlas Refactoring | deferred | deferred |
| 71 | swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4 | SWE-bench Pro | pending | pending |
| 72 | deepswe_helm-array-merge-strategies | DeepSWE | pending | pending |
| 73 | swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12 | SWE-bench Pro | pending | pending |
| 74 | rf_task-69391d8d1ce51c407be1e531 | SWE Atlas Refactoring | deferred | deferred |
| 75 | deepswe_fastapi-implicit-head-options | DeepSWE | pending | pending |

## Scored attempt details

Cached input is part of input tokens. Reasoning output is part of output tokens.

| Task | Arm | Reward | Input | Cached input | Output | Reasoning output | Total | Elapsed (s) | Steps | Calls | Continues | Reused |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| deepswe_fastapi-deprecation-response-headers | stock | 0 | 235,138 | 201,728 | 3,488 | 329 | 238,626 | 143 | 12 | 22 | 0 | yes |
| deepswe_fastapi-deprecation-response-headers | adapt | 0 | 178,094 | 154,624 | 2,174 | 138 | 180,268 | 71 | 10 | 18 | 0 | no |
| deepswe_kombu-single-active-consumer-priority | stock | 0 | 180,347 | 137,344 | 3,039 | 128 | 183,386 | 145 | 10 | 18 | 0 | yes |
| deepswe_kombu-single-active-consumer-priority | adapt | 1 | 631,453 | 592,640 | 7,449 | 1,634 | 638,902 | 214 | 24 | 45 | 0 | no |
| deepswe_awilix-async-container-initialization | stock | 0 | 183,072 | 139,904 | 2,519 | 0 | 185,591 | 88 | 11 | 21 | 0 | yes |
| deepswe_awilix-async-container-initialization | adapt | 0 | 217,602 | 171,136 | 3,179 | 459 | 220,781 | 81 | 12 | 22 | 0 | no |
| swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d | stock | 0 | 519,060 | 482,176 | 8,532 | 907 | 527,592 | 687 | 20 | 36 | 0 | no |
| swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d | adapt | 0 | 264,539 | 211,456 | 5,030 | 497 | 269,569 | 554 | 14 | 25 | 0 | no |
| deepswe_wazero-multi-module-snapshots | stock | 1 | 148,737 | 126,464 | 3,507 | 459 | 152,244 | 157 | 13 | 23 | 0 | yes |
| deepswe_wazero-multi-module-snapshots | adapt | 0 | 161,479 | 118,912 | 3,541 | 516 | 165,020 | 145 | 12 | 21 | 0 | no |
| deepswe_cattrs-partial-structuring-recovery | stock | 0 | 152,411 | 120,320 | 2,595 | 243 | 155,006 | 77 | 12 | 23 | 0 | yes |
| deepswe_cattrs-partial-structuring-recovery | adapt | 0 | 219,900 | 193,408 | 3,393 | 401 | 223,293 | 85 | 12 | 22 | 0 | no |
| swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367 | stock | 1 | 101,036 | 75,136 | 2,115 | 184 | 103,151 | 152 | 9 | 16 | 0 | no |
| swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367 | adapt | 1 | 222,684 | 184,832 | 4,051 | 563 | 226,735 | 120 | 15 | 28 | 0 | no |
| swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26 | stock | 1 | 457,615 | 390,912 | 8,491 | 1,425 | 466,106 | 485 | 20 | 36 | 0 | no |
| swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26 | adapt | 0 | 79,841 | 60,288 | 1,106 | 98 | 80,947 | 188 | 6 | 10 | 0 | no |
| deepswe_tomlkit-toml-table-converters | stock | 0 | 261,528 | 224,384 | 3,109 | 280 | 264,637 | 95 | 12 | 25 | 0 | yes |
| deepswe_tomlkit-toml-table-converters | adapt | 0 | 372,058 | 342,912 | 5,683 | 843 | 377,741 | 132 | 16 | 35 | 0 | no |
| deepswe_sqlite-utils-safe-import-checkpoints | stock | 0 | 181,449 | 146,688 | 2,981 | 293 | 184,430 | 98 | 12 | 22 | 0 | yes |
| deepswe_sqlite-utils-safe-import-checkpoints | adapt | 0 | 1,044,018 | 972,544 | 11,253 | 3,033 | 1,055,271 | 272 | 37 | 71 | 0 | no |
| deepswe_etree-xml-diff-patch | stock | 0 | 64,712 | 41,600 | 2,421 | 0 | 67,133 | 129 | 6 | 10 | 0 | no |
| deepswe_etree-xml-diff-patch | adapt | 0 | 204,710 | 179,712 | 5,360 | 511 | 210,070 | 136 | 12 | 21 | 0 | no |
| swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan | stock | 0 | 175,393 | 135,424 | 5,631 | 454 | 181,024 | 318 | 11 | 19 | 0 | no |
| swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan | adapt | 0 | 245,871 | 203,776 | 7,413 | 1,089 | 253,284 | 236 | 13 | 24 | 0 | no |
| deepswe_arcane-drift-detection-baselines | stock | 0 | 892,923 | 813,824 | 15,334 | 1,446 | 908,257 | 726 | 32 | 66 | 0 | no |
| deepswe_arcane-drift-detection-baselines | adapt | 0 | 2,157,418 | 1,997,824 | 23,018 | 2,400 | 2,180,436 | 686 | 69 | 134 | 0 | no |
| deepswe_testem-bail-on-test-failure | stock | 0 | 315,529 | 287,872 | 3,218 | 308 | 318,747 | 179 | 14 | 26 | 0 | no |
| deepswe_testem-bail-on-test-failure | adapt | 0 | 104,489 | 84,608 | 1,165 | 45 | 105,654 | 58 | 8 | 14 | 0 | no |
| deepswe_httpx-streaming-json-iteration | stock | 0 | 179,122 | 158,464 | 2,768 | 497 | 181,890 | 165 | 12 | 24 | 0 | no |
| deepswe_httpx-streaming-json-iteration | adapt | 0 | 332,933 | 309,376 | 5,548 | 1,519 | 338,481 | 141 | 18 | 33 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c | stock | 0 | 148,275 | 117,376 | 2,972 | 0 | 151,247 | 80 | 11 | 22 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c | adapt | 0 | 271,488 | 221,184 | 5,220 | 445 | 276,708 | 127 | 14 | 26 | 0 | no |
| swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e | stock | 0 | 135,505 | 115,328 | 3,321 | 259 | 138,826 | 222 | 9 | 19 | 0 | no |
| swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e | adapt | 0 | 257,706 | 229,248 | 5,274 | 905 | 262,980 | 207 | 13 | 23 | 0 | no |
| deepswe_mobly-grouped-test-barriers | stock | 0 | 197,576 | 170,368 | 1,897 | 192 | 199,473 | 56 | 10 | 22 | 0 | no |
| deepswe_mobly-grouped-test-barriers | adapt | 0 | 205,876 | 181,504 | 2,689 | 217 | 208,565 | 76 | 12 | 22 | 0 | no |
| swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86 | stock | 0 | 155,256 | 110,592 | 1,532 | 191 | 156,788 | 151 | 8 | 14 | 0 | no |
| swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86 | adapt | 0 | 174,723 | 149,632 | 2,644 | 247 | 177,367 | 104 | 11 | 20 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818 | stock | 0 | 362,690 | 321,536 | 4,096 | 619 | 366,786 | 215 | 12 | 22 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818 | adapt | 0 | 249,605 | 217,600 | 3,456 | 181 | 253,061 | 90 | 12 | 22 | 0 | no |
| swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | stock | 0 | 136,762 | 117,248 | 2,768 | 341 | 139,530 | 173 | 9 | 16 | 0 | no |
| swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | adapt | 0 | 298,124 | 246,400 | 8,989 | 1,791 | 307,113 | 219 | 17 | 30 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26 | stock | 0 | 229,662 | 178,304 | 5,534 | 0 | 235,196 | 255 | 11 | 23 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26 | adapt | 0 | 812,682 | 767,360 | 7,567 | 1,626 | 820,249 | 196 | 25 | 48 | 0 | no |
| deepswe_clack-async-autocomplete-options | stock | 0 | 135,664 | 106,368 | 4,224 | 191 | 139,888 | 249 | 9 | 14 | 0 | no |
| deepswe_clack-async-autocomplete-options | adapt | 0 | 136,849 | 109,056 | 2,736 | 214 | 139,585 | 152 | 10 | 16 | 0 | no |
| swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86 | stock | 0 | 147,098 | 113,920 | 2,012 | 87 | 149,110 | 167 | 9 | 16 | 0 | no |
| swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86 | adapt | 0 | 210,488 | 166,912 | 1,457 | 0 | 211,945 | 88 | 10 | 18 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4 | stock | 1 | 156,635 | 129,792 | 2,572 | 144 | 159,207 | 224 | 12 | 20 | 0 | no |
| swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4 | adapt | 1 | 514,726 | 476,672 | 9,207 | 2,931 | 523,933 | 215 | 23 | 44 | 0 | no |
| deepswe_httpx-deterministic-cookie-store | stock | 0 | 121,395 | 102,784 | 4,845 | 63 | 126,240 | 248 | 10 | 16 | 0 | no |
| deepswe_httpx-deterministic-cookie-store | adapt | 0 | 151,741 | 131,968 | 4,195 | 471 | 155,936 | 108 | 11 | 20 | 0 | no |
| swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | stock | 1 | 117,271 | 97,280 | 3,286 | 394 | 120,557 | 536 | 8 | 14 | 0 | no |

## Attempt history

See the [structured attempt records](attempts.json) for statuses, settings, and provenance hashes.
