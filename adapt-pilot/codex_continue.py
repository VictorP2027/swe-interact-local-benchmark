"""Delegate to pinned Codex and resume clarification questions inside the harness."""

import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


def asks_question(message):
    # The preprint does not specify a detector. Inspect the final visible
    # line and ignore fenced code, quoted examples and trailing Markdown.
    lines = []
    fenced = False
    for line in message.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and not line.lstrip().startswith(">") and line.strip():
            lines.append(line.strip())
    return bool(lines and re.search(r"\?[*_`”\"')\]]*\s*$", lines[-1]))


def run_turn(binary, args, cwd=None):
    thread_id = None
    with subprocess.Popen([binary, *args], cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE) as turn:
        try:
            for line in turn.stdout:
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("type") == "thread.started":
                    thread_id = event["thread_id"]
            return turn.wait(), thread_id
        finally:
            if turn.poll() is None:
                turn.terminate()
                try:
                    turn.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    turn.kill()


def main():
    binary = os.environ["SWE_CONTINUE_CODEX"]
    args = sys.argv[1:]
    # The real delegate implements CODEX_CODE_MODE_STORE_LOAD.
    if not args or args[0] != "exec" or "--output-last-message" not in args or "-C" not in args:
        os.execv(binary, [binary, *args])
    last_message = Path(args[args.index("--output-last-message") + 1])
    workspace = args[args.index("-C") + 1]
    code, thread_id = run_turn(binary, args)
    log = last_message.parent / "continuations.jsonl"
    limit = int(os.environ["SWE_CONTINUE_LIMIT"])
    for _ in range(limit):
        if code or not thread_id or not last_message.is_file() or not asks_question(last_message.read_text()):
            return code
        with log.open("a") as file:
            file.write(json.dumps({"thread_id": thread_id, "message": "continue"}) + "\n")
        last_message.unlink()
        code, resumed = run_turn(binary, [
            "exec", "resume", "--strict-config", "--json", "--skip-git-repo-check",
            "--output-last-message", str(last_message), thread_id, "continue",
        ], cwd=workspace)
        if not code and resumed != thread_id:
            print("Continuation did not retain the original thread", file=sys.stderr)
            return 1
    if not code and last_message.is_file() and asks_question(last_message.read_text()):
        (last_message.parent / "continuation-limit.txt").write_text("The final response still ends with a question.\n")
    return code


if __name__ == "__main__":
    # Let the harness timeout unwind the wrapper and stop the active Codex child.
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
