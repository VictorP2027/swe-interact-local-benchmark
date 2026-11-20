#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash grade.sh RUN_DIRECTORY" >&2
  exit 2
fi

pilot_dir="$(cd "$(dirname "$0")" && pwd)"
run_dir="$(cd "$1" && pwd)"
dataset_dir="${SWE_INTERACT_DATASET:-$pilot_dir/../../../../SWE-Interact}"
task_dir="$dataset_dir/data/singleturn/deepswe_fastapi-deprecation-response-headers"
test_dir="$(cd "$task_dir/tests" && pwd)"
image="cs224v-fastapi-smoke:b32f98c"
upstream_base="11614be9021aa4ac078d4d0693a8b5250a1010d8"
git_args=(--git-dir="$run_dir/workspace.git" --work-tree="$run_dir/workspace")

if [[ "$(jq -r .status "$run_dir/run.json")" != "ended" ]]; then
  echo "Wait for the agent run to end before grading." >&2
  exit 1
fi

snapshot_base="$(git "${git_args[@]}" rev-list --max-parents=0 HEAD)"
index_dir="$(mktemp -d)"
trap 'rm -rf "$index_dir"' EXIT
export GIT_INDEX_FILE="$index_dir/index"

git "${git_args[@]}" read-tree "$snapshot_base"
git "${git_args[@]}" -C "$run_dir/workspace" add --all -- . ':(exclude)trace' ':(exclude)data_structures'
git "${git_args[@]}" diff --cached --binary "$snapshot_base" > "$run_dir/implementation.patch"
# SWE-Interact scores production changes after peeling off the agent's test commit.
git "${git_args[@]}" -C "$run_dir/workspace" diff --cached --binary "$snapshot_base" \
  -- . ':(exclude)tests' > "$run_dir/scored.patch"
unset GIT_INDEX_FILE
grading_dir="$run_dir/${PILOT_GRADING_DIR:-grading}"
mkdir -p "$grading_dir"

docker run --rm --network none --platform linux/amd64 \
  --env "PYTEST_ADDOPTS=${PILOT_PYTEST_ADDOPTS:-}" \
  --mount "type=bind,source=$test_dir,target=/tests,readonly" \
  --mount "type=bind,source=$run_dir/scored.patch,target=/pilot.patch,readonly" \
  --mount "type=bind,source=$grading_dir,target=/logs" \
  --entrypoint bash "$image" -c '
    set -euo pipefail
    cd /app
    test "$(git rev-parse HEAD)" = "$1"
    test -z "$(git status --porcelain)"
    if test -s /pilot.patch; then
      git apply --whitespace=nowarn /pilot.patch
    fi
    mkdir -p /logs/verifier
    bash /tests/test.sh
  ' bash "$upstream_base" > "$grading_dir/verifier.log" 2>&1
