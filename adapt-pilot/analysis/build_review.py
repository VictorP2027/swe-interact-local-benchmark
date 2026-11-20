"""Build a deduplicated audit of the two SWE-Interact checkpoints."""
import argparse
import ast
import collections
import datetime
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--historical", required=True, type=Path, help="Nov 13 macOS single-turn output")
parser.add_argument("--current", required=True, type=Path, help="Nov 20 paired campaign output")
parser.add_argument("--output", required=True, type=Path, help="Local directory for analysis artifacts")
args = parser.parse_args()
HERE = args.output.resolve()
HERE.mkdir(parents=True, exist_ok=True)
OLD = args.historical.resolve()
NEW = args.current.resolve()
ARMS = ("stock", "adapt")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
LABELS = {
    "ansible-4c5ce": ("Interpreter respawn and SELinux support", "feature"),
    "ansible-c616": ("Ansible collection import resolution", "bug fix"),
    "ansible-e408": ("Ansible requirements from Git", "feature"),
    "element-web-d06": ("Element React root migration", "refactor"),
    "element-web-fe1": ("Element voice broadcast state", "refactor"),
    "flipt-c172": ("Flipt CUE validation command", "feature"),
    "flipt-e5fe": ("Flipt OCI storage source", "feature"),
    "teleport-d6ff": ("Teleport expression parsing", "bug fix"),
    "openlibrary-0a90": ("Open Library publisher/place split", "bug fix"),
    "openlibrary-4b7": ("Open Library author identifier matching", "feature"),
    "openlibrary-5de": ("Open Library ISBN and ASIN validation", "bug fix"),
    "openlibrary-b671": ("Open Library MARC 880 extraction", "bug fix"),
    "openlibrary-d40": ("Open Library import preview", "feature"),
    "nodebb-8168": ("NodeBB cover/profile file cleanup", "bug fix"),
    "nodebb-f083": ("NodeBB sorted-set scores", "feature"),
    "qutebrowser-702": ("qutebrowser delayed command units", "feature"),
    "qutebrowser-96b": ("qutebrowser duration parser", "bug fix"),
    "qutebrowser-bed": ("qutebrowser progress color interpolation", "bug fix"),
    "qutebrowser-deeb": ("qutebrowser URL numeric increment", "bug fix"),
    "qutebrowser-fea": ("qutebrowser runtime Qt version", "bug fix"),
}
ATLAS_LABELS = {
    "ed988137": "Suricata decode error propagation",
    "ed98813b": "Netdata RRD component extraction",
    "10d4b436": "k6 module resolution",
}

def read(path):
    return json.loads(path.read_text())

def name_category(task):
    if task.startswith("deepswe_"):
        return task.removeprefix("deepswe_").replace("-", " "), "feature"
    if task.startswith("rf_task-"):
        return ATLAS_LABELS.get(task[-8:], task), "refactor"
    suffix = task.split("__", 1)[-1]
    for key, val in LABELS.items():
        if suffix.startswith(key):
            return val
    return task, "refactor" if task.startswith("rf_") else "unclassified"

