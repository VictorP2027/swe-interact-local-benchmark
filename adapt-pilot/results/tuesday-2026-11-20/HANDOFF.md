# Tuesday harness validation and smoke test

This is the shared single-turn SWE-Interact setup for stock Codex versus ADAPT.
Both arms receive the full task specification plus the same Linux execution instructions.
The fixed task-order seed is 224. Model temperature and sampling seed are not exposed.
A literal `continue` resumes a clarification question, within the original one-hour budget.

## Verifier controls

The control patches are only used to validate grading and never enter the coding containers.

| Task | Control | Expected reward | Actual reward | Passed |
| --- | --- | ---: | ---: | --- |
| deepswe_returns-validated-error-accumulation | known-good | 1 | 1 | True |
| deepswe_returns-validated-error-accumulation | untouched | 0 | 0 | True |
| deepswe_vitest-duration-sharding | known-good | 1 | 1 | True |
| deepswe_vitest-duration-sharding | untouched | 0 | 0 | True |

## Saved runs

| Arm | Status | Reward | Agent seconds | Linux calls | Effective settings |
| --- | --- | ---: | ---: | ---: | --- |
| adapt | scored | 0.0 | 107.631 | 10 | True |
| stock | scored | 0.0 | 161.497 | 17 | True |

Matched setup audit: `deepswe_returns-validated-error-accumulation` — **True**.

## Earlier smoke attempt

The first stock Kombu smoke patch stalled in an existing filesystem-consumer test. It was interrupted and saved as unscored. Its untouched/known-good verifier controls passed. That run exposed missing container cleanup on interrupted verification; the final harness fixes it. The complete earlier configuration and result are included below as a separate experiment.

## Harness checks

Harness regression checks: 11 passed. A separate forced-timeout test in real Docker confirmed that the verifier container was removed. The benchmark coding budget remains 3,600 seconds; the benchmark verifier limit remains upstream's 1,800 seconds.

## Findings and next steps

- Tuesday checklist: shared harness pinned; full single-turn specs and Linux project tools matched; effective context, output cap, compaction defaults and budgets audited; untouched and known-good controls validated for Returns and the planned Vitest audit task.
- Stock Returns: 61 baseline tests and 20 subtests passed. The feature suite stopped after 17 passes because Valid(5).lash(recover) returned None rather than Valid(5).
- ADAPT Returns: the baseline passed, but the first feature test failed because apply reversed the function/value direction and attempted to call an integer.
- Both coding sessions completed normally, used the shared Linux terminal and passed all effective-setting checks. Both frozen patches received reward 0. This is one selected smoke pair, not an accuracy estimate.
- The initial stock Kombu smoke patch stalled in test_FilesystemTransport::test_produce_consume. It was manually interrupted, retained as unscored and used to identify missing verifier-container cleanup. No hidden grading feedback was supplied to either coding actor.
- Next: Victor P. should check out this shared harness and run the same Returns smoke pair on his machine. Run the planned paired Vitest case next, inspect its traces and implementations, then split the remaining task pairs across machines. The Tuesday work does not include those distributed runs or the full manual context-retention analysis.
- The currently cached Vitest image is ready for that paired audit. One older unfinished Atlas image was preserved under cs224v-pilot-preserved so its historical frozen patch remains gradeable. Raw workspaces, traces, credentials and the private ADAPT release stay local.

## Architecture and limits

- Pinned macOS ADAPT binary, both arms
- Separate Linux containers from the same upstream image ID
- Shared task_terminal MCP tool; hidden tests and credentials are not mounted
- Fresh Linux container from the coding image; frozen patch and upstream tests
- Follow upstream task allow_internet setting for both coding and grading
- Pinned Codex default: 43,200-token automatic threshold for 48K context; 45,600 usable input tokens. No override.
- The supplied release has no Linux binary, so the controller remains on macOS.
- Data-structure pytest validation is skipped by this release on macOS.
- The native host shell still exists; the shared prompt requires all project work through the Linux tool.
- Compaction defaults are derived from the exact Codex source commit named in the release license; actual context pressure still requires trace review.
- The smoke task was selected using a previously passing patch and is not an unbiased accuracy estimate.
- Old macOS coding pilot results are a separate experiment.

Compaction calculation: [pinned Codex source](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535).

## Complete configuration and result records

