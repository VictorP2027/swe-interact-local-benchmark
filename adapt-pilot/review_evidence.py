#!/usr/bin/env python3
"""Build a private case packet with context history and header-free request views."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile

import campaign
import review
import run


def request_view(record):
    view = {key: record.get(key) for key in ("file", "started", "ended", "kind", "path", "status")}
    view["request"] = record.get("request", {})
    return view


@contextmanager
def open_requests(path):
    try:
        archive = tarfile.open(path, "r:zst")
    except (tarfile.CompressionError, tarfile.ReadError):
        if not shutil.which("zstd"):
            raise RuntimeError("Request-body views need Python 3.14+ or the zstd command; original archives remain saved.")
        with subprocess.Popen(["zstd", "-d", "-c", str(path)], stdout=subprocess.PIPE) as process:
            with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
                yield archive
            if process.wait():
                raise RuntimeError("Could not decode the saved request archive")
    else:
        with archive:
            yield archive


def enrich(output, task, destination):
    if not (run.SINGLE_TURN / task / "task.toml").is_file():
        raise ValueError("Unknown review task")
    destination = destination.resolve()
    if not destination.is_relative_to((output / "manual-review").resolve()):
        raise ValueError("Keep evidence in the private manual-review directory")
    # Prototype trace files are immutable. Make only our existing copies
    # writable so rebuilding a packet never changes the original evidence.
    if destination.exists():
        for path in destination.rglob("*"):
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
    summary = review.build(output, task, destination)
    rows = run.records(output)
    for arm in run.ARMS:
        candidates = [row for row in rows if row["task"] == task and row["arm"] == arm]
        if not candidates or not candidates[-1].get("run_path"):
            continue
        row = candidates[-1]
        native = output / row["run_path"]
        target = destination / arm
        bundle = target / "context-history.bundle"
        if (native / "workspace.git").is_dir() and not bundle.exists():
            subprocess.run(["git", f"--git-dir={native / 'workspace.git'}", "bundle", "create", str(bundle), "--all"],
                           stdout=subprocess.DEVNULL, check=True)
        if bundle.exists():
            summary["arms"][arm]["context_history_sha256"] = run.digest(bundle)
        references = [{"path_relative_to_output": str(path.relative_to(output)), "sha256": run.digest(path),
                       "bytes": path.stat().st_size} for path in (native / "requests").glob("*") if path.is_file()]
        run.save(target / "request-archive-references.json", references)
        archive_path = native / "requests/bodies.tar.zst"
        count = 0
        if archive_path.exists() and archive_path.stat().st_size > 32:
            bodies = target / "recorded-request-bodies"
            bodies.mkdir(exist_ok=True)
            with open_requests(archive_path) as archive:
                for member in archive:
                    if not member.isfile() or not member.name.endswith(".json"):
                        continue
                    record = json.load(archive.extractfile(member))
                    run.save(bodies / Path(member.name).name, request_view(record))
                    count += 1
        summary["arms"][arm]["recorded_request_views"] = count
    summary["evidence_builder_sha256"] = run.digest(Path(__file__))
    run.save(destination / "review-summary.json", summary)
    return summary


def checksums(destination):
    run.save(destination / "CHECKSUMS.json", {
        str(path.relative_to(destination)): {"sha256": run.digest(path), "bytes": path.stat().st_size}
        for path in sorted(destination.rglob("*"))
        if path.is_file() and path.name not in {"CHECKSUMS.json", "README.md", "NOTES.md"}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--task", default=campaign.SMOKE_TASK)
    parser.add_argument("--historical-output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    destination = output / "manual-review" / args.task
    enrich(output, args.task, destination)
    if args.historical_output:
        old = args.historical_output.resolve()
        old_case = old / "manual-review" / args.task
        enrich(old, args.task, old_case)
        review.copy_directory(old_case, destination / "historical-reference")
    with (destination / "README.md").open("a") as file:
        file.write("\nContext-history Git bundles preserve earlier workspace versions. Recorded request views exclude HTTP request and response headers. Original archives stay indexed in the experiment output. The historical reference, when supplied, is separate from primary results. Inspect CASE_OVERVIEW.md when present.\n")
    checksums(destination)
    if list(destination.rglob("auth.json")):
        raise RuntimeError("Unexpected sign-in file in review packet")
    print("Saved private evidence packet:", destination)


if __name__ == "__main__":
    main()
