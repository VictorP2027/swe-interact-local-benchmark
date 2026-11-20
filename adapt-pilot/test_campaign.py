"""Check assignment coverage, host binding, partial recovery and review evidence."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import campaign
import review
import review_evidence
import run


class CampaignChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = {"task_order": list(run.task_manifest(224, "deepswe_fastapi-deprecation-response-headers")),
                        "tasks": run.task_manifest(224, "deepswe_fastapi-deprecation-response-headers"),
                        "configuration": {"task_order_seed": 224}, "harness_sources": run.source_hashes()}
        cls.plan = campaign.create_plan(cls.manifest)

    def test_plan_covers_every_task_once_with_balanced_families(self):
        assignments = self.plan["assignments"]
        self.assertEqual(sorted(map(len, assignments.values())), [37, 38])
        self.assertFalse(set(assignments["victor-c"]) & set(assignments["victor-p"]))
        self.assertEqual(set(sum(assignments.values(), [])), set(self.manifest["tasks"]))
        for tasks in assignments.values():
            for prefix in ("deepswe_", "rf_", "swebenchpro_"):
                self.assertIn(sum(t.startswith(prefix) for t in tasks), (12, 13))

    def test_plan_is_repeatable_and_manual_case_is_first_for_victor_c(self):
        self.assertEqual(self.plan, campaign.create_plan(self.manifest))
        self.assertEqual(self.plan["assignments"]["victor-c"][0], campaign.SMOKE_TASK)

    def test_wrong_owner_and_duplicate_tasks_are_rejected(self):
        for tasks in ([self.plan["assignments"]["victor-p"][0]], [campaign.SMOKE_TASK] * 2):
            with self.assertRaises(ValueError):
                campaign.selected_tasks(self.plan, "victor-c", False, tasks)

    def test_calibration_only_allows_shared_smoke(self):
        self.assertEqual(campaign.selected_tasks(self.plan, "victor-p", True, None), [campaign.SMOKE_TASK])

    def test_host_switch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("campaign.machine_id", return_value="host-a"):
                campaign.bind_output(root, self.plan, "victor-c")
                campaign.bind_output(root, self.plan, "victor-c")
            with patch("campaign.machine_id", return_value="host-b"), self.assertRaises(ValueError):
                campaign.bind_output(root, self.plan, "victor-c")

    def test_plan_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            run.save(path, {**self.plan, "seed": 999})
            with self.assertRaises(ValueError):
                campaign.read_plan(path)

    def test_partial_quota_candidate_is_not_graded_as_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            attempt = root / "0001"
            attempt.mkdir()
            (attempt / "implementation.patch").write_text("partial work")
            run.save(attempt / "result.json", {"status": "quota", "candidate_artifacts": {"patch_sha256": "x"}})
            with patch("run.verify_candidate") as grade:
                self.assertFalse(run.resume_grading(root, {}, {}, "task", root))
                grade.assert_not_called()

    def test_review_packet_keeps_evidence_and_excludes_auth_home(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            dataset = output / "dataset/task"
            (dataset / "tests").mkdir(parents=True)
            (dataset / "instruction.md").write_text("Example specification")
            (dataset / "task.toml").write_text("[metadata]\n")
            (dataset / "tests/test.sh").write_text("true\n")
            attempt = output / "attempts/task/stock/0001"
            session = attempt / "runs/example"
            (session / "trace").mkdir(parents=True)
            (session / "trace/result.txt").write_text("tool evidence")
            (session / "harness/codex_home/sessions").mkdir(parents=True)
            (session / "harness/codex_home/auth.json").write_text("never copy this synthetic credential")
            (session / "harness/codex_home/sessions/example.jsonl").write_text(
                json.dumps({"type": "compacted", "payload": {"message": "summary"}}) + "\n")
            (attempt / "implementation.patch").write_text("candidate")
            row = {"task": "task", "arm": "stock", "status": "scored", "reward": 0,
                   "artifact_path": str(attempt.relative_to(output)), "run_path": str(session.relative_to(output))}
            run.save(attempt / "result.json", row)
            target = output / "manual-review/task"
            with patch("run.SINGLE_TURN", output / "dataset"), redirect_stdout(io.StringIO()):
                summary = review.build(output, "task", target)
                (target / "NOTES.md").write_text("My existing manual notes")
                (target / "stock/trace/result.txt").chmod(0o444)
                review_evidence.enrich(output, "task", target)
            self.assertEqual(summary["arms"]["stock"]["compaction_markers"], 1)
            self.assertEqual((target / "stock/trace/result.txt").read_text(), "tool evidence")
            self.assertEqual((target / "NOTES.md").read_text(), "My existing manual notes")
            self.assertFalse(list(target.rglob("auth.json")))
            self.assertFalse(list(target.rglob("codex_home")))

    def test_request_views_exclude_http_credentials(self):
        record = {"request_headers": {"Authorization": "sensitive-request-header"},
                  "response_headers": {"Set-Cookie": "sensitive-response-header"},
                  "request": {"input": "the recorded model context"}, "kind": "main"}
        view = review_evidence.request_view(record)
        self.assertEqual(view["request"], record["request"])
        self.assertNotIn("sensitive-request-header", json.dumps(view))
        self.assertNotIn("sensitive-response-header", json.dumps(view))


if __name__ == "__main__":
    unittest.main()
