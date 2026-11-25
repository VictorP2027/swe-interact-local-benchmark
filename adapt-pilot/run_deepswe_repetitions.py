#!/usr/bin/env python3
"""Run three fresh stock/ADAPT pairs each for Wazero, KCP, and Kombu."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

import campaign
import run
from run_batch import latest


REGISTRY = "public.ecr.aws/d3j8x8q7/swe-bench-202605"
# Image IDs and registry digests from the current paired campaign.
IMAGES = {
    "deepswe_wazero-multi-module-snapshots": (
        "95d33baf0f33e75232442896a661a7d2d7b3dab1277ac7eea1c33e61f36eeeeb",
        "d9296c52cefa4a91df82d4c283475605822923855a488ef8433bd919a6fe0c68",
    ),
    "deepswe_kcp-go-multiplexed-kcp-streams": (
        "09314933bf2f4a8e74f889a9e34f4d1a3bfe0501cc32e5411eee044bce85ab8f",
        "42eeb7153103d8824d05fea1a5df51adaa6d7c50c363b1cb7ab1b3502d50fe71",
    ),
    "deepswe_kombu-single-active-consumer-priority": (
        "f4158875f866062831172c5c4b24f8fc042fa8d13feec31d390f6751139cf44d",
        "532b2458f9a85e47354912fda4c36ce47d1d1232f43a0ef6f35827e82a131a9e",
    ),
}


def direction(task, repetition):
    return "adapt" if (list(IMAGES).index(task) + repetition - 1) % 2 else "stock"


def slot(output, task, repetition):
    return output / task / f"repeat-{repetition:02d}"


def read_results(output, task, repetition):
    folder = slot(output, task, repetition)
    results = {}
    for arm in run.ARMS:
        row = latest(folder, task, arm)
        if not row:
            results[arm] = {"status": "pending"}
            continue
        artifact = folder / row["artifact_path"]
        if row.get("reused") or not artifact.resolve().is_relative_to(folder.resolve()):
            raise ValueError(f"Unexpected reused candidate: {task} repeat {repetition} {arm}")
        if row.get("image_id") and row["image_id"] != f"sha256:{IMAGES[task][0]}":
            raise ValueError(f"Unexpected image: {task} repeat {repetition} {arm}")
        results[arm] = {key: row[key] for key in (
            "status", "reward", "attempt", "updated", "patch_sha256", "image_id",
            "agent_usage", "verifier_exit_code", "agent_exit", "continuations",
        ) if key in row}
    return results


def snapshot(output, state, error=None, as_of=None):
    rows = []
    totals = {arm: {"scored": 0, "passed": 0} for arm in run.ARMS}
    for task in IMAGES:
        for repetition in range(1, 4):
            results = read_results(output, task, repetition)
            for arm, row in results.items():
                if row["status"] == "scored":
                    totals[arm]["scored"] += 1
                    totals[arm]["passed"] += row["reward"] == 1
            rows.append({"task": task, "rep": repetition, "first": direction(task, repetition), **results})
    data = {"state": state, "updated": as_of or run.now(), "target_pairs": 9,
            "scored_pairs": sum(all(row[arm]["status"] == "scored" for arm in run.ARMS) for row in rows),
            "totals": totals, "pairs": rows}
    if error:
        data["detail"] = error
    return data


def pin_plan(output, owner):
    plan = campaign.read_plan(campaign.DEFAULT_PLAN)
    for assigned in plan["assignments"].values():
        assigned[:] = [task for task in assigned if task not in IMAGES]
    plan["assignments"][owner].extend(IMAGES)
    del plan["plan_sha256"]
    plan["policy"] = "Three fresh repetitions of Wazero, KCP, and Kombu with both arms on the same machine."
    plan["plan_sha256"] = campaign.checksum(plan)
    path = output / "assignment.json"
    if path.exists() and json.loads(path.read_text()) != plan:
        raise ValueError("Output belongs to a different assignment or configuration.")
    run.save(path, plan)
    campaign.bind_output(output, plan, owner)
    return path, plan


def inspect_image(reference):
    result = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", reference],
                            text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def tag_pinned_image(task, config, control_dir):
    tag = run.task_image_tag(task)
    image, digest = (f"sha256:{value}" for value in IMAGES[task])
    run.guard_cycle_image(tag)
    if inspect_image(tag) not in ("", image):
        raise run.Blocked(f"Unexpected existing task tag for {task}")
    if not inspect_image(image):
        reference = f"{REGISTRY}@{digest}"
        if run.logged(["docker", "pull", "--platform", config["platform"], reference],
                      control_dir / "image-pull.log", timeout=900):
            raise run.Blocked(f"Pinned image pull failed for {task}. See image-pull.log.")
        if inspect_image(reference) != image:
            raise run.Blocked(f"Registry digest produced a different image for {task}")
    if inspect_image(image) != image:
        raise run.Blocked(f"Exact paired image unavailable for {task}")
    run.docker("tag", image, tag)
    return image


def control_task(output, task, config, manifest):
    controls = output / "controls" / task
    controls.mkdir(parents=True, exist_ok=True)
    path = controls / "verifier-validation.json"
    with (run.ROOT / ".image-cycle.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        image = tag_pinned_image(task, config, controls)
        if path.exists():
            evidence = json.loads(path.read_text())
            if (evidence["passed"] and evidence["image_id"] == image
                    and evidence["configuration"] == config and evidence["source_sha256"] == run.source_hashes()):
                return evidence
        solution = run.SINGLE_TURN / task / "solution/solution.patch"
        if run.validate_verifier(controls, config, manifest, task, solution, cycle=True):
            raise run.Blocked(f"Verifier controls did not score 0 and 1 for {task}")
        return json.loads(path.read_text())


def run_repetitions(output, owner):
    checkpoint = output / "status.json"
    path, plan = pin_plan(output, owner)
    config, manifest = run.load_experiment(output, local_rubric=True)
    if config != plan["configuration"]:
        raise ValueError("Experiment manifest differs from the pinned campaign.")
    run.save(checkpoint, snapshot(output, "running"))
    env = dict(os.environ, SWE_FRESH_REPETITIONS="1")
    active = set(run.docker("image", "ls", "--format", "{{.Repository}}:{{.Tag}}",
                            "--filter", f"reference={run.TASK_IMAGE_REPO}:*").splitlines())
    for task in sorted(IMAGES, key=lambda name: run.task_image_tag(name) not in active):
        remaining = [rep for rep in range(1, 4) if any(
            result["status"] != "scored" for result in read_results(output, task, rep).values())]
        if not remaining:
            continue
        print(f"Preparing pinned verifier for {task}", flush=True)
        evidence = control_task(output, task, config, manifest)
        image = evidence["image_id"]
        cache = f"cs224v-repeat-image:{IMAGES[task][0][:12]}"
        run.docker("tag", image, cache)
        try:
            for rep in remaining:
                folder = slot(output, task, rep)
                folder.mkdir(parents=True, exist_ok=True)
                run.save(folder / "manifest.json", manifest)
                run.save(folder / "verifier-validation.json", evidence)
                with (run.ROOT / ".image-cycle.lock").open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    tag_pinned_image(task, config, output / "controls" / task)
                first = direction(task, rep)
                command = [sys.executable, str(run.ROOT / "run_batch.py"), "--plan", str(path),
                           "--owner", owner, "--output", str(folder), "--task", task]
                if first == "adapt":
                    command.append("--adapt-first")
                print(f"{task} repeat {rep}/3, {first} first", flush=True)
                code = subprocess.run(command, env=env).returncode
                state = {75: "quota", 130: "paused"}.get(code, "running")
                status = snapshot(output, state)
                run.save(checkpoint, status)
                print(f"{status['scored_pairs']}/9 pairs scored", flush=True)
                if code in (75, 130):
                    return code
                if code not in (0, 2):
                    raise run.Blocked(f"Batch exited {code} on {task} repeat {rep}.")
        finally:
            if inspect_image(cache) == image:
                run.docker("image", "rm", cache)
    final = snapshot(output, "finished")
    if final["scored_pairs"] != final["target_pairs"]:
        final["state"] = "incomplete"
    run.save(checkpoint, final)
    return 0 if final["state"] == "finished" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", choices=campaign.OWNERS, default="victor-c")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    output = (args.output or run.ROOT / f"output-deepswe-three-repeats-{args.owner}").resolve()
    if args.status:
        previous = output / "status.json"
        data = json.loads(previous.read_text()) if previous.exists() else {"state": "pending"}
        print(json.dumps(snapshot(output, data["state"], data.get("detail"), data.get("updated")), indent=2))
        return 0
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".repetitions.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            return run_repetitions(output, args.owner)
        except KeyboardInterrupt:
            run.save(output / "status.json", snapshot(output, "paused"))
            return 130
        except (run.Blocked, ValueError, OSError, subprocess.SubprocessError) as error:
            print(str(error), file=sys.stderr)
            run.save(output / "status.json", snapshot(output, "blocked", str(error)))
            return 2


if __name__ == "__main__":
    sys.exit(main())
