"""Compare archived Victor P. scores and classify the paired audit results."""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--review", required=True, type=Path, help="Directory containing case-evidence.json")
parser.add_argument("--archive", type=Path, default=Path(__file__).resolve().parents[2] / "results")
args = parser.parse_args()
HERE = args.review.resolve()
ARCHIVE_ROOT = args.archive.resolve()
ARCHIVE = json.loads((ARCHIVE_ROOT / "summary.json").read_text())
SNAPSHOT = json.loads((HERE / "case-evidence.json").read_text())
ARCHIVE_BY_TASK = {r["task"]: r for r in ARCHIVE["tasks"]}
ARMS = ("stock", "adapt")
LABELS = ("Pass", "Verifier setup", "Build or type error", "No implementation",
          "Missed requirement", "Failed test", "Test coverage unresolved", "Other unresolved failure")
REQUIREMENTS = {
    ("deepswe_fastapi-deprecation-response-headers", "adapt"): "FastAPI.get did not accept the requested sunset keyword.",
    ("deepswe_httpx-deterministic-cookie-store", "stock"): "The required public httpx.CookieStore class was absent.",
    ("deepswe_vitest-duration-sharding", "adapt"): "recordedAt was stored in seconds, while the expected timestamp and explicit TTL formula use milliseconds.",
    ("deepswe_sqlite-utils-safe-import-checkpoints", "adapt"): "The expected enable-safe-import command was absent from the registered commands.",
    ("deepswe_cattrs-partial-structuring-recovery", "stock"): "Refining changed an already structured field from 1 to 999, contrary to the preservation requirement.",
    ("deepswe_cattrs-partial-structuring-recovery", "adapt"): "Refining changed an already structured field from 1 to 999, contrary to the preservation requirement.",
}
BASE_LABELS = {
    "pass": "Pass",
    "verifier setup": "Verifier setup",
    "build or type error": "Build or type error",
    "no implementation": "No implementation",
    "rubric requirement": "Missed requirement",
    "failed functional check": "Failed test",
    "missing test coverage": "Test coverage unresolved",
    "unresolved verifier cause": "Other unresolved failure",
}
TYPES = ("feature", "bug fix", "refactor")


def observations(log_path):
    if not log_path:
        return [], {}, None
    log = Path(log_path)
    observed_path = log.parent / "verifier/output.json"
    if not observed_path.is_file():
        return [], {}, None
    tests = json.loads(observed_path.read_text()).get("tests", [])
    statuses = {t["name"]: str(t.get("status", "")).upper() for t in tests if "name" in t}
    match = re.findall(r"^Missing tests: (.+)$", log.read_text(errors="replace"), re.M)
    expected = ast.literal_eval(match[-1]) if match else []
    return expected, statuses, str(observed_path)


def classify(case, arm, record):
    task = case["task_id"]
    label = BASE_LABELS[record["failure_label"]]
    detail = record["detail"]
    expected, observed, parsed = observations(record["verifier_log"])
    missing_breakdown = Counter(observed.get(name, "ABSENT") for name in expected)
    first_failed = next((name for name in expected if observed.get(name) in {"FAILED", "ERROR"}), None)
    if (task, arm) in REQUIREMENTS and label in {"Failed test", "Other unresolved failure"}:
        label, detail = "Missed requirement", REQUIREMENTS[task, arm]
    elif label == "Test coverage unresolved":
        if first_failed:
            label = "Failed test"
            detail = f"Parsed test results mark {first_failed} {observed[first_failed].lower()}."
        elif "flipt-c172805" in task:
            label = "Build or type error"
            detail = "The verifier could not resolve the required cuelang.org/go/cue/cuecontext module, so the expected tests did not run."
        elif expected:
            detail = f"{missing_breakdown['ABSENT']} expected test names have no matching parsed result. Example: {expected[0]}."
    return {
        "reward": record["reward"], "label": label, "detail": detail,
        "previous_label": record["failure_label"], "patch": record["patch"], "log": record["verifier_log"],
        "test_results": parsed, "test_status_counts": dict(Counter(observed.values())),
        "not_passing_expected_test_status_counts": dict(missing_breakdown),
        "first_confirmed_failed_expected_test": first_failed,
        "first_failed_checks": record["first_failed_checks"],
    }


