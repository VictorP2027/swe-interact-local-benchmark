#!/usr/bin/env python3
"""Start the pinned actor runner with a recorded, host-compatible CPU limit."""

from functools import wraps
import sys
import tomllib

import run


def cap_coding_cpus(args, available):
    if args[:1] != ("run",) or "cs224v.role=coding" not in args:
        return args
    index = args.index("--cpus") + 1
    adjusted = list(args)
    adjusted[index] = min(float(args[index]), available)
    return tuple(adjusted)


def main():
    docker = run.docker
    trial = run.trial
    available = int(docker("info", "--format", "{{.NCPU}}"))

    def host_docker(*args, **kwargs):
        return docker(*cap_coding_cpus(args, available), **kwargs)

    @wraps(trial)
    def recorded_trial(output, manifest, config, task, arm, attempt, row, cycle=False):
        settings = tomllib.loads((run.SINGLE_TURN / task / "task.toml").read_text())["environment"]
        requested = settings.get("cpus", 2)
        run.checkpoint(output, attempt, row, manifest, actor_cpus={
            "requested": requested, "effective": min(requested, available),
            "runtime_adapter_sha256": run.digest(run.ROOT / "actor_runtime.py"),
        })
        return trial(output, manifest, config, task, arm, attempt, row, cycle)

    run.docker = host_docker
    run.trial = recorded_trial
    return run.main()


if __name__ == "__main__":
    sys.exit(main())
