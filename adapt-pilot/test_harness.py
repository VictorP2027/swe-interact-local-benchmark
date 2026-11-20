"""Regression checks for scoring, continuation and the shared Linux tool."""

import json
from contextlib import nullcontext
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import run
import task_terminal
from codex_continue import asks_question


class HarnessChecks(unittest.TestCase):
    def reward(self, reward, log="", code=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "verifier").mkdir()
            (root / "verifier/reward.txt").write_text(str(reward))
            (root / "verifier/run-script-stderr.txt").write_text(log)
            return run.verifier_reward(root, code)

    def test_failed_implementation_is_a_score(self):
        self.assertEqual(self.reward(0, "2 failed, 18 passed", 1), (0, 1))

    def test_offline_dependency_error_is_unscored(self):
        with self.assertRaises(run.Blocked):
            self.reward(0, 'go: cuelang.org/go: Get "https://proxy.golang.org": network is unreachable')

    def test_missing_reward_is_unscored(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(run.Blocked):
            run.verifier_reward(Path(folder), 3)

    def test_success_is_a_score(self):
        self.assertEqual(self.reward(1, "21 passed"), (1, 0))

    def test_continuation_only_uses_final_prose_question(self):
        self.assertTrue(asks_question("Should I implement this?"))
        self.assertFalse(asks_question("```python\nprint('Ready?')\n```\nDone."))
        self.assertFalse(asks_question("> Is this correct?"))

    def test_terminal_runs_in_selected_container(self):
        process = subprocess.CompletedProcess([], 0, "Linux\n", "")
        with patch("task_terminal.subprocess.run", return_value=process) as execute:
            result = task_terminal.execute("task-owned", "/app", "uname -s", 5)
        self.assertEqual(result["stdout"], "Linux\n")
        self.assertEqual(execute.call_args.args[0][:6],
                         ["docker", "exec", "--workdir", "/app", "task-owned", "timeout"])

    def test_terminal_rejects_unbounded_timeout(self):
        with self.assertRaises(ValueError):
            task_terminal.execute("task-owned", "/app", "sleep 10000", 10000)

    def test_mcp_lists_only_task_terminal(self):
        tools = task_terminal.response({"method": "tools/list"}, "task-owned", "/app", Path("unused"))
        self.assertEqual([t["name"] for t in tools["tools"]], ["run"])

    def test_timeout_is_visible_in_tool_result(self):
        process = subprocess.CompletedProcess([], 124, "partial", "")
        with patch("task_terminal.subprocess.run", return_value=process):
            self.assertTrue(task_terminal.execute("task-owned", "/app", "sleep 60", 1)["timed_out"])

    def test_task_network_follows_upstream(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for allowed, expected in ((True, "bridge"), (False, "none")):
                (root / "task.toml").write_text(f"[environment]\nallow_internet = {str(allowed).lower()}\n")
                self.assertEqual(run.task_network(root), expected)
            (root / "task.toml").write_text("[environment]\n")
            self.assertEqual(run.task_network(root), "bridge")

    def test_verifier_cleanup_on_timeout_and_interrupt(self):
        for error, expected in ((subprocess.TimeoutExpired("docker", 1), run.Blocked),
                                (KeyboardInterrupt(), KeyboardInterrupt)):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "task.toml").write_text("[verifier]\ntimeout_sec = 1\n")
                with patch("run.verifier_environment", return_value=nullcontext(({}, []))), \
                     patch("run.logged", side_effect=error), patch("run.subprocess.run") as cleanup:
                    with self.assertRaises(expected):
                        run.verify_candidate("test", root, "image", "/app", root / "candidate.patch",
                                             {"platform": "linux/amd64", "verifier_pytest_addopts": {}}, root)
                    self.assertEqual(cleanup.call_args.args[0][:3], ["docker", "rm", "--force"])


if __name__ == "__main__":
    unittest.main()