def arm_summary(root, row, path):
    artifact = (root / row["artifact_path"]).resolve()
    native = (root / row["run_path"]).resolve() if row.get("run_path") else None
    patch = artifact / "implementation.patch"
    text = patch.read_text(errors="replace") if patch.exists() else ""
    changed = re.findall(r"^diff --git a/(.*?) b/.*$", text, re.M)
    graders = sorted(artifact.glob("grading*/verifier.log"), key=lambda p: p.stat().st_mtime)
    log_path = graders[-1] if graders else None
    log = ANSI.sub("", log_path.read_text(errors="replace")) if log_path else ""
    errs = sorted((log_path.parent / "verifier").glob("run-script-stderr.txt")) if log_path else []
    stderr = "\n".join(p.read_text(errors="replace") for p in errs)
    found = []
    sessions = []
    if native:
        sessions = sorted((native / "harness/codex_home/sessions").rglob("*.jsonl"))
        for session in sessions:
            for lineno, line in enumerate(session.open(), 1):
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("type") == "compacted":
                    found.append({"time": event.get("timestamp"), "source": str(session), "line": lineno})
    outcomes = [l.strip() for l in log.splitlines()
                if re.search(r"^\s*Tests\s+\d|^=+ .* (?:passed|failed|error)|\[verifier\] (?:Baseline|New tests) exit code|^FINAL:|^RESULT:|^Tests reward:", l)]
    findings = [l.strip() for l in log.splitlines()
                if re.search(r"^FAILED |^\s*FAIL\s|^\s*--- FAIL:|^E\s+|^\d+ failed|error TS\d+|\[build failed\]|already declared through import|(?:TypeError|ReferenceError|ModuleNotFoundError):", l)]
    missing = re.findall(r"^Missing tests: (.+)$", log, re.M)
    if missing:
        try:
            missing = ast.literal_eval(missing[-1])
        except (ValueError, SyntaxError):
            missing = missing[-1:]
    infra = None
    task = row["task"]
    if "flipt-c172805" in task and "network is unreachable" in stderr:
        infra = "Verifier could not fetch the Go module in its offline container."
    if task.endswith("ed988137") and "ERROR: make clean failed" in log and "Running BASELINE tests" in log:
        infra = "Untouched baseline failed during make clean after the verifier reported missing libhtp."
    if row["reward"] == 1:
        category, detail = "pass", "Verifier recorded a full pass."
    elif infra:
        category, detail = "verifier setup", infra
    elif patch.exists() and patch.stat().st_size == 0:
        category, detail = "no implementation", "Frozen candidate patch is empty."
    elif re.search(r"Duplicate identifier|\[build failed\]|too many errors|error TS\d+|already declared through import", log + stderr):
        category, detail = "build or type error", (findings + [l for l in stderr.splitlines() if "error" in l.lower()])[:1]
    elif "must_have_pass=False" in log:
        category, detail = "rubric requirement", next((l for l in reversed(outcomes) if l.startswith("FINAL:")), "Must-have rubric failed.")
    elif missing:
        category, detail = "missing test coverage", f"Verifier reports missing expected tests, including {str(missing[0])[:190]}. Cause requires replay."
    elif findings:
        category, detail = "failed functional check", findings[0]
    else:
        category, detail = "unresolved verifier cause", "Reward is zero. Saved verifier evidence does not isolate a cause."
    if isinstance(detail, list):
        detail = detail[0] if detail else category
    return {"reward": row["reward"], "failure_label": category, "detail": detail[:290],
            "outcomes": outcomes[-8:], "changed_files": changed, "patch_bytes": patch.stat().st_size if patch.exists() else None,
            "patch": str(patch) if patch.exists() else None, "verifier_log": str(log_path) if log_path else None,
            "first_failed_checks": [l[:230] for l in findings[:4]], "missing_tests": len(missing),
            "compactions": found, "sessions_available": bool(sessions),
            "trace": row.get("trace"), "source": str(path),
            "image_id": row.get("image_id"), "upstream_base": row.get("upstream_base")}

def snapshot(root):
    results = collections.defaultdict(dict)
    for path in sorted(root.glob("attempts/*/*/*/result.json")):
        row = read(path)
        results[row["task"]][row["arm"]] = (row, path)
    pairs = {}
    incomplete = {}
    for task, entries in results.items():
        if any(a not in entries or entries[a][0]["status"] != "scored" for a in ARMS):
            incomplete[task] = {a: entries[a][0]["status"] if a in entries else "pending" for a in ARMS}
            continue
        a, b = (entries[arm][0] for arm in ARMS)
        assert a["image_id"] == b["image_id"], task
        assert not a.get("upstream_base") or not b.get("upstream_base") or a["upstream_base"] == b["upstream_base"], task
        pairs[task] = {arm: arm_summary(root, *entries[arm]) for arm in ARMS}
    return pairs, incomplete

def rates(rows):
    return {arm: {"passed": sum(v[arm]["reward"] == 1 for v in rows.values()), "total": len(rows)} for arm in ARMS}

def rate_text(d):
    p, n = d["passed"], d["total"]
    return f"{p}/{n} ({p / n:.1%})" if n else "—"

