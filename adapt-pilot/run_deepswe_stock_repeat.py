"""Run a fresh stock Codex arm for all 25 DeepSWE tasks."""

import json
import os
from pathlib import Path
import subprocess
import sys

import campaign
import run


ROOT = Path(__file__).resolve().parent
PRIMARY = ROOT / "output-wednesday-victor-c"
CROSS_RUN = ROOT / "output-deepswe-victor-c"
OUTPUT = ROOT / "output-deepswe-stock-repeat"
PLAN_PATH = CROSS_RUN / "deepswe-plan.json"


def copy_validation():
    for source in [
        PRIMARY / "verifier-validation.json",
        *PRIMARY.glob("validation/*/*/validation.json"),
    ]:
        destination = OUTPUT / source.relative_to(PRIMARY)
        destination.parent.mkdir(parents=True, exist_ok=True)
        run.save(destination, json.loads(source.read_text()))


def update_summary(state, code, tasks):
    rows = [row for row in run.records(OUTPUT) if row["task"] in tasks and row["arm"] == "stock"]
    latest = {}
    for row in rows:
        current = latest.get(row["task"])
        if current is None or row.get("updated", "") > current.get("updated", ""):
            latest[row["task"]] = row
    scored = [row for row in latest.values() if row["status"] == "scored"]
    summary = {
        "state": state,
        "updated": run.now(),
        "tasks": len(tasks),
        "scored": len(scored),
        "passed": sum(row["reward"] == 1 for row in scored),
        "unscored": {
            task: {
                "status": latest.get(task, {}).get("status", "not started"),
                "detail": latest.get(task, {}).get("detail"),
            }
            for task in tasks
            if latest.get(task, {}).get("status") != "scored"
        },
        "exit_code": code,
        "configuration": json.loads((OUTPUT / "manifest.json").read_text())["configuration"],
        "assignment_plan_sha256": json.loads(PLAN_PATH.read_text())["plan_sha256"],
    }
    run.save(OUTPUT / "stock-repeat-status.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main():
    plan = campaign.read_plan(PLAN_PATH)
    tasks = [
        task for task in json.loads((PRIMARY / "manifest.json").read_text())["task_order"]
        if task.startswith("deepswe_")
    ]
    if len(tasks) != 25 or any(task not in plan["assignments"]["victor-c"] for task in tasks):
        raise ValueError("Expected Victor C's local plan to include all 25 DeepSWE tasks")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    run.save(OUTPUT / "manifest.json", json.loads((PRIMARY / "manifest.json").read_text()))
    copy_validation()
    campaign.bind_output(OUTPUT, plan, "victor-c")

    environment = dict(
        os.environ,
        SWE_CAMPAIGN_OWNER="victor-c",
        SWE_CAMPAIGN_PLAN_SHA256=plan["plan_sha256"],
    )
    for task in tasks:
        rows = [row for row in run.records(OUTPUT)
                if row["task"] == task and row["arm"] == "stock"]
        if any(row["status"] == "scored" for row in rows):
            continue
        command = [
            sys.executable, str(ROOT / "run.py"), "run", "--output", str(OUTPUT),
            "--arm", "stock", "--cycle-images", "--local-rubric", "--task", task,
        ]
        code = subprocess.run(command, env=environment).returncode
        if code in (75, 130):
            update_summary("quota" if code == 75 else "paused", code, tasks)
            return code
    summary = update_summary("finished", 0, tasks)
    return 0 if summary["scored"] == len(tasks) else 2


if __name__ == "__main__":
    sys.exit(main())
