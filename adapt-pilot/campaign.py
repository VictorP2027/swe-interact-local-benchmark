#!/usr/bin/env python3
"""Plan and run Wednesday's paired tasks without splitting arms across machines."""

import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import tomllib

import run
from provenance import machine_id

OWNERS = ("victor-c", "victor-p")
SMOKE_TASK = "deepswe_vitest-duration-sharding"
DEFAULT_PLAN = run.ROOT / "assignments/wednesday.json"


def checksum(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def create_plan(manifest):
    assignments = {owner: [] for owner in OWNERS}
    for family_index, family in enumerate(run.FAMILIES.values()):
        tasks = [task for task in manifest["task_order"] if manifest["tasks"][task]["family"] == family]
        for index, task in enumerate(tasks):
            assignments[OWNERS[(index + family_index) % 2]].append(task)
    if SMOKE_TASK in assignments["victor-p"]:
        swap = next(task for task in reversed(assignments["victor-c"]) if task.startswith("deepswe_"))
        assignments["victor-c"].remove(swap)
        assignments["victor-p"].remove(SMOKE_TASK)
        assignments["victor-c"].append(SMOKE_TASK)
        assignments["victor-p"].append(swap)
    for owner in OWNERS:
        assignments[owner].sort(key=manifest["task_order"].index)
    assignments["victor-c"].remove(SMOKE_TASK)
    assignments["victor-c"].insert(0, SMOKE_TASK)
    task_metadata = {}
    for task in manifest["tasks"]:
        directory = run.SINGLE_TURN / task
        definition = tomllib.loads((directory / "task.toml").read_text())
        task_metadata[task] = {"family": manifest["tasks"][task]["family"],
                               **definition.get("metadata", {}),
                               "image_reference": definition["environment"].get("docker_image"),
                               "environment_dockerfile_sha256": run.digest(directory / "environment/Dockerfile"),
                               "network": run.task_network(directory),
                               "prompt_sha256": run.digest(directory / "instruction.md")}
    plan = {"format": "cs224v-paired-campaign-v1", "seed": manifest["configuration"]["task_order_seed"],
            "configuration": manifest["configuration"], "source_sha256": manifest["harness_sources"],
            "assignments": assignments, "tasks": task_metadata, "smoke_task": SMOKE_TASK,
            "policy": "Both arms of every primary task run on its owner's same machine. Calibration runs are separate."}
    plan["plan_sha256"] = checksum(plan)
    return plan


def read_plan(path, verify_sources=True):
    plan = json.loads(path.read_text())
    original = dict(plan)
    expected = original.pop("plan_sha256")
    if checksum(original) != expected:
        raise ValueError("Assignment plan checksum changed")
    assigned = [task for tasks in plan["assignments"].values() for task in tasks]
    if len(assigned) != 75 or len(set(assigned)) != 75 or set(assigned) != set(plan["tasks"]):
        raise ValueError("Expected exactly 75 uniquely assigned tasks")
    if verify_sources and plan["source_sha256"] != run.source_hashes():
        raise ValueError("Harness changed after the plan was pinned. Check out the plan's source version.")
    return plan


def bind_output(output, plan, owner, calibration=False):
    output.mkdir(parents=True, exist_ok=True)
    binding = {"plan_sha256": plan["plan_sha256"], "owner": owner, "machine_id": machine_id(),
               "calibration": calibration, "system": platform.system(), "architecture": platform.machine()}
    path = output / "campaign.json"
    if path.exists() and json.loads(path.read_text()) != binding:
        raise ValueError("Output belongs to another machine, owner, plan or calibration mode. Keep each pair on its original machine.")
    run.save(path, binding)
    return binding


def selected_tasks(plan, owner, calibration, requested):
    allowed = [plan["smoke_task"]] if calibration else plan["assignments"][owner]
    tasks = requested or allowed
    if len(set(tasks)) != len(tasks) or set(tasks) - set(allowed):
        raise ValueError("Requested tasks are duplicated or assigned to the other owner")
    return list(tasks)


def invoke(command, output, tasks=(), extra=(), binding=None, keep_awake=False):
    args = [sys.executable, str(run.ROOT / "run.py"), command, "--output", str(output), "--local-rubric"]
    for task in tasks:
        args += ["--task", task]
    args += list(extra)
    if keep_awake and platform.system() == "Darwin":
        args = ["caffeinate", "-i", *args]
    env = dict(os.environ)
    if binding:
        env.update(SWE_CAMPAIGN_OWNER=binding["owner"], SWE_CAMPAIGN_PLAN_SHA256=binding["plan_sha256"])
    return subprocess.run(args, env=env).returncode


def arrange_tasks(output, tasks):
    rows = run.records(output)
    for task in tasks:
        scored = {r["arm"] for r in rows if r["task"] == task and r["status"] == "scored"}
        if scored != set(run.ARMS) and any(r["task"] == task and r.get("image_id") for r in rows):
            return [task, *[t for t in tasks if t != task]]
    control = json.loads((output / "verifier-validation.json").read_text())
    task = control["task"]
    if run.local_image_id(run.task_image_tag(task)) == control["image_id"]:
        if task in tasks:
            return [task, *[t for t in tasks if t != task]]
        if not any(r["task"] == task for r in rows):
            # Control-only images have no pending coding arm to preserve.
            image_settings = tomllib.loads((run.SINGLE_TURN / task / "task.toml").read_text())
            for ref in (run.task_image_tag(task), image_settings["environment"]["docker_image"]):
                if run.local_image_id(ref) == control["image_id"]:
                    run.docker("image", "rm", ref)
    return tasks


def status(output, plan):
    rows = run.records(output)
    latest = {(row["task"], row["arm"]): row for row in rows}
    binding = json.loads((output / "campaign.json").read_text())
    tasks = selected_tasks(plan, binding["owner"], binding["calibration"], None)
    pairs = []
    for task in tasks:
        pair = [latest.get((task, arm), {}) for arm in run.ARMS]
        if all(row.get("status") == "scored" for row in pair):
            if len({row.get("machine_id") for row in pair}) != 1 or pair[0].get("machine_id") != binding["machine_id"]:
                raise ValueError(f"Pair ran on different machines: {task}")
            if any(row.get("campaign_owner") != binding["owner"] or
                   row.get("campaign_plan_sha256") != plan["plan_sha256"] or
                   not row.get("effective_settings", {}).get("passed") for row in pair):
                raise ValueError(f"Pair does not match the campaign or effective settings: {task}")
            for field in ("image_id", "upstream_base", "prompt_sha256", "actor_prompt_sha256", "runner_source_sha256"):
                if pair[0].get(field) != pair[1].get(field):
                    raise ValueError(f"Paired settings differ: {task}, {field}")
            pairs.append(task)
    return {"binding": binding, "assigned_tasks": len(tasks), "completed_pairs": len(pairs),
            "completed_tasks": pairs, "attempt_states": dict(Counter(row["status"] for row in latest.values())),
            "wins": {arm: sum(latest[(task, arm)]["reward"] == 1 for task in pairs) for arm in run.ARMS}}


def judge_smoke(output, plan):
    logs = output / "judge-smoke"
    logs.mkdir(exist_ok=True)
    image = run.task_image_tag(plan["smoke_task"])
    body = {"model": "gpt-6-luna", "messages": [
        {"role": "system", "content": "Grade whether the supplied calculation is correct. Return one rating, YES or NO, and a short justification."},
        {"role": "user", "content": "Criterion: two plus two equals four. Candidate: 2 + 2 = 4."}]}
    program = ("import os,json,urllib.request; body=json.load(__import__('sys').stdin); "
               "req=urllib.request.Request(os.environ['EVAL_BASE_URL']+'/chat/completions', "
               "data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+os.environ['EVAL_API_KEY'],"
               "'Content-Type':'application/json'}); print(urllib.request.urlopen(req,timeout=310).read().decode())")
    with run.verifier_environment("rf_judge_smoke", plan["configuration"], logs) as (env, options):
        result = subprocess.run(["docker", "run", "--rm", "--platform", "linux/amd64", *options,
                                 "--interactive", "--entrypoint", "python3", image, "-c", program],
                                input=json.dumps(body), capture_output=True, text=True, env=env, timeout=330)
    if result.returncode:
        raise RuntimeError("Local judge smoke failed; inspect the private judge-smoke artifacts")
    response = json.loads(result.stdout)
    rating = json.loads(response["choices"][0]["message"]["content"])["ratings"][0]
    proof = {"passed": rating["status"] == "YES", "model": response["model"],
             "transport": "Docker to local bridge to headless Codex using its existing sign-in",
             "usage": response["usage"], "rating": rating}
    run.save(logs / "smoke-result.json", proof)
    if not proof["passed"]:
        raise ValueError("Local judge returned the wrong synthetic rating")
    print("Headless rubric transport passed (no tool use).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "prepare", "run", "status", "judge-smoke", "review", "export"))
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--owner", choices=OWNERS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--task", action="append")
    parser.add_argument("--calibration", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        with tempfile.TemporaryDirectory() as folder:
            _, manifest = run.load_experiment(Path(folder), local_rubric=True)
            plan = create_plan(manifest)
        args.plan.parent.mkdir(parents=True, exist_ok=True)
        if args.plan.exists() and json.loads(args.plan.read_text()) != plan:
            raise ValueError("Existing plan differs; use a new --plan path for a new campaign")
        run.save(args.plan, plan)
        print(json.dumps({owner: len(tasks) for owner, tasks in plan["assignments"].items()}))
        return 0
    plan = read_plan(args.plan, verify_sources=args.command not in {"status", "review", "export"})
    if not args.output:
        parser.error("--output is required")
    output = args.output.resolve()
    if args.command in {"status", "review", "export"}:
        summary = status(output, plan)
        if args.command == "status":
            print(json.dumps(summary, indent=2))
        elif args.command == "review":
            import review
            for task in args.task or summary["completed_tasks"]:
                review.build(output, task, args.destination or output / "manual-review" / task)
        else:
            import export_results
            destination = args.destination or output / "shareable"
            export_results.export(output, destination)
            run.save(destination / "campaign-status.json", summary)
        return 0
    if not args.owner:
        parser.error("--owner is required")
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".campaign.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        binding = bind_output(output, plan, args.owner, args.calibration)
        tasks = selected_tasks(plan, args.owner, args.calibration, args.task)
        if args.dry_run:
            print(json.dumps({"binding": binding, "tasks": tasks, "arms": list(run.ARMS)}, indent=2))
            return 0
        if args.command == "prepare":
            code = invoke("preflight", output)
            if code:
                return code
            manifest = json.loads((output / "manifest.json").read_text())
            if manifest["configuration"] != plan["configuration"]:
                raise ValueError("Configuration differs from the pinned campaign plan")
            task = plan["smoke_task"]
            return invoke("validate", output, [task], ["--cycle-images", "--known-good-patch",
                          str(run.ROOT.parent / "patches" / f"{task}.patch")])
        if args.command == "judge-smoke":
            judge_smoke(output, plan)
            return 0
        tasks = arrange_tasks(output, tasks)
        return invoke("run", output, tasks, ["--cycle-images"], binding, keep_awake=True)


if __name__ == "__main__":
    sys.exit(main())
