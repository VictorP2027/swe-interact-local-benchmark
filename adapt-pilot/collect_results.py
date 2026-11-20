#!/usr/bin/env python3
"""Combine primary owner packets while rejecting calibration and mismatched pairs."""

import argparse
import json
from pathlib import Path

import campaign
import run


def collect(plan, inputs):
    owners = set()
    latest = {}
    sources = []
    for path in inputs:
        packet = json.loads(path.read_text())
        binding = packet.get("campaign") or {}
        owner = binding.get("owner")
        if owner not in campaign.OWNERS or binding.get("calibration") is not False:
            raise ValueError("Collect primary campaign packets; calibration and historical pilots are separate")
        if owner in owners:
            raise ValueError("Supply only the latest packet from each owner")
        owners.add(owner)
        manifest = packet["manifest"]
        if (binding["plan_sha256"] != plan["plan_sha256"] or
                manifest["configuration"] != plan["configuration"] or
                manifest["harness_sources"] != plan["source_sha256"]):
            raise ValueError("Packet configuration or harness differs from the shared plan")
        sources.append({"owner": owner, "packet": path.name, "sha256": run.digest(path)})
        for row in packet["attempts"]:
            task = row["task"]
            if task not in plan["assignments"][owner]:
                raise ValueError("Packet contains another owner's task")
            if (row.get("machine_id") != binding["machine_id"] or
                    row.get("campaign_owner") != owner or
                    row.get("campaign_plan_sha256") != plan["plan_sha256"]):
                raise ValueError("Attempt ownership or machine differs from the campaign")
            if row["status"] == "scored":
                expected = plan["configuration"]
                if (row.get("prompt_sha256") != plan["tasks"][task]["prompt_sha256"] or
                        row.get("runner_source_sha256") != plan["source_sha256"] or
                        not row.get("effective_settings", {}).get("passed") or
                        any(row.get("agent_settings", {}).get(k) != expected[k] for k in
                            ("model", "reasoning_effort", "context_window", "lane"))):
                    raise ValueError("Scored attempt does not match the effective settings or task specification")
            latest[(task, row["arm"])] = row
    pairs = []
    pending = []
    for owner, tasks in plan["assignments"].items():
        for task in tasks:
            rows = [latest.get((task, arm), {}) for arm in run.ARMS]
            if not all(row.get("status") == "scored" for row in rows):
                pending.append({"task": task, "owner": owner,
                                "states": {arm: row.get("status", "pending") for arm, row in zip(run.ARMS, rows)}})
                continue
            for field in ("machine_id", "image_id", "upstream_base", "actor_prompt_sha256", "agent_settings"):
                if rows[0].get(field) != rows[1].get(field):
                    raise ValueError(f"Unmatched pair: {task}, {field}")
            pairs.append({"task": task, "owner": owner, "family": plan["tasks"][task]["family"],
                          "category": plan["tasks"][task].get("category"),
                          "arms": dict(zip(run.ARMS, rows))})
    return {"format": "cs224v-combined-paired-results-v1", "plan_sha256": plan["plan_sha256"],
            "configuration": plan["configuration"], "source_packets": sources,
            "missing_owners": sorted(set(campaign.OWNERS) - owners), "expected_pairs": 75,
            "completed_pairs": len(pairs), "pairs": pairs, "unscored_or_pending": pending,
            "resolved": {arm: sum(pair["arms"][arm]["reward"] == 1 for pair in pairs) for arm in run.ARMS}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=campaign.DEFAULT_PLAN)
    parser.add_argument("--input", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    plan = campaign.read_plan(args.plan, verify_sources=False)
    result = collect(plan, args.input)
    if args.require_complete and result["completed_pairs"] != 75:
        raise ValueError("Not all 75 pairs have scored results")
    result["collector_sha256"] = run.digest(Path(__file__))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    run.save(args.output, result)
    print(f"Saved {result['completed_pairs']}/75 matched pairs to {args.output}")


if __name__ == "__main__":
    main()
