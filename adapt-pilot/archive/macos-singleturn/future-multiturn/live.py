"""Archived prototype. Reconnect to a dedicated multi-turn runner before use."""

import json
import hashlib
import os
import re
import secrets
import subprocess
import sys
import time
import tomllib
from urllib.error import HTTPError
from urllib.request import urlopen

from run import (
    ROOT, RELEASE, Blocked, QUOTA, agent_environment, capture, checkpoint, digest, docker, logged,
    grading_directory, metadata, record_agent, save, stock_command, verifier_reward,
)


STAGES = ("01_plan", "02_implement", "03_handoff", "04_write_tests", "05_test_handoff")
ADAPTER = """Run this SWE-Interact stage in your current repository checkout.
The repository directory in the upstream instructions maps to your current directory.
For this run, .swe-interact/plan.md is the plan location, .swe-interact/base_commit.txt
is the base marker, and .swe-interact/logs/agent/ is the handoff directory.
Use the user-server MCP tool for ask_user when directed. Keep the original stage
boundaries and Git commit requirements. Execute locally with the available tools.
"""


def stage_prompt(path, repo):
    prompt = path.read_text()
    # Replace tokens once so the relative handoff paths cannot be mapped twice.
    replacements = {
        "/tmp/plan.md": ".swe-interact/plan.md",
        "/app/plan.md": ".swe-interact/plan.md",
        "/tmp/base_commit.txt": ".swe-interact/base_commit.txt",
        "/logs": ".swe-interact/logs",
        repo: ".",
        "/app": ".",
    }
    pattern = r"(?<![\w./])(?:" + "|".join(map(re.escape, sorted(replacements, key=len, reverse=True))) + r")(?=$|[\s/`'\".,;)])"
    prompt = re.sub(pattern, lambda match: replacements[match.group()], prompt)
    return ADAPTER + "\n" + prompt


def start_maintainer(task_dir, platform, attempt, config, cleanup):
    identity = "swe-live-" + secrets.token_hex(5)
    docker("network", "create", "--internal", identity)
    cleanup.append(("network", "rm", identity))
    environment = task_dir / "environment"
    server_dir = environment / "user-server"
    tag = "cs224v-swe-user:" + digest(server_dir / "persona.md")[:16]
    iid = attempt / "maintainer-image-id"
    if logged(["docker", "build", "--platform", platform, "--iidfile", iid, "-t", tag, server_dir],
              attempt / "maintainer-build.log"):
        raise Blocked("Maintainer image build failed. See maintainer-build.log.")
    server_image = iid.read_text().strip()
    secrets_env = dict(os.environ, SIM_USER_MODEL=config["simulator_model"])
    user = docker("create", "--name", f"{identity}-user", "--platform", platform,
                  "--network", "bridge", "-p", "127.0.0.1::8000",
                  "--env", "LITELLM_API_KEY", "--env", "LITELLM_BASE_URL", "--env", "SIM_USER_MODEL",
                  "--env", "SIM_USER_MAX_TOOL_ROUNDS=6",
                  "--env", f"SIM_USER_EXPORT_TOKEN={secrets.token_hex(24)}", server_image, env=secrets_env)
    cleanup.append(("rm", "-f", user))
    docker("network", "connect", "--alias", "user-server", identity, user)
    docker("start", user)
    port = docker("port", user, "8000/tcp").rsplit(":", 1)[1]
    url = f"http://127.0.0.1:{port}/mcp"
    for _ in range(30):
        try:
            # Any HTTP response proves that the service is accepting connections.
            with urlopen(url, timeout=2):
                pass
        except HTTPError:
            pass
        except OSError:
            time.sleep(1)
            continue
        break
    else:
        logged(["docker", "logs", user], attempt / "maintainer.log")
        raise Blocked("Maintainer did not start. See maintainer.log.")
    return url, user, server_image, identity