def archive_evidence(task):
    archived = ARCHIVE_BY_TASK[task]
    file = ARCHIVE_ROOT / archived["result"]
    evidence = json.loads(file.read_text())
    return {
        "reward": archived["reward"], "archived_status": archived["status"], "result": str(file),
        "evidence": evidence.get("verifier") or evidence.get("note"),
        "notes": archived.get("evaluation_notes"),
        "passed_baseline_tests": evidence.get("passed_baseline_tests"),
        "passed_feature_tests": evidence.get("passed_feature_tests"),
    }


def link(path, label):
    return f"[{label}](<{path}>)" if path else label


def successes(rows, arm):
    return sum(r[arm]["reward"] == 1 for r in rows)


def rate(rows, arm):
    return f"{successes(rows, arm)}/{len(rows)} ({successes(rows, arm) / len(rows):.1%})" if rows else "—"


def pair_outcomes(rows):
    counter = Counter(tuple(r[a]["reward"] == 1 for a in ARMS) for r in rows)
    return {k: counter[p] for k, p in (("Both pass", (True, True)), ("Stock only", (True, False)),
                                       ("ADAPT only", (False, True)), ("Neither", (False, False)))}


def table_type(rows):
    lines = ["| Task type | Pairs | Stock Codex | ADAPT | Victor P. archive | Both pass | Stock only | ADAPT only | Neither |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name in (*TYPES, "Total"):
        sub = rows if name == "Total" else [r for r in rows if r["task_type"] == name]
        cols = " | ".join(map(str, pair_outcomes(sub).values()))
        lines.append(f"| {name} | {len(sub)} | {rate(sub, 'stock')} | {rate(sub, 'adapt')} | {rate(sub, 'victor_p')} | {cols} |")
    return lines


rows = []
for case in SNAPSHOT["cases"]:
    selected = case["nov_20"] or case["nov_13"]
    task = case["task_id"]
    rows.append({"task_id": task, "name": case["name"], "task_type": case["task_type"],
                 "selected_week": case["selected_week"], "excluded": case["confirmed_verifier_exclusion"],
                 **{arm: classify(case, arm, selected[arm]) for arm in ARMS},
                 "victor_p": archive_evidence(task)})

audited = [r for r in rows if not r["excluded"]]
both_failed = [r for r in rows if r["victor_p"]["reward"] == 1 and not any(r[a]["reward"] == 1 for a in ARMS)]
one_failed = [r for r in rows if r["victor_p"]["reward"] == 1 and sum(r[a]["reward"] == 1 for a in ARMS) == 1]
categories = {a: Counter(r[a]["label"] for r in rows) for a in ARMS}
type_failure = {kind: {a: Counter(r[a]["label"] for r in rows if r["task_type"] == kind) for a in ARMS}
                for kind in TYPES}
legacy_missing = [r[a] for r in rows for a in ARMS if r[a]["previous_label"] == "missing test coverage"]
had_failed = [r for r in legacy_missing if r["first_confirmed_failed_expected_test"]]
assert len({r["task_id"] for r in rows}) == len(rows)
assert all(sum(categories[a].values()) == len(rows) for a in ARMS)
assert all(r["victor_p"]["reward"] == 1 and r["stock"]["reward"] == r["adapt"]["reward"] == 0 for r in both_failed)
assert not {r["task_id"] for r in both_failed} & {r["task_id"] for r in one_failed}

lines = [
    "# SWE-Interact aggregate and Victor P. comparison", "",
    f"Two-week checkpoint from {SNAPSHOT['snapshot_at']}. Each task uses the newer complete pair when repeated.", "",
    f"Victor P.'s first-attempt archive reports **{len(both_failed)} passes where both of our arms scored zero** "
    f"and **{len(one_failed)} more where one arm scored zero**. His archive includes coding done directly in chat and some alternative grading paths. "
    "The results below compare task IDs. They cannot isolate the effect of the harness or the actor model.", "",
    "## Victor P. passed and both of our arms failed", "",
    "| Task | Type | Stock Codex failure | ADAPT failure | Victor P. evidence |",
    "| --- | --- | --- | --- | --- |",
]
for r in both_failed:
    external = r["victor_p"]
    notes = {"passed_existing_implementation": "Earlier implementation, native verification",
             "passed_native_verifier": "Supplied tests, native verifier"}.get(external["archived_status"], "Archived pass")
    if external["passed_feature_tests"] is not None:
        notes = f"{external['passed_baseline_tests']}/{external['passed_baseline_tests']} baseline and {external['passed_feature_tests']}/{external['passed_feature_tests']} feature tests"
    elif external["notes"] and "NodeBB" in r["name"]:
        notes = "Archived pass, baseline-checked runtime retry"
    cells = [f"{r[a]['label']} · {link(r[a]['log'], 'grader')}" for a in ARMS]
    lines.append(f"| {r['name']} | {r['task_type']} | {cells[0]} | {cells[1]} | {link(external['result'], notes)} |")
lines += ["", "## Victor P. and one of our arms passed", "",
          "| Task | Type | Our passing arm | Our failing arm | Victor P. evidence |",
          "| --- | --- | --- | --- | --- |"]
for r in one_failed:
    passed, = (a for a in ARMS if r[a]["reward"] == 1)
    failed, = (a for a in ARMS if a != passed)
    lines.append(f"| {r['name']} | {r['task_type']} | {passed} | {failed}, {r[failed]['label']} | {link(r['victor_p']['result'], 'Archived pass')} |")
lines += ["", "## Task type and paired outcomes", "",
          "Features add or extend behavior. Bug fixes correct existing behavior. Refactors change structure or interfaces primarily to improve the existing implementation. "
          f"The table excludes {len(rows) - len(audited)} confirmed verifier blockers from the {len(rows)} recorded pairs.", "",
          *table_type(audited), "",
          "## Failure categories", "",
          "Each arm has one primary label based on the strongest saved evidence. A missed requirement is a concrete absent interface, wrong specified behavior or failed must-have rubric. "
          "A failed test is an observed failure where the available evidence does not establish that narrower cause.", "",
          "| Primary outcome | Stock, all recorded | ADAPT, all recorded |",
          "| --- | ---: | ---: |",
          *[f"| {k} | {categories['stock'][k]} | {categories['adapt'][k]} |" for k in LABELS], "",
          f"Of {len(legacy_missing)} attempts previously labeled missing test coverage, {len(had_failed)} have expected tests explicitly marked failed in the parser output. "
          "Element voice broadcast remains unresolved because expected test names were absent in both arms. "
          "The Flipt CUE task has an offline dependency error in stock and a missing CUE module in ADAPT. Suricata failed during baseline setup for both arms.", "",
          "### Failure categories by task type, recorded scores", "",
          "| Task type | Outcome | Stock Codex | ADAPT |", "| --- | --- | ---: | ---: |"]
for kind in TYPES:
    for label in LABELS:
        a, b = (type_failure[kind][arm][label] for arm in ARMS)
        if a or b:
            lines.append(f"| {kind} | {label} | {a} | {b} |")
lines += ["", "## Per-task evidence", "",
          "| Task | Type | Stock Codex | ADAPT | Victor P. archive |",
          "| --- | --- | --- | --- | --- |"]
for r in rows:
    cells = [f"{r[a]['reward']:g} · {r[a]['label']} · {link(r[a]['log'], 'grader')}" for a in ARMS]
    lines.append(f"| {r['name']} | {r['task_type']} | {cells[0]} | {cells[1]} | {link(r['victor_p']['result'], f'{r["victor_p"]["reward"]:g}')} |")
lines += ["", link(str(HERE / "aggregate-evidence.json"), "Machine-readable evidence") + "."]
(HERE / "AGGREGATE.md").write_text("\n".join(lines) + "\n")
(HERE / "aggregate-evidence.json").write_text(json.dumps({
    "snapshot_at": SNAPSHOT["snapshot_at"], "rows": rows, "failure_counts": categories,
    "failure_counts_by_type": type_failure, "audited_pair_outcomes": pair_outcomes(audited),
    "victor_pass_both_failed": [r["task_id"] for r in both_failed],
    "victor_pass_one_failed": [r["task_id"] for r in one_failed],
    "logged_as_missing_arms": len(legacy_missing), "confirmed_failed_test_arms": len(had_failed),
}, indent=2) + "\n")
print("Pairs:", len(rows), "Audited:", len(audited), "Victor-only over both:", len(both_failed), "Victor plus one arm:", len(one_failed))
print("Both-failed by type:", Counter(r["task_type"] for r in both_failed))
print("Failures confirmed from prior missing label:",len(had_failed),"/", len(legacy_missing))
print("Failure counts:", categories)