```json
{
  "format": "cs224v-tuesday-handoff-v1",
  "exported": "2026-11-20T16:18:40+00:00",
  "exporter_sha256": "62b699b7e24aef753a49cc43f254240d3186628516e0613c75ecb82746d8ddd1",
  "harness_commit": "1243f28847fc9b7f5a590c915f6ae367b314fd15",
  "manifest": {
    "arms": {
      "adapt": "codex",
      "stock": "codex-shipped"
    },
    "configuration": {
      "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
      "catalog_share": 0.1,
      "codex_version": "0.159.0",
      "context_window": 48000,
      "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
      "environment_mode": "linux-terminal",
      "first_task": "deepswe_fastapi-deprecation-response-headers",
      "image_overrides": {},
      "image_source": "upstream-prebuilt",
      "lane": "subscription",
      "max_continuations": 8,
      "model": "gpt-6-luna",
      "model_seed": null,
      "platform": "linux/amd64",
      "protocol": "singleturn-with-conditional-continue",
      "reasoning_effort": "medium",
      "require_verifier_validation": true,
      "rubric_bridge_sha256": "1ce49aa69da1fbd6ae69b057f1d5ba2853be96c01adb151af6bfaffab9e64b36",
      "rubric_model": "gpt-6-luna",
      "rubric_reasoning_effort": "medium",
      "rubric_transport": "local-codex-cli",
      "task_order_seed": 224,
      "temperature": null,
      "tool_output_limit": 10000,
      "trial_wall_clock_s": 3600,
      "verifier_pytest_addopts": {
        "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
      }
    },
    "harness_sources": {
      "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
      "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
      "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
    },
    "model_catalog_sha256": "a5e25107506f0934cb62144c093c72bf8c7fa5de1436f4aa02fe54769d789618",
    "runner_sha256": "96fb6d40ce455c428280639ca82e426f3f6a34454acd55bc30f360e516464373",
    "task_order": [
      "deepswe_fastapi-deprecation-response-headers",
      "deepswe_kombu-single-active-consumer-priority",
      "deepswe_awilix-async-container-initialization",
      "rf_task-69b7c2a04b6f8ff9ed98813b",
      "swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d",
      "rf_task-69d196f015a150488265afb7",
      "deepswe_wazero-multi-module-snapshots",
      "deepswe_cattrs-partial-structuring-recovery",
      "swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367",
      "rf_task-69b7c2a04b6f8ff9ed988137",
      "swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26",
      "rf_task-69b7c2a04b6f8ff9ed98812f",
      "rf_task-696719205599a51110d4b436",
      "rf_task-694b4b99829f00e24fd11891",
      "deepswe_tomlkit-toml-table-converters",
      "rf_task-696719205599a51110d4b458",
      "deepswe_sqlite-utils-safe-import-checkpoints",
      "deepswe_etree-xml-diff-patch",
      "swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan",
      "deepswe_arcane-drift-detection-baselines",
      "deepswe_testem-bail-on-test-failure",
      "rf_task-696719205599a51110d4b428",
      "deepswe_httpx-streaming-json-iteration",
      "rf_task-694b4b99829f00e24fd11889",
      "rf_task-696719205599a51110d4b40c",
      "swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c",
      "rf_task-696719205599a51110d4b451",
      "swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e",
      "deepswe_mobly-grouped-test-barriers",
      "swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86",
      "rf_task-696719205599a51110d4b447",
      "deepswe_bandit-structured-nosec-directives",
      "deepswe_pwntools-tube-multiplexing",
      "swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818",
      "swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171",
      "rf_task-696719205599a51110d4b441",
      "rf_task-696719205599a51110d4b446",
      "swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26",
      "deepswe_clack-async-autocomplete-options",
      "rf_task-69d196f015a150488265afb9",
      "rf_task-696719205599a51110d4b434",
      "rf_task-696719205599a51110d4b455",
      "swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86",
      "swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4",
      "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e",
      "deepswe_httpx-deterministic-cookie-store",
      "swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171",
      "rf_task-69b7c2a04b6f8ff9ed98813d",
      "deepswe_returns-validated-error-accumulation",
      "rf_task-69391d8d1ce51c407be1e533",
      "swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d",
      "swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb",
      "rf_task-69d196f015a150488265afc1",
      "swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125",
      "swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan",
      "deepswe_vitest-duration-sharding",
      "rf_task-694b4b99829f00e24fd11885",
      "swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86",
      "swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan",
      "swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566",
      "deepswe_drizzle-orm-window-function-builders",
      "deepswe_ofetch-per-origin-circuit-breaker",
      "rf_task-696719205599a51110d4b440",
      "swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288",
      "rf_task-696719205599a51110d4b476",
      "deepswe_boa-hierarchical-evaluation-cancellation",
      "deepswe_participle-grammar-conflict-analysis",
      "swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f",
      "deepswe_kcp-go-multiplexed-kcp-streams",
      "rf_task-694b4b99829f00e24fd118a1",
      "swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4",
      "deepswe_helm-array-merge-strategies",
      "swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12",
      "rf_task-69391d8d1ce51c407be1e531",
      "deepswe_fastapi-implicit-head-options"
    ],
    "tasks": {
      "deepswe_arcane-drift-detection-baselines": {
        "definition_sha256": {
          "multiturn": "e98a4380f4decbd07a68005aaa49cfb2533a28d4e4f6305c229ad8ec45b6bb47",
          "singleturn": "0dd4d16d85d68926aec874005f1f2108486a3010ea10a8cca3e2858d52760b30"
        },
        "family": "DeepSWE"
      },
      "deepswe_awilix-async-container-initialization": {
        "definition_sha256": {
          "multiturn": "a8ab7fb385b490e4be5b681987b7b5d72f7e4dc8f06363288e6cc1b305be1d62",
          "singleturn": "28db387fe7e67ac634126ed9d453647315e50cbd0b5f109a25e7da63a4a8aec2"
        },
        "family": "DeepSWE"
      },
      "deepswe_bandit-structured-nosec-directives": {
        "definition_sha256": {
          "multiturn": "07559c20cdfe90e4e86620f7897e1c49e1baceba4472eb65af056cb93575d71d",
          "singleturn": "b8d25d646139c9881f6dc326852df5c8ba3cf1f390f487c4132347b0b9dd4ee3"
        },
        "family": "DeepSWE"
      },
      "deepswe_boa-hierarchical-evaluation-cancellation": {
        "definition_sha256": {
          "multiturn": "3c63e77f3fdf712ee3b547f9f30b10d7ab7dc56cc53932c19bcf6329dd6ecff9",
          "singleturn": "f67447f82a04fd9ad1e3e6c330f68ec89b9deb98084f4650cfbe89cff7533068"
        },
        "family": "DeepSWE"
      },
      "deepswe_cattrs-partial-structuring-recovery": {
        "definition_sha256": {
          "multiturn": "e7982202cf7ae92fef1efef3cc48bce6c7bbcd79f86a699327b63779aa54b4cf",
          "singleturn": "399472bc4f4ae276c5c415227bccf22bdfd11b85225bb6be4cabb1b6dfc75410"
        },
        "family": "DeepSWE"
      },
      "deepswe_clack-async-autocomplete-options": {
        "definition_sha256": {
          "multiturn": "92ae989e0832d4c942c105fa33c8e3a4d19fcec2b84501f7b23de0db35b1ef0a",
          "singleturn": "3027742d60971bbc24caea4bfc424763b71cfccdf18614a019668c9d7a2524bc"
        },
        "family": "DeepSWE"
      },
      "deepswe_drizzle-orm-window-function-builders": {
        "definition_sha256": {
          "multiturn": "7423e124245a1707bff0f8b0a0d02c14a184656b52f4e9c2e22dc024f0c4b154",
          "singleturn": "4387441bb3a9635f85bc2921ebac8ad910d0a8bc36c5ef61f2c9b5ba7c467d6c"
        },
        "family": "DeepSWE"
      },
      "deepswe_etree-xml-diff-patch": {
        "definition_sha256": {
          "multiturn": "f156812a76bc081cedd94aa5fbe2408d02e0c7fee3b4a7f899d94c3dd7dc5c2d",
          "singleturn": "51f1c00e93cb1926e7b7d5863bd76a5bade6b65eff87da8988abfe968d1a9690"
        },
        "family": "DeepSWE"
      },
      "deepswe_fastapi-deprecation-response-headers": {
        "definition_sha256": {
          "multiturn": "9b39b52d85448808a447b0dc742707e40aa5ebdb56910294d9243656ce7dd292",
          "singleturn": "9b1be50e6fc5c9c80d68556c4a65f781c143b456cdb70e13ff9c068f3d61c652"
        },
        "family": "DeepSWE"
      },
      "deepswe_fastapi-implicit-head-options": {
        "definition_sha256": {
          "multiturn": "0016ca26b455fc38fbb49d928c3bd10a69bf7b97e9ce9416aa344f00a0e5a64c",
          "singleturn": "34a65c36fb919724ab9f0e7d6e91fa9a64588f1db215015673923da7828a8167"
        },
        "family": "DeepSWE"
      },
      "deepswe_helm-array-merge-strategies": {
        "definition_sha256": {
          "multiturn": "6bab0e45b366d3ec60fb9ae3214b3db069983bfa3f7a050e0659649ae8480d38",
          "singleturn": "63ccf5d6d3818bea88c088b286ea55edc89c9178e6958b6216baca3dca791356"
        },
        "family": "DeepSWE"
      },
      "deepswe_httpx-deterministic-cookie-store": {
        "definition_sha256": {
          "multiturn": "6ec038c72fe718aec699a04c89a938085dcb1d3217dba0d3a05c630529c1e7ae",
          "singleturn": "58d610b3ffefea9e7d8d90764ed8284e0ee2c34ceb7545c7ff1f45aca8be9c5a"
        },
        "family": "DeepSWE"
      },
      "deepswe_httpx-streaming-json-iteration": {
        "definition_sha256": {
          "multiturn": "8992bfbfc1cda4c03bebe3d9086f993dcab7681d03a1ddd1bc02249aed4d8594",
          "singleturn": "142be505eb4bdf811fca2c642f2ca85a1fbcafeeb55b8ff08cafee5207fe51f3"
        },
        "family": "DeepSWE"
      },
      "deepswe_kcp-go-multiplexed-kcp-streams": {
        "definition_sha256": {
          "multiturn": "2c94fa7120b35f9f80644cb52cdeca3c794e7fec191d0ca7061a81149972f68c",
          "singleturn": "51d7c77f3ec12e1a6acf484b56014dc0c2931c2a65f7b995f8f678a337daffb7"
        },
        "family": "DeepSWE"
      },
      "deepswe_kombu-single-active-consumer-priority": {
        "definition_sha256": {
          "multiturn": "c69587c7b134861f8c9ffe450f5a680d0073d6e5633f628ef62de73c1c5ad2de",
          "singleturn": "9adb5dba1f5781be2a376d0282d96b40a098fa07134e93d34261d266fcf446e5"
        },
        "family": "DeepSWE"
      },
      "deepswe_mobly-grouped-test-barriers": {
        "definition_sha256": {
          "multiturn": "feaa44254f26e5a25a6cce2d6051a680947f56cd8c2b339565f467e3e8128247",
          "singleturn": "f543dab0c5c77ac45b0135d4d430c76f34c2482747af8bbdc4b774b8f4d5d111"
        },
        "family": "DeepSWE"
      },
      "deepswe_ofetch-per-origin-circuit-breaker": {
        "definition_sha256": {
          "multiturn": "949d73413dd9a9b32850dffc946b9449b18c876c4badf1a96512ba6dce00c173",
          "singleturn": "01cf71ecfc57dbbf91b489d336701fb7ce65b365cdcbd457c963adc77ee50ddd"
        },
        "family": "DeepSWE"
      },
      "deepswe_participle-grammar-conflict-analysis": {
        "definition_sha256": {
          "multiturn": "a4d700f59eadab1d22d85f9a5f2df8eee89f4669c5b450cf7931ed6608f82c4a",
          "singleturn": "d59e4277344a8794923806c2f6656d1f167204b40608496d59bbee8ad8c049e9"
        },
        "family": "DeepSWE"
      },
      "deepswe_pwntools-tube-multiplexing": {
        "definition_sha256": {
          "multiturn": "bdb3c018b6577e6faa3aae0cbe155f354f684054e47c1bb61fcd9ed0b3c1082a",
          "singleturn": "7da1943dd50ff31b2498d3b76546cfb0909051b0fdf4db22d8a7c833ff4aa79b"
        },
        "family": "DeepSWE"
      },
      "deepswe_returns-validated-error-accumulation": {
        "definition_sha256": {
          "multiturn": "fae26435c7573a5a124b9c5e3c3cd0e0f9088918437bdf9302ff8307d27076c2",
          "singleturn": "f419e38330363c79ef93a6ac96712de151b61e59f8563d91b4964545347bc318"
        },
        "family": "DeepSWE"
      },
      "deepswe_sqlite-utils-safe-import-checkpoints": {
        "definition_sha256": {
          "multiturn": "f33b9540ace6a9c58943efed5b724ffec4f88360664acfa070abaa19748df083",
          "singleturn": "29f81b5cd9477ce5597738fffef36bdce3c686a06686ac899824b6c9c89d3104"
        },
        "family": "DeepSWE"
      },
      "deepswe_testem-bail-on-test-failure": {
        "definition_sha256": {
          "multiturn": "edfabf0859035d40c7abc4062ddc455e47a7399ef4032a5cb41f86a672a060bb",
          "singleturn": "011e5dc7ad975c6b756af4f899297a5fe655d9511509494ea5ae355974db3605"
        },
        "family": "DeepSWE"
      },
      "deepswe_tomlkit-toml-table-converters": {
        "definition_sha256": {
          "multiturn": "4af1a89e1a2f0bc3f15ee5772e1a0ff98dd7ebd575cfb8008750eb62b079b07f",
          "singleturn": "6d100e2bd44741340e2107d29a90b834bc6788083f369697ce89dfc6b4be86af"
        },
        "family": "DeepSWE"
      },
      "deepswe_vitest-duration-sharding": {
        "definition_sha256": {
          "multiturn": "5a763a854fc4de57334d1c4f6bec67c5251f4b9d99b677e5885ce6bc4d9f69ac",
          "singleturn": "540b6b7c1bfeb1ab62772740a5a79abf37105c2a6146cd40a39d1c31f8920fb2"
        },
        "family": "DeepSWE"
      },
      "deepswe_wazero-multi-module-snapshots": {
        "definition_sha256": {
          "multiturn": "ed9b13500af126a369d18a634b44180c00c5f36663b1810351acb10d783b7893",
          "singleturn": "b0c66b4dffb612ed3d79c20c391684807b6dd74446698721a368f347a44de155"
        },
        "family": "DeepSWE"
      },
      "rf_task-69391d8d1ce51c407be1e531": {
        "definition_sha256": {
          "multiturn": "f977d33266976cfaa7322b5f3045cc0afe89a804a57536677ee88c482ffe3ef5",
          "singleturn": "cb780e1f086fabd30de7bec6d0f84ccc84f88b2710ebc449259fa776f5f22825"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69391d8d1ce51c407be1e533": {
        "definition_sha256": {
          "multiturn": "9150daedd87e825ec00ab49e3c160700e162e200a158ae4f5a9990b5d756fa50",
          "singleturn": "34a3f62a91ed354374439c4650754e27fad9a474b2f0932645cf67d66082f61e"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-694b4b99829f00e24fd11885": {
        "definition_sha256": {
          "multiturn": "713a9019147dc8bf43a532b31f022fd755ee210fc831482860ac6f7b506f1aeb",
          "singleturn": "847def97d9034cce23562c64aca2dee9f17659955be69381b697c70c7c0848dc"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-694b4b99829f00e24fd11889": {
        "definition_sha256": {
          "multiturn": "370d0b9e069dc27e78df7f985f274bd7bd86fca7fa513cd5078c17de2b0b05a9",
          "singleturn": "c25f1462c109f813a5d125ea95b46f11bfe87eec4a975e630187b7309ba9482a"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-694b4b99829f00e24fd11891": {
        "definition_sha256": {
          "multiturn": "28c8b24cdd0907a42d0cb8b24a4f32b70d9574301904b11df9ca44fc7bbb680b",
          "singleturn": "18c8633391e47a46e9f329226981dd31be491b4a59e2557abe0ff7c0a8caf8b1"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-694b4b99829f00e24fd118a1": {
        "definition_sha256": {
          "multiturn": "a6c300d10ebe9fe02d786833ec9fc83b3796347024ff18b708cea7935a48a479",
          "singleturn": "6dfabf6b1606c2e277643a192e51435d465ad1b95cd209c4e1e2fa29a360dd74"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b40c": {
        "definition_sha256": {
          "multiturn": "13c9c4e64cfb499ca396283c42a326790eb945ada366867493f383165d05d76b",
          "singleturn": "32db68230cb9fe379daa2125bc1ff39b580a224ef2b3be664c96a863f9a5608c"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b428": {
        "definition_sha256": {
          "multiturn": "9477cd432fa524e145e8238544059450efc421787660d0b3a1e502a26b6a92b0",
          "singleturn": "66dd0ccc3c4f63225612e03055e8a5b58dd5b85a762435130494eb52d776e4e4"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b434": {
        "definition_sha256": {
          "multiturn": "626c9145869413d36114d48e814a79146d6846e904e16c77a949e8f36be18190",
          "singleturn": "e41cb6fcc03614dddc1f6c7c5d7a090cdf2958a02276f104c0dd80641b07e3dd"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b436": {
        "definition_sha256": {
          "multiturn": "10fc8eb923d1d398e9f08dd3192de6bd9b553fe19eea419e72a2b09cbff782d2",
          "singleturn": "98f71d6bfa71fcd0b221f663b76a225d0f7d7168aaac372f30a0018d74befd17"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b440": {
        "definition_sha256": {
          "multiturn": "9faa8634f39664357a8bdef97ea6a3bef95f6ee936fdcd0413c1364eb42862b8",
          "singleturn": "d1f184a8ec4d60fc0412fbba6c107ac27f0ddc6a1acf055bac8f0293b3fd4213"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b441": {
        "definition_sha256": {
          "multiturn": "601acf3ab12e265eba973aaf4b02076b52677e1684875942c7e1363545fbe9e6",
          "singleturn": "5b3143da6ada52e44f18d704eb2ea27028fe2d92f0db533040299eaff4027c79"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b446": {
        "definition_sha256": {
          "multiturn": "09f29da1976a791cbef0fe7c2e8600cdbcdcf9a3554ede0630e0479bbb031b0d",
          "singleturn": "458463c4b93b8f95fe1d890daec1e4f0422383391187e966d68d22e9ba525d18"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b447": {
        "definition_sha256": {
          "multiturn": "d817f20627fa0033a56db5f838fb8a2c129dc6bbb270e050395aa0e2034c266e",
          "singleturn": "6c1af11acb07a147fa82d2de06489e068a945cf27b5328185145007defb7a533"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b451": {
        "definition_sha256": {
          "multiturn": "50eee5c5a7de328e1ff0ed34c9fcb943a7675b20abea838aca317f07266ac603",
          "singleturn": "ae5e50307e81f9329fb01bd9f652a6cc4b6e8c0cdea580c3a1d1252cac796613"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b455": {
        "definition_sha256": {
          "multiturn": "5fc2d7fa81e8b4538d4bbc14dbec4ff9c7f8f10aafac5923ed34206966047c25",
          "singleturn": "a7f43901affee4cb7b53d507d35f385d5eebf5fb6bde6667ffa732d3dee5b56f"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b458": {
        "definition_sha256": {
          "multiturn": "b13790800d7d854d3327cb48ec1cc447020d52fb9984677642629406c4422610",
          "singleturn": "4ec9be2a77e9ea9bd4b13b5d7bf3638cf57a4da45596acef2aac45e5193df1b3"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-696719205599a51110d4b476": {
        "definition_sha256": {
          "multiturn": "1b267945741d7501a939f7881f68373f19d740090a1371104230deb75e12e221",
          "singleturn": "f3d9eadd355ec1d059cacde1c839c830a03bef4a13a00e975e16bdb4c85e7d67"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69b7c2a04b6f8ff9ed98812f": {
        "definition_sha256": {
          "multiturn": "34ea8c9879852d09e01d5f87b9e90101657c5df79f25cff817bb7a33c0196e0f",
          "singleturn": "3e5e01cfab550c2d15c5f868f338f5aae3986af680fa96d2b33b63b958932287"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69b7c2a04b6f8ff9ed988137": {
        "definition_sha256": {
          "multiturn": "51679b1b035103f803d1031e70a4583db46d9ac46df3e8fcb07621c71194841a",
          "singleturn": "65f1d0a32ef9d9685bf73a1581fcfbc07c6232bfec911e384e22912f5ba1e69c"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69b7c2a04b6f8ff9ed98813b": {
        "definition_sha256": {
          "multiturn": "08df2026ab68e5cfdf710c3abd4ce60722a98356f06433d52cb8e3d353997e86",
          "singleturn": "3210d2b568dd858493ccb1cf8fa7622fc910fcb9bba35af540d88c3e60cf66c7"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69b7c2a04b6f8ff9ed98813d": {
        "definition_sha256": {
          "multiturn": "02c613eac2cff202da19a606cedcb188d1b014be8f6ccb586e630833076cd5b5",
          "singleturn": "9287ddacdd70ee05dd11b0949a8673c6b3640070f84b1aa408c457329540bad7"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69d196f015a150488265afb7": {
        "definition_sha256": {
          "multiturn": "d0fdd057584afa6e3272601f4091fb9333c3bf3f81f07c0ddb608b3ac097c063",
          "singleturn": "97892c66d1fbddce6cd5e016c3f6477fabe1ceb4de9a420b626e6709fc165f8c"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69d196f015a150488265afb9": {
        "definition_sha256": {
          "multiturn": "76bc4aeb9a2cfb6f7a1e97a6a46084fbac0065a21ffb90fa3b999b38f1d60442",
          "singleturn": "52067daf8a458ba11f4db6038c4434019ef97a8f2930966718539f1d9071a06f"
        },
        "family": "SWE Atlas Refactoring"
      },
      "rf_task-69d196f015a150488265afc1": {
        "definition_sha256": {
          "multiturn": "8f4a66333360bc1455b3cd0fbd1f2a0dcb5d6caa551c05939b972ee1dc314bad",
          "singleturn": "5caa65d11f6158c4741cdadc0c210908bf24deceb758fbb110e907dbecde33e9"
        },
        "family": "SWE Atlas Refactoring"
      },
      "swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86": {
        "definition_sha256": {
          "multiturn": "f15d3c13c16ef21af14499d030966c56beaaa31dc87600511ee4f75ec8263d6f",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86": {
        "definition_sha256": {
          "multiturn": "b1c08613862e3161774791dd557be7ce72ddc9b7f769989d96bb5efb70d0423c",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86": {
        "definition_sha256": {
          "multiturn": "e1a90767d49eb5b1f3c26564d00d0453796afbde2c2449ed0579b866cb03fb46",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan": {
        "definition_sha256": {
          "multiturn": "4d7819a1fcb802c0460221f86a79f06f32e0e0c84b12ba6d8c1e596fe5cdcc60",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan": {
        "definition_sha256": {
          "multiturn": "0edcd9fa1092249e60eb9dd6e05183b031bbf90dcc8d48c052b2b2322fd75c85",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f": {
        "definition_sha256": {
          "multiturn": "c1e430450d5f9c6d6d1fe8a0a86074327f742f4ece9afceae60564b3183a4107",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125": {
        "definition_sha256": {
          "multiturn": "c93e5ac1b00cf5faf90912e4348093888a5159b669901bab2a6c041f086f5a99",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26": {
        "definition_sha256": {
          "multiturn": "8c5a7d3e0fc005736468a853779130a5e6f0abc998e32ecd46fe726af111bf84",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e": {
        "definition_sha256": {
          "multiturn": "408b57b283efccd29c561e4224efb9f3f221d15f73f5ce9c1d9a52f706f146f1",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d": {
        "definition_sha256": {
          "multiturn": "66216a566db830f9619e66c1ff8c8fec5c1ea50701f093f09699306ec43c534e",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12": {
        "definition_sha256": {
          "multiturn": "80da11658b27be58a7642c35168dbf4f358fa2ff97a209c621a929f9de2e0c76",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c": {
        "definition_sha256": {
          "multiturn": "f8096a4fac83e9af7f4b5a43adba3c91a323a010ffb2eae1fdb5b11208c25561",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4": {
        "definition_sha256": {
          "multiturn": "548c8a0f30387b74e4da594b4cf507572362fe117aa4c14ab4cff6d7e9c03709",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb": {
        "definition_sha256": {
          "multiturn": "363b9a5bfef65c9bc2e430da3e46f189d9158ac0176347573d035e206da11fbf",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818": {
        "definition_sha256": {
          "multiturn": "a38e573e2390f79c622416633116174905404c50249d98d31820db54c9e1f295",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26": {
        "definition_sha256": {
          "multiturn": "4477446d1e1d6294f0a6c3128136635e6befadab74daeb1ad7772b35a4b72b55",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288": {
        "definition_sha256": {
          "multiturn": "346bd4c67ae9206932b304356e010a47647f01928879509fc84f1935c01cdb0c",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e": {
        "definition_sha256": {
          "multiturn": "90c6087e871d66a7c67484a8520dd7a288ea728ae86a1f98fae6e7dcb3f961ca",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan": {
        "definition_sha256": {
          "multiturn": "7ec7ba6394c09daf292dd7888f3ec35c22c1500efbe2e6d589e9a4d2a19d07f4",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4": {
        "definition_sha256": {
          "multiturn": "a3abb6ebfe113f7756950ab37f6122fbd5d7f12195bf938dc5a52b8edd39f056",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171": {
        "definition_sha256": {
          "multiturn": "cf9eaa496400f3fcac9de93a1de66870ac6ae5ea260c1aed4bcedbc3452baa73",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367": {
        "definition_sha256": {
          "multiturn": "b601e4fec849a218510c0ca16b95a3e8312c691c23ff147fb7ba464e9a778d50",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171": {
        "definition_sha256": {
          "multiturn": "73fac0daccfbd6915d7b9ea9276ba4516ee90ab38d9668defc6a790b1ccdc0e2",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d": {
        "definition_sha256": {
          "multiturn": "cb10bf531b17363142009544fd25f7215eff4c31ae9be615575755f1782fe38d",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      },
      "swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566": {
        "definition_sha256": {
          "multiturn": "9086258c4b20da32fe7d84c8b9f86f7e02847bd63e6c4c28db5b6c7eb87b3027",
          "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
        },
        "family": "SWE-bench Pro"
      }
    }
  },
  "verifier_validations": [
    {
      "base_commit": "41607fae1289de2787523c452d75212206b9c7c0",
      "configuration": {
        "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
        "catalog_share": 0.1,
        "codex_version": "0.159.0",
        "context_window": 48000,
        "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
        "environment_mode": "linux-terminal",
        "first_task": "deepswe_fastapi-deprecation-response-headers",
        "image_overrides": {},
        "image_source": "upstream-prebuilt",
        "lane": "subscription",
        "max_continuations": 8,
        "model": "gpt-6-luna",
        "model_seed": null,
        "platform": "linux/amd64",
        "protocol": "singleturn-with-conditional-continue",
        "reasoning_effort": "medium",
        "require_verifier_validation": true,
        "rubric_bridge_sha256": "1ce49aa69da1fbd6ae69b057f1d5ba2853be96c01adb151af6bfaffab9e64b36",
        "rubric_model": "gpt-6-luna",
        "rubric_reasoning_effort": "medium",
        "rubric_transport": "local-codex-cli",
        "task_order_seed": 224,
        "temperature": null,
        "tool_output_limit": 10000,
        "trial_wall_clock_s": 3600,
        "verifier_pytest_addopts": {
          "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
        }
      },
      "controls": {
        "known-good": {
          "exit_code": 0,
          "expected": 1.0,
          "passed": true,
          "patch_sha256": "a8f5455e5869497e2e2e342bd28b7ba6c38efdec5ca2d5728161a7d73e778909",
          "reward": 1.0
        },
        "untouched": {
          "exit_code": 0,
          "expected": 0.0,
          "passed": true,
          "patch_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "reward": 0.0
        }
      },
      "finished": "2026-11-20T16:05:06+00:00",
      "image_id": "sha256:2b7933a7c57daa5532fd1d097dc4a97694047076ac4a213334025bbaec08e34b",
      "passed": true,
      "source_sha256": {
        "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
        "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
        "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
      },
      "started": "2026-11-20T16:04:53+00:00",
      "task": "deepswe_returns-validated-error-accumulation",
      "tests_sha256": {
        "tests/test.patch": "d4f92adfa57f16c3a05b6990022f4e9cd75979ef63e8f9ee10eb63fe313847d3",
        "tests/test.sh": "2b154992f156f78b6feb653a743d6e2989dce808f0f7af8db0c501d8ef0b37a2"
      }
    },
    {
      "base_commit": "647e6ade3b99523e3a0387a65fccfe918c331236",
      "configuration": {
        "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
        "catalog_share": 0.1,
        "codex_version": "0.159.0",
        "context_window": 48000,
        "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
        "environment_mode": "linux-terminal",
        "first_task": "deepswe_fastapi-deprecation-response-headers",
        "image_overrides": {},
        "image_source": "upstream-prebuilt",
        "lane": "subscription",
        "max_continuations": 8,
        "model": "gpt-6-luna",
        "model_seed": null,
        "platform": "linux/amd64",
        "protocol": "singleturn-with-conditional-continue",
        "reasoning_effort": "medium",
        "require_verifier_validation": true,
        "rubric_bridge_sha256": "1ce49aa69da1fbd6ae69b057f1d5ba2853be96c01adb151af6bfaffab9e64b36",
        "rubric_model": "gpt-6-luna",
        "rubric_reasoning_effort": "medium",
        "rubric_transport": "local-codex-cli",
        "task_order_seed": 224,
        "temperature": null,
        "tool_output_limit": 10000,
        "trial_wall_clock_s": 3600,
        "verifier_pytest_addopts": {
          "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
        }
      },
      "controls": {
        "known-good": {
          "exit_code": 0,
          "expected": 1.0,
          "passed": true,
          "patch_sha256": "c68cb8d4cee97c4c4a48f28fae04c42d1dece9ff8da3d470bfc5f1342a26d911",
          "reward": 1.0
        },
        "untouched": {
          "exit_code": 0,
          "expected": 0.0,
          "passed": true,
          "patch_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "reward": 0.0
        }
      },
      "finished": "2026-11-20T16:17:13+00:00",
      "image_id": "sha256:7ea5066862dcde784cb49ba556e5989a3b48bbc82c99a492987e71a664d18d8b",
      "passed": true,
      "source_sha256": {
        "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
        "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
        "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
      },
      "started": "2026-11-20T16:10:49+00:00",
      "task": "deepswe_vitest-duration-sharding",
      "tests_sha256": {
        "tests/test.patch": "96479d5febcfa6d74499fe5da3abc8c6e861f557f26237acf8b51fe4fc8fc406",
        "tests/test.sh": "f8664ff5d27cf134a5cb900307c66a9d2dca4292cf78d83630396e1ed7699af4"
      }
    }
  ],
  "paired_checks": [
    {
      "task": "deepswe_returns-validated-error-accumulation",
      "checks": {
        "image_id": true,
        "upstream_base": true,
        "prompt_sha256": true,
        "actor_prompt_sha256": true,
        "agent_settings": true,
        "runner_source_sha256": true,
        "both_scored": true,
        "effective_settings": true
      },
      "passed": true
    }
  ],
  "attempts": [
    {
      "actor_prompt_sha256": "07bf5962a2f22433ad6ef85466507216bae074558a5dc52a250d00fbdf255bd6",
      "agent_exit": "completed",
      "agent_settings": {
        "context_window": 48000,
        "lane": "subscription",
        "model": "gpt-6-luna",
        "reasoning_effort": "medium"
      },
      "agent_usage": {
        "cached_input_tokens": 336384,
        "completed_turns": 1,
        "input_tokens": 372798,
        "output_tokens": 4443,
        "reasoning_output_tokens": 928,
        "total_tokens": 377241
      },
      "arm": "adapt",
      "artifact_path": "attempts/deepswe_returns-validated-error-accumulation/adapt/0001",
      "attempt": "0001",
      "continuation_limit_reached": false,
      "continuations": 0,
      "cycle_images": true,
      "effective_settings": {
        "auto_compaction": "Pinned Codex default; no threshold override. Exact trigger is not exposed by the bundle.",
        "catalog_share": 0.1,
        "checks": {
          "budget": true,
          "catalog_share": true,
          "compaction_default": true,
          "context": true,
          "effort": true,
          "model": true,
          "release": true,
          "tool_cap": true,
          "version": true
        },
        "config_sha256": "9b9cbd42eb22dada057ef70ee850887587909d692344f43a09672d85654e87f5",
        "context_window": 48000,
        "mcp_servers": [
          "task_terminal"
        ],
        "model_catalog_sha256": "0874a59f0bca5de9d343ddd140dabe22ba7b94f98d386f2f76136df3ff14d647",
        "passed": true,
        "tool_output_limit": {
          "limit": 10000,
          "mode": "tokens"
        }
      },
      "family": "DeepSWE",
      "image_id": "sha256:2b7933a7c57daa5532fd1d097dc4a97694047076ac4a213334025bbaec08e34b",
      "patch_sha256": "77ad4ddfd7e999cc23c7df907915b25ba6468876b4ec5cabd086648a37549b80",
      "prompt_sha256": "4a1ff83df1e3502f3e15fab4647cc4a607f4affc51db970b5ac1f45359b20f0d",
      "repository_path": "/app",
      "reward": 0.0,
      "run_path": "attempts/deepswe_returns-validated-error-accumulation/adapt/0001/runs/deepswe_returns-validated-error-accumulation-20261120T160806-5e7f",
      "runner_source_sha256": {
        "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
        "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
        "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
      },
      "started": "2026-11-20T16:08:05+00:00",
      "status": "scored",
      "task": "deepswe_returns-validated-error-accumulation",
      "trace": {
        "calls": 29,
        "steps": 16,
        "user_messages": 1
      },
      "updated": "2026-11-20T16:09:59+00:00",
      "upstream_base": "41607fae1289de2787523c452d75212206b9c7c0",
      "verifier_exit_code": 0,
      "compaction_source_audit": {
        "codex_commit": "687a119f0fcaace47e1f1abcc77cec6c813fd6da",
        "default_auto_compact_token_limit": 43200,
        "usable_input_context": 45600,
        "source": "https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535"
      },
      "agent_seconds": 107.631,
      "linux_terminal_calls": 10,
      "linux_terminal_seconds": 2.858,
      "published_patch": "patches/deepswe_returns-validated-error-accumulation/adapt-0001.patch",
      "verifier_summary": [
        "[verifier] Baseline exit code: 0",
        "FAILED tests/test_validated/test_validated_apply.py::test_apply_valid_valid",
        "[verifier] New tests exit code: 1"
      ]
    },
    {
      "actor_prompt_sha256": "07bf5962a2f22433ad6ef85466507216bae074558a5dc52a250d00fbdf255bd6",
      "agent_exit": "completed",
      "agent_settings": {
        "context_window": 48000,
        "lane": "subscription",
        "model": "gpt-6-luna",
        "reasoning_effort": "medium"
      },
      "agent_usage": {
        "cached_input_tokens": 379776,
        "completed_turns": 1,
        "input_tokens": 421821,
        "output_tokens": 7264,
        "reasoning_output_tokens": 1609,
        "total_tokens": 429085
      },
      "arm": "stock",
      "artifact_path": "attempts/deepswe_returns-validated-error-accumulation/stock/0001",
      "attempt": "0001",
      "continuation_limit_reached": false,
      "continuations": 0,
      "cycle_images": true,
      "effective_settings": {
        "auto_compaction": "Pinned Codex default; no threshold override. Exact trigger is not exposed by the bundle.",
        "catalog_share": 0.1,
        "checks": {
          "budget": true,
          "catalog_share": true,
          "compaction_default": true,
          "context": true,
          "effort": true,
          "model": true,
          "release": true,
          "tool_cap": true,
          "version": true
        },
        "config_sha256": "874759a1eaaca11401a3b8cb3f88c47e79fc5524fca429b23f1f429521f2a2a1",
        "context_window": 48000,
        "mcp_servers": [
          "task_terminal"
        ],
        "model_catalog_sha256": "f48a58c26f49e7535798db2eb54c45b66ae1e2fe6555d50a0aea1739e81f26d5",
        "passed": true,
        "tool_output_limit": {
          "limit": 10000,
          "mode": "tokens"
        }
      },
      "family": "DeepSWE",
      "image_id": "sha256:2b7933a7c57daa5532fd1d097dc4a97694047076ac4a213334025bbaec08e34b",
      "patch_sha256": "274beab82bd59e35651a8cac1b8740f720c6f8faedb879a90603f976fc864888",
      "prompt_sha256": "4a1ff83df1e3502f3e15fab4647cc4a607f4affc51db970b5ac1f45359b20f0d",
      "repository_path": "/app",
      "reward": 0.0,
      "run_path": "attempts/deepswe_returns-validated-error-accumulation/stock/0001/runs/deepswe_returns-validated-error-accumulation-20261120T160518-ed1c",
      "runner_source_sha256": {
        "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
        "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
        "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
      },
      "started": "2026-11-20T16:05:17+00:00",
      "status": "scored",
      "task": "deepswe_returns-validated-error-accumulation",
      "trace": {
        "calls": 35,
        "steps": 19,
        "user_messages": 1
      },
      "updated": "2026-11-20T16:08:05+00:00",
      "upstream_base": "41607fae1289de2787523c452d75212206b9c7c0",
      "verifier_exit_code": 0,
      "compaction_source_audit": {
        "codex_commit": "687a119f0fcaace47e1f1abcc77cec6c813fd6da",
        "default_auto_compact_token_limit": 43200,
        "usable_input_context": 45600,
        "source": "https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535"
      },
      "agent_seconds": 161.497,
      "linux_terminal_calls": 17,
      "linux_terminal_seconds": 6.063,
      "published_patch": "patches/deepswe_returns-validated-error-accumulation/stock-0001.patch",
      "verifier_summary": [
        "[verifier] Baseline exit code: 0",
        "FAILED tests/test_validated/test_validated_bind.py::test_lash_valid - assert ...",
        "[verifier] New tests exit code: 1"
      ]
    }
  ],
  "prior_experiments": [
    {
      "analysis_notes": [],
      "architecture": {
        "coding": "Separate Linux containers from the same upstream image ID",
        "compaction": "Pinned Codex default: 43,200-token automatic threshold for 48K context; 45,600 usable input tokens. No override.",
        "controller": "Pinned macOS ADAPT binary, both arms",
        "limitations": [
          "The supplied release has no Linux binary, so the controller remains on macOS.",
          "Data-structure pytest validation is skipped by this release on macOS.",
          "The native host shell still exists; the shared prompt requires all project work through the Linux tool.",
          "Compaction defaults are derived from the exact Codex source commit named in the release license; actual context pressure still requires trace review.",
          "The smoke task was selected using a previously passing patch and is not an unbiased accuracy estimate.",
          "Old macOS coding pilot results are a separate experiment."
        ],
        "network": "Follow upstream task allow_internet setting for both coding and grading",
        "project_io": "Shared task_terminal MCP tool; hidden tests and credentials are not mounted",
        "verifier": "Fresh Linux container from the coding image; frozen patch and upstream tests"
      },
      "attempts": [
        {
          "actor_prompt_sha256": "c2cfe7cb454b9937c39f0ced0f655dd5c97b687a36ea859ec863127aa316a7bb",
          "agent_exit": "completed",
          "agent_seconds": 103.413,
          "agent_settings": {
            "context_window": 48000,
            "lane": "subscription",
            "model": "gpt-6-luna",
            "reasoning_effort": "medium"
          },
          "agent_usage": {
            "cached_input_tokens": 252800,
            "completed_turns": 1,
            "input_tokens": 283142,
            "output_tokens": 4380,
            "reasoning_output_tokens": 384,
            "total_tokens": 287522
          },
          "arm": "stock",
          "artifact_path": "attempts/deepswe_kombu-single-active-consumer-priority/stock/0001",
          "attempt": "0001",
          "compaction_source_audit": {
            "codex_commit": "687a119f0fcaace47e1f1abcc77cec6c813fd6da",
            "default_auto_compact_token_limit": 43200,
            "source": "https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535",
            "usable_input_context": 45600
          },
          "continuation_limit_reached": false,
          "continuations": 0,
          "cycle_images": true,
          "effective_settings": {
            "auto_compaction": "Pinned Codex default; no threshold override. Exact trigger is not exposed by the bundle.",
            "catalog_share": 0.1,
            "checks": {
              "budget": true,
              "catalog_share": true,
              "compaction_default": true,
              "context": true,
              "effort": true,
              "model": true,
              "release": true,
              "tool_cap": true,
              "version": true
            },
            "config_sha256": "f568e2736edb1d1efd2284347fa367a069bfceb8b085115a6dd85706a25a9953",
            "context_window": 48000,
            "mcp_servers": [
              "task_terminal"
            ],
            "model_catalog_sha256": "f48a58c26f49e7535798db2eb54c45b66ae1e2fe6555d50a0aea1739e81f26d5",
            "passed": true,
            "tool_output_limit": {
              "limit": 10000,
              "mode": "tokens"
            }
          },
          "family": "DeepSWE",
          "free_disk_gib": 17.72,
          "image_id": "sha256:f4158875f866062831172c5c4b24f8fc042fa8d13feec31d390f6751139cf44d",
          "linux_terminal_calls": 11,
          "linux_terminal_seconds": 3.352,
          "patch_sha256": "4eb62fd8e5d2236b5d31379c10c052eab9aa4a278cf88f452bf065dca7001d29",
          "prompt_sha256": "b5b29541383998df2dcc73e96536ee4a1100b1d346ba1d56b6633042455563bc",
          "published_patch": "patches/deepswe_kombu-single-active-consumer-priority/stock-0001.patch",
          "repository_path": "/app",
          "run_path": "attempts/deepswe_kombu-single-active-consumer-priority/stock/0001/runs/deepswe_kombu-single-active-consumer-priority-20261120T155847-51ad",
          "runner_source_sha256": {
            "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
            "run.py": "c7ddd16d9a9865c2d2f30df75350ab7a88a0dd2824265c74b25fe27a9cc7c6e0",
            "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
          },
          "started": "2026-11-20T15:58:46+00:00",
          "status": "interrupted",
          "task": "deepswe_kombu-single-active-consumer-priority",
          "trace": {
            "calls": 28,
            "steps": 16,
            "user_messages": 1
          },
          "updated": "2026-11-20T16:04:02+00:00",
          "upstream_base": "3c5c1bd86376ee73d52a4cc770bdaeab15bbc2f3",
          "verifier_summary": []
        }
      ],
      "exported": "2026-11-20T16:18:40+00:00",
      "exporter_sha256": "62b699b7e24aef753a49cc43f254240d3186628516e0613c75ecb82746d8ddd1",
      "format": "cs224v-tuesday-handoff-v1",
      "harness_commit": null,
      "harness_regressions": null,
      "linux_environment_audit": null,
      "manifest": {
        "arms": {
          "adapt": "codex",
          "stock": "codex-shipped"
        },
        "configuration": {
          "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
          "catalog_share": 0.1,
          "codex_version": "0.159.0",
          "context_window": 48000,
          "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
          "environment_mode": "linux-terminal",
          "first_task": "deepswe_fastapi-deprecation-response-headers",
          "image_overrides": {},
          "image_source": "upstream-prebuilt",
          "lane": "subscription",
          "max_continuations": 8,
          "model": "gpt-6-luna",
          "model_seed": null,
          "platform": "linux/amd64",
          "protocol": "singleturn-with-conditional-continue",
          "reasoning_effort": "medium",
          "require_verifier_validation": true,
          "rubric_bridge_sha256": "1ce49aa69da1fbd6ae69b057f1d5ba2853be96c01adb151af6bfaffab9e64b36",
          "rubric_model": "gpt-6-luna",
          "rubric_reasoning_effort": "medium",
          "rubric_transport": "local-codex-cli",
          "task_order_seed": 224,
          "temperature": null,
          "tool_output_limit": 10000,
          "trial_wall_clock_s": 3600,
          "verifier_pytest_addopts": {
            "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
          }
        },
        "harness_sources": {
          "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
          "run.py": "c7ddd16d9a9865c2d2f30df75350ab7a88a0dd2824265c74b25fe27a9cc7c6e0",
          "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
        },
        "model_catalog_sha256": "a5e25107506f0934cb62144c093c72bf8c7fa5de1436f4aa02fe54769d789618",
        "runner_sha256": "96fb6d40ce455c428280639ca82e426f3f6a34454acd55bc30f360e516464373",
        "task_order": [
          "deepswe_fastapi-deprecation-response-headers",
          "deepswe_kombu-single-active-consumer-priority",
          "deepswe_awilix-async-container-initialization",
          "rf_task-69b7c2a04b6f8ff9ed98813b",
          "swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d",
          "rf_task-69d196f015a150488265afb7",
          "deepswe_wazero-multi-module-snapshots",
          "deepswe_cattrs-partial-structuring-recovery",
          "swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367",
          "rf_task-69b7c2a04b6f8ff9ed988137",
          "swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26",
          "rf_task-69b7c2a04b6f8ff9ed98812f",
          "rf_task-696719205599a51110d4b436",
          "rf_task-694b4b99829f00e24fd11891",
          "deepswe_tomlkit-toml-table-converters",
          "rf_task-696719205599a51110d4b458",
          "deepswe_sqlite-utils-safe-import-checkpoints",
          "deepswe_etree-xml-diff-patch",
          "swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan",
          "deepswe_arcane-drift-detection-baselines",
          "deepswe_testem-bail-on-test-failure",
          "rf_task-696719205599a51110d4b428",
          "deepswe_httpx-streaming-json-iteration",
          "rf_task-694b4b99829f00e24fd11889",
          "rf_task-696719205599a51110d4b40c",
          "swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c",
          "rf_task-696719205599a51110d4b451",
          "swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e",
          "deepswe_mobly-grouped-test-barriers",
          "swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86",
          "rf_task-696719205599a51110d4b447",
          "deepswe_bandit-structured-nosec-directives",
          "deepswe_pwntools-tube-multiplexing",
          "swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818",
          "swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171",
          "rf_task-696719205599a51110d4b441",
          "rf_task-696719205599a51110d4b446",
          "swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26",
          "deepswe_clack-async-autocomplete-options",
          "rf_task-69d196f015a150488265afb9",
          "rf_task-696719205599a51110d4b434",
          "rf_task-696719205599a51110d4b455",
          "swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86",
          "swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4",
          "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e",
          "deepswe_httpx-deterministic-cookie-store",
          "swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171",
          "rf_task-69b7c2a04b6f8ff9ed98813d",
          "deepswe_returns-validated-error-accumulation",
          "rf_task-69391d8d1ce51c407be1e533",
          "swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d",
          "swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb",
          "rf_task-69d196f015a150488265afc1",
          "swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125",
          "swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan",
          "deepswe_vitest-duration-sharding",
          "rf_task-694b4b99829f00e24fd11885",
          "swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86",
          "swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan",
          "swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566",
          "deepswe_drizzle-orm-window-function-builders",
          "deepswe_ofetch-per-origin-circuit-breaker",
          "rf_task-696719205599a51110d4b440",
          "swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288",
          "rf_task-696719205599a51110d4b476",
          "deepswe_boa-hierarchical-evaluation-cancellation",
          "deepswe_participle-grammar-conflict-analysis",
          "swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f",
          "deepswe_kcp-go-multiplexed-kcp-streams",
          "rf_task-694b4b99829f00e24fd118a1",
          "swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4",
          "deepswe_helm-array-merge-strategies",
          "swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12",
          "rf_task-69391d8d1ce51c407be1e531",
          "deepswe_fastapi-implicit-head-options"
        ],
        "tasks": {
          "deepswe_arcane-drift-detection-baselines": {
            "definition_sha256": {
              "multiturn": "e98a4380f4decbd07a68005aaa49cfb2533a28d4e4f6305c229ad8ec45b6bb47",
              "singleturn": "0dd4d16d85d68926aec874005f1f2108486a3010ea10a8cca3e2858d52760b30"
            },
            "family": "DeepSWE"
          },
          "deepswe_awilix-async-container-initialization": {
            "definition_sha256": {
              "multiturn": "a8ab7fb385b490e4be5b681987b7b5d72f7e4dc8f06363288e6cc1b305be1d62",
              "singleturn": "28db387fe7e67ac634126ed9d453647315e50cbd0b5f109a25e7da63a4a8aec2"
            },
            "family": "DeepSWE"
          },
          "deepswe_bandit-structured-nosec-directives": {
            "definition_sha256": {
              "multiturn": "07559c20cdfe90e4e86620f7897e1c49e1baceba4472eb65af056cb93575d71d",
              "singleturn": "b8d25d646139c9881f6dc326852df5c8ba3cf1f390f487c4132347b0b9dd4ee3"
            },
            "family": "DeepSWE"
          },
          "deepswe_boa-hierarchical-evaluation-cancellation": {
            "definition_sha256": {
              "multiturn": "3c63e77f3fdf712ee3b547f9f30b10d7ab7dc56cc53932c19bcf6329dd6ecff9",
              "singleturn": "f67447f82a04fd9ad1e3e6c330f68ec89b9deb98084f4650cfbe89cff7533068"
            },
            "family": "DeepSWE"
          },
          "deepswe_cattrs-partial-structuring-recovery": {
            "definition_sha256": {
              "multiturn": "e7982202cf7ae92fef1efef3cc48bce6c7bbcd79f86a699327b63779aa54b4cf",
              "singleturn": "399472bc4f4ae276c5c415227bccf22bdfd11b85225bb6be4cabb1b6dfc75410"
            },
            "family": "DeepSWE"
          },
          "deepswe_clack-async-autocomplete-options": {
            "definition_sha256": {
              "multiturn": "92ae989e0832d4c942c105fa33c8e3a4d19fcec2b84501f7b23de0db35b1ef0a",
              "singleturn": "3027742d60971bbc24caea4bfc424763b71cfccdf18614a019668c9d7a2524bc"
            },
            "family": "DeepSWE"
          },
          "deepswe_drizzle-orm-window-function-builders": {
            "definition_sha256": {
              "multiturn": "7423e124245a1707bff0f8b0a0d02c14a184656b52f4e9c2e22dc024f0c4b154",
              "singleturn": "4387441bb3a9635f85bc2921ebac8ad910d0a8bc36c5ef61f2c9b5ba7c467d6c"
            },
            "family": "DeepSWE"
          },
          "deepswe_etree-xml-diff-patch": {
            "definition_sha256": {
              "multiturn": "f156812a76bc081cedd94aa5fbe2408d02e0c7fee3b4a7f899d94c3dd7dc5c2d",
              "singleturn": "51f1c00e93cb1926e7b7d5863bd76a5bade6b65eff87da8988abfe968d1a9690"
            },
            "family": "DeepSWE"
          },
          "deepswe_fastapi-deprecation-response-headers": {
            "definition_sha256": {
              "multiturn": "9b39b52d85448808a447b0dc742707e40aa5ebdb56910294d9243656ce7dd292",
              "singleturn": "9b1be50e6fc5c9c80d68556c4a65f781c143b456cdb70e13ff9c068f3d61c652"
            },
            "family": "DeepSWE"
          },
          "deepswe_fastapi-implicit-head-options": {
            "definition_sha256": {
              "multiturn": "0016ca26b455fc38fbb49d928c3bd10a69bf7b97e9ce9416aa344f00a0e5a64c",
              "singleturn": "34a65c36fb919724ab9f0e7d6e91fa9a64588f1db215015673923da7828a8167"
            },
            "family": "DeepSWE"
          },
          "deepswe_helm-array-merge-strategies": {
            "definition_sha256": {
              "multiturn": "6bab0e45b366d3ec60fb9ae3214b3db069983bfa3f7a050e0659649ae8480d38",
              "singleturn": "63ccf5d6d3818bea88c088b286ea55edc89c9178e6958b6216baca3dca791356"
            },
            "family": "DeepSWE"
          },
          "deepswe_httpx-deterministic-cookie-store": {
            "definition_sha256": {
              "multiturn": "6ec038c72fe718aec699a04c89a938085dcb1d3217dba0d3a05c630529c1e7ae",
              "singleturn": "58d610b3ffefea9e7d8d90764ed8284e0ee2c34ceb7545c7ff1f45aca8be9c5a"
            },
            "family": "DeepSWE"
          },
          "deepswe_httpx-streaming-json-iteration": {
            "definition_sha256": {
              "multiturn": "8992bfbfc1cda4c03bebe3d9086f993dcab7681d03a1ddd1bc02249aed4d8594",
              "singleturn": "142be505eb4bdf811fca2c642f2ca85a1fbcafeeb55b8ff08cafee5207fe51f3"
            },
            "family": "DeepSWE"
          },
          "deepswe_kcp-go-multiplexed-kcp-streams": {
            "definition_sha256": {
              "multiturn": "2c94fa7120b35f9f80644cb52cdeca3c794e7fec191d0ca7061a81149972f68c",
              "singleturn": "51d7c77f3ec12e1a6acf484b56014dc0c2931c2a65f7b995f8f678a337daffb7"
            },
            "family": "DeepSWE"
          },
          "deepswe_kombu-single-active-consumer-priority": {
            "definition_sha256": {
              "multiturn": "c69587c7b134861f8c9ffe450f5a680d0073d6e5633f628ef62de73c1c5ad2de",
              "singleturn": "9adb5dba1f5781be2a376d0282d96b40a098fa07134e93d34261d266fcf446e5"
            },
            "family": "DeepSWE"
          },
          "deepswe_mobly-grouped-test-barriers": {
            "definition_sha256": {
              "multiturn": "feaa44254f26e5a25a6cce2d6051a680947f56cd8c2b339565f467e3e8128247",
              "singleturn": "f543dab0c5c77ac45b0135d4d430c76f34c2482747af8bbdc4b774b8f4d5d111"
            },
            "family": "DeepSWE"
          },
          "deepswe_ofetch-per-origin-circuit-breaker": {
            "definition_sha256": {
              "multiturn": "949d73413dd9a9b32850dffc946b9449b18c876c4badf1a96512ba6dce00c173",
              "singleturn": "01cf71ecfc57dbbf91b489d336701fb7ce65b365cdcbd457c963adc77ee50ddd"
            },
            "family": "DeepSWE"
          },
          "deepswe_participle-grammar-conflict-analysis": {
            "definition_sha256": {
              "multiturn": "a4d700f59eadab1d22d85f9a5f2df8eee89f4669c5b450cf7931ed6608f82c4a",
              "singleturn": "d59e4277344a8794923806c2f6656d1f167204b40608496d59bbee8ad8c049e9"
            },
            "family": "DeepSWE"
          },
          "deepswe_pwntools-tube-multiplexing": {
            "definition_sha256": {
              "multiturn": "bdb3c018b6577e6faa3aae0cbe155f354f684054e47c1bb61fcd9ed0b3c1082a",
              "singleturn": "7da1943dd50ff31b2498d3b76546cfb0909051b0fdf4db22d8a7c833ff4aa79b"
            },
            "family": "DeepSWE"
          },
          "deepswe_returns-validated-error-accumulation": {
            "definition_sha256": {
              "multiturn": "fae26435c7573a5a124b9c5e3c3cd0e0f9088918437bdf9302ff8307d27076c2",
              "singleturn": "f419e38330363c79ef93a6ac96712de151b61e59f8563d91b4964545347bc318"
            },
            "family": "DeepSWE"
          },
          "deepswe_sqlite-utils-safe-import-checkpoints": {
            "definition_sha256": {
              "multiturn": "f33b9540ace6a9c58943efed5b724ffec4f88360664acfa070abaa19748df083",
              "singleturn": "29f81b5cd9477ce5597738fffef36bdce3c686a06686ac899824b6c9c89d3104"
            },
            "family": "DeepSWE"
          },
          "deepswe_testem-bail-on-test-failure": {
            "definition_sha256": {
              "multiturn": "edfabf0859035d40c7abc4062ddc455e47a7399ef4032a5cb41f86a672a060bb",
              "singleturn": "011e5dc7ad975c6b756af4f899297a5fe655d9511509494ea5ae355974db3605"
            },
            "family": "DeepSWE"
          },
          "deepswe_tomlkit-toml-table-converters": {
            "definition_sha256": {
              "multiturn": "4af1a89e1a2f0bc3f15ee5772e1a0ff98dd7ebd575cfb8008750eb62b079b07f",
              "singleturn": "6d100e2bd44741340e2107d29a90b834bc6788083f369697ce89dfc6b4be86af"
            },
            "family": "DeepSWE"
          },
          "deepswe_vitest-duration-sharding": {
            "definition_sha256": {
              "multiturn": "5a763a854fc4de57334d1c4f6bec67c5251f4b9d99b677e5885ce6bc4d9f69ac",
              "singleturn": "540b6b7c1bfeb1ab62772740a5a79abf37105c2a6146cd40a39d1c31f8920fb2"
            },
            "family": "DeepSWE"
          },
          "deepswe_wazero-multi-module-snapshots": {
            "definition_sha256": {
              "multiturn": "ed9b13500af126a369d18a634b44180c00c5f36663b1810351acb10d783b7893",
              "singleturn": "b0c66b4dffb612ed3d79c20c391684807b6dd74446698721a368f347a44de155"
            },
            "family": "DeepSWE"
          },
          "rf_task-69391d8d1ce51c407be1e531": {
            "definition_sha256": {
              "multiturn": "f977d33266976cfaa7322b5f3045cc0afe89a804a57536677ee88c482ffe3ef5",
              "singleturn": "cb780e1f086fabd30de7bec6d0f84ccc84f88b2710ebc449259fa776f5f22825"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69391d8d1ce51c407be1e533": {
            "definition_sha256": {
              "multiturn": "9150daedd87e825ec00ab49e3c160700e162e200a158ae4f5a9990b5d756fa50",
              "singleturn": "34a3f62a91ed354374439c4650754e27fad9a474b2f0932645cf67d66082f61e"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-694b4b99829f00e24fd11885": {
            "definition_sha256": {
              "multiturn": "713a9019147dc8bf43a532b31f022fd755ee210fc831482860ac6f7b506f1aeb",
              "singleturn": "847def97d9034cce23562c64aca2dee9f17659955be69381b697c70c7c0848dc"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-694b4b99829f00e24fd11889": {
            "definition_sha256": {
              "multiturn": "370d0b9e069dc27e78df7f985f274bd7bd86fca7fa513cd5078c17de2b0b05a9",
              "singleturn": "c25f1462c109f813a5d125ea95b46f11bfe87eec4a975e630187b7309ba9482a"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-694b4b99829f00e24fd11891": {
            "definition_sha256": {
              "multiturn": "28c8b24cdd0907a42d0cb8b24a4f32b70d9574301904b11df9ca44fc7bbb680b",
              "singleturn": "18c8633391e47a46e9f329226981dd31be491b4a59e2557abe0ff7c0a8caf8b1"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-694b4b99829f00e24fd118a1": {
            "definition_sha256": {
              "multiturn": "a6c300d10ebe9fe02d786833ec9fc83b3796347024ff18b708cea7935a48a479",
              "singleturn": "6dfabf6b1606c2e277643a192e51435d465ad1b95cd209c4e1e2fa29a360dd74"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b40c": {
            "definition_sha256": {
              "multiturn": "13c9c4e64cfb499ca396283c42a326790eb945ada366867493f383165d05d76b",
              "singleturn": "32db68230cb9fe379daa2125bc1ff39b580a224ef2b3be664c96a863f9a5608c"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b428": {
            "definition_sha256": {
              "multiturn": "9477cd432fa524e145e8238544059450efc421787660d0b3a1e502a26b6a92b0",
              "singleturn": "66dd0ccc3c4f63225612e03055e8a5b58dd5b85a762435130494eb52d776e4e4"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b434": {
            "definition_sha256": {
              "multiturn": "626c9145869413d36114d48e814a79146d6846e904e16c77a949e8f36be18190",
              "singleturn": "e41cb6fcc03614dddc1f6c7c5d7a090cdf2958a02276f104c0dd80641b07e3dd"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b436": {
            "definition_sha256": {
              "multiturn": "10fc8eb923d1d398e9f08dd3192de6bd9b553fe19eea419e72a2b09cbff782d2",
              "singleturn": "98f71d6bfa71fcd0b221f663b76a225d0f7d7168aaac372f30a0018d74befd17"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b440": {
            "definition_sha256": {
              "multiturn": "9faa8634f39664357a8bdef97ea6a3bef95f6ee936fdcd0413c1364eb42862b8",
              "singleturn": "d1f184a8ec4d60fc0412fbba6c107ac27f0ddc6a1acf055bac8f0293b3fd4213"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b441": {
            "definition_sha256": {
              "multiturn": "601acf3ab12e265eba973aaf4b02076b52677e1684875942c7e1363545fbe9e6",
              "singleturn": "5b3143da6ada52e44f18d704eb2ea27028fe2d92f0db533040299eaff4027c79"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b446": {
            "definition_sha256": {
              "multiturn": "09f29da1976a791cbef0fe7c2e8600cdbcdcf9a3554ede0630e0479bbb031b0d",
              "singleturn": "458463c4b93b8f95fe1d890daec1e4f0422383391187e966d68d22e9ba525d18"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b447": {
            "definition_sha256": {
              "multiturn": "d817f20627fa0033a56db5f838fb8a2c129dc6bbb270e050395aa0e2034c266e",
              "singleturn": "6c1af11acb07a147fa82d2de06489e068a945cf27b5328185145007defb7a533"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b451": {
            "definition_sha256": {
              "multiturn": "50eee5c5a7de328e1ff0ed34c9fcb943a7675b20abea838aca317f07266ac603",
              "singleturn": "ae5e50307e81f9329fb01bd9f652a6cc4b6e8c0cdea580c3a1d1252cac796613"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b455": {
            "definition_sha256": {
              "multiturn": "5fc2d7fa81e8b4538d4bbc14dbec4ff9c7f8f10aafac5923ed34206966047c25",
              "singleturn": "a7f43901affee4cb7b53d507d35f385d5eebf5fb6bde6667ffa732d3dee5b56f"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b458": {
            "definition_sha256": {
              "multiturn": "b13790800d7d854d3327cb48ec1cc447020d52fb9984677642629406c4422610",
              "singleturn": "4ec9be2a77e9ea9bd4b13b5d7bf3638cf57a4da45596acef2aac45e5193df1b3"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-696719205599a51110d4b476": {
            "definition_sha256": {
              "multiturn": "1b267945741d7501a939f7881f68373f19d740090a1371104230deb75e12e221",
              "singleturn": "f3d9eadd355ec1d059cacde1c839c830a03bef4a13a00e975e16bdb4c85e7d67"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69b7c2a04b6f8ff9ed98812f": {
            "definition_sha256": {
              "multiturn": "34ea8c9879852d09e01d5f87b9e90101657c5df79f25cff817bb7a33c0196e0f",
              "singleturn": "3e5e01cfab550c2d15c5f868f338f5aae3986af680fa96d2b33b63b958932287"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69b7c2a04b6f8ff9ed988137": {
            "definition_sha256": {
              "multiturn": "51679b1b035103f803d1031e70a4583db46d9ac46df3e8fcb07621c71194841a",
              "singleturn": "65f1d0a32ef9d9685bf73a1581fcfbc07c6232bfec911e384e22912f5ba1e69c"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69b7c2a04b6f8ff9ed98813b": {
            "definition_sha256": {
              "multiturn": "08df2026ab68e5cfdf710c3abd4ce60722a98356f06433d52cb8e3d353997e86",
              "singleturn": "3210d2b568dd858493ccb1cf8fa7622fc910fcb9bba35af540d88c3e60cf66c7"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69b7c2a04b6f8ff9ed98813d": {
            "definition_sha256": {
              "multiturn": "02c613eac2cff202da19a606cedcb188d1b014be8f6ccb586e630833076cd5b5",
              "singleturn": "9287ddacdd70ee05dd11b0949a8673c6b3640070f84b1aa408c457329540bad7"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69d196f015a150488265afb7": {
            "definition_sha256": {
              "multiturn": "d0fdd057584afa6e3272601f4091fb9333c3bf3f81f07c0ddb608b3ac097c063",
              "singleturn": "97892c66d1fbddce6cd5e016c3f6477fabe1ceb4de9a420b626e6709fc165f8c"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69d196f015a150488265afb9": {
            "definition_sha256": {
              "multiturn": "76bc4aeb9a2cfb6f7a1e97a6a46084fbac0065a21ffb90fa3b999b38f1d60442",
              "singleturn": "52067daf8a458ba11f4db6038c4434019ef97a8f2930966718539f1d9071a06f"
            },
            "family": "SWE Atlas Refactoring"
          },
          "rf_task-69d196f015a150488265afc1": {
            "definition_sha256": {
              "multiturn": "8f4a66333360bc1455b3cd0fbd1f2a0dcb5d6caa551c05939b972ee1dc314bad",
              "singleturn": "5caa65d11f6158c4741cdadc0c210908bf24deceb758fbb110e907dbecde33e9"
            },
            "family": "SWE Atlas Refactoring"
          },
          "swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86": {
            "definition_sha256": {
              "multiturn": "f15d3c13c16ef21af14499d030966c56beaaa31dc87600511ee4f75ec8263d6f",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_ansible__ansible-c616e54a6e23fa5616a1d56d243f69576164ef9b-v1055803c3a812189a1133297f7f5468579283f86": {
            "definition_sha256": {
              "multiturn": "b1c08613862e3161774791dd557be7ce72ddc9b7f769989d96bb5efb70d0423c",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_ansible__ansible-e40889e7112ae00a21a2c74312b330e67a766cc0-v1055803c3a812189a1133297f7f5468579283f86": {
            "definition_sha256": {
              "multiturn": "e1a90767d49eb5b1f3c26564d00d0453796afbde2c2449ed0579b866cb03fb46",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_element-hq__element-web-d06cf09bf0b3d4a0fbe6bd32e4115caea2083168-vnan": {
            "definition_sha256": {
              "multiturn": "4d7819a1fcb802c0460221f86a79f06f32e0e0c84b12ba6d8c1e596fe5cdcc60",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_element-hq__element-web-fe14847bb9bb07cab1b9c6c54335ff22ca5e516a-vnan": {
            "definition_sha256": {
              "multiturn": "0edcd9fa1092249e60eb9dd6e05183b031bbf90dcc8d48c052b2b2322fd75c85",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_flipt-io__flipt-96820c3ad10b0b2305e8877b6b303f7fafdf815f": {
            "definition_sha256": {
              "multiturn": "c1e430450d5f9c6d6d1fe8a0a86074327f742f4ece9afceae60564b3183a4107",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125": {
            "definition_sha256": {
              "multiturn": "c93e5ac1b00cf5faf90912e4348093888a5159b669901bab2a6c041f086f5a99",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_flipt-io__flipt-e5fe37c379e1eec2dd3492c5737c0be761050b26": {
            "definition_sha256": {
              "multiturn": "8c5a7d3e0fc005736468a853779130a5e6f0abc998e32ecd46fe726af111bf84",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e": {
            "definition_sha256": {
              "multiturn": "408b57b283efccd29c561e4224efb9f3f221d15f73f5ce9c1d9a52f706f146f1",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_gravitational__teleport-d6ffe82aaf2af1057b69c61bf9df777f5ab5635a-vee9b09fb20c43af7e520f57e9239bbcf46b7113d": {
            "definition_sha256": {
              "multiturn": "66216a566db830f9619e66c1ff8c8fec5c1ea50701f093f09699306ec43c534e",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_gravitational__teleport-f432a71a13e698b6e1c4672a2e9e9c1f32d35c12": {
            "definition_sha256": {
              "multiturn": "80da11658b27be58a7642c35168dbf4f358fa2ff97a209c621a929f9de2e0c76",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_internetarchive__openlibrary-0a90f9f0256e4f933523e9842799e39f95ae29ce-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c": {
            "definition_sha256": {
              "multiturn": "f8096a4fac83e9af7f4b5a43adba3c91a323a010ffb2eae1fdb5b11208c25561",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_internetarchive__openlibrary-4b7ea2977be2747496ba792a678940baa985f7ea-v0f5aece3601a5b4419f7ccec1dbda2071be28ee4": {
            "definition_sha256": {
              "multiturn": "548c8a0f30387b74e4da594b4cf507572362fe117aa4c14ab4cff6d7e9c03709",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_internetarchive__openlibrary-5de7de19211e71b29b2f2ba3b1dff2fe065d660f-v08d8e8889ec945ab821fb156c04c7d2e2810debb": {
            "definition_sha256": {
              "multiturn": "363b9a5bfef65c9bc2e430da3e46f189d9158ac0176347573d035e206da11fbf",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_internetarchive__openlibrary-b67138b316b1e9c11df8a4a8391fe5cc8e75ff9f-ve8c8d62a2b60610a3c4631f5f23ed866bada9818": {
            "definition_sha256": {
              "multiturn": "a38e573e2390f79c622416633116174905404c50249d98d31820db54c9e1f295",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_internetarchive__openlibrary-d40ec88713dc95ea791b252f92d2f7b75e107440-v13642507b4fc1f8d234172bf8129942da2c2ca26": {
            "definition_sha256": {
              "multiturn": "4477446d1e1d6294f0a6c3128136635e6befadab74daeb1ad7772b35a4b72b55",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_navidrome__navidrome-3972616585e82305eaf26aa25697b3f5f3082288": {
            "definition_sha256": {
              "multiturn": "346bd4c67ae9206932b304356e010a47647f01928879509fc84f1935c01cdb0c",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_nodebb__nodebb-8168c6c40707478f71b8af60300830fe554c778c-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e": {
            "definition_sha256": {
              "multiturn": "90c6087e871d66a7c67484a8520dd7a288ea728ae86a1f98fae6e7dcb3f961ca",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_nodebb__nodebb-f083cd559d69c16481376868c8da65172729c0ca-vnan": {
            "definition_sha256": {
              "multiturn": "7ec7ba6394c09daf292dd7888f3ec35c22c1500efbe2e6d589e9a4d2a19d07f4",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_protonmail__webclients-e65cc5f33719e02e1c378146fb981d27bc24bdf4": {
            "definition_sha256": {
              "multiturn": "a3abb6ebfe113f7756950ab37f6122fbd5d7f12195bf938dc5a52b8edd39f056",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_qutebrowser__qutebrowser-70248f256f93ed9b1984494d0a1a919ddd774892-v2ef375ac784985212b1805e1d0431dc8f1b3c171": {
            "definition_sha256": {
              "multiturn": "cf9eaa496400f3fcac9de93a1de66870ac6ae5ea260c1aed4bcedbc3452baa73",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_qutebrowser__qutebrowser-96b997802e942937e81d2b8a32d08f00d3f4bc4e-v5fc38aaf22415ab0b70567368332beee7955b367": {
            "definition_sha256": {
              "multiturn": "b601e4fec849a218510c0ca16b95a3e8312c691c23ff147fb7ba464e9a778d50",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_qutebrowser__qutebrowser-bedc9f7fadf93f83d8dee95feeecb9922b6f063f-v2ef375ac784985212b1805e1d0431dc8f1b3c171": {
            "definition_sha256": {
              "multiturn": "73fac0daccfbd6915d7b9ea9276ba4516ee90ab38d9668defc6a790b1ccdc0e2",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_qutebrowser__qutebrowser-deeb15d6f009b3ca0c3bd503a7cef07462bd16b4-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d": {
            "definition_sha256": {
              "multiturn": "cb10bf531b17363142009544fd25f7215eff4c31ae9be615575755f1782fe38d",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          },
          "swebenchpro_instance_qutebrowser__qutebrowser-fea33d607fde83cf505b228238cf365936437a63-v9f8e9d96c85c85a605e382f1510bd08563afc566": {
            "definition_sha256": {
              "multiturn": "9086258c4b20da32fe7d84c8b9f86f7e02847bd63e6c4c28db5b6c7eb87b3027",
              "singleturn": "b0d8f883580ad808751e86fce8ae1ab380fb69a2a70c9023cc5737cf3ac73910"
            },
            "family": "SWE-bench Pro"
          }
        }
      },
      "paired_checks": [
        {
          "checks": {
            "actor_prompt_sha256": false,
            "agent_settings": false,
            "both_scored": false,
            "effective_settings": false,
            "image_id": false,
            "prompt_sha256": false,
            "runner_source_sha256": false,
            "upstream_base": false
          },
          "passed": false,
          "task": "deepswe_kombu-single-active-consumer-priority"
        }
      ],
      "prior_experiments": [],
      "run_events": [
        {
          "at": "2026-11-20T16:04:02+00:00",
          "detail": "Stopped the stock Kombu smoke verifier after it stalled in test_FilesystemTransport::test_produce_consume. Preserved the frozen patch and unscored interrupted record. No hidden-test feedback was sent to an actor.",
          "image_id": "sha256:f4158875f866062831172c5c4b24f8fc042fa8d13feec31d390f6751139cf44d",
          "repo_digests": [
            "public.ecr.aws/d3j8x8q7/swe-bench-202605@sha256:532b2458f9a85e47354912fda4c36ce47d1d1232f43a0ef6f35827e82a131a9e"
          ]
        }
      ],
      "timeout_cleanup_check": null,
      "verifier_validations": [
        {
          "base_commit": "3c5c1bd86376ee73d52a4cc770bdaeab15bbc2f3",
          "configuration": {
            "adapt_commit": "166c433f79dd667f76d093898a39aa795f3e3349",
            "catalog_share": 0.1,
            "codex_version": "0.159.0",
            "context_window": 48000,
            "dataset_commit": "b32f98c3b8f76ca65e84341d1f30e5af7135f85d",
            "environment_mode": "linux-terminal",
            "first_task": "deepswe_fastapi-deprecation-response-headers",
            "image_overrides": {},
            "image_source": "upstream-prebuilt",
            "lane": "subscription",
            "max_continuations": 8,
            "model": "gpt-6-luna",
            "model_seed": null,
            "platform": "linux/amd64",
            "protocol": "singleturn-with-conditional-continue",
            "reasoning_effort": "medium",
            "require_verifier_validation": true,
            "rubric_bridge_sha256": "1ce49aa69da1fbd6ae69b057f1d5ba2853be96c01adb151af6bfaffab9e64b36",
            "rubric_model": "gpt-6-luna",
            "rubric_reasoning_effort": "medium",
            "rubric_transport": "local-codex-cli",
            "task_order_seed": 224,
            "temperature": null,
            "tool_output_limit": 10000,
            "trial_wall_clock_s": 3600,
            "verifier_pytest_addopts": {
              "deepswe_fastapi-deprecation-response-headers": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"
            }
          },
          "controls": {
            "known-good": {
              "exit_code": 0,
              "expected": 1.0,
              "passed": true,
              "patch_sha256": "84361606f4ec2cd2996466fe86f8b12d7ddc6c30a5853a9565b76ba5bd48552c",
              "reward": 1.0
            },
            "untouched": {
              "exit_code": 0,
              "expected": 0.0,
              "passed": true,
              "patch_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
              "reward": 0.0
            }
          },
          "finished": "2026-11-20T15:58:26+00:00",
          "image_id": "sha256:f4158875f866062831172c5c4b24f8fc042fa8d13feec31d390f6751139cf44d",
          "passed": true,
          "source_sha256": {
            "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
            "run.py": "c7ddd16d9a9865c2d2f30df75350ab7a88a0dd2824265c74b25fe27a9cc7c6e0",
            "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
          },
          "started": "2026-11-20T15:56:59+00:00",
          "task": "deepswe_kombu-single-active-consumer-priority",
          "tests_sha256": {
            "tests/test.patch": "d1b4ae8f13799d4d7590f70707482e5d76a18712a9c332ff15e933de089edae7",
            "tests/test.sh": "b53a7435766b5149d1fd355bfcee189301059f0053540643267d9119bc677f02"
          }
        }
      ]
    }
  ],
  "linux_environment_audit": {
    "image_id": "sha256:2b7933a7c57daa5532fd1d097dc4a97694047076ac4a213334025bbaec08e34b",
    "no_grading_tests_or_candidate_patch_in_image": true,
    "runtime": [
      "Linux x86_64",
      "41607fae1289de2787523c452d75212206b9c7c0"
    ],
    "live_coding_containers": [
      {
        "image_id": "sha256:2b7933a7c57daa5532fd1d097dc4a97694047076ac4a213334025bbaec08e34b",
        "mounts": [],
        "cpus": 2.0,
        "memory_bytes": 8589934592,
        "network": "bridge"
      }
    ]
  },
  "run_events": [],
  "timeout_cleanup_check": {
    "container_removed": true,
    "forced_timeout_sec": 1,
    "passed": true,
    "real_docker_check": true,
    "timeout_record": {
      "at": "2026-11-20T16:15:53+00:00",
      "image_id": "sha256:7ea5066862dcde784cb49ba556e5989a3b48bbc82c99a492987e71a664d18d8b",
      "timeout_sec": 1
    }
  },
  "harness_regressions": {
    "command": "python3 -m unittest -v test_harness.py",
    "tests_run": 11,
    "failures": 0,
    "errors": 0,
    "passed": true,
    "test_source_sha256": "50b48d62707c573590f6c58d068b0cedec660185cb47d75af82d4b0d49780a3b",
    "harness_sources": {
      "codex_continue.py": "ddbbbc256dd7d4c25e6c1478dc7b4e902ca380f905197176f8e2075977a9d723",
      "run.py": "dd876e08e49b164484d8174047a43f889c2908296e7e0dc9aa361ce14ff167f1",
      "task_terminal.py": "f55849a767ff159d3cee282cacb1ee15bedbfd3277421077a49c1ceb2e7fd25e"
    }
  },
  "analysis_notes": [
    "Tuesday checklist: shared harness pinned; full single-turn specs and Linux project tools matched; effective context, output cap, compaction defaults and budgets audited; untouched and known-good controls validated for Returns and the planned Vitest audit task.",
    "Stock Returns: 61 baseline tests and 20 subtests passed. The feature suite stopped after 17 passes because Valid(5).lash(recover) returned None rather than Valid(5).",
    "ADAPT Returns: the baseline passed, but the first feature test failed because apply reversed the function/value direction and attempted to call an integer.",
    "Both coding sessions completed normally, used the shared Linux terminal and passed all effective-setting checks. Both frozen patches received reward 0. This is one selected smoke pair, not an accuracy estimate.",
    "The initial stock Kombu smoke patch stalled in test_FilesystemTransport::test_produce_consume. It was manually interrupted, retained as unscored and used to identify missing verifier-container cleanup. No hidden grading feedback was supplied to either coding actor.",
    "Next: Victor P. should check out this shared harness and run the same Returns smoke pair on his machine. Run the planned paired Vitest case next, inspect its traces and implementations, then split the remaining task pairs across machines. The Tuesday work does not include those distributed runs or the full manual context-retention analysis.",
    "The currently cached Vitest image is ready for that paired audit. One older unfinished Atlas image was preserved under cs224v-pilot-preserved so its historical frozen patch remains gradeable. Raw workspaces, traces, credentials and the private ADAPT release stay local."
  ],
  "architecture": {
    "controller": "Pinned macOS ADAPT binary, both arms",
    "coding": "Separate Linux containers from the same upstream image ID",
    "project_io": "Shared task_terminal MCP tool; hidden tests and credentials are not mounted",
    "verifier": "Fresh Linux container from the coding image; frozen patch and upstream tests",
    "network": "Follow upstream task allow_internet setting for both coding and grading",
    "compaction": "Pinned Codex default: 43,200-token automatic threshold for 48K context; 45,600 usable input tokens. No override.",
    "limitations": [
      "The supplied release has no Linux binary, so the controller remains on macOS.",
      "Data-structure pytest validation is skipped by this release on macOS.",
      "The native host shell still exists; the shared prompt requires all project work through the Linux tool.",
      "Compaction defaults are derived from the exact Codex source commit named in the release license; actual context pressure still requires trace review.",
      "The smoke task was selected using a previously passing patch and is not an unbiased accuracy estimate.",
      "Old macOS coding pilot results are a separate experiment."
    ]
  }
}
```