def run_with_inspector(command, attempt, task_dir, image, platform, network, cleanup):
    with (attempt / "agent.log").open("w") as log:
        with subprocess.Popen([str(arg) for arg in command], cwd=RELEASE, env=agent_environment(),
                              stdout=log, stderr=subprocess.STDOUT) as agent:
            try:
                for _ in range(300):
                    workspace = next(iter((attempt / "runs").glob("*/workspace/.git/HEAD")), None)
                    if workspace is not None or agent.poll() is not None:
                        break
                    time.sleep(0.1)
                if workspace is None:
                    if agent.poll() is None:
                        raise Blocked("Codex did not initialize a Git workspace for the maintainer.")
                    return
                inspector = docker(
                    "run", "-d", "--platform", platform, "--network", network, "--network-alias", "main",
                    "--mount", f"type=bind,source={workspace.parent.parent},target=/candidate,readonly",
                    "--mount", f"type=bind,source={task_dir / 'environment/repo_exec_server.py'},target=/repo_exec.py,readonly",
                    "--entrypoint", "bash", image, "-c",
                    'git config --global --add safe.directory /candidate; '
                    'REPO_EXEC_ROOT=/candidate exec python3 /repo_exec.py',
                )
                cleanup.append(("rm", "-f", inspector))
                agent.wait()
            finally:
                if agent.poll() is None:
                    agent.terminate()
                    try:
                        agent.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        agent.kill()


def grade_live(task_dir, task, config, attempt, image, repo, base, run):
    workspace = run / "workspace"
    logs = grading_directory(attempt)
    git = ["git", "-C", workspace]
    candidate = capture([*git, "rev-parse", "HEAD"])
    dirty = bool(capture([*git, "status", "--porcelain", "--untracked-files=no"]))
    marker = workspace / ".swe-interact/base_commit.txt"
    if dirty or not marker.is_file() or marker.is_symlink() or marker.read_text().strip() != base:
        # These are task failures in the upstream final handoff wrapper.
        save(logs / "handoff_failure.json", {"dirty_tracked_files": dirty, "valid_base_marker": (
            marker.is_file() and not marker.is_symlink() and marker.read_text().strip() == base)})
        return 0, 0
    if candidate == base or capture([*git, "rev-parse", "HEAD~1"]) == base:
        save(logs / "handoff_failure.json", {"error": "Missing separate implementation and test commits."})
        return 0, 0
    # The verifier sees the original commit history, including a separate test commit.
    bundle = attempt / "candidate.bundle"
    if not bundle.exists():
        subprocess.run([*git, "bundle", "create", bundle, f"{base}..HEAD"], check=True)
    for file in ("change-log.txt", "final-status.txt", "final.diff", "test-handoff-status.txt"):
        artifact = workspace / ".swe-interact/logs/agent" / file
        if artifact.is_file() and not artifact.is_symlink():
            (logs / "agent").mkdir(exist_ok=True)
            (logs / "agent" / file).write_bytes(artifact.read_bytes())
    final = task_dir / "steps/05_test_handoff"
    task_settings = tomllib.loads((task_dir / "task.toml").read_text())
    env = dict(os.environ)
    network = ["--network", "none"]
    if task.startswith("rf_"):
        env.update(EVAL_API_KEY=env["OPENAI_API_KEY"], EVAL_BASE_URL=env["OPENAI_API_BASE"],
                   EVAL_MODEL=config["rubric_model"])
        network = ["--env", "EVAL_API_KEY", "--env", "EVAL_BASE_URL", "--env", "EVAL_MODEL"]
    command = [
        "docker", "run", "--rm", "--platform", config["platform"], *network,
        "--mount", f"type=bind,source={final / 'tests'},target=/tests,readonly",
        "--mount", f"type=bind,source={bundle},target=/candidate.bundle,readonly",
        "--mount", f"type=bind,source={logs},target=/logs",
        "--env", f"PYTEST_ADDOPTS={config['verifier_pytest_addopts'].get(task, '')}",
        "--workdir", repo, "--entrypoint", "bash", image, "-c",
        'set -e; test "$(git rev-parse HEAD)" = "$1"; git fetch /candidate.bundle HEAD; '
        'git checkout --detach FETCH_HEAD; test "$(git rev-parse HEAD)" = "$2"; '
        'printf "%s\\n" "$1" >/tmp/base_commit.txt; bash /tests/test.sh',
        "bash", base, candidate,
    ]
    timeout = task_settings["steps"][-1]["verifier"]["timeout_sec"]
    code = logged(command, logs / "verifier.log", timeout=timeout, env=env)
    return verifier_reward(logs, code)


