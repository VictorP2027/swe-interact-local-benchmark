#!/usr/bin/env python3
"""Save a private, portable manual-review packet without copying sign-in files."""

import argparse
import json
from pathlib import Path
import shutil

import run


def copy_directory(source, target):
    if source.exists():
        shutil.copytree(source, target, dirs_exist_ok=True,
                        ignore=lambda directory, names: [n for n in names if (Path(directory) / n).is_symlink()])


def session_events(run_directory, destination):
    count = 0
    compactions = []
    home = run_directory / "harness/codex_home"
    with (destination / "session-events.jsonl").open("w") as output:
        for path in sorted((home / "sessions").rglob("*.jsonl")):
            if path.is_symlink():
                continue
            with path.open() as stream:
                for number, line in enumerate(stream, 1):
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if event.get("type") not in {"event_msg", "response_item", "compacted", "turn_context"}:
                        continue
                    entry = {"source": str(path.relative_to(home)), "line": number, "event": event}
                    output.write(json.dumps(entry) + "\n")
                    count += 1
                    payload = event.get("payload") or {}
                    if event.get("type") == "compacted" or payload.get("type") == "context_compacted":
                        compactions.append(entry)
    run.save(destination / "compaction-events.json", compactions)
    return count, len(compactions)


def build(output, task, destination):
    destination = destination.resolve()
    if not destination.is_relative_to(output.resolve()):
        raise ValueError("Keep raw review packets inside the private experiment output directory")
    destination.mkdir(parents=True, exist_ok=True)
    task_directory = run.SINGLE_TURN / task
    shutil.copyfile(task_directory / "instruction.md", destination / "SPECIFICATION.md")
    shutil.copyfile(task_directory / "task.toml", destination / "task.toml")
    copy_directory(task_directory / "tests", destination / "upstream-tests")
    rows = run.records(output)
    summary = {"task": task, "purpose": "Manual comparison; original results and candidate patches are unchanged.",
               "arms": {}, "private_packet": True}
    for arm in run.ARMS:
        candidates = [row for row in rows if row["task"] == task and row["arm"] == arm]
        if not candidates:
            continue
        row = candidates[-1]
        artifact = output / row["artifact_path"]
        target = destination / arm
        target.mkdir(exist_ok=True)
        run.save(target / "result.json", row)
        for name in ("implementation.patch", "candidate-source.tar.gz", "candidate-tree.json",
                     "effective-settings.json", "terminal.jsonl", "agent.log"):
            if (artifact / name).exists():
                shutil.copyfile(artifact / name, target / name)
        if row.get("candidate_artifacts"):
            if run.digest(target / "candidate-source.tar.gz") != row["candidate_artifacts"]["source_sha256"]:
                raise ValueError("Candidate source snapshot changed")
        for grading in sorted(artifact.glob("grading*")):
            if grading.is_dir():
                copy_directory(grading, target / grading.name)
        event_count = compact_count = 0
        if row.get("run_path"):
            run_directory = output / row["run_path"]
            copy_directory(run_directory / "trace", target / "trace")
            copy_directory(run_directory / "workspace/data_structures", target / "data_structures")
            if (run_directory / "result/answer.txt").exists():
                shutil.copyfile(run_directory / "result/answer.txt", target / "ANSWER.txt")
            event_count, compact_count = session_events(run_directory, target)
        summary["arms"][arm] = {"status": row["status"], "reward": row.get("reward"),
            "machine_id": row.get("machine_id"), "image_id": row.get("image_id"),
            "patch_sha256": row.get("patch_sha256"), "candidate_artifacts": row.get("candidate_artifacts"),
            "session_events": event_count, "compaction_markers": compact_count,
            "context_window": row.get("agent_settings", {}).get("context_window"),
            "trace": row.get("trace"), "usage": row.get("agent_usage")}
    run.save(destination / "review-summary.json", summary)
    files = {str(path.relative_to(destination)): {"sha256": run.digest(path), "bytes": path.stat().st_size}
             for path in sorted(destination.rglob("*"))
             if path.is_file() and path.name not in {"CHECKSUMS.json", "README.md", "NOTES.md"}}
    run.save(destination / "CHECKSUMS.json", files)
    (destination / "README.md").write_text(
        f"# Manual review: {task}\n\n"
        "Read SPECIFICATION.md, then compare stock/ and adapt/. Each arm includes its frozen patch, "
        "tracked candidate source snapshot, actor commands and outputs, upstream grading results, "
        "model answer, context data, full tool trace and filtered native session events. "
        "The source archive contains tracked and newly added project files without dependency caches or Git history. Submodule contents remain in the recorded upstream image.\n\n"
        "Use terminal.jsonl timestamps to find tests the actor actually ran. Use session-events.jsonl "
        "and compaction-events.json to inspect evidence before and after compaction. Marker counts "
        "count recorded events, not necessarily distinct compactions. The trace directory preserves "
        "original tool inputs and results. CHECKSUMS.json records the saved evidence.\n\n"
        "Keep this packet private. It includes raw traces and grading feedback. Sign-in files, "
        "the Codex home, request archives and the private ADAPT binary are excluded.\n")
    notes = destination / "NOTES.md"
    if not notes.exists():
        notes.write_text(
            "# Case notes\n\n"
            "| Question | Stock evidence | ADAPT evidence |\n| --- | --- | --- |\n"
            "| Which requirements were implemented or missed? | | |\n"
            "| Which tests did the actor run? | | |\n"
            "| Which grading checks failed, and why? | | |\n"
            "| Did setup or dependencies prevent evaluation? | | |\n"
            "| Was the needed evidence seen before compaction? | | |\n"
            "| Was it retained in context data or recovered later? | | |\n"
            "| Did missing earlier evidence cause the failure? | | |\n"
            "| Did this task actually put pressure on context? | | |\n\n"
            "Keep implementation mistakes, verifier problems and context loss as separate explanations. "
            "Cite trace steps, session lines, source files and failed assertions.\n")
    print(destination)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--task", required=True)
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    build(output, args.task, args.destination or output / "manual-review" / args.task)
