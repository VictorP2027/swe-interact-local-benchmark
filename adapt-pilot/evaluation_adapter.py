#!/usr/bin/env python3
"""Recover grading from image-baseline artifacts without rerunning a coding actor."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import run


def atomic_bytes(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)


def normalize_patch(output, attempt, row, manifest):
    """Reconstruct the exact saved candidate, then diff it against image state."""
    original = attempt / "implementation-head-relative.patch"
    patch = attempt / "implementation.patch"
    if not original.exists():
        shutil.copyfile(patch, original)
    expected_tree = row["candidate_artifacts"]["git_tree"]
    container = run.docker("run", "--detach", "--network", "none", "--platform", "linux/amd64",
                           "--workdir", row["repository_path"], "--entrypoint", "bash",
                           row["image_id"], "-lc", "exec sleep infinity")
    try:
        command = 'export GIT_INDEX_FILE=/tmp/evaluation.index; git read-tree "$1"; git add --all -- .; git write-tree'
        baseline = run.docker("exec", "--workdir", row["repository_path"], container, "bash", "-ec",
                              command, "baseline", row["upstream_base"])
        run.docker("cp", original, f"{container}:/tmp/actor.patch")
        reconstruct = ('git reset --hard "$1" >/dev/null; git clean -ffd >/dev/null; '
                       'if test -s /tmp/actor.patch; then git apply --whitespace=nowarn /tmp/actor.patch; fi; '
                       'export GIT_INDEX_FILE=/tmp/evaluation.index; git read-tree "$1"; '
                       'git add --all -- .; git write-tree')
        candidate = run.docker("exec", "--workdir", row["repository_path"], container, "bash", "-ec",
                               reconstruct, "candidate", row["upstream_base"])
        if candidate != expected_tree:
            raise ValueError("Reconstructed candidate differs from the frozen actor tree; grading repair refused")
        corrected = subprocess.check_output(["docker", "exec", "--workdir", row["repository_path"],
                                             container, "git", "diff", "--binary", baseline, candidate])
    finally:
        subprocess.run(["docker", "rm", "--force", container], stdout=subprocess.DEVNULL, check=True)
    proof = {"adapter_sha256": run.digest(Path(__file__)), "original_patch": original.name,
             "original_patch_sha256": run.digest(original), "evaluation_patch_sha256": hashlib.sha256(corrected).hexdigest(),
             "image_baseline_tree": baseline, "candidate_tree": candidate, "candidate_tree_verified": True,
             "reason": "Diff the saved actor tree against the actual image starting state, including preexisting untracked files.",
             "model_rerun": False, "model_candidate_changed": False}
    run.save(attempt / "patch-normalization.json", proof)
    atomic_bytes(patch, corrected)
    run.checkpoint(output, attempt, row, manifest, patch_sha256=proof["evaluation_patch_sha256"],
                   patch_normalization=proof)
    return proof


def grading_config(task, image, config):
    effective = copy.deepcopy(config)
    changes = []
    requested = config["verifier_pytest_addopts"].get(task, "")
    if requested == "-W ignore::starlette.exceptions.StarletteDeprecationWarning":
        probe = subprocess.run(["docker", "run", "--rm", "--network", "none", "--platform", "linux/amd64",
                                "--entrypoint", "python3", image, "-c",
                                "import starlette.exceptions as e; raise SystemExit(0 if hasattr(e, 'StarletteDeprecationWarning') else 1)"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode == 1:
            effective["verifier_pytest_addopts"][task] = ""
            changes.append({"setting": "PYTEST_ADDOPTS", "requested": requested, "effective": "",
                            "reason": "The legacy warning class does not exist in this supplied image; use the upstream test script's warning policy."})
        elif probe.returncode:
            raise RuntimeError("Could not inspect the supplied image warning class")
    return effective, changes


def grade_saved(output, attempt, row, manifest, config):
    if not row.get("patch_normalization"):
        normalize_patch(output, attempt, row, manifest)
    effective, changes = grading_config(row["task"], row["image_id"], config)
    run.checkpoint(output, attempt, row, manifest, status="grading", evaluation_adjustments=changes,
                   evaluation_adapter_sha256=run.digest(Path(__file__)))
    reward, code = run.verify_candidate(row["task"], run.SINGLE_TURN / row["task"], row["image_id"],
                                       row["repository_path"], attempt / "implementation.patch", effective, attempt)
    run.checkpoint(output, attempt, row, manifest, status="scored", reward=reward, verifier_exit_code=code)
    return reward