def file_link(path, text):
    return f"[{text}](<{path}>)" if path else text

def section_table(sets):
    return ["| Selection | Stock Codex | ADAPT |", "| --- | ---: | ---: |",
            *[f"| {key} | {rate_text(x['stock'])} | {rate_text(x['adapt'])} |" for key, x in sets.items()]]

old, old_open = snapshot(OLD)
new, new_open = snapshot(NEW)
all_pairs = old | new
excluded = {t for t, p in all_pairs.items() if any(p[a]["failure_label"] == "verifier setup" for a in ARMS)}
audited = {t: p for t, p in all_pairs.items() if t not in excluded}
totals = {"Nov 13 saved pairs": rates(old), "Nov 20 saved pairs": rates(new),
          "Combined unique pairs, using recorded scores": rates(all_pairs),
          "Combined, excluding confirmed verifier blockers": rates(audited)}
by_type = {kind: rates({t:p for t,p in audited.items() if name_category(t)[1] == kind})
           for kind in ("feature", "bug fix", "refactor")}
by_family = {name: rates({t:p for t,p in audited.items() if t.startswith(prefix)})
             for prefix, name in (("deepswe_", "DeepSWE"), ("swebenchpro_", "SWE-bench Pro"), ("rf_", "SWE Atlas"))}
labels = {arm: dict(collections.Counter(p[arm]["failure_label"] for p in all_pairs.values())) for arm in ARMS}
tstamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
payload = {"snapshot_at": tstamp, "counts": totals, "by_task_type_audited": by_type, "by_family_audited": by_family,
           "failure_labels": labels, "overlap": sorted(old.keys() & new.keys()), "excluded_from_audited_rate": sorted(excluded),
           "nov_13_incomplete": old_open, "nov_20_incomplete": new_open,
           "cases": [{"task_id":t, "name":name_category(t)[0], "task_type":name_category(t)[1],
                      "selected_week":"Nov 20" if t in new else "Nov 13",
                      "nov_13":old.get(t), "nov_20":new.get(t),
                      "confirmed_verifier_exclusion":t in excluded} for t in sorted(all_pairs)]}
(HERE / "case-evidence.json").write_text(json.dumps(payload, indent=2) + "\n")

lines = ["# SWE-Interact two-week review", "", f"Snapshot {tstamp}", "",
         "Each task contributes one complete stock/ADAPT pair. The newer complete pair takes precedence where both weeks cover the same task. "
         "Partial pairs stay pending. The two weeks share the actor model, effort, budget and dataset pin, but differ in coding environments and some verifier paths. "
         "The combined figures describe coverage across these setups.", "",
         *section_table(totals), "",
         f"Repeated pairs replaced: {len(old.keys() & new.keys())}. Newly covered task IDs: {len(new.keys() - old.keys())}. "
         f"Confirmed verifier blockers removed from the audited denominator: {len(excluded)}.", "",
         "## Aggregate by task type", "", *section_table(by_type), "",
         "## Aggregate by benchmark family", "", *section_table(by_family), "",
         "## Failure labels on recorded pairs", "",
         "Labels describe the strongest observable evidence. Missing test coverage may reflect a candidate problem, discovery mismatch or verifier setup. "
         "Only confirmed verifier blockers are excluded from the audited figures.", "",
         "| Outcome or failure label | Stock Codex | ADAPT |", "| --- | ---: | ---: |",
         *[f"| {k} | {labels['stock'].get(k,0)} | {labels['adapt'].get(k,0)} |"
           for k in sorted(set(labels["stock"]) | set(labels["adapt"]))], "",
         "## Vitest duration sharding", "",
         "| Run | Stock feature tests | ADAPT feature tests | Recorded compactions, stock / ADAPT |",
         "| --- | ---: | ---: | ---: |", "| Nov 13 | 70/71 | 67/71 | 0 / 1 |",
         "| Nov 20 | 15/71, empty patch | 70/71 | 0 / 1 |", "",
         "Both weeks scored 0/0. The old stock patch failed duration-based sorting. The old ADAPT patch failed timestamp recency, sorting and two isolation checks. "
         "In the rerun, stock inspected the repo and wrote no code. ADAPT shipped the requested sharding changes and failed only timestamp recency.", "",
         "Both ADAPT patches convert recordedAt to seconds. The supplied example uses a ten-digit timestamp, while the explicit TTL formula compares against Date.now() in milliseconds. "
         "The exact formula was present in all 23 pre-compaction and 20 post-compaction ordinary requests on Nov 13, and all 16 before and 18 after on Nov 20. "
         "The Nov 20 compaction summary also preserved the units question. The recorded trace supports an implementation or interpretation error. It supplies no evidence that compaction removed the requirement.", "",
         "See the saved Vitest review packet for the patch and timestamp write timeline.", "",
         "## Context review beyond Vitest", ""]
