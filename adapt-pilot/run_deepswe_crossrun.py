"""Resume the paired DeepSWE run on Victor C's machine across all 25 tasks."""
import fcntl
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import campaign
import run
from run_batch import latest

OUTPUT = ROOT / "output-deepswe-victor-c"
PRIMARY = ROOT / "output-wednesday-victor-c"
PLAN_PATH = OUTPUT / "deepswe-plan.json"


def main():
    original = campaign.read_plan(campaign.DEFAULT_PLAN)
    owner = "victor-c"
    other = "victor-p"
    assigned = [task for task in original["assignments"][owner] if task.startswith("deepswe_")]
    extra = [task for task in original["assignments"][other] if task.startswith("deepswe_")]
    if len(assigned) + len(extra) != 25:
        raise ValueError("Expected all 25 DeepSWE tasks across the two original assignments")
    control = json.loads((PRIMARY / "verifier-validation.json").read_text())
    config, manifest = run.load_experiment(OUTPUT, local_rubric=True)
    if (manifest != json.loads((PRIMARY / "manifest.json").read_text())
            or control.get("passed") is not True or control["configuration"] != config
            or control["source_sha256"] != manifest["harness_sources"]):
        raise ValueError("Saved manifest or verifier control does not match the follow-up settings")
    for path in [PRIMARY / "verifier-validation.json", *PRIMARY.glob("validation/*/*/validation.json")]:
        target = OUTPUT / path.relative_to(PRIMARY)
        target.parent.mkdir(parents=True, exist_ok=True)
        run.save(target, json.loads(path.read_text()))
    plan = {key: value for key, value in original.items() if key != "plan_sha256"}
    plan["assignments"] = {
        owner: [*original["assignments"][owner], *extra],
        other: [task for task in original["assignments"][other] if task not in extra],
    }
    plan["policy"] = "DeepSWE cross-run. The original primary assignments and results are preserved; all 25 DeepSWE tasks are included."
    plan["plan_sha256"] = campaign.checksum(plan)
    if PLAN_PATH.exists() and json.loads(PLAN_PATH.read_text()) != plan:
        # Migrate the earlier local plan that omitted the pwntools task.
        previous = json.loads(PLAN_PATH.read_text())
        previous_without_hash = {key: value for key, value in previous.items() if key != "plan_sha256"}
        expected_previous = {key: value for key, value in plan.items() if key != "plan_sha256"}
        previous_extra = [task for task in extra if task != "deepswe_pwntools-tube-multiplexing"]
        previous_assignments = {
            owner: [*original["assignments"][owner], *previous_extra],
            other: [task for task in original["assignments"][other] if task not in previous_extra],
        }
        expected_previous["assignments"] = previous_assignments
        expected_previous["policy"] = "DeepSWE cross-run. The original primary assignments and results are preserved."
        old_binding = json.loads((OUTPUT / "campaign.json").read_text())
        if (previous_without_hash != expected_previous or old_binding["owner"] != owner
                or old_binding["plan_sha256"] != previous["plan_sha256"]):
            raise ValueError("Cannot safely extend the saved follow-up plan")
        old_binding["plan_sha256"] = plan["plan_sha256"]
        run.save(OUTPUT / "campaign.json", old_binding)
    run.save(PLAN_PATH, plan)
    supplemental = campaign.read_plan(PLAN_PATH)
    campaign.bind_output(OUTPUT, supplemental, owner)

    def checkpoint(state, **details):
        rows = {}
        for directory, selected in [(PRIMARY, assigned), (OUTPUT, extra)]:
            for record in run.records(directory):
                if record["task"] in selected and record["status"] == "scored":
                    rows[(record["task"], record["arm"])] = record
        totals = {}
        for arm in run.ARMS:
            scored = [row for (_, name), row in rows.items() if name == arm]
            totals[arm] = {"scored": len(scored), "passed": sum(row["reward"] == 1 for row in scored)}
        run.save(OUTPUT / "followup-status.json", {
            "state": state, "updated": run.now(), "eligible_task_count": len(assigned) + len(extra),
            "excluded_tasks": [], "config": config, "totals": totals,
            "scored_pairs": sum(all((task, arm) in rows for arm in run.ARMS) for task in assigned + extra),
            **details,
        })
        print(state, totals, flush=True)

    for label, directory, plan_path, tasks in [
        ("primary_deepswe", PRIMARY, campaign.DEFAULT_PLAN, assigned),
        ("supplemental_deepswe", OUTPUT, PLAN_PATH, extra),
    ]:
        checkpoint(label)
        # Launch just one pair at a time and refresh the combined status after it.
        for task in tasks:
            if all((row := latest(directory, task, arm)) and row["status"] == "scored"
                   for arm in run.ARMS):
                continue
            print(f"Starting {label} pair: {task}", flush=True)
            code = subprocess.run([
                sys.executable, str(ROOT / "run_batch.py"), "--owner", owner, "--plan", str(plan_path),
                "--output", str(directory), "--task", task,
            ]).returncode
            checkpoint(label, last_task=task, last_exit_code=code)
            if code not in (0, 2):
                checkpoint("quota" if code == 75 else "stopped", last_task=task, exit_code=code)
                return code
    checkpoint("finished")
    result = json.loads((OUTPUT / "followup-status.json").read_text())
    if result["scored_pairs"] != len(assigned) + len(extra):
        checkpoint("incomplete")
        return 2
    return 0


if __name__ == "__main__":
    with (OUTPUT / ".followup.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.exit(main())
