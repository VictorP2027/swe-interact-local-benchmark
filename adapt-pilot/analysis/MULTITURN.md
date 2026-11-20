# Paired Vitest retention test

Use two fresh Vitest workspaces with the same base commit and upstream task image. Start both actors without the full single-turn specification. Keep the pinned actor model, medium effort, 48K context setting and coding budget in both arms. Change the Codex harness between stock and ADAPT.

Run the upstream maintainer with the provided persona and GPT-5.5 high through the same gateway for each arm. Use a separate maintainer session per arm. Let each maintainer inspect its actor's workspace and reply through the original `ask_user` MCP tool. Preserve the five upstream stages in order.

| Stage | Fixture | Evidence to save |
| --- | --- | --- |
| 1 | `01_plan` | Initial prompt, actor plan and maintainer feedback |
| 2 | `02_implement` | Requirements delivered, clarification replies and implementation commits |
| 3 | `03_handoff` | Maintainer requests, revisions and handoff commit |
| 4 | `04_write_tests` | Test requirements and agent-authored test patch |
| 5 | `05_test_handoff` | Final requests, verdict and upstream reward |

Record each actual requirement disclosure with the arm, stage, message timestamp and trace reference. Track the first disclosure of sharding strategy, timestamp units, TTL formula, config serialization, sorting and isolation. Record the agent's first use of that evidence, any compaction, and whether the later model input preserves it. Adaptive responses can differ between arms even with the same maintainer configuration.

Before launching, validate a real maintainer response that includes a workspace tool call. The original code and fixtures are present. The required GPT-5.5 high gateway is unconfigured on this Mac, and the earlier relay has not completed a live exchange. No pair has been run under this protocol.

[SWE-Interact, §§2.3–2.4](https://arxiv.org/html/2606.30573v1#S2.SS3)
