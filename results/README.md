# SWE-Interact direct local evaluations

Last updated (UTC): 2026-11-13T01:34:51.377041+00:00

These are direct implementations in the current Codex chat using the supplied
single-turn specifications. They are separate from the autonomous GPT-6 Luna
multiturn/API run, which stopped on API quota and later an expired API key. They do not measure
GPT-6 Luna actor performance, user-simulator interaction quality, or an official full benchmark score.
RF tasks use the unchanged supplied test and rubric scripts with a local completion
transport to the supported Codex CLI, explicitly configured as GPT-6 Luna with
medium reasoning effort through the existing ChatGPT sign-in. This replaces the
supplied default Claude rubric grader. Per-call prompts, responses, model settings,
and usage are archived; no tool use is allowed by the grading transport. The CLI
receives the original 2048-token output budget as an instruction because it has no
per-call output-token-limit flag. RF results are therefore adapted-grader results.

Attempted implementations: **75/75**. Assessed first attempts: **75/75**.
First-attempt passes: **41**. Confirmed failures: **34**.
Ungraded: **0**.
The local adapted assessment is complete: **41/75 = 54.7%**. This is not an official GPT-6 Luna actor benchmark score. Assessments include certain source
failures whose complete canonical evaluation did not finish; their result files
retain `evaluation_valid: false` and identify the separate failure assessment.
Arcane reuses the earlier implementation and native canonical verification.
Clack uses the unchanged canonical test modes natively because the supplied
emulated Linux environment stalled on its unchanged baseline. Its implementation
commit did not change between infrastructure attempts. Wazero also uses the
unchanged test modes natively: the emulated Linux Go compiler and GCC segfaulted
before tests executed. Its original native result and feedback-assisted revision
are separate. Recovered Grafana results explicitly combine unchanged test and
rubric artifacts from identical frozen implementations; hashes and coverage
audits are included. Other task-specific verification limits remain documented
in the result files. No feedback-assisted correction replaces its first attempt.

| Task | First attempt | Revision after test feedback |
| --- | --- | --- |
| deepswe_arcane-drift-detection-baselines | Pass | — |
| deepswe_awilix-async-container-initialization | Fail | Pass |
| deepswe_bandit-structured-nosec-directives | Fail | Pass |
| deepswe_boa-hierarchical-evaluation-cancellation | Pass | — |
| deepswe_cattrs-partial-structuring-recovery | Pass | — |
| deepswe_clack-async-autocomplete-options | Pass | — |
| deepswe_drizzle-orm-window-function-builders | Pass | — |
| deepswe_etree-xml-diff-patch | Pass | — |
| deepswe_fastapi-deprecation-response-headers | Pass | — |
| deepswe_fastapi-implicit-head-options | Pass | — |
| deepswe_helm-array-merge-strategies | Fail | Pass |
| deepswe_httpx-deterministic-cookie-store | Pass | — |
| deepswe_httpx-streaming-json-iteration | Pass | — |
| deepswe_kcp-go-multiplexed-kcp-streams | Pass | — |
| deepswe_kombu-single-active-consumer-priority | Pass | — |
| deepswe_mobly-grouped-test-barriers | Pass | — |
| deepswe_ofetch-per-origin-circuit-breaker | Pass | — |
| deepswe_participle-grammar-conflict-analysis | Fail | Pass |
| deepswe_pwntools-tube-multiplexing | Pass | — |
| deepswe_returns-validated-error-accumulation | Pass | — |
| deepswe_sqlite-utils-safe-import-checkpoints | Pass | — |
| deepswe_testem-bail-on-test-failure | Fail | Pass |
| deepswe_tomlkit-toml-table-converters | Pass | — |
| deepswe_vitest-duration-sharding | Pass | — |
| deepswe_wazero-multi-module-snapshots | Fail | Pass |
| rf_task-69391d8d1ce51c407be1e531 | Fail | Pass |
| rf_task-69391d8d1ce51c407be1e533 | Fail | Pass |
| rf_task-694b4b99829f00e24fd11885 | Pass | — |
| rf_task-694b4b99829f00e24fd11889 | Pass | — |
| rf_task-694b4b99829f00e24fd11891 | Fail | — |
| rf_task-694b4b99829f00e24fd118a1 | Fail | Pass |
| rf_task-696719205599a51110d4b40c | Pass | — |
| rf_task-696719205599a51110d4b428 | Pass | — |
| rf_task-696719205599a51110d4b434 | Fail | — |
| rf_task-696719205599a51110d4b436 | Fail | — |
| rf_task-696719205599a51110d4b440 | Pass | — |
| rf_task-696719205599a51110d4b441 | Pass | Fail |
| rf_task-696719205599a51110d4b446 | Pass | — |
| rf_task-696719205599a51110d4b447 | Fail | Pass |
| rf_task-696719205599a51110d4b451 | Fail | Pass |
| rf_task-696719205599a51110d4b455 | Pass | — |
| rf_task-696719205599a51110d4b458 | Pass | — |
| rf_task-696719205599a51110d4b476 | Pass | — |
| rf_task-69b7c2a04b6f8ff9ed98812f | Pass | — |
| rf_task-69b7c2a04b6f8ff9ed988137 | Fail | — |
| rf_task-69b7c2a04b6f8ff9ed98813b | Fail | — |
| rf_task-69b7c2a04b6f8ff9ed98813d | Fail | Fail |
| rf_task-69d196f015a150488265afb7 | Fail | Fail |
| rf_task-69d196f015a150488265afb9 | Fail | — |
| rf_task-69d196f015a150488265afc1 | Fail | — |
| swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86 | Fail | Pass |
| swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86 | Pass | — |
| swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86 | Fail | Fail |
| swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan | Pass | — |
| swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan | Fail | Fail |
| swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f | Fail | Pass |
| swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125 | Fail | Pass |
| swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26 | Pass | — |
| swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e | Pass | — |
| swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d | Fail | Pass |
| swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12 | Pass | — |
| swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c | Fail | Pass |
| swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4 | Pass | — |
| swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb | Fail | Pass |
| swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818 | Fail | Fail |
| swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26 | Fail | Fail |
| swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288 | Fail | Pass |
| swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e | Pass | — |
| swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan | Pass | — |
| swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4 | Fail | Pass |
| swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | Fail | Pass |
| swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367 | Pass | — |
| swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171 | Pass | — |
| swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d | Fail | — |
| swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566 | Pass | — |

