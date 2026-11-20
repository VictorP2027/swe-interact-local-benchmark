"""Check the backup launch gate and assignment provenance without model calls."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import campaign
import run
import run_overflow


class BackupChecks(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.primary = Path(temp.name) / "primary"
        self.backup = Path(temp.name) / "backup"
        self.plan_path = campaign.DEFAULT_PLAN
        self.plan = campaign.read_plan(self.plan_path)
        machine = patch("campaign.machine_id", return_value="test-machine")
        machine.start()
        self.addCleanup(machine.stop)
        campaign.bind_output(self.primary, self.plan, "victor-c")

    def state(self):
        return json.loads((self.backup / "backup-status.json").read_text())

    def test_backup_waits_for_all_primary_scores(self):
        with patch("campaign.status", return_value={"completed_pairs": 37}), \
                patch("run_overflow.subprocess.run") as launch:
            self.assertEqual(run_overflow.run_backup(self.primary, self.backup, self.plan_path), 2)
        launch.assert_not_called()
        self.assertEqual(self.state()["state"], "primary_incomplete")
        self.assertEqual(self.state()["required_pairs"], 38)

    def test_completed_primary_launches_backup_and_exports_both(self):
        configuration = self.plan["configuration"]
        manifest = {"configuration": configuration, "harness_sources": self.plan["source_sha256"]}
        run.save(self.primary / "manifest.json", manifest)
        run.save(self.primary / "verifier-validation.json",
                 {"passed": True, "configuration": configuration, "source_sha256": manifest["harness_sources"]})

        def launch_backup(command):
            self.assertEqual(self.state()["state"], "running")
            self.assertEqual(command[command.index("--owner") + 1], "victor-p")
            tasks = {command[i + 1] for i, part in enumerate(command) if part == "--task"}
            self.assertEqual(tasks, set(self.plan["assignments"]["victor-p"]) - run_overflow.EXCLUDED)
            return subprocess.CompletedProcess(command, 0)

        with patch("campaign.status", side_effect=[{"completed_pairs": 38}, {"completed_pairs": 35}]), \
                patch("run.load_experiment", return_value=(configuration, manifest)), \
                patch("export_results.export", side_effect=lambda _, target: target.mkdir()) as export, \
                patch("run_overflow.subprocess.run", side_effect=launch_backup):
            self.assertEqual(run_overflow.run_backup(self.primary, self.backup, self.plan_path), 0)
        self.assertEqual(export.call_count, 2)
        self.assertEqual(self.state()["backup_scored_pairs"], 35)
        self.assertEqual(self.state()["run_by"], "victor-c")


if __name__ == "__main__":
    unittest.main()
