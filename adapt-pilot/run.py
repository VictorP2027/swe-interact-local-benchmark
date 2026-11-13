#!/usr/bin/env python3
"""Run and checkpoint the CS224V SWE-Interact comparison."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import random
import re
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import time
import tomllib
from datetime import datetime, timezone

from codex_continue import asks_question


ROOT = Path(__file__).resolve().parent
DATASET = Path(os.environ.get("SWE_INTERACT_DATASET", ROOT.parent.parent / "SWE-Interact")).expanduser().resolve()
RELEASE = Path(os.environ.get("SWE_ADAPT_RELEASE", ROOT.parent.parent / "prototype" / "ours-166c433f-darwin-arm64")).expanduser().resolve()
LOCAL_RUBRIC_BRIDGE = ROOT.parent / "harness" / "codex_rubric_bridge.py"
ARMS = {
    "stock": "codex-shipped",
    "adapt": "codex",
}
SINGLE_TURN = DATASET / "data/singleturn"
LEGACY_OUTPUT = ROOT / "output"
FAMILIES = {"deepswe": "DeepSWE", "swebenchpro": "SWE-bench Pro", "rf": "SWE Atlas Refactoring"}
QUOTA = re.compile(r"usage_limit_reached|usage limit|quota exceeded|insufficient_quota|out of credits", re.I)
TASK_IMAGE_REPO = "cs224v-swe-interact"
CYCLE_BUILDER = "cs224v-swe-cycle-" + hashlib.sha256(os.fsencode(ROOT)).hexdigest()[:12]
REVIEW_TASKS = {
    "deepswe_bandit-structured-nosec-directives",
    "deepswe_pwntools-tube-multiplexing",
    "swebenchpro_instance_future-architect__vuls-7eb77f5b5127c847481bcf600b4dca2b7a85cf3e",
}


class Blocked(Exception):
    pass


class QuotaReached(Blocked):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as file:
        temporary = Path(file.name)
        file.write(data.encode())
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(path, data):
    atomic_write(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def capture(args, **kwargs):
    return subprocess.check_output([str(x) for x in args], text=True, **kwargs).strip()


def logged(args, path, **kwargs):
    with path.open("w") as log:
        return subprocess.run([str(x) for x in args], stdout=log, stderr=subprocess.STDOUT, **kwargs).returncode


def task_manifest(seed, first):
    roots = {split: DATASET / "data" / split for split in ("singleturn", "multiturn")}
    ids = {split: sorted(p.parent.name for p in root.glob("*/task.toml")) for split, root in roots.items()}
    if ids["singleturn"] != ids["multiturn"] or len(ids["singleturn"]) != 75:
        raise ValueError("Expected the same 75 task IDs in both SWE-Interact splits")
    rest = [task for task in ids["singleturn"] if task != first]
    if len(rest) != 74:
        raise ValueError("First task is missing from the dataset")
    random.Random(seed).shuffle(rest)
    return {
        task: {
            "family": FAMILIES[task.split("_", 1)[0]],
            "definition_sha256": {split: digest(root / task / "task.toml") for split, root in roots.items()},
        }
        for task in [first, *rest]
    }


def load_experiment(out, local_rubric=False):
    config = json.loads((ROOT / "config.json").read_text())
    if local_rubric:
        config.update(rubric_model="gpt-6-luna", rubric_reasoning_effort="medium",
                      rubric_transport="local-codex-cli",
                      rubric_bridge_sha256=digest(LOCAL_RUBRIC_BRIDGE))
    dataset_commit = capture(["git", "-C", DATASET, "rev-parse", "HEAD"])
    if dataset_commit != config["dataset_commit"]:
        raise ValueError(f"Expected dataset {config['dataset_commit']}, found {dataset_commit}")
    if capture(["git", "-C", DATASET, "status", "--porcelain", "--untracked-files=no"]):
        raise ValueError("Tracked SWE-Interact files have local changes")
    version = (RELEASE / "VERSION").read_text().splitlines()
    if version[0] != f"commit {config['adapt_commit']}":
        raise ValueError("ADAPT release does not match config.json")
    for line in version:
        if line.startswith("sha256 "):
            _, checksum, relative_path = line.split()
            if digest(RELEASE / relative_path) != checksum:
                raise ValueError(f"ADAPT binary checksum mismatch: {relative_path}")
    catalog = RELEASE / "lib/task_agents/codex/upstream/codex-rs/models-manager/models.json"
    model = next(item for item in json.loads(catalog.read_text())["models"] if item["slug"] == config["model"])
    if model["truncation_policy"] != {"mode": "tokens", "limit": config["tool_output_limit"]}:
        raise ValueError("Bundled model tool output limit does not match config.json")
    tasks = task_manifest(config["task_order_seed"], config["first_task"])
    manifest = {"configuration": config, "task_order": list(tasks), "tasks": tasks, "arms": ARMS,
                "runner_sha256": digest(RELEASE / "lib/ours"), "model_catalog_sha256": digest(catalog)}
    manifest = json.loads(json.dumps(manifest))
    path = out / "manifest.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if previous != manifest:
            rubric_keys = {"rubric_model", "rubric_reasoning_effort", "rubric_transport", "rubric_bridge_sha256"}
            old_config = previous.pop("configuration")
            same_trials = (previous == {key: value for key, value in manifest.items() if key != "configuration"}
                           and {k: v for k, v in old_config.items() if k not in rubric_keys}
                           == {k: v for k, v in config.items() if k not in rubric_keys})
            has_rubric_scores = any(r["task"].startswith("rf_") and r["status"] == "scored" for r in records(out))
            if not (local_rubric and same_trials and not has_rubric_scores):
                raise ValueError("Experiment settings changed. Use a fresh --output directory for a different configuration.")
            save(path, manifest)
    if not path.exists():
        save(path, manifest)
    return config, manifest


def records(out):
    return [json.loads(path.read_text()) for path in sorted(out.glob("attempts/*/*/*/result.json"))]


def import_stock(out, config):
    """Reuse finished stock runs where the continuation policy would do nothing."""
    if not (LEGACY_OUTPUT / "manifest.json").exists():
        return
    if out == LEGACY_OUTPUT:
        return
    previous_manifest = json.loads((LEGACY_OUTPUT / "manifest.json").read_text())
    current_manifest = json.loads((out / "manifest.json").read_text())
    if any(previous_manifest[key] != current_manifest[key]
           for key in ("runner_sha256", "model_catalog_sha256")):
        return
    previous = previous_manifest["configuration"]
    excluded = {"protocol", "max_continuations"}
    if any(previous.get(key) != value for key, value in config.items() if key not in excluded):
        return
    for row in records(LEGACY_OUTPUT):
        task = row["task"]
        if row["arm"] != "baseline" or row["status"] != "scored" or task in REVIEW_TASKS:
            continue
        parent = out / "attempts" / task / "stock"
        if parent.exists():
            continue
        old_run = LEGACY_OUTPUT / row["run_path"]
        old_attempt = LEGACY_OUTPUT / row["artifact_path"]
        details = json.loads((old_run / "run.json").read_text())
        prompt = SINGLE_TURN / task / "instruction.md"
        user_messages = list((old_run / "trace").glob("user_*/message.md"))
        settings = details["settings"]
        if (details["exit_reason"] != "completed"
                or details["harness"]["name"] != "codex-shipped"
                or details["harness"]["version"] != f"codex-cli {config['codex_version']}"
                or details["code"]["commit"] != config["adapt_commit"]
                or details["code"]["dirty"]
                or any(settings[key] != config[key] for key in
                       ("model", "reasoning_effort", "context_window", "lane"))
                or settings["wall_clock_s"] != config["trial_wall_clock_s"]
                or len(user_messages) != 1
                or user_messages[0].read_text().strip() != prompt.read_text().strip()
                or asks_question((old_run / "result/answer.txt").read_text())
                or digest(old_attempt / "implementation.patch") != row["patch_sha256"]
                or float((old_attempt / "grading/verifier/reward.txt").read_text()) != row["reward"]):
            continue
        catalog = json.loads((old_run / "harness/codex_home/model_catalog.json").read_text())
        model = next(model for model in catalog["models"] if model["slug"] == config["model"])
        if model["truncation_policy"] != {"mode": "tokens", "limit": config["tool_output_limit"]}:
            continue
        attempt = parent / "0001"
        attempt.mkdir(parents=True)
        artifact_path = os.path.relpath(old_attempt, out)
        save(attempt / "result.json", {
            **row, "arm": "stock", "attempt": attempt.name, "reused": True,
            "artifact_path": artifact_path, "run_path": os.path.relpath(old_run, out),
            "prompt_sha256": digest(prompt), "continuations": 0,
        })


def dependency_gap(task, config):
    if config.get("rubric_transport") == "local-codex-cli":
        return None
    if task.startswith("rf_") and not all(os.getenv(key) for key in ("OPENAI_API_KEY", "OPENAI_API_BASE")):
        return "SWE Atlas grading requires OPENAI_API_KEY and OPENAI_API_BASE."
    return None


def elapsed_seconds(row):
    if row.get("status") != "scored" or not row.get("started") or not row.get("updated"):
        return None
    return (datetime.fromisoformat(row["updated"]) - datetime.fromisoformat(row["started"])).total_seconds()


def printable(value):
    return f"{value:,.0f}" if value is not None else "—"


def report(out, manifest, destination=None):
    config = manifest["configuration"]
    attempts = records(out)
    latest = {(row["task"], row["arm"]): row for row in attempts}
    counts = {}
    for arm in ARMS:
        rows = [row for (_, name), row in latest.items() if name == arm and row["status"] == "scored"]
        counts[arm] = (sum(row["reward"] == 1 for row in rows), len(rows))
    pairs = [task for task in manifest["task_order"]
             if all(latest.get((task, arm), {}).get("status") == "scored" for arm in ("stock", "adapt"))]
    lines = [
        "# CS224V SWE-Interact evaluation", "",
        f"Report updated {now()}.",
        "",
        "The same 75 task IDs are available in single-turn and multi-turn form.",
        "Both arms use the single-turn SWE-Interact task and receive the same full specification upfront.",
        "If the final reply ends with a question, resume the same session with the literal message continue.",
        "The detector checks the last nonempty prose line, skipping fenced code and Markdown blockquotes.",
        "This follows the ADAPT paper's clarification policy. The detector and continuation cap are local choices.",
        "A future experiment can use SWE-Interact's multi-turn protocol with a live simulated maintainer.",
        "The agent uses the pinned Codex release and GPT-6 Luna on the ChatGPT subscription.",
        "The 48K context and 10K tool output cap follow ADAPT §3.3. All continuations share the one-hour coding budget.",
        "The fixed seed controls task order. The compiled runner exposes no model seed or temperature.",
        "A trial counts as resolved when the upstream verifier returns reward 1.",
        "Only scored attempts enter the denominators. Interrupted and unscored attempts stay in the history.",
        "Token totals include cached input. A context window is a per-call budget.",
        "The local adapter runs the coding agent on macOS and upstream verification in Linux Docker.",
        "The upstream single-turn verifier runs on the frozen candidate.",
        "Attempts using image cycling share a task image across both arms and retire it after both scores are saved.",
        "Prior local stock attempts are reused only after checking their prompt, model settings, release,",
        "patch hash and final reply. Every reused attempt already satisfied the continue rule.",
        "The previous Terra pilot and Victor's historical 41/75 single-turn result are separate from this experiment.",
        "The local stock harness serves as the baseline. Historical results are not a third matched arm.",
        f"{len(REVIEW_TASKS)} tasks are held because they involve security scanning or exploit tooling.",
        "", "## Results", "",
        "| Arm | Resolved | Scored | Eligible |", "| --- | ---: | ---: | ---: |",
        *[f"| {arm} | {wins} | {scored} | {len(manifest['tasks']) - len(REVIEW_TASKS)} |"
          for arm, (wins, scored) in counts.items()],
        "", f"Matched stock/ADAPT tasks scored: {len(pairs)}.",
    ]
    scoped = [task for task in manifest["task_order"] if task not in REVIEW_TASKS]
    deferred = [task for task in scoped if dependency_gap(task, config)
                and any(latest.get((task, arm), {}).get("status") != "scored" for arm in ARMS)]
    in_flight = [row for row in latest.values() if row["status"] in {"running", "agent_complete", "grading"}]
    lines += ["", f"Dataset coverage: {len(pairs)}/{len(manifest['task_order'])} matched pairs; "
              f"{len(scoped)} tasks in scope, {len(deferred)} currently deferred for grader setup."]
    for row in in_flight:
        lines.append(f"- In progress: `{row['task']}` ({row['arm']}, {row['status']}).")
    events = out / "run-events.json"
    if events.exists():
        lines += ["", "Run events", ""]
        for event in json.loads(events.read_text()):
            lines.append(f"- {event['at']}: {event['detail']}")
    if config.get("rubric_transport") == "local-codex-cli":
        lines += ["", "SWE Atlas uses the upstream tests and rubric prompts with GPT-6 Luna at medium effort "
                  "through the Codex CLI. Both arms use this substitute judge. The upstream default is Claude Opus 4.5."]
    gaps = {gap for task in manifest["task_order"] if task not in REVIEW_TASKS for arm in ARMS
            if latest.get((task, arm), {}).get("status") != "scored"
            if (gap := dependency_gap(task, config))}
    if gaps or shutil.disk_usage(out).free < 2 * 1024**3:
        lines += ["", "Current blockers", ""]
        lines.extend(f"- {gap}" for gap in sorted(gaps))
        if shutil.disk_usage(out).free < 2 * 1024**3:
            lines.append("- Local storage is below the runner's 2 GiB floor for starting a trial.")
    if pairs:
        wins = {arm: sum(latest[(task, arm)]["reward"] == 1 for task in pairs) for arm in ("stock", "adapt")}
        lines += ["", f"On these tasks, stock resolved {wins['stock']}/{len(pairs)} and ADAPT resolved {wins['adapt']}/{len(pairs)}."]
        lines += ["", "| Matched task | Stock reward | ADAPT reward | Stock tokens | ADAPT tokens |",
                  "| --- | ---: | ---: | ---: | ---: |"]
        for task in pairs:
            stock, adapt = (latest[(task, arm)] for arm in ("stock", "adapt"))
            totals = [row.get("agent_usage", {}).get("total_tokens") for row in (stock, adapt)]
            formatted = [f"{value:,}" if value is not None else "unavailable" for value in totals]
            lines.append(f"| {task} | {stock['reward']:g} | {adapt['reward']:g} | {' | '.join(formatted)} |")
        lines += ["", "Paired resource use", "",
                  "Token and time summaries include only matched tasks where both arms reported the corresponding value.",
                  "Elapsed time is measured from attempt start to saved score; it can include image preparation, verifier time, and pauses before resuming.",
                  "The subscription runs do not expose a per-trial dollar charge. Token counts are recorded separately from account usage.",
                  "", "| Arm | Token pairs | Total tokens | Median tokens | Min–max tokens | At least 544K | Time pairs | Median elapsed (s) |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        token_rows = [[latest[(task, arm)].get("agent_usage", {}).get("total_tokens") for arm in ARMS]
                      for task in pairs]
        time_rows = [[elapsed_seconds(latest[(task, arm)]) for arm in ARMS] for task in pairs]
        for index, arm in enumerate(ARMS):
            tokens = [row[index] for row in token_rows if all(v is not None for v in row)]
            elapsed = [row[index] for row in time_rows if all(v is not None for v in row)]
            stats = ([printable(sum(tokens)), printable(statistics.median(tokens)),
                      f"{printable(min(tokens))}–{printable(max(tokens))}",
                      str(sum(v >= 544000 for v in tokens))] if tokens else ["—"] * 4)
            lines.append(f"| {arm} | {len(tokens)} | {' | '.join(stats)} | "
                         f"{len(elapsed)} | {printable(statistics.median(elapsed) if elapsed else None)} |")
    lines += ["", "| Task family | Stock resolved / scored | ADAPT resolved / scored |",
              "| --- | ---: | ---: |"]
    for family in FAMILIES.values():
        counts_by_family = []
        for arm in ARMS:
            rows = [row for (_, name), row in latest.items()
                    if name == arm and row["status"] == "scored" and row["family"] == family]
            counts_by_family.append(f"{sum(row['reward'] == 1 for row in rows)} / {len(rows)}")
        lines.append(f"| {family} | {' | '.join(counts_by_family)} |")
    lines += ["", "## Configuration", "", "```json",
              json.dumps({key: value for key, value in manifest.items() if key not in {"tasks", "task_order"}}, indent=2),
              "```", "", "## Per-task results in scheduled order", "",
              "| # | Task | Family | Stock | ADAPT |", "| ---: | --- | --- | --- | --- |"]
    for index, task in enumerate(manifest["task_order"], 1):
        cells = []
        for arm in ARMS:
            row = latest.get((task, arm))
            if not row:
                cells.append("held" if task in REVIEW_TASKS else "deferred" if task in deferred else "pending")
            elif row["status"] == "scored":
                cells.append(f"{'pass' if row['reward'] == 1 else 'fail'} ({row['reward']:g})")
            else:
                cells.append(row["status"])
        lines.append(f"| {index} | {task} | {manifest['tasks'][task]['family']} | {' | '.join(cells)} |")
    lines += ["", "## Scored attempt details", "",
              "Cached input is part of input tokens. Reasoning output is part of output tokens.",
              "", "| Task | Arm | Reward | Input | Cached input | Output | Reasoning output | Total | Elapsed (s) | Steps | Calls | Continues | Reused |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for task in manifest["task_order"]:
        for arm in ARMS:
            row = latest.get((task, arm), {})
            if row.get("status") != "scored":
                continue
            usage = row.get("agent_usage") or {}
            values = [usage.get(k) for k in ("input_tokens", "cached_input_tokens", "output_tokens",
                                             "reasoning_output_tokens", "total_tokens")]
            trace = row.get("trace") or {}
            values += [elapsed_seconds(row), trace.get("steps"), trace.get("calls"), row.get("continuations")]
            lines.append(f"| {task} | {arm} | {row['reward']:g} | {' | '.join(map(printable, values))} | "
                         f"{'yes' if row.get('reused') else 'no'} |")
    lines += ["", "## Attempt history", "",
              "This report includes attempt records and relative artifact paths. Raw traces, model requests, and credentials are excluded.",
              "Reproduce the run with README.md, config.json, run.py and codex_continue.py.",
              "", "```json", json.dumps(attempts, indent=2), "```", ""]
    atomic_write(destination or out / "REPORT.md", "\n".join(lines))


def follow_report(out, manifest, destination):
    """Refresh a snapshot when the active runner publishes a checkpoint."""
    source = out / "REPORT.md"
    revision = None
    with (out / ".lock").open("a") as lock:
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError:
                next_revision = source.stat().st_mtime_ns if source.exists() else None
                if next_revision != revision:
                    report(out, manifest, destination)
                    revision = next_revision
                time.sleep(2)
            else:
                report(out, manifest, destination)
                return


def checkpoint(out, attempt, row, manifest, **fields):
    row.update(fields, updated=now())
    save(attempt / "result.json", row)
    report(out, manifest)


def source_hashes():
    names = ("run.py", "codex_continue.py")
    return {name: digest(ROOT / name) for name in names if (ROOT / name).is_file()}


def docker(*args, **kwargs):
    return capture(["docker", *args], **kwargs)


def task_image_tag(task):
    relative = (SINGLE_TURN / task).relative_to(DATASET)
    return f"{TASK_IMAGE_REPO}:{hashlib.sha256(str(relative).encode()).hexdigest()[:12]}"


def local_image_id(ref):
    result = subprocess.run(["docker", "image", "ls", "--no-trunc", "--format", "{{.ID}}", ref],
                            capture_output=True, text=True, check=True)
    return next(iter(result.stdout.splitlines()), "")


def retire_scored_image(task, rows):
    scored = {r["arm"]: r.get("image_id") for r in rows if r["task"] == task and r["status"] == "scored"}
    ids = set(scored.values())
    if scored.keys() != ARMS.keys() or len(ids) != 1 or None in ids:
        return
    refs = [task_image_tag(task)]
    # The earlier FastAPI pilot is the only experiment override we own.
    if task == "deepswe_fastapi-deprecation-response-headers":
        refs.append("cs224v-fastapi-smoke:b32f98c")
    for ref in refs:
        if local_image_id(ref) in ids:
            docker("image", "rm", ref)
            print(f"Retired saved task image: {ref}", flush=True)


def guard_cycle_image(tag):
    existing = docker("image", "ls", "--format", "{{.Repository}}:{{.Tag}}",
                      "--filter", f"reference={TASK_IMAGE_REPO}:*").splitlines()
    if others := sorted(set(existing) - {tag}):
        raise Blocked(f"Another task image is still on disk: {', '.join(others)}. "
                      "Finish its pending arm(s) first so they use the same image.")


def clear_cycle_builder():
    builders = docker("buildx", "ls", "--format", "{{.Name}}").splitlines()
    if CYCLE_BUILDER in {name.rstrip("*") for name in builders}:
        docker("buildx", "rm", CYCLE_BUILDER)


def build_image(command, attempt):
    with (attempt / "image-build.log").open("w") as log:
        with subprocess.Popen([str(arg) for arg in command], stdout=log, stderr=subprocess.STDOUT) as build:
            try:
                while build.poll() is None:
                    if shutil.disk_usage(attempt).free < 2 * 1024**3:
                        raise Blocked("Stopped the Docker build at the 2 GiB free-space floor.")
                    try:
                        build.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass
            finally:
                if build.poll() is None:
                    build.send_signal(signal.SIGINT)
                    try:
                        build.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        build.kill()
            code = build.returncode
    if code:
        raise Blocked("Task image build failed. See image-build.log.")


def image_for(task_dir, task, config, attempt, cycle=False):
    override = config["image_overrides"].get(task)
    tag = task_image_tag(task)
    if cycle:
        guard_cycle_image(tag)
    image_id = override or local_image_id(tag)
    if not image_id:
        command = ["--platform", config["platform"], "-t", tag, task_dir / "environment"]
        if cycle:
            docker("buildx", "create", "--name", CYCLE_BUILDER, "--driver", "docker-container")
            try:
                build_image(["docker", "buildx", "build", "--builder", CYCLE_BUILDER, "--load", *command],
                            attempt)
            finally:
                clear_cycle_builder()
        else:
            build_image(["docker", "build", *command], attempt)
        image_id = local_image_id(tag)
        if not image_id:
            raise Blocked(f"Build succeeded but Docker did not load {tag}.")
    try:
        return docker("image", "inspect", "--format", "{{.Id}}", image_id, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise Blocked(f"Local image unavailable: {image_id}. See README.") from exc


def prepare_seed(image, repo, base, platform, attempt):
    seed = attempt / "seed"
    seed.mkdir()
    container = ["docker", "run", "--rm", "--network", "none", "--platform", platform,
                 "--entrypoint", "git", image]
    archive_path = attempt / "seed.tar"

    def export_tree(repository, commit, destination):
        with archive_path.open("wb") as archive:
            subprocess.run([*container, "-C", repository, "archive", commit],
                           stdout=archive, check=True)
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run(["tar", "-xf", archive_path, "-C", destination], check=True)
        archive_path.unlink()

    export_tree(repo, base, seed)
    # The parent archive omits submodule contents. Use the exact commits
    # recorded by the upstream image so tracked links into them resolve.
    modules = capture([*container, "-C", repo, "submodule", "status", "--recursive"])
    for line in modules.splitlines():
        if line.startswith("-"):
            continue  # This submodule was not initialized in the upstream image.
        match = re.fullmatch(r"[ +]([0-9a-f]{40,64}) (.+?)(?: \([^\n]*\))?", line)
        if not match:
            # capture() trims the leading space on the first initialized entry.
            match = re.fullmatch(r"([0-9a-f]{40,64}) (.+?)(?: \([^\n]*\))?", line)
        if not match:
            raise Blocked("Unexpected submodule status in the upstream image.")
        commit, relative = match.groups()
        if line.startswith("+"):
            commit = capture([*container, "-C", repo, "rev-parse", f"HEAD:{relative}"])
        destination = seed / relative
        if not destination.resolve().is_relative_to(seed.resolve()):
            raise Blocked("Submodule path is outside the task seed.")
        export_tree(f"{repo}/{relative}", commit, destination)
    return seed


def repo_location(task_dir, image, config, task):
    compose = DATASET / "data/multiturn" / task / "environment/docker-compose.yaml"
    match = re.search(r"\bREPO_EXEC_ROOT=(/[^\s\"']+)", compose.read_text())
    repo = match.group(1) if match else "/app"
    base = docker("run", "--rm", "--network", "none", "--platform", config["platform"], "--entrypoint",
                  "git", image, "-C", repo, "rev-parse", "HEAD")
    expected = tomllib.loads((task_dir / "task.toml").read_text()).get("metadata", {}).get("base_commit_hash")
    if expected and base != expected:
        raise ValueError(f"Task image at {base}, expected {expected}")
    return repo, base


def agent_command(attempt, config, task, harness, seed, prompt, delegate):
    return [RELEASE / "ours", "run", "--harness", harness, "--task", task,
            "--model", config["model"], "--reasoning-effort", config["reasoning_effort"],
            "--context-window", config["context_window"], "--lane", config["lane"],
            "--wall-clock-s", config["trial_wall_clock_s"], "--seed", seed,
            "--runs-root", attempt / "runs", "--prompt", prompt, "--codex-bin", delegate]


def agent_environment():
    # The coding role uses saved subscription authentication. Keep simulator
    # and verifier credentials out of its tool subprocess environment.
    return {key: value for key, value in os.environ.items()
            if not key.startswith(("OPENAI_", "LITELLM_", "EVAL_", "SIM_USER_"))
            and key not in {"CODEX_API_KEY", "ANTHROPIC_API_KEY", "DOCKER_HOST", "DOCKER_CONTEXT"}}


def metadata(attempt):
    paths = list((attempt / "runs").glob("*/run.json"))
    if len(paths) != 1:
        raise Blocked("Runner did not produce one run.json. See agent.log.")
    return paths[0].parent, json.loads(paths[0].read_text())


def freeze_patch(run, attempt):
    workspace = run / "workspace"
    git = ["git", f"--git-dir={run / 'workspace.git'}", f"--work-tree={workspace}", "-C", str(workspace)]
    base = capture([*git, "rev-list", "--max-parents=0", "HEAD"])
    index = dict(os.environ, GIT_INDEX_FILE=str(attempt / "patch.index"))
    try:
        subprocess.run([*git, "read-tree", base], env=index, check=True)
        subprocess.run([*git, "add", "--all", "--", ".", ":(exclude)trace", ":(exclude)data_structures"],
                       env=index, check=True)
        patch = attempt / "implementation.patch"
        with patch.open("wb") as file:
            subprocess.run([*git, "diff", "--cached", "--binary", base], env=index, stdout=file, check=True)
        return patch
    finally:
        Path(index["GIT_INDEX_FILE"]).unlink(missing_ok=True)


@contextmanager
def verifier_environment(task, config, logs):
    env = dict(os.environ)
    if not task.startswith("rf_"):
        yield env, ["--network", "none"]
        return
    options = ["--env", "EVAL_API_KEY", "--env", "EVAL_BASE_URL", "--env", "EVAL_MODEL"]
    env["EVAL_MODEL"] = config["rubric_model"]
    if config.get("rubric_transport") != "local-codex-cli":
        env.update(EVAL_API_KEY=env["OPENAI_API_KEY"], EVAL_BASE_URL=env["OPENAI_API_BASE"])
        yield env, options
        return
    spec = spec_from_file_location("swe_atlas_codex_bridge", LOCAL_RUBRIC_BRIDGE)
    bridge_module = module_from_spec(spec)
    spec.loader.exec_module(bridge_module)
    bridge_module.CODEX = str(RELEASE / "codex/bin/codex")
    bridge = bridge_module.Bridge(logs / "rubric-codex", bind="127.0.0.1")
    env.update(EVAL_API_KEY=bridge.token, EVAL_BASE_URL=f"http://host.docker.internal:{bridge.port}/v1")
    try:
        yield env, options
    finally:
        bridge.close()


def verify_candidate(task, task_dir, image, repo, patch, config, attempt):
    logs = grading_directory(attempt)
    settings = tomllib.loads((task_dir / "task.toml").read_text())
    with verifier_environment(task, config, logs) as (env, options):
        verifier_command = [
            "docker", "run", "--rm", "--platform", config["platform"], *options,
            "--mount", f"type=bind,source={task_dir / 'tests'},target=/tests,readonly",
            "--mount", f"type=bind,source={patch},target=/candidate.patch,readonly",
            "--mount", f"type=bind,source={logs},target=/logs",
            "--env", f"PYTEST_ADDOPTS={config['verifier_pytest_addopts'].get(task, '')}",
            "--workdir", repo, "--entrypoint", "bash", image, "-c",
            'set -e; if test -s /candidate.patch; then git apply --whitespace=nowarn /candidate.patch; fi; '
            'mkdir -p /logs/verifier /logs/artifacts; bash /tests/test.sh',
        ]
        code = logged(verifier_command, logs / "verifier.log", env=env, timeout=settings["verifier"]["timeout_sec"])
    if task.startswith("rf_") and config.get("rubric_transport") == "local-codex-cli":
        rubric_path = logs / "verifier/rubrics_results.json"
        if not rubric_path.is_file():
            raise Blocked("Local rubric did not produce a results file. See grading artifacts.")
        rubric = json.loads(rubric_path.read_text())
        if rubric.get("evaluable_count", 0) < rubric.get("rubric_count", 0):
            raise Blocked("Local rubric did not produce every required rating. See grading artifacts.")
    return verifier_reward(logs, code)


def verifier_reward(logs, code):
    reward_path = logs / "verifier/reward.txt"
    json_path = logs / "verifier/reward.json"
    if json_path.exists():
        data = json.loads(json_path.read_text())
    else:
        data = {}
    if reward_path.exists():
        reward = float(reward_path.read_text())
    elif "reward" in data:
        reward = float(data["reward"])
    else:
        raise Blocked(f"Verifier exited {code} without a task reward.")
    if not 0 <= reward <= 1:
        raise Blocked("Unexpected verifier reward. See grading artifacts.")
    task_errors = ("working tree must be clean", "/tmp/base_commit.txt is missing",
                   "base commit is invalid", "missing implementation parent commit",
                   "missing separate implementation and test commits", "test commit diff is empty")
    if data.get("error") and not (reward == 0 and str(data["error"]).startswith(task_errors)):
        raise Blocked("The verifier recorded an evaluation error. See grading artifacts.")
    # Rubric API errors can be emitted in a separate JSON report while the
    # wrapper still writes a zero reward.
    for path in logs.rglob("*.json"):
        if "rubric" not in path.name.lower():
            continue
        try:
            result = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(result, dict) and result.get("error"):
            if QUOTA.search(str(result["error"])):
                raise QuotaReached("Rubric grader quota reached.")
            raise Blocked("Rubric grading did not complete. See grading artifacts.")
    return reward, code


def grading_directory(attempt):
    logs = attempt / "grading"
    if logs.exists():
        number = len(list(attempt.glob("grading-retry-*"))) + 1
        logs = attempt / f"grading-retry-{number:04d}"
    logs.mkdir()
    return logs


def trial(out, manifest, config, task, arm, attempt, row, cycle=False):
    harness = ARMS[arm]
    task_dir = SINGLE_TURN / task
    if gap := dependency_gap(task, config):
        raise Blocked(gap)
    if shutil.disk_usage(out).free < 2 * 1024**3:
        raise Blocked("Less than 2 GiB free for the next trial. Free storage before resuming.")
    image = image_for(task_dir, task, config, attempt, cycle)
    for previous in records(out):
        if previous["task"] != task or not previous.get("image_id"):
            continue
        if previous["image_id"] != image:
            raise Blocked("Docker image differs from the saved trial. Restore the recorded image before resuming.")
    repo, base = repo_location(task_dir, image, config, task)
    if task.startswith("rf_"):
        row["rubric"] = {key: value for key, value in config.items() if key.startswith("rubric_")}
    checkpoint(out, attempt, row, manifest, image_id=image, upstream_base=base, repository_path=repo)
    seed = prepare_seed(image, repo, base, config["platform"], attempt)
    prompt = task_dir.joinpath("instruction.md").read_text()
    checkpoint(out, attempt, row, manifest, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="swe-continue-") as folder:
        delegate = Path(folder) / "codex"
        delegate.write_text(f"#!{sys.executable}\n" + (ROOT / "codex_continue.py").read_text())
        delegate.chmod(0o700)
        binaries = RELEASE / "codex/bin"
        (delegate.parent / "codex-code-mode-host").symlink_to(binaries / "codex-code-mode-host")
        env = agent_environment()
        env.update(SWE_CONTINUE_CODEX=str(binaries / "codex"), SWE_CONTINUE_LIMIT=str(config["max_continuations"]))
        logged(agent_command(attempt, config, task, harness, seed, prompt, delegate), attempt / "agent.log",
               cwd=RELEASE, env=env)
    run, details = metadata(attempt)
    shutil.rmtree(seed)
    if not record_agent(out, manifest, attempt, row, run, details):
        return
    patch = freeze_patch(run, attempt)
    checkpoint(out, attempt, row, manifest, status="grading", patch_sha256=digest(patch))
    reward, code = verify_candidate(task, task_dir, image, repo, patch, config, attempt)
    checkpoint(out, attempt, row, manifest, status="scored", reward=reward, verifier_exit_code=code)


def resume_grading(out, manifest, config, task, parent):
    for path in sorted(parent.glob("*/result.json"), reverse=True):
        row = json.loads(path.read_text())
        patch = path.parent / "implementation.patch"
        if row["status"] not in {"grading", "interrupted", "infrastructure_error", "blocked", "quota"}:
            return False
        if not row.get("patch_sha256") or not patch.is_file():
            continue
        if digest(patch) != row["patch_sha256"]:
            raise Blocked("Frozen candidate hash changed. Verify the patch before grading.")
        checkpoint(out, path.parent, row, manifest, status="grading", grading_resumed=now())
        try:
            reward, code = verify_candidate(task, SINGLE_TURN / task, row["image_id"], row["repository_path"],
                                           patch, config, path.parent)
        except QuotaReached as exc:
            checkpoint(out, path.parent, row, manifest, status="quota", detail=str(exc))
            raise
        checkpoint(out, path.parent, row, manifest, status="scored", reward=reward, verifier_exit_code=code)
        return True
    return False


def record_agent(out, manifest, attempt, row, run, details):
    usage = details.get("usage") or {}
    agent_usage = {key: value for key, value in usage.items() if key != "attribution"}
    try:
        with (run / "harness/exec.jsonl").open() as file:
            events = (json.loads(line) for line in file)
            completed_turns = [event["usage"] for event in events if event.get("type") == "turn.completed"]
        if completed_turns:
            # Each resumed codex exec event reports usage cumulative within the session.
            agent_usage = {key: completed_turns[-1].get(key, 0)
                           for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")}
            agent_usage["completed_turns"] = len(completed_turns)
            agent_usage["total_tokens"] = agent_usage["input_tokens"] + agent_usage["output_tokens"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    exit_reason = details.get("exit_reason")
    logs = (attempt / "agent.log", run / "harness/exec.err", run / "harness/exec.jsonl")
    log_tail = ""
    for path in logs:
        if path.exists():
            with path.open("rb") as log:
                log.seek(max(0, path.stat().st_size - 16000))
                log_tail += log.read().decode(errors="replace")
    quota_hit = exit_reason == "usage_limit" or (exit_reason != "completed" and QUOTA.search(log_tail))
    status = "quota" if quota_hit else ("agent_complete" if exit_reason == "completed" else "agent_error")
    settings = details.get("settings", {})
    if status == "agent_complete":
        expected = manifest["configuration"]
        fields = ("model", "reasoning_effort", "context_window", "lane")
        if any(settings.get(key) != expected[key] for key in fields):
            status = "agent_error"
            row["detail"] = "Recorded agent settings differ from the experiment manifest."
        model_path = run / "harness/codex_home/model_catalog.json"
        catalog = json.loads(model_path.read_text())["models"]
        model = next((model for model in catalog if model["slug"] == expected["model"]), {})
        if model.get("truncation_policy") != {"mode": "tokens", "limit": expected["tool_output_limit"]}:
            status = "agent_error"
            row["detail"] = "Recorded tool output cap differs from the experiment manifest."
        if details.get("harness", {}).get("name") != ARMS[row["arm"]]:
            status = "agent_error"
            row["detail"] = "Recorded harness differs from the requested arm."
    continuation_log = run / "harness/continuations.jsonl"
    continuations = len(continuation_log.read_text().splitlines()) if continuation_log.exists() else 0
    checkpoint(out, attempt, row, manifest, status=status, agent_exit=exit_reason,
               continuations=continuations,
               continuation_limit_reached=(run / "harness/continuation-limit.txt").exists(),
               agent_settings={key: settings.get(key) for key in ("model", "reasoning_effort", "context_window", "lane")},
               agent_usage=agent_usage, trace=details.get("trace"), run_path=str(run.relative_to(out)))
    return status == "agent_complete"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "report", "preflight"))
    parser.add_argument("--output", type=Path, default=ROOT / "output-singleturn")
    parser.add_argument("--task", action="append")
    parser.add_argument("--arm", action="append", choices=ARMS)
    parser.add_argument("--cycle-images", action="store_true", help="Keep only the current task's Docker image")
    parser.add_argument("--local-rubric", action="store_true", help="Use the Codex login for SWE Atlas rubric grading")
    parser.add_argument("--limit", type=int, help="Maximum number of new trial attempts for this invocation")
    parser.add_argument("--snapshot", type=Path, help="Write a separate report from saved results while the run is active")
    parser.add_argument("--follow", action="store_true", help="Refresh a report snapshot until the active batch stops")
    args = parser.parse_args()
    out = args.output.resolve()
    if args.follow and not args.snapshot:
        parser.error("--follow requires --snapshot")
    if args.snapshot:
        destination = args.snapshot.resolve()
        if args.command != "report" or destination.parent != out or destination.suffix != ".md" or destination.name == "REPORT.md":
            parser.error("--snapshot requires report and a separate .md path inside the experiment output directory")
        manifest = json.loads((out / "manifest.json").read_text())
        if args.follow:
            print(f"Following checkpoints in {destination}", flush=True)
            follow_report(out, manifest, destination)
        else:
            report(out, manifest, destination)
        print(destination, flush=True)
        return 0
    out.mkdir(parents=True, exist_ok=True)
    with (out / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous_manifest = out / "manifest.json"
        local_rubric = args.local_rubric or (
            previous_manifest.exists()
            and json.loads(previous_manifest.read_text())["configuration"].get("rubric_transport") == "local-codex-cli"
        )
        config, manifest = load_experiment(out, local_rubric)
        import_stock(out, config)
        report(out, manifest)
        if args.command == "report":
            print(out / "REPORT.md")
            return 0
        arms = args.arm or list(ARMS)
        tasks = args.task or manifest["task_order"]
        if unknown := set(tasks) - manifest["tasks"].keys():
            parser.error(f"Unknown task: {sorted(unknown)}")
        if args.command == "preflight":
            print(f"{len(manifest['tasks'])} pinned tasks, {len(ARMS)} arms, "
                  f"{(len(manifest['tasks']) - len(REVIEW_TASKS)) * len(ARMS)} eligible trials.")
            print(capture([RELEASE / "codex/bin/codex", "login", "status"]))
            if local_rubric:
                print("SWE Atlas rubric: GPT-6 Luna at medium via the Codex CLI")
            else:
                for key in ("OPENAI_API_KEY", "OPENAI_API_BASE"):
                    print(f"{key}: {'set' if os.getenv(key) else 'missing'}")
            print(f"Free disk space: {shutil.disk_usage(out).free / 1024**3:.1f} GiB")
            return 0
        if args.cycle_images:
            with (ROOT / ".image-cycle.lock").open("w") as cycle_lock:
                fcntl.flock(cycle_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return run_trials(args, out, config, manifest, tasks, arms)
        return run_trials(args, out, config, manifest, tasks, arms)


def run_trials(args, out, config, manifest, tasks, arms):
    cycle = args.cycle_images
    if cycle:
        clear_cycle_builder()
        saved = records(out)
        for task in sorted({row["task"] for row in saved if row["status"] == "scored"}):
            retire_scored_image(task, saved)
    for path in sorted(out.glob("attempts/*/*/*/result.json")):
        row = json.loads(path.read_text())
        if row["status"] == "running":
            checkpoint(out, path.parent, row, manifest, status="interrupted",
                       detail="Previous invocation exited before finalizing this attempt.")
    completed = {(row["task"], row["arm"]) for row in records(out) if row["status"] == "scored"}
    attempts = 0
    deferred = set()
    for task in tasks:
        for arm in arms:
            if (task, arm) in completed:
                continue
            if task in REVIEW_TASKS:
                print(f"{task} {arm}: skipped for scope review", flush=True)
                continue
            if args.task is None and (gap := dependency_gap(task, config)):
                deferred.add(gap)
                continue
            family = manifest["tasks"][task]["family"]
            parent = out / "attempts" / task / arm
            try:
                if resume_grading(out, manifest, config, task, parent):
                    print(f"{task} {arm}: graded the saved candidate", flush=True)
                    continue
            except QuotaReached as exc:
                print(str(exc), file=sys.stderr)
                return 75
            except (Blocked, OSError, subprocess.SubprocessError, ValueError) as exc:
                print(f"{task} {arm}: could not grade the saved candidate ({type(exc).__name__})", file=sys.stderr)
                return 1
            if args.limit is not None and attempts >= args.limit:
                return 0
            attempt = parent / f"{len(list(parent.glob('[0-9][0-9][0-9][0-9]'))) + 1:04d}"
            attempt.mkdir(parents=True)
            row = {"task": task, "family": family, "arm": arm, "attempt": attempt.name,
                   "started": now(), "artifact_path": str(attempt.relative_to(out)),
                   "cycle_images": cycle,
                   "runner_source_sha256": source_hashes()}
            checkpoint(out, attempt, row, manifest, status="running")
            attempts += 1
            print(f"{task} {arm} attempt {attempt.name}", flush=True)
            try:
                trial(out, manifest, config, task, arm, attempt, row, cycle)
            except KeyboardInterrupt:
                checkpoint(out, attempt, row, manifest, status="interrupted",
                           free_disk_gib=round(shutil.disk_usage(out).free / 1024**3, 2))
                return 130
            except QuotaReached as exc:
                checkpoint(out, attempt, row, manifest, status="quota", detail=str(exc))
            except Blocked as exc:
                checkpoint(out, attempt, row, manifest, status="blocked", detail=str(exc))
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                checkpoint(out, attempt, row, manifest, status="infrastructure_error",
                           detail=type(exc).__name__)
                print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
            print(f"Saved {row['status']} in {out / 'REPORT.md'}", flush=True)
            if row["status"] != "scored":
                if detail := row.get("detail"):
                    print(detail, flush=True)
                return 75 if row["status"] == "quota" else 1
        if cycle:
            retire_scored_image(task, records(out))
    if deferred:
        for gap in sorted(deferred):
            print(gap, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
