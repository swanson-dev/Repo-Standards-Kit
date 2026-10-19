#!/usr/bin/env python3
"""RFC-0007 spike: an enforce-once Stop hook with a fixed test reason.

First stop (`stop_hook_active` false or missing): print a block decision, exit 0.
Second stop (`stop_hook_active` true): print nothing, exit 0.
`--wrapped` also nests the decision in VS Code's `hookSpecificOutput` wrapper.
Each run appends its input and output to `spike-hook.log` beside this file;
`--no-log` skips that.
"""
import json
import sys
import time
from pathlib import Path


def main(argv):
    wrapped = "--wrapped" in argv
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    out = None
    if not payload.get("stop_hook_active"):
        fmt = "wrapped" if wrapped else "top-level"
        event = payload.get("hook_event_name") or payload.get("hookEventName") or "unnamed"
        reason = (
            "RFC-0007 spike: the Stop hook blocked this stop. "
            f"Reply with exactly one line, SPIKE-ACK {fmt} {event}, and then stop."
        )
        out = {"decision": "block", "reason": reason}
        if wrapped:
            out["hookSpecificOutput"] = {"hookEventName": "Stop", "decision": "block", "reason": reason}
        print(json.dumps(out), flush=True)
    if "--no-log" not in argv:
        entry = {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "argv": argv, "input": payload, "output": out}
        try:
            with Path(__file__).with_name("spike-hook.log").open("a", encoding="utf-8") as log:
                log.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # ponytail: the log is a test aid; never let it change the hook's result
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