for task, p in sorted(all_pairs.items()):
    if task == "deepswe_vitest-duration-sharding":
        continue
    history = [("Nov 13", old.get(task)), ("Nov 20", new.get(task))]
    marks = [f"{week} {arm} {len(pair[arm]['compactions'])}" for week, pair in history if pair
             for arm in ARMS if pair[arm]["compactions"]]
    if not marks:
        continue
    if task.startswith("deepswe_arcane"):
        reason = "ADAPT's patch accesses Docker inspect fields absent from the pinned client type. ContainerInspect and HostConfig appear before and after each compaction in the session. Stock compiles the baseline, then the candidate build fails on a pagination name collision. Pagination appears before and after stock compaction. The trace shows continued work on the relevant code and does not isolate a missing observation."
    elif task.endswith("ed988137"):
        reason = "Both candidates were blocked during baseline setup before candidate tests. The ADAPT compactions cannot explain the two verifier zeros."
    else:
        reason = "The newer pair's tests succeeded and both implementations missed required rubric checks. The stock replacement history retains RRD_ALGORITHM and its extraction file, and both reappear later in the session. No specific missed rubric has been traced to a lost requirement."
    lines += [f"- **{name_category(task)[0]}** ({', '.join(marks)}). {reason}"]
lines += ["", "## Evidence for each complete pair", "",
          "Each row links to the selected frozen patches and verifier logs. The JSON includes both weeks for repeated tasks, changed files, test outcomes, and recorded compaction timestamps. "
          "A zero in the compaction column means no explicit marker was found in the saved sessions.", "",
          "| Task | Type | Pair week | Stock | ADAPT | Compactions, S/A |",
          "| --- | --- | --- | --- | --- | --- |"]
for t, pair in sorted(all_pairs.items()):
    title, kind = name_category(t)
    arm_cells = []
    for a in ARMS:
        d = pair[a]
        arm_cells.append(f"{d['reward']:g} · {d['failure_label']} · {file_link(d['patch'], 'patch')} · {file_link(d['verifier_log'], 'log')}")
    marks = "/".join(str(len(pair[a]["compactions"])) if pair[a]["sessions_available"] else "?" for a in ARMS)
    lines.append(f"| {title} | {kind} | {'Nov 20' if t in new else 'Nov 13'} | {arm_cells[0]} | {arm_cells[1]} | {marks} |")
lines += ["", "## Multi-turn status", "",
          "The upstream five-stage Vitest task and adaptive maintainer are present in the dataset. The original maintainer needs the GPT-5.5 high model gateway. "
          "No configured gateway credentials were present in the shell or the documented local environment file. The prior local relay was a prototype and no live model exchange was completed. "
          "No new multi-turn pair was run. The paired Vitest protocol holds the maintainer model, persona, stage fixtures, tool access and verifier constant and logs the requirements actually revealed for each arm.", "",
          "[SWE-Interact, §§2.3–2.4](https://arxiv.org/html/2606.30573v1#S2.SS3) and " +
          "See the paired Vitest protocol in the analysis folder.", "",
          file_link(str(HERE / "case-evidence.json"), "Full per-task evidence and counts") + "."]
(HERE / "REVIEW.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"counts":totals, "by_family":by_family, "by_type":by_type, "excluded":sorted(excluded), "overlap":len(old.keys() & new.keys()), "pending":new_open}, indent=2))
