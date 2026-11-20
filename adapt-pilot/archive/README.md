# Historical harness code

These files preserve Victor C.'s earlier CS224V implementation for the automation comparison. Use the [current campaign guide](../WEDNESDAY.md) for new matched runs.

- [macos-singleturn](macos-singleturn/) contains the November 13 CLI controller, continuation wrapper, and configuration. The historical project workspace was on macOS and the verifier ran in Linux. The copy resolves the dataset and private release with the same environment variables as the current runner. Its old FastAPI image override refers to the original local image.
- [macos-singleturn/future-multiturn](macos-singleturn/future-multiturn/) preserves the experimental maintainer bridge and stdio relay. The archived bridge expects earlier runner helpers and requires a dedicated driver to run. It is reference code.
- [fastapi-pilot](fastapi-pilot/) preserves the initial staged FastAPI prompts and task-specific grading script. The script expects the old smoke image and a completed workspace snapshot in the documented format.

The archived CLI scripts and staged prompts are separate from the AppleScript automation discussed in the November 20 sync. The compiled release, account files, raw conversations, and request archives stay outside this public repository.
