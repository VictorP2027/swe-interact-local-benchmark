# Tuesday deliverable

Finish one reproducible single-turn harness, validate the grader and run one matched smoke pair before scaling.

1. Pin GPT-6 Luna, medium effort, Codex 0.159.0, ADAPT commit `166c433f`, a 48K context, a 10K tool-output cap and a 3,600-second coding budget. Pass catalog share 0.1 explicitly. Keep model seed and temperature unset because the supplied runner does not expose them.
2. Give stock and ADAPT the same full task specification, execution instructions, project tool, base commit, Linux image, resources and network policy. Resume clarification questions with `continue` inside the same budget.
3. Read and edit project code through `task_terminal.run`. Keep the original repository and installed dependencies together inside Linux. Start a separate container for each arm. Freeze its code changes before destroying it.
4. Grade each frozen patch in a fresh container from the same image using the supplied tests. Keep the hidden tests, control patches and grader feedback outside both coding containers.
5. Reject the untouched audit checkout with reward 0 and accept Victor P.'s archived passing patch with reward 1. Use that patch only as a grader control. Save its hash, test hashes, image ID and configuration.
6. Audit the generated Codex config and model catalog after each arm: model, effort, effective context, output cap, CLI/build version, catalog share and budget. Keep the pinned Codex compaction default; derive its 43,200-token automatic threshold and 45,600 usable input tokens from the exact Codex source commit named in the release license.
7. Save every completed or interrupted attempt atomically. Resume grading a saved patch without rerunning the actor. Keep infrastructure failures outside accuracy denominators. Retire task images only after both scores are saved.
8. Export one `HANDOFF.md` containing the architecture, limits, configuration, verifier controls and both result records. Keep raw traces and the private release local.

The supplied release only offers a macOS binary. The shared Linux terminal fixes project runtime/dependency parity while keeping the original ADAPT controller and context policy. This is a documented tool adaptation, not a Linux execution of the original controller. Native host tools remain available for ADAPT context files. Project edits in the host workspace invalidate a run; the prompt requires all project commands through Linux. The release also skips data-structure pytest validation on macOS.

Use the commands in [README.md](README.md) to reproduce the validation and paired smoke test. `test_harness.py` checks the scoring and tool adapter; its eleven checks are harness regressions, not eleven additional SWE-Interact tasks. The smoke pair uses one of the 75 tasks and does not estimate benchmark accuracy.

Keep the historical macOS coding pilot and Victor P.'s direct-chat results separate from the new runs. The archived passing patch is suitable for checking the verifier, but it does not establish a matched baseline model or protocol.

The first Kombu controls returned 0 and 1, but the new stock implementation stalled in a filesystem-consumer test during its smoke run. That interrupted attempt and patch remain saved as unscored. The final paired smoke uses Returns to check the complete execution path. Vitest remains the planned manual analysis task; its grader is validated separately.
