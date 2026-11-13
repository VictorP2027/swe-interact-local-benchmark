"""Run original RF test/rubric scripts with an explicit local Codex grader."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import tomllib
from codex_rubric_bridge import Bridge

parser = argparse.ArgumentParser()
parser.add_argument('task')
parser.add_argument('repository', type=Path)
parser.add_argument('--reuse-container', required=True)
parser.add_argument('--revision', action='store_true')
parser.add_argument('--revision-label')
parser.add_argument('--infrastructure-retry', action='store_true')
parser.add_argument('--infrastructure-label')
parser.add_argument('--application-path', help='Select the preinstalled application runtime on PATH')
parser.add_argument('--go-flags', help='Go build parallelism options for the local VM')
parser.add_argument('--gomaxprocs', type=int, help='Go runtime CPU limit for the local VM')
parser.add_argument('--runner', choices=('go', 'jest', 'both'), help='Use the supplied Grafana runner selection environment option')
parser.add_argument('--cargo-low-memory', action='store_true', help='Compile with one Cargo worker and without release optimization or debug information')
args = parser.parse_args()
ROOT = Path(os.environ.get('SWE_INTERACT_WORKSPACE', str(Path.cwd()))).resolve()
TASK = ROOT / 'SWE-Interact/data/singleturn' / args.task
OUTPUT = ROOT / 'outputs/swe-interact-direct' / args.task
original_output = OUTPUT
if args.revision and args.infrastructure_retry:
    raise ValueError('Source feedback corrections and infrastructure retries must be separate')
label = args.revision_label if args.revision else args.infrastructure_label
if label and not all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label):
    raise ValueError('Invalid output label')
if args.revision or args.infrastructure_retry:
    OUTPUT /= ('post-feedback' if args.revision else 'infrastructure-retry') + ('-' + label if label else '')
OUTPUT.mkdir(parents=True, exist_ok=True)
if (OUTPUT / 'result.json').exists():
    raise RuntimeError('Refusing to overwrite a recorded evaluation')
if not args.task.startswith('rf_task-') or not args.reuse_container.startswith('direct-dev-'):
    raise ValueError('Expected an RF task and an owned development container')
definition = tomllib.loads((TASK / 'task.toml').read_text())
env = dict(os.environ, DOCKER_CONFIG='/private/tmp/swe-docker-config',
    DOCKER_HOST=os.environ['DOCKER_HOST'])
def docker(*command, **kw):
    return subprocess.run(['docker', *command], env=env, check=True, **kw)
def git(*command):
    return subprocess.check_output(['git', '-C', str(args.repository), *command], text=True).strip()
if git('status', '--porcelain'):
    raise RuntimeError('Freeze the entire source implementation before running the verifier')
commit = git('rev-parse', 'HEAD')
base = git('rev-list', '--max-parents=0', 'HEAD')
if '\n' in base:
    raise ValueError('Expected the squashed RF repository')
if args.infrastructure_retry:
    previous = json.loads((original_output / 'result.json').read_text())
    if previous.get('evaluation_valid', True) or previous['implementation_commit'] != commit:
        raise ValueError('Infrastructure retry needs an invalid evaluation and identical implementation')
patch = subprocess.check_output(['git', '-C', str(args.repository), 'diff', '--binary', base, commit])
(OUTPUT / 'implementation.patch').write_bytes(patch)
image = definition['environment']['docker_image']
name = args.reuse_container
workspace = docker('exec', name, 'git', 'rev-parse', '--show-toplevel', capture_output=True, text=True).stdout.strip()
if docker('inspect', '-f', '{{.Config.Image}}', name, capture_output=True, text=True).stdout.strip() != image:
    raise ValueError('Incorrect development image')
if docker('exec', name, 'git', '-C', workspace, 'rev-parse', 'HEAD', capture_output=True, text=True).stdout.strip() != base:
    raise ValueError('Image Git HEAD must remain the original benchmark base')
docker('exec', name, 'git', '-C', workspace, 'reset', '--hard', base)
docker('exec', name, 'git', '-C', workspace, 'clean', '-fd')
docker('exec', name, 'bash', '-c', 'mkdir -p /tests /logs/verifier /logs/artifacts; rm -f /logs/verifier/*')
docker('cp', str(OUTPUT / 'implementation.patch'), name + ':/tmp/direct-implementation.patch')
docker('exec', name, 'git', '-C', workspace, 'apply', '/tmp/direct-implementation.patch')
# Only after the host implementation commit and patch are frozen do we expose supplied checks.
docker('cp', str(TASK / 'tests') + '/.', name + ':/tests')
bridge = Bridge(OUTPUT / 'grader')
runtime_env = ['-e', 'EVAL_MODEL=gpt-6-luna', '-e', 'EVAL_API_KEY=' + bridge.token,
    '-e', f'EVAL_BASE_URL=http://host.lima.internal:{bridge.port}/v1']
if args.application_path:
    runtime_env += ['-e', 'PATH=' + args.application_path]
if args.go_flags:
    runtime_env += ['-e', 'GOFLAGS=' + args.go_flags]
if args.gomaxprocs:
    runtime_env += ['-e', 'GOMAXPROCS=' + str(args.gomaxprocs)]
if args.runner:
    runtime_env += ['-e', 'RUN_SCRIPT_RUNNER=' + args.runner]
if args.cargo_low_memory:
    runtime_env += ['-e', 'NPROC=1', '-e', 'CARGO_BUILD_JOBS=1', '-e', 'CARGO_PROFILE_RELEASE_DEBUG=0', '-e', 'CARGO_PROFILE_RELEASE_OPT_LEVEL=0']
timed_out = False
try:
    with (OUTPUT / 'verifier.log').open('w') as log:
        process = subprocess.Popen(['docker', 'exec', *runtime_env, name, 'bash', '/tests/test.sh'],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        def expire():
            global timed_out
            if process.poll() is None:
                timed_out = True
                subprocess.run(['docker', 'kill', name], env=env, stdout=subprocess.DEVNULL)
        timer = threading.Timer(definition['verifier']['timeout_sec'], expire)
        timer.daemon = True
        timer.start()
        try:
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end='', flush=True)
            exit_code = process.wait()
        finally:
            timer.cancel()
finally:
    bridge.close()
docker('cp', name + ':/logs/verifier/.', str(OUTPUT))
reward_path = OUTPUT / 'reward.txt'
reward = float(reward_path.read_text().strip()) if reward_path.exists() else None
reasons = []
rubrics_path = OUTPUT / 'rubrics_results.json'
rubrics = json.loads(rubrics_path.read_text()) if rubrics_path.exists() else {}
if not rubrics.get('rubric_count') or rubrics.get('evaluable_count') != rubrics.get('rubric_count'):
    reasons.append('Rubric evaluation did not produce an evaluable rating for every check')
test_runs = {}
for path in OUTPUT.glob('*_results.json'):
    data = json.loads(path.read_text())
    if 'passed_test_count' in data:
        test_runs[path.name] = {k: data.get(k, 0) for k in ('passed_test_count', 'failed_test_count', 'skipped_test_count', 'exit_code')}
if len(test_runs) < 2 or any(run['passed_test_count'] + run['failed_test_count'] == 0 for run in test_runs.values()):
    reasons.append('Baseline and mutation must each execute nonzero tests')
if timed_out or reward is None:
    reasons.append('Verifier timed out or did not produce a reward')
valid = not reasons
result = {
    'task': args.task, 'format': 'direct single-turn implementation in the current Codex chat',
    'implementation_commit': commit, 'base_commit': base,
    'task_verifier_reward': reward if valid else None,
    'raw_task_verifier_reward': reward, 'evaluation_valid': valid,
    'evaluation_invalid_reasons': reasons, 'verifier_exit_code': exit_code,
    'verifier': 'original supplied RF test.sh, master validator, test patch and rubric evaluator',
    'docker_image': image, 'docker_host': env['DOCKER_HOST'], 'workspace': workspace,
    'uses_hidden_test_feedback': args.revision,
    'infrastructure_retry_of': str(original_output / 'result.json') if args.infrastructure_retry else None,
    'verifier_timed_out': timed_out, 'application_path': args.application_path,
    'go_flags': args.go_flags, 'gomaxprocs': args.gomaxprocs,
    'run_script_runner': args.runner,
    'cargo_low_memory': args.cargo_low_memory,
    'test_runs': test_runs,
    'grader': {'model': 'gpt-6-luna', 'reasoning_effort': 'medium',
        'transport': 'local OpenAI-compatible bridge to supported Codex CLI exec',
        'authentication': 'existing Codex CLI ChatGPT sign-in; no API key extracted',
        'original_default_model': 'anthropic/claude-opus-4-5-20251101',
        'tool_use': False, 'calls': bridge.calls,
        'max_tokens': '2048 instructed; CLI has no output-token-limit flag'},
    'verifier_scripts_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (TASK / 'tests').iterdir() if p.is_file()},
    'updated_at_utc': datetime.now(timezone.utc).isoformat(),
}
(OUTPUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
ledger_path = ROOT / 'outputs/swe-interact-direct/progress.json'
ledger = json.loads(ledger_path.read_text())
for task in ledger['tasks']:
    if task['task'] == args.task:
        if args.revision:
            if task.get('revision_result') and task['revision_result'] != str(OUTPUT / 'result.json'):
                task.setdefault('revision_history', []).append(dict(commit=task.get('revision_commit'), reward=task.get('post_feedback_reward'), result=task['revision_result']))
            task.update(post_feedback_reward=result['task_verifier_reward'], revision_commit=commit, revision_result=str(OUTPUT / 'result.json'))
        else:
            task.update(status='passed' if valid and reward == 1 else 'failed' if valid else 'ungraded',
                reward=result['task_verifier_reward'], commit=commit, result=str(OUTPUT / 'result.json'))
        task['grader'] = result['grader']
ledger['completed_tasks'] = sum(t.get('reward') is not None for t in ledger['tasks'])
ledger['updated_at_utc'] = result['updated_at_utc']
ledger['current_task'] = None
ledger['full_benchmark_score'] = sum(t['reward'] for t in ledger['tasks']) / 75 if ledger['completed_tasks'] == 75 else None
ledger_path.write_text(json.dumps(ledger, indent=2) + '\n')
