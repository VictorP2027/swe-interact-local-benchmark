#!/usr/bin/env python3
"""Run the backup shard on this Mac after the primary shard is fully scored."""

import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys

import campaign
import export_results
import run


# These tasks request offensive tooling features outside the backup run's scope.
EXCLUDED = {
    "deepswe_pwntools-tube-multiplexing",
    "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e",
}


def run_backup(primary, output, plan_path):
    if output == primary:
        raise ValueError("Use a separate output for the backup")
    plan = campaign.read_plan(plan_path)
    binding = json.loads((primary / "campaign.json").read_text())
    owner = binding["owner"]
    if binding["calibration"] or binding["plan_sha256"] != plan["plan_sha256"]:
        raise ValueError("Primary output must belong to this experiment")
    backup_owner = next(candidate for candidate in campaign.OWNERS if candidate != owner)
    tasks = campaign.selected_tasks(plan, backup_owner, False, None)
    eligible = [task for task in tasks if task not in EXCLUDED]
    primary_count = len(plan["assignments"][owner])
    result_path = output / "backup-status.json"
    provenance = {
        "role": "backup",
        "run_by": owner,
        "assigned_owner": backup_owner,
        "machine_id": binding["machine_id"],
        "plan_sha256": plan["plan_sha256"],
        "eligible_tasks": len(eligible),
        "excluded_tasks": sorted(set(tasks) & EXCLUDED),
    }

    def save_state(state, **fields):
        run.save(result_path, {**provenance, "state": state, "updated": run.now(), **fields})

    output.mkdir(parents=True, exist_ok=True)
    with (output / ".backup.lock").open("a") as backup_lock:
        fcntl.flock(backup_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        bound = campaign.bind_output(output, plan, backup_owner)
        if bound["machine_id"] != binding["machine_id"]:
            raise ValueError("Backup must run on the same Mac as the primary shard")
        run.save(output / "backup.json", provenance)
        save_state("waiting_for_primary", required_pairs=primary_count)
        print(f"Backup queued for {len(eligible)} tasks after {primary_count} primary pairs are scored.", flush=True)
        with (primary / ".campaign.lock").open("a") as primary_lock:
            fcntl.flock(primary_lock, fcntl.LOCK_EX)
            status = campaign.status(primary, plan)
            scored = status["completed_pairs"]
            if scored != primary_count:
                save_state("primary_incomplete", required_pairs=primary_count, scored_pairs=scored)
                print(f"Backup held at {scored}/{primary_count} scored primary pairs.", flush=True)
                return 2
            config, manifest = run.load_experiment(output, local_rubric=True)
            validation = json.loads((primary / "verifier-validation.json").read_text())
            if (manifest != json.loads((primary / "manifest.json").read_text()) or
                    validation.get("passed") is not True or validation.get("configuration") != config or
                    validation.get("source_sha256") != manifest["harness_sources"]):
                raise ValueError("The existing verifier validation does not match the backup configuration")
            # Reference the same-machine validation rather than run the controls again.
            run.save(output / "verifier-validation.json", validation)
            for path in primary.glob("validation/*/*/validation.json"):
                target = output / path.relative_to(primary)
                target.parent.mkdir(parents=True, exist_ok=True)
                run.save(target, json.loads(path.read_text()))
            export_results.export(primary, primary / "shareable")
            run.save(primary / "shareable/campaign-status.json", status)
            save_state("running", primary_scored_pairs=scored)
            command = [sys.executable, str(run.ROOT / "run_batch.py"), "--plan", str(plan_path),
                       "--owner", backup_owner, "--output", str(output)]
            for task in eligible:
                command.extend(("--task", task))
            code = subprocess.run(command).returncode
            result = campaign.status(output, plan)
            export_results.export(output, output / "shareable")
            run.save(output / "shareable/campaign-status.json", result)
            save_state("finished" if code == 0 else "stopped", exit_code=code,
                       primary_scored_pairs=scored, backup_scored_pairs=result["completed_pairs"])
            return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--plan", default=campaign.DEFAULT_PLAN, type=Path)
    args = parser.parse_args()
    sys.exit(run_backup(args.primary.resolve(), args.output.resolve(), args.plan.resolve()))
