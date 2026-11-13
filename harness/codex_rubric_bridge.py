"""Local completion-only transport for the unchanged RF rubric evaluator.

Uses the supported Codex CLI and its existing login; never reads credentials.
The grading model is explicit and differs from the supplied default grader.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CODEX = os.environ.get('CODEX_CLI', 'codex')
SCHEMA = {
    'type': 'object', 'additionalProperties': False, 'required': ['ratings'],
    'properties': {'ratings': {'type': 'array', 'minItems': 1, 'maxItems': 1,
        'items': {'type': 'object', 'additionalProperties': False,
            'required': ['status', 'justification'], 'properties': {
                'status': {'type': 'string', 'enum': ['YES', 'NO']},
                'justification': {'type': 'string'}}}}}}


class Bridge:
    def __init__(self, output, bind='0.0.0.0'):
        self.output = Path(output).resolve()
        self.output.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.calls = 0
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == '/health':
                    self.reply(200, {'ok': True})
                else:
                    self.reply(404, {'error': 'not found'})

            def reply(self, status, data):
                body = json.dumps(data).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                if self.headers.get('Authorization') != 'Bearer ' + bridge.token:
                    self.reply(401, {'error': 'unauthorized'})
                    return
                if self.path != '/v1/chat/completions':
                    self.reply(404, {'error': 'unsupported endpoint'})
                    return
                try:
                    size = int(self.headers['Content-Length'])
                    if not 0 < size < 4_000_000:
                        raise ValueError('invalid request size')
                    request = json.loads(self.rfile.read(size))
                    with bridge.lock:
                        self.reply(200, bridge.complete(request))
                except Exception as e:
                    # No credentials are included in exception text.
                    self.reply(500, {'error': {'message': str(e), 'type': 'local_grader_error'}})

        self.server = ThreadingHTTPServer((bind, 0), Handler)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def complete(self, request):
        if request.get('model') != 'gpt-6-luna' or request.get('stream'):
            raise ValueError('only nonstreaming gpt-6-luna grading is supported')
        messages = request.get('messages', [])
        if [m.get('role') for m in messages] != ['system', 'user']:
            raise ValueError('expected the original system/user rubric messages')
        if any(not isinstance(m.get('content'), str) for m in messages):
            raise ValueError('only text grading is supported')
        self.calls += 1
        folder = self.output / f'call-{self.calls:03d}'
        folder.mkdir()
        (folder / 'request.json').write_text(json.dumps(request, indent=2))
        (folder / 'system.txt').write_text(messages[0]['content'])
        (folder / 'schema.json').write_text(json.dumps(SCHEMA))
        empty = folder / 'empty-workspace'
        empty.mkdir()
        command = [CODEX, 'exec', '--ignore-user-config', '--ephemeral',
            '--skip-git-repo-check', '--sandbox', 'read-only', '--model', 'gpt-6-luna',
            '--config', 'model_reasoning_effort="medium"',
            '--config', 'approval_policy="never"',
            '--config', 'model_instructions_file=' + json.dumps(str(folder / 'system.txt')),
            '--config', 'developer_instructions=' + json.dumps(
                'Grade only the supplied text using the system rubric. Do not use any tools, '
                'inspect files, or delegate work. Return only the required JSON, with concise '
                'evidence-based justification within the requested 2048-token output budget.'),
            '--config', 'features.shell_tool=false', '--config', 'features.apps=false',
            '--config', 'features.plugins=false', '--config', 'features.memories=false',
            '--config', 'features.request_permissions_tool=false',
            '--config', 'skills.bundled.enabled=false',
            '--config', 'skills.include_instructions=false',
            '--config', 'project_doc_max_bytes=0', '--config', 'web_search="disabled"',
            '--output-schema', str(folder / 'schema.json'),
            '--output-last-message', str(folder / 'result.json'),
            '--cd', str(empty), '--json', '-']
        env = dict(os.environ)
        for name in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_API_BASE'):
            env.pop(name, None)
        start = time.time()
        with (folder / 'events.jsonl').open('w') as out, (folder / 'stderr.log').open('w') as err:
            result = subprocess.run(command, input=messages[1]['content'], text=True,
                stdout=out, stderr=err, env=env, timeout=300)
        if result.returncode:
            raise RuntimeError(f'Codex CLI failed with exit {result.returncode}; see call-{self.calls:03d}')
        usage = {}
        for line in (folder / 'events.jsonl').read_text().splitlines():
            event = json.loads(line)
            item = event.get('item') or {}
            if item and item.get('type') not in ('agent_message', 'reasoning'):
                raise RuntimeError('tool activity is forbidden in the grading transport')
            if event.get('type') == 'turn.completed':
                usage = event.get('usage', {})
        content = (folder / 'result.json').read_text().strip()
        data = json.loads(content)
        ratings = data.get('ratings')
        if not isinstance(ratings, list) or len(ratings) != 1 or ratings[0].get('status') not in ('YES', 'NO') or not isinstance(ratings[0].get('justification'), str):
            raise ValueError('grader returned invalid or unevaluable ratings')
        response = {'id': f'local-codex-rubric-{self.calls}', 'object': 'chat.completion',
            'created': int(time.time()), 'model': 'gpt-6-luna',
            'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': content},
                'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': usage.get('input_tokens', 0),
                'completion_tokens': usage.get('output_tokens', 0),
                'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}}
        (folder / 'response.json').write_text(json.dumps(response, indent=2))
        (folder / 'transport.json').write_text(json.dumps({
            'elapsed_seconds': time.time() - start, 'model': 'gpt-6-luna',
            'reasoning_effort': 'medium', 'authentication': 'existing Codex CLI login',
            'usage': usage, 'tool_activity': False,
            'max_tokens_handling': 'included as instruction; CLI has no per-call output-token limit flag',
            'original_system_prompt': 'model_instructions_file; original user message on stdin'}, indent=2))
        return response