def run_live(out, manifest, config, task, harness, attempt, row, task_dir, image, repo, base, seed):
    cleanup = []
    try:
        url, server, server_image, network = start_maintainer(task_dir, config["platform"], attempt, config, cleanup)
        for previous in (out / "attempts" / task).glob("*/*/result.json"):
            saved = json.loads(previous.read_text())
            if saved.get("maintainer_image_id") and saved["maintainer_image_id"] != server_image:
                raise Blocked("Maintainer image differs from a saved attempt for this task.")
        checkpoint(out, attempt, row, manifest, maintainer_image_id=server_image)
        mcp = attempt / "mcp.json"
        save(mcp, {"user-server": {"command": sys.executable, "args": [str(ROOT / "mcp_proxy.py"), url]}})
        stages = [stage_prompt(task_dir / "steps" / stage / "instruction.md", repo) for stage in STAGES]
        checkpoint(out, attempt, row, manifest, stage_prompt_sha256={
            name: hashlib.sha256(prompt.encode()).hexdigest() for name, prompt in zip(STAGES, stages)
        })
        followups = [part for stage in stages[1:] for part in ("--follow-up", stage)]
        command = stock_command(attempt, config, task, harness, seed, stages[0],
                                "--mcp-servers", mcp, *followups)
        run_with_inspector(command, attempt, task_dir, image, config["platform"], network, cleanup)
        run, details = metadata(attempt)
        complete = record_agent(out, manifest, attempt, row, run, details)
        logged(["docker", "logs", server], attempt / "maintainer.log")
        if subprocess.run(["docker", "cp", f"{server}:/tmp/user-server-logs", str(attempt / "maintainer")],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode and complete:
            raise Blocked("The coding agent made no recorded calls to the live maintainer.")
        if not complete:
            return
        events = [json.loads(line) for line in (attempt / "maintainer/events.jsonl").read_text().splitlines()]
        finished = sum(event["event"] == "ask_user_finish" for event in events)
        errors = [event for event in events if event["event"] in {"ask_user_model_error", "llm_plain_error"}]
        checkpoint(out, attempt, row, manifest, maintainer_replies=finished, maintainer_errors=len(errors))
        if errors:
            if any(QUOTA.search(event.get("error_preview", "")) for event in errors):
                checkpoint(out, attempt, row, manifest, status="quota", detail="Maintainer model quota reached.")
                return
            raise Blocked("Maintainer model errors occurred. See local maintainer logs.")
        if finished < 2 or row["agent_usage"].get("completed_turns") != len(STAGES):
            raise Blocked("The agent did not complete the live maintainer protocol.")
        candidate = capture(["git", "-C", run / "workspace", "rev-parse", "HEAD"])
        checkpoint(out, attempt, row, manifest, status="grading", candidate_commit=candidate)
        reward, code = grade_live(task_dir, task, config, attempt, image, repo, base, run)
        bundle = attempt / "candidate.bundle"
        checkpoint(out, attempt, row, manifest, status="scored", reward=reward, verifier_exit_code=code,
                   candidate_sha256=digest(bundle) if bundle.exists() else None)
    finally:
        for args in reversed(cleanup):
            subprocess.run(["docker", *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
