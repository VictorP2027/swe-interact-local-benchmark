"""Check grading repairs cannot silently change the saved model candidate."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import evaluation_adapter
import run_batch
from actor_runtime import cap_coding_cpus


class EvaluationChecks(unittest.TestCase):
    def test_cpu_cap_only_changes_coding_containers_above_capacity(self):
        args = ("run", "--label", "cs224v.role=coding", "--cpus", 16, "image")
        self.assertEqual(cap_coding_cpus(args, 10)[4], 10)
        self.assertEqual(cap_coding_cpus(args, 20), args)
        verifier = ("run", "--label", "cs224v.role=verifier", "--cpus", 16, "image")
        self.assertEqual(cap_coding_cpus(verifier, 10), verifier)

    def test_atomic_patch_writer_preserves_non_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.patch"
            content = b"patch\xff\x00data\n"
            evaluation_adapter.atomic_bytes(path, content)
            self.assertEqual(path.read_bytes(), content)

    def test_tree_mismatch_refuses_to_replace_original_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = b"original actor export\n"
            (root / "implementation.patch").write_bytes(original)
            row = {"candidate_artifacts": {"git_tree": "expected"}, "repository_path": "/app",
                   "upstream_base": "base", "image_id": "image"}
            with patch("run.docker", side_effect=["container", "baseline", "", "different-tree"]), \
                 patch("evaluation_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
                with self.assertRaises(ValueError):
                    evaluation_adapter.normalize_patch(root, root, row, {})
            self.assertEqual((root / "implementation.patch").read_bytes(), original)
            self.assertEqual((root / "implementation-head-relative.patch").read_bytes(), original)
            self.assertFalse((root / "patch-normalization.json").exists())

    def test_only_unavailable_legacy_warning_override_is_removed(self):
        original = {"verifier_pytest_addopts": {"task": "-W ignore::starlette.exceptions.StarletteDeprecationWarning"}}
        for code in (0, 1):
            with patch("evaluation_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], code)):
                effective, changes = evaluation_adapter.grading_config("task", "image", original)
            self.assertEqual(effective["verifier_pytest_addopts"]["task"], "" if code else original["verifier_pytest_addopts"]["task"])
            self.assertEqual(bool(changes), bool(code))
            self.assertTrue(original["verifier_pytest_addopts"]["task"])

    def test_completed_actor_is_not_repeated_after_unscored_record(self):
        scored = {"task": "task", "arm": "stock", "status": "scored"}
        blocked = {"task": "task", "arm": "stock", "status": "blocked"}
        with patch("run.records", return_value=[scored, blocked]):
            self.assertEqual(run_batch.latest(Path("unused"), "task", "stock"), scored)


if __name__ == "__main__":
    unittest.main()
