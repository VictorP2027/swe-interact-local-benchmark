#!/usr/bin/env python3
"""Expose one task-owned Linux container as a small stdio MCP terminal."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def execute(container, repository, command, timeout):
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a nonempty shell command")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 600:
        raise ValueError("timeout_s must be an integer from 1 to 600")
    started = time.monotonic()
    # GNU timeout runs inside the container, so a timeout also stops child processes.
    process = subprocess.run(
        ["docker", "exec", "--workdir", repository, container,
         "timeout", "--signal=TERM", "--kill-after=5s", f"{timeout}s", "bash", "-lc", command],
        capture_output=True, text=True, errors="replace", timeout=timeout + 20,
    )
    return {"exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr,
            "elapsed_s": round(time.monotonic() - started, 3), "timed_out": process.returncode == 124}


def response(request, container, repository, log):
    method = request.get("method")
    if method == "initialize":
        return {"protocolVersion": request["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cs224v-task-terminal", "version": "1.0.0"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [{
            "name": "run",
            "description": (f"Run a shell command in the isolated Linux task repository at {repository}. "
                            "Read, edit, build and test project files here. State persists between calls. "
                            "Use Python or shell heredocs to edit files. Hidden grading tests are unavailable."),
            "inputSchema": {"type": "object", "properties": {
                "command": {"type": "string"}, "timeout_s": {"type": "integer", "minimum": 1,
                                                               "maximum": 600, "default": 120}},
                "required": ["command"], "additionalProperties": False},
        }]}
    if method == "tools/call":
        params = request["params"]
        if params.get("name") != "run":
            raise ValueError("Unknown tool")
        arguments = params.get("arguments", {})
        result = execute(container, repository, arguments.get("command"), arguments.get("timeout_s", 120))
        with log.open("a") as stream:
            stream.write(json.dumps({"command": arguments["command"], **result}) + "\n")
        return {"content": [{"type": "text", "text": json.dumps(result)}],
                "isError": result["exit_code"] in (125, 126, 127)}
    raise ValueError(f"Unsupported method: {method}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        try:
            result = response(request, args.container, args.repository, args.log)
            reply = {"jsonrpc": "2.0", "id": request["id"], "result": result}
        except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            reply = {"jsonrpc": "2.0", "id": request["id"],
                     "error": {"code": -32602, "message": str(exc)}}
        print(json.dumps(reply), flush=True)


if __name__ == "__main__":
    main()
