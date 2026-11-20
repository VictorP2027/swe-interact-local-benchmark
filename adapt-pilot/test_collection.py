"""Prevent calibration, duplicated owners and unmatched pairs entering aggregates."""

import json
from pathlib import Path
import tempfile
import unittest

import campaign
import collect_results
import run


class CollectionChecks(unittest.TestCase):
    def setUp(self):
        self.plan = campaign.read_plan(campaign.DEFAULT_PLAN)
        task = campaign.SMOKE_TASK
        config = self.plan["configuration"]
        binding = {"owner": "victor-c", "calibration": False, "machine_id": "host-c",
                   "plan_sha256": self.plan["plan_sha256"]}
        rows = [{"task": task, "arm": arm, "status": "scored", "reward": 0,
                 "machine_id": "host-c", "campaign_owner": "victor-c",
                 "campaign_plan_sha256": self.plan["plan_sha256"],
                 "prompt_sha256": self.plan["tasks"][task]["prompt_sha256"],
                 "actor_prompt_sha256": "same-full-spec-and-tools", "image_id": "same-image",
                 "upstream_base": "same-base", "runner_source_sha256": self.plan["source_sha256"],
                 "effective_settings": {"passed": True},
                 "agent_settings": {key: config[key] for key in ("model", "reasoning_effort", "context_window", "lane")}}
                for arm in run.ARMS]
        self.packet = {"campaign": binding, "attempts": rows,
                       "manifest": {"configuration": config, "harness_sources": self.plan["source_sha256"]}}

    def collect(self, duplicate=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handoff.json"
            path.write_text(json.dumps(self.packet))
            return collect_results.collect(self.plan, [path, path] if duplicate else [path])

    def test_partial_primary_collection_preserves_missing_coverage(self):
        result = self.collect()
        self.assertEqual(result["completed_pairs"], 1)
        self.assertEqual(len(result["unscored_or_pending"]), 74)
        self.assertEqual(result["missing_owners"], ["victor-p"])

    def test_calibration_is_rejected(self):
        self.packet["campaign"]["calibration"] = True
        with self.assertRaises(ValueError):
            self.collect()

    def test_duplicate_owner_is_rejected(self):
        with self.assertRaises(ValueError):
            self.collect(duplicate=True)

    def test_mismatched_machine_or_image_is_rejected(self):
        for key in ("machine_id", "image_id"):
            with self.subTest(key=key):
                previous = self.packet["attempts"][1][key]
                self.packet["attempts"][1][key] = "different"
                with self.assertRaises(ValueError):
                    self.collect()
                self.packet["attempts"][1][key] = previous


if __name__ == "__main__":
    unittest.main()
