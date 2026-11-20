# Future multi-turn comparison

The default experiment follows ADAPT Appendix C.2 on single-turn SWE-Interact tasks. A separate experiment can test how stock Codex and Codex + ADAPT react when requirements are revealed or revised during a task.

This folder preserves the earlier Mac-to-Docker maintainer adapter and MCP relay as reference code. They depend on helpers from the previous runner. Reconnect them to a dedicated multi-turn entry point and manifest before use. The maintainer transport and final verifier were tested separately. A live model exchange was not completed.

Use the same live simulator configuration and verifier in both arms. SWE-Interact's upstream configuration uses GPT-5.5 at high reasoning effort as the maintainer. Record the five stage prompts, simulator events, coding agent context settings, and final task reward.
