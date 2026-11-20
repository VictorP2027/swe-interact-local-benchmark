# Two-week analysis

The [published snapshot](summary-2026-11-20.json) contains the November 20 task-level scores and failure labels. Atlas task IDs use the last eight characters after the `atlas/` prefix. Use the [team handoff](../TEAM-HANDOFF.md) for the scope and the cases to compare.

To reproduce the two-week checkpoint on a machine with the trial artifacts, run from the repository root:

```sh
python3 adapt-pilot/analysis/build_review.py \
  --historical /path/to/nov-13/output-singleturn \
  --current /path/to/nov-20/output-wednesday-victor-c \
  --output /path/to/private-review
python3 adapt-pilot/analysis/build_aggregate.py --review /path/to/private-review
```

The first script matches complete pairs by task ID and prefers the later complete pair for repeated tasks. The second checks the parsed verifier results and joins against the direct-chat archive. The generated Markdown and evidence include links to private local files. Share the summary snapshot across machines.
