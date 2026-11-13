"""Run the original rubric evaluator, aborting immediately on a usage limit."""
import argparse, importlib.util, json, os
from pathlib import Path
from types import SimpleNamespace
from codex_rubric_bridge import Bridge

p=argparse.ArgumentParser()
p.add_argument('task');p.add_argument('patch',type=Path);p.add_argument('output',type=Path)
a=p.parse_args()
root=Path(os.environ.get('SWE_INTERACT_WORKSPACE', str(Path.cwd()))).resolve()
tests=root/'SWE-Interact/data/singleturn'/a.task/'tests'
a.output.mkdir(exist_ok=False,parents=True)
spec=importlib.util.spec_from_file_location('original_rf_evaluator',tests/'evaluate_rubrics.py')
evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
evaluator.TESTS_DIR=str(tests)
class UsageUnavailable(BaseException):pass
bridge=Bridge(a.output/'grader',bind='127.0.0.1')
class Completion:
 def create(self,**request):
  try:response=bridge.complete(request)
  except RuntimeError as error:
   folder=bridge.output/f'call-{bridge.calls:03d}'
   log=''.join(f.read_text(errors='replace') for f in [folder/'stderr.log',folder/'events.jsonl'] if f.exists())
   if 'usage limit' in log.lower():raise UsageUnavailable(str(error))
   raise
  return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=response['choices'][0]['message']['content']))])
try:
 result=evaluator.evaluate_rubrics(SimpleNamespace(chat=SimpleNamespace(completions=Completion())),
  'gpt-6-luna',(tests/'prompt.txt').read_text(),a.patch.read_text(),json.loads((tests/'rubrics.json').read_text()))
 (a.output/'rubrics_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}),flush=True)
except UsageUnavailable as error:
 (a.output/'infrastructure-error.json').write_text(json.dumps({'error':'Codex CLI usage limit','detail':str(error),'calls':bridge.calls},indent=2)+'\n')
 print('Rubric grading stopped on usage limit; no repeated retries.',flush=True)
finally:bridge.close()
