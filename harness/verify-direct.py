import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import re
import threading
import tomllib
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument('task')
parser.add_argument('repository', type=Path)
parser.add_argument('--revision', action='store_true')
parser.add_argument('--revision-label', help='Label an additional feedback-assisted correction')
parser.add_argument('--infrastructure-retry', action='store_true')
parser.add_argument('--infrastructure-label', help='Label an additional infrastructure retry')
parser.add_argument('--node-options', help='Node runtime options for an emulation workaround')
parser.add_argument('--reuse-container', help='Reuse an owned development container and its build cache')
parser.add_argument('--keep-container', action='store_true', help='Keep the exact task-owned container for subsequent checks')
parser.add_argument('--restore-test-fixtures-from', help='Restore omitted original test inputs from this test revision')
parser.add_argument('--test-fixture-path', action='append', default=[], help='Original fixtures/testdata path to restore in the verifier only')
parser.add_argument('--docker-host', required=True, help='Explicit task-owned Docker socket')
args = parser.parse_args()
if args.restore_test_fixtures_from:
    if re.fullmatch('[0-9a-f]{40}', args.restore_test_fixtures_from) is None or not args.test_fixture_path:
        raise ValueError('Test fixture restoration requires a full commit and explicit paths')
    for path in args.test_fixture_path:
        if Path(path).is_absolute() or '..' in Path(path).parts or not ({'fixtures', 'testdata'} & set(Path(path).parts)):
            raise ValueError('Only original fixture/testdata paths can be restored')
elif args.test_fixture_path:
    raise ValueError('A fixture revision must be specified')
ROOT = Path(os.environ.get('SWE_INTERACT_WORKSPACE', str(Path.cwd()))).resolve()
TASK = ROOT / 'SWE-Interact/data/singleturn' / args.task
definition = tomllib.loads((TASK / 'task.toml').read_text())
OUTPUT = ROOT / 'outputs/swe-interact-direct' / args.task
original_output = OUTPUT
if args.revision and args.infrastructure_retry:
    raise ValueError('Feedback revisions and infrastructure retries are separate')
if args.revision:
    suffix = 'post-feedback'
    if args.revision_label:
        if re.fullmatch('[a-z0-9-]+', args.revision_label) is None:
            raise ValueError('Revision labels must contain lowercase letters, numbers or hyphens')
        suffix += '-' + args.revision_label
    OUTPUT = OUTPUT / suffix
elif args.infrastructure_retry:
    suffix = 'infrastructure-retry'
    if args.infrastructure_label:
        if re.fullmatch('[a-z0-9-]+', args.infrastructure_label) is None:
            raise ValueError('Infrastructure labels must contain lowercase letters, numbers or hyphens')
        suffix += '-' + args.infrastructure_label
    OUTPUT = OUTPUT / suffix
OUTPUT.mkdir(parents=True, exist_ok=True)
if (OUTPUT / 'result.json').exists():
    raise RuntimeError('This evaluation already has a recorded result; refusing to overwrite it')
environment = dict(os.environ)
environment.update({
    'DOCKER_CONFIG': '/private/tmp/swe-docker-config',
    'DOCKER_HOST': args.docker_host,
})

def docker(*command, **kwargs):
    return subprocess.run(['docker', *command], env=environment, check=True, **kwargs)

dockerfile = TASK / 'environment/Dockerfile'
base = definition['metadata'].get('base_commit_hash')
if base is None:
    match = re.search(r'git reset --hard ([0-9a-f]{40})', dockerfile.read_text())
    if match is None:
        raise ValueError('No benchmark base commit is declared')
    base = match.group(1)
commit = subprocess.check_output(['git', '-C', str(args.repository), 'rev-parse', 'HEAD'], text=True).strip()
if args.infrastructure_retry:
    original = json.loads((original_output / 'result.json').read_text())
    if (original['task_verifier_reward'] is not None and original.get('evaluation_valid') is not False) or original['implementation_commit'] != commit:
        raise ValueError('Infrastructure retries require an ungraded original and an identical implementation commit')
