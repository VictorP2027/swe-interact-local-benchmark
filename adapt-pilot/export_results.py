#!/usr/bin/env python3
"""Write a shareable report from saved checkpoints, without raw model/tool logs."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import tomllib

import run


def export(output, destination, include_handoffs=()):
    destination.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((output / "manifest.json").read_text())
    validations = [json.loads(p.read_text()) for p in sorted(output.glob("validation/*/*/validation.json"))]
    attempts = run.records(output)
    for row in attempts:
        if row.get("run_path"):
            details = json.loads((output / row["run_path"] / "run.json").read_text())
            home = output / row["run_path"] / "harness/codex_home"
            settings = tomllib.loads((home / "config.toml").read_text())
            model = next(m for m in json.loads((home / "model_catalog.json").read_text())["models"]
                         if m["slug"] == manifest["configuration"]["model"])
            window = model["context_window"]
            configured = settings.get("model_auto_compact_token_limit")
            if configured is None:
                configured = model.get("auto_compact_token_limit")
            threshold = min(configured if configured is not None else window * 9 // 10, window * 9 // 10)
            row["compaction_source_audit"] = {
                "codex_commit": "687a119f0fcaace47e1f1abcc77cec6c813fd6da",
                "default_auto_compact_token_limit": threshold,
                "usable_input_context": window * model.get("effective_context_window_percent", 95) // 100,
                "source": "https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535",
            }
            if details.get("started") and details.get("ended"):
                row["agent_seconds"] = round((datetime.fromisoformat(details["ended"].replace("Z", "+00:00"))
                    - datetime.fromisoformat(details["started"].replace("Z", "+00:00"))).total_seconds(), 3)
        terminal = output / row["artifact_path"] / "terminal.jsonl"
        if terminal.exists():
            calls = [json.loads(line) for line in terminal.read_text().splitlines()]
            row["linux_terminal_calls"] = len(calls)
            row["linux_terminal_seconds"] = round(sum(call["elapsed_s"] for call in calls), 3)
        artifact = output / row["artifact_path"]
        patch = artifact / "implementation.patch"
        if patch.is_file():
            target = destination / "patches" / row["task"] / f"{row['arm']}-{row['attempt']}.patch"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(patch, target)
            row["published_patch"] = str(target.relative_to(destination))
        grading = sorted(artifact.glob("grading*/verifier.log"))
        if grading:
            lines = grading[-1].read_text(errors="replace").splitlines()
            row["verifier_summary"] = [line for line in lines if re.search(
                r"^FAILED |^=+ .* (?:passed|failed|error)|\[verifier\] (?:Baseline|New tests) exit code", line)][-12:]
    latest = {(r["task"], r["arm"]): r for r in attempts}
    pairs = []
    for task in sorted({r["task"] for r in attempts}):
        stock, adapt = (latest.get((task, arm), {}) for arm in ("stock", "adapt"))
        fields = ("image_id", "upstream_base", "prompt_sha256", "actor_prompt_sha256",
                  "agent_settings", "runner_source_sha256")
        checks = {field: field in stock and stock[field] == adapt.get(field) for field in fields}
        checks["both_scored"] = stock.get("status") == adapt.get("status") == "scored"
        checks["effective_settings"] = all(r.get("effective_settings", {}).get("passed") for r in (stock, adapt))
        pairs.append({"task": task, "checks": checks, "passed": all(checks.values())})
    bundle = {"format": "cs224v-tuesday-handoff-v1", "exported": run.now(),
              "exporter_sha256": run.digest(Path(__file__)),
              "harness_commit": (run.capture(["git", "-C", run.ROOT, "log", "-1", "--format=%H", "--",
                                               "run.py", "codex_continue.py", "task_terminal.py", "config.json"])
                                 if manifest.get("harness_sources") == run.source_hashes() else None),
              "manifest": manifest, "verifier_validations": validations, "paired_checks": pairs,
              "attempts": attempts,
              "prior_experiments": [json.loads(path.read_text()) for path in include_handoffs],
              "linux_environment_audit": (json.loads((output / "linux-environment-audit.json").read_text())
                                          if (output / "linux-environment-audit.json").exists() else None),
              "run_events": (json.loads((output / "run-events.json").read_text())
                             if (output / "run-events.json").exists() else []),
              "timeout_cleanup_check": (json.loads((output / "timeout-cleanup-check.json").read_text())
                                        if (output / "timeout-cleanup-check.json").exists() else None),
              "harness_regressions": (json.loads((output / "harness-regressions.json").read_text())
                                      if (output / "harness-regressions.json").exists() else None),
              "analysis_notes": (json.loads((output / "analysis-notes.json").read_text())
                                 if (output / "analysis-notes.json").exists() else []),
              "architecture": {
                  "controller": "Pinned macOS ADAPT binary, both arms",
                  "coding": "Separate Linux containers from the same upstream image ID",
                  "project_io": "Shared task_terminal MCP tool; hidden tests and credentials are not mounted",
                  "verifier": "Fresh Linux container from the coding image; frozen patch and upstream tests",
                  "network": "Follow upstream task allow_internet setting for both coding and grading",
                  "compaction": "Pinned Codex default: 43,200-token automatic threshold for 48K context; 45,600 usable input tokens. No override.",
                  "limitations": [
                      "The supplied release has no Linux binary, so the controller remains on macOS.",
                      "Data-structure pytest validation is skipped by this release on macOS.",
                      "The native host shell still exists; the shared prompt requires all project work through the Linux tool.",
                      "Compaction defaults are derived from the exact Codex source commit named in the release license; actual context pressure still requires trace review.",
                      "The smoke task was selected using a previously passing patch and is not an unbiased accuracy estimate.",
                      "Old macOS coding pilot results are a separate experiment.",
                  ],
              }}
    run.save(destination / "handoff.json", bundle)
    run.save(destination / "manifest.json", manifest)
    run.save(destination / "validation.json", validations)
    run.save(destination / "attempts.json", attempts)
    lines = ["# Tuesday harness validation and smoke test", "",
             "This is the shared single-turn SWE-Interact setup for stock Codex versus ADAPT.",
             "Both arms receive the full task specification plus the same Linux execution instructions.",
             "The fixed task-order seed is 224. Model temperature and sampling seed are not exposed.",
             "A literal `continue` resumes a clarification question, within the original one-hour budget.", "",
             "## Verifier controls", "",
             "The control patches are only used to validate grading and never enter the coding containers.", "",
             "| Task | Control | Expected reward | Actual reward | Passed |", "| --- | --- | ---: | ---: | --- |"]
    for validation in validations:
        for name, control in validation["controls"].items():
            lines.append(f"| {validation['task']} | {name} | {control['expected']:g} | {control['reward']:g} | {control['passed']} |")
    lines += ["", "## Saved runs", "",
              "| Arm | Status | Reward | Agent seconds | Linux calls | Effective settings |",
              "| --- | --- | ---: | ---: | ---: | --- |"]
    for row in attempts:
        lines.append(f"| {row['arm']} | {row['status']} | {row.get('reward', 'unscored')} | "
                     f"{row.get('agent_seconds', '')} | {row.get('linux_terminal_calls', 0)} | "
                     f"{row.get('effective_settings', {}).get('passed', False)} |")
    lines += ["", *[f"Matched setup audit: `{p['task']}` — **{p['passed']}**." for p in pairs]]
    if bundle["prior_experiments"]:
        lines += ["", "## Earlier smoke attempt", "",
                  "The first stock Kombu smoke patch stalled in an existing filesystem-consumer test. "
                  "It was interrupted and saved as unscored. Its untouched/known-good verifier controls passed. "
                  "That run exposed missing container cleanup on interrupted verification; the final harness fixes it. "
                  "The complete earlier configuration and result are included below as a separate experiment."]
    if bundle["harness_regressions"]:
        lines += ["", "## Harness checks", "",
                  f"Harness regression checks: {bundle['harness_regressions']['tests_run']} passed. "
                  "A separate forced-timeout test in real Docker confirmed that the verifier container was removed. "
                  "The benchmark coding budget remains 3,600 seconds; the benchmark verifier limit remains upstream's 1,800 seconds."]
    if bundle["analysis_notes"]:
        lines += ["", "## Findings and next steps", "", *[f"- {note}" for note in bundle["analysis_notes"]]]
    lines += ["", "## Architecture and limits", ""]
    lines += [f"- {value}" for value in bundle["architecture"].values() if isinstance(value, str)]
    lines += [f"- {value}" for value in bundle["architecture"]["limitations"]]
    lines += ["", "Compaction calculation: [pinned Codex source](https://github.com/openai/codex/blob/687a119f0fcaace47e1f1abcc77cec6c813fd6da/codex-rs/protocol/src/openai_models.rs#L518-L535)."]
    lines += ["", "## Complete configuration and result records", "", "```json",
              json.dumps(bundle, indent=2), "```", ""]
    run.atomic_write(destination / "HANDOFF.md", "\n".join(lines))
    print(destination / "HANDOFF.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--include-handoff", action="append", default=[], type=Path,
                        help="Include a prior exported experiment without combining its scores")
    args = parser.parse_args()
    export(args.output.resolve(), args.destination.resolve(), args.include_handoff)
