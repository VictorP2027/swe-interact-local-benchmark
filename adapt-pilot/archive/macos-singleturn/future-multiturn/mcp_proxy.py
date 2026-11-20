"""Archived stdio relay for the upstream SWE-Interact maintainer."""

import json
import sys
from urllib.request import Request, urlopen


def proxy(url):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    for line in sys.stdin:
        request = json.loads(line)
        request_id = request.get("id")
        method = request.get("method")
        if method == "tools/call" and request.get("params", {}).get("name") != "ask_user":
            reply = {"error": {"code": -32601, "message": "Only ask_user is available"}}
        else:
            try:
                with urlopen(Request(url, data=line.encode(), headers=headers), timeout=600) as response:
                    if session := response.headers.get("Mcp-Session-Id"):
                        headers["Mcp-Session-Id"] = session
                    if request_id is None:
                        continue
                    if response.headers.get_content_type() == "text/event-stream":
                        events = (json.loads(part[6:]) for part in response if part.startswith(b"data: "))
                        reply = next(event for event in events if event.get("id") == request_id)
                    else:
                        reply = json.load(response)
                    if method == "initialize":
                        headers["MCP-Protocol-Version"] = reply["result"]["protocolVersion"]
            except (OSError, ValueError, KeyError, StopIteration):
                reply = {"error": {"code": -32603, "message": "SWE-Interact maintainer transport failed"}}
        if request_id is not None:
            print(json.dumps({"jsonrpc": "2.0", "id": request_id, **reply}), flush=True)


if __name__ == "__main__":
    proxy(sys.argv[1])