patch = subprocess.check_output(['git', '-C', str(args.repository), 'diff', '--binary', base, commit])
(OUTPUT / 'implementation.patch').write_bytes(patch)
name = args.reuse_container or 'direct-' + args.task.replace('_', '-').lower()[:70]
image = definition['environment'].get('docker_image')
dockerfile_sha256 = None
if image is None:
    dockerfile_sha256 = hashlib.sha256(dockerfile.read_bytes()).hexdigest()
    image = 'direct-task:' + dockerfile_sha256[:16]
    found = subprocess.run(['docker', 'image', 'inspect', image], env=environment,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if found.returncode:
        docker('build', '--platform', 'linux/amd64', '-t', image, str(dockerfile.parent))
if args.reuse_container:
    if not name.startswith('direct-dev-'):
        raise ValueError('Only task-owned direct-dev containers may be reused')
    actual_image = docker('inspect', '-f', '{{.Config.Image}}', name,
                          capture_output=True, text=True).stdout.strip()
    if actual_image != image:
        raise ValueError(f'Development container uses the wrong image: {actual_image}')
else:
    memory_mb = min(definition['environment'].get('memory_mb', 8192), 8192)
    cpus = min(definition['environment'].get('cpus', 4), 4)
    docker('create', '--name', name, '--platform', 'linux/amd64', '--memory', str(memory_mb) + 'm', '--cpus', str(cpus),
           '--entrypoint', '/bin/bash', image, '-lc', 'sleep infinity')
try:
    if not args.reuse_container:
        docker('start', name)
    actual_base = docker('exec', name, 'git', '-C', '/app', 'rev-parse', 'HEAD', capture_output=True, text=True).stdout.strip()
    if actual_base != base:
        raise RuntimeError(f'Unexpected image base commit: {actual_base}')
    if args.reuse_container:
        # Restore the source before applying the frozen host implementation.
        # Ignored build artifacts remain reusable; no user containers qualify.
        docker('exec', name, 'git', '-C', '/app', 'reset', '--hard', base)
        docker('exec', name, 'git', '-C', '/app', 'clean', '-fd')
    docker('exec', name, 'mkdir', '-p', '/tests', '/logs/verifier', '/logs/artifacts')
    docker('cp', str(OUTPUT / 'implementation.patch'), name + ':/tmp/implementation.patch')
    docker('cp', str(TASK / 'tests') + '/.', name + ':/tests')
    docker('exec', name, '/bin/bash', '-lc', 'cd /app && git apply /tmp/implementation.patch')
    if args.restore_test_fixtures_from:
        docker('exec', name, 'git', '-C', '/app', 'checkout', args.restore_test_fixtures_from, '--', *args.test_fixture_path)
    with (OUTPUT / 'verifier.log').open('w') as log:
        exec_options = ['-e', 'TERM=xterm-256color']
        if args.node_options:
            exec_options += ['-e', 'NODE_OPTIONS=' + args.node_options]
        process = subprocess.Popen(['docker', 'exec', *exec_options, name, 'bash', '/tests/test.sh'], env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        timed_out = False
        def expire():
            global timed_out
            if process.poll() is None:
                timed_out = True
                subprocess.run(['docker', 'kill', name], env=environment,
                               check=False, stdout=subprocess.DEVNULL)
        timer = threading.Timer(definition.get('verifier', {}).get('timeout_sec', 1800), expire)
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
    docker('cp', name + ':/logs/verifier/.', str(OUTPUT))
    reward_path = OUTPUT / 'reward.txt'
    reward = float(reward_path.read_text().strip()) if reward_path.exists() else None
    result = {
        'task': args.task,
        'format': 'direct single-turn implementation in the current Codex chat',
        'implementation_commit': commit,
        'base_commit': base,
        'verifier_exit_code': exit_code,
        'task_verifier_reward': reward,
        'verifier': ('original supplied test.sh and test.patch in the supplied Linux image' if (TASK / 'tests/test.patch').exists()
                     else 'original supplied test.sh, run_script.sh, parser.py and config.json in the supplied Linux image'),
        'docker_image': image,
        'dockerfile_sha256': dockerfile_sha256,
        'docker_host': args.docker_host,
        'uses_hidden_test_feedback': args.revision,
        'reused_development_build_cache': bool(args.reuse_container),
        'retained_task_container': name if args.keep_container else None,
        'restored_original_test_fixtures': ({'commit': args.restore_test_fixtures_from, 'paths': args.test_fixture_path}
                                           if args.restore_test_fixtures_from else None),
        'verifier_timed_out': timed_out,
        'terminal': 'xterm-256color',
        'node_options': args.node_options,
        'infrastructure_retry_of': str(original_output / 'result.json') if args.infrastructure_retry else None,
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
                    previous = dict(commit=task.get('revision_commit'), reward=task.get('post_feedback_reward'), result=task['revision_result'])
                    if previous not in task.setdefault('revision_history', []):
                        task['revision_history'].append(previous)
                task.update(post_feedback_reward=reward, revision_commit=commit, revision_result=str(OUTPUT / 'result.json'))
            else:
                task.update(status='passed' if reward == 1 else 'failed' if reward is not None else 'verifier_error',
                            reward=reward, commit=commit, result=str(OUTPUT / 'result.json'))
    ledger['completed_tasks'] = sum(task.get('reward') is not None for task in ledger['tasks'])
    ledger['updated_at_utc'] = result['updated_at_utc']
    ledger['current_task'] = None
    ledger['full_benchmark_score'] = sum(task['reward'] for task in ledger['tasks']) / 75 if ledger['completed_tasks'] == 75 else None
    ledger_path.write_text(json.dumps(ledger, indent=2) + '\n')
finally:
    if not args.keep_container:
        subprocess.run(['docker', 'rm', '-f', name], env=environment, check=False)