Current task: `none`.

Published first-attempt patches are in `../patches/`; result records are in `tasks/`.
Raw logs and feedback-assisted correction artifacts are retained locally and are not bundled.
Feedback-assisted outcomes never replace the first-attempt reward.

The complete machine-readable task list is in [summary.json](summary.json).

Known implementation limits:

- `deepswe_wazero-multi-module-snapshots`: Gzip output cannot strictly decrease through every link of an unbounded incremental chain. Valid chains remain supported; sparse increments usually compress smaller.

Evaluation notes:

- `deepswe_vitest-duration-sharding`: Identical frozen commit passed both supplied modes (8 baseline and 71 feature tests) in the original Linux image after infrastructure retries. Earlier raw build/worker failures are preserved and marked invalid.
- `rf_task-69b7c2a04b6f8ff9ed98812f`: Original complete 14 ratings reused. Frozen source patch, all 12 production files, and every supplied test/rubric input hash match exactly.
- `rf_task-69b7c2a04b6f8ff9ed98812f`: Combined resumed native commands; not a new single canonical invocation. Framework output interleaving leaves six old case names missing from the line parser, although the complete C framework summary reports 2585 passed and zero failed.
- `rf_task-69b7c2a04b6f8ff9ed98813d`: Confirmed initial public-header compilation failure; all 19 required cases (105 assertions) pass after the separate header correction.
- `rf_task-69d196f015a150488265afb7`: The separate correction passes all relevant tests without regressions. The rubric grader still fails the all-35-IE-length criterion by citing PCO byte headers, which are a separate structure; AST evidence verifies all 35 existing IE classes use ShortField(length, None). The automated reward is retained unchanged.
- `rf_task-69d196f015a150488265afc1`: gcol.innodb_virtual_stats regresses: persistent statistics for newly added indexes are missing after ALTER TABLE. Other three required cases pass.
- `rf_task-69d196f015a150488265afc1`: The sole rejected rubric is self-contradictory: its justification acknowledges that the header returns the requested enum. The original NO rating is retained without rerolling. The runtime regression independently establishes failure.
- `swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86`: Seven remaining canonical parser tests require wildcard version and an unspecified/GalaxyAPI third tuple field; the supplied instruction explicitly requires a None default version and an inferred or explicit type string. The implementation retains the instructed interface.
- `swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan`: Final correction passed 105/108 required tests. The only remaining failures invoke .instance() as a function, contrary to the required static .instance property getter.
- `swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125`: The first attempt failed to compile the private helper tests because of argument order. The correction is separate. Its verifier restores the two original YAML input fixtures omitted by the supplied test checkout, from the same original test revision; production source and test logic are not changed by that restoration.
- `swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818`: The first implementation passed 54/64 reported tests. The separate correction passes 63/64. The remaining fixture omits a real 245$b subtitle ([rasskazy, roman]) present in its input while pointing to absent 880 data; the parser preserves that metadata. No test or fixture was changed.
- `swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26`: The first implementation passes 76/85 reported tests. The separate default-allowlist correction passes 81/85. Three remaining tests expect prior honorific behavior; the specification requires removing honorifics. One expects an upload from www.covers.org outside the configured allowlist; the specification requires rejecting disallowed hosts. The requested behavior is preserved and no test was changed.
- `swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e`: A preexisting password/login test times out with JavaScript optimization disabled, leaving the password-strength setting elevated and causing cascading missing-user failures. The identical focused test on untouched production source also times out; enabling normal JavaScript optimization while keeping baseline WebAssembly passes the unchanged-base control in 1.98 seconds. Retry keeps the original frozen image-cleanup commit and unchanged tests.
- `swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan`: The original Mocha root before-all hook timed out before any test ran (zero tests/passes); npm preparation also spent 33 minutes resolving a dependency. No score API was reached. Retry uses the identical frozen commit, cached/offline npm installs and V8 --jitless.
- `swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan`: Zero tests executed: V8 --jitless disables WebAssembly, but NodeBB’s unchanged benchpress compiler requires it.
- `swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d`: The canonical verifier reports the port-changing test as missing/failing; it expects port changes, explicitly prohibited by the supplied requirements. The implementation preserves ports. All other reported test outcomes are retained. The specification also contradicts itself about first versus last numeric selection; established last-number behavior is preserved.
