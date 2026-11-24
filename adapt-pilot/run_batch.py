#!/usr/bin/env python3
"""Run assigned pairs, recover grading artifacts, and retain unscored cases."""

import argparse
import fcntl
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

import campaign
import evaluation_adapter
import run


def latest(output, task, arm):
    rows = [row for row in run.records(output) if row["task"] == task and row["arm"] == arm]
    scored = [row for row in rows if row["status"] == "scored"]
    return (scored or rows)[-1] if rows else None


def invoke_arm(output, task, arm, binding):
    env = dict(os.environ, SWE_CAMPAIGN_OWNER=binding["owner"],
               SWE_CAMPAIGN_PLAN_SHA256=binding["plan_sha256"])
    return subprocess.run([sys.executable, str(run.ROOT / "actor_runtime.py"), "run",
                           "--output", str(output), "--task", task, "--arm", arm,
                           "--local-rubric", "--cycle-images"], env=env).returncode


def restore_image(output, row):
    if not row or not row.get("image_id"):
        return
    probe = subprocess.run(["docker", "image", "inspect", row["image_id"]],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not probe.returncode:
        return
    if row.get("retained_image_archive"):
        path = output / row["retained_image_archive"]
        subprocess.run(["docker", "load", "--input", str(path)], check=True, stdout=subprocess.DEVNULL)
        run.docker("tag", row["image_id"], run.task_image_tag(row["task"]))


def quota_in_logs(attempt):
    for path in [attempt / "agent.log", *attempt.glob("grading*/rubric-codex/call-*/stderr.log")]:
        if path.is_file():
            with path.open("rb") as stream:
                stream.seek(max(0, path.stat().st_size - 16000))
                if run.QUOTA.search(stream.read().decode(errors="replace")):
                    return True
    return False


def retain_and_release(output, task, rows, manifest):
    """Keep immutable prebuilt digests or archive an unfinished built image."""
    usable = [row for row in rows if row and row.get("image_id")]
    if not usable:
        return
    image = usable[-1]["image_id"]
    if subprocess.run(["docker", "image", "inspect", image], stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode:
        return
    if not usable[-1].get("registry_digests"):
        directory = output / "retained-images"
        directory.mkdir(exist_ok=True)
        archive = directory / (image.split(":")[-1] + ".tar.gz")
        if not archive.exists():
            print(f"Archiving the unfinished task image for {task}", flush=True)
            with subprocess.Popen(["docker", "save", image], stdout=subprocess.PIPE) as process:
                with gzip.open(archive, "wb", compresslevel=1) as compressed:
                    while chunk := process.stdout.read(1024 * 1024):
                        compressed.write(chunk)
                if process.wait():
                    archive.unlink(missing_ok=True)
                    raise RuntimeError("Could not preserve unfinished task image")
        for row in usable:
            run.checkpoint(output, output / row["artifact_path"], row, manifest,
                           retained_image_archive=str(archive.relative_to(output)))
    settings = run.tomllib.loads((run.SINGLE_TURN / task / "task.toml").read_text())
    for ref in (run.task_image_tag(task), settings["environment"].get("docker_image")):
        if ref and run.local_image_id(ref) == image:
            run.docker("image", "rm", ref)


def execute(args):
    output = args.output.resolve()
    plan = campaign.read_plan(args.plan)
    binding = campaign.bind_output(output, plan, args.owner, args.calibration)
    manifest = json.loads((output / "manifest.json").read_text())
    if manifest["configuration"] != plan["configuration"]:
        raise ValueError("Campaign configuration differs from the pinned plan")
    config = manifest["configuration"]
    tasks = campaign.arrange_tasks(output, campaign.selected_tasks(plan, args.owner, args.calibration, args.task))
    # Finish any task with a locally cached image before retrying a deferred task.
    tags = set(run.docker("image", "ls", "--format", "{{.Repository}}:{{.Tag}}",
                          "--filter", f"reference={run.TASK_IMAGE_REPO}:*").splitlines())
    tasks.sort(key=lambda task: run.task_image_tag(task) not in tags)
    deferred = []
    for task in tasks:
        for arm in run.ARMS:
            row = latest(output, task, arm)
            if row and row["status"] == "scored":
                continue
            if row and row.get("artifact_path"):
                attempt = output / row["artifact_path"]
                if any(attempt.glob("grading*/timeout.json")):
                    deferred.append({"task": task, "arm": arm, "status": "blocked",
                                     "detail": "The frozen candidate already reached the verifier time limit."})
                    print(f"Skipping repeat after verifier timeout: {task} {arm}", flush=True)
                    continue
            restore_image(output, row)
            code = invoke_arm(output, task, arm, binding)
            row = latest(output, task, arm)
            if code == 130:
                return code
            if code == 75 or (row and row["status"] == "quota"):
                return 75
            if row and row["status"] == "scored":
                continue
            if not row:
                raise RuntimeError("Runner stopped without an attempt record")
            attempt = output / row["artifact_path"]
            if quota_in_logs(attempt):
                run.checkpoint(output, attempt, row, manifest, status="quota", detail="Account quota reached; candidate saved.")
                return 75
            verifier_timed_out = any(attempt.glob("grading*/timeout.json"))
            if row.get("patch_sha256") and row.get("agent_exit") == "completed" and not verifier_timed_out:
                print(f"Recovering saved verifier candidate: {task} {arm}", flush=True)
                try:
                    with (output / ".lock").open("w") as lock:
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        reward = evaluation_adapter.grade_saved(output, attempt, row, manifest, config)
                    print(f"Saved recovered score: {task} {arm} {reward:g}", flush=True)
                except run.QuotaReached as exc:
                    run.checkpoint(output, attempt, row, manifest, status="quota", detail=str(exc))
                    return 75
                except (run.Blocked, ValueError, OSError, subprocess.SubprocessError) as exc:
                    run.checkpoint(output, attempt, row, manifest, status="blocked", detail=str(exc))
            if row["status"] != "scored":
                deferred.append({"task": task, "arm": arm, "status": row["status"], "detail": row.get("detail")})
                print(f"Retained unscored case: {task} {arm}", flush=True)
        rows = [latest(output, task, arm) for arm in run.ARMS]
        if all(row and row["status"] == "scored" for row in rows):
            run.retire_scored_image(task, run.records(output))
        else:
            retain_and_release(output, task, rows, manifest)
        run.save(output / "batch-status.json", {"updated": run.now(), "last_task": task,
                 "supervisor_sha256": run.digest(Path(__file__)), "deferred": deferred,
                 "completed_pairs": campaign.status(output, plan)["completed_pairs"]})
    return 2 if deferred else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=campaign.DEFAULT_PLAN)
    parser.add_argument("--owner", required=True, choices=campaign.OWNERS)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--task", action="append")
    parser.add_argument("--calibration", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / ".campaign.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return execute(args)


if __name__ == "__main__":
    sys.exit(main())
