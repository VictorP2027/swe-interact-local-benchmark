# Complete local SWE-Interact assessment

**75/75 initial attempts assessed. Local adapted score: 41/75 = 54.7%.**

| First-attempt outcome | Tasks |
| --- | ---: |
| Passed | 41 |
| Failed | 34 |
| Ungraded | 0 |

This is the direct single-turn implementation run in this Codex chat. It is **not an official GPT-6 Luna coding-agent benchmark**. Rubric grading uses GPT-6 Luna with medium reasoning effort through the supported Codex CLI, replacing the supplied default grader. Initial implementations were frozen before exposing supplied checks. Test sources, fixtures, and assertions were not edited by this agent; the supplied patches were applied for verification.

Separately, 20 failed tasks have passing feedback-assisted grades. Corrections never replace initial outcomes. Some additional corrections have passing tests without a combined rubric grade.

## The final three tasks

- **Suricata FFI — pass.** All 12 required Rust cases pass. The resumed full C framework reports 2,585 passes and zero failures; the full Rust suite also reports no failures. The baseline report had 3,296 passes. Original complete rubric ratings (14/14) were reused only after checking the frozen binary patch, all 12 production files, and all supplied test/rubric hashes match. The record explicitly identifies resumed native commands and their lower-memory release profile. Six old C case names are lost by the line parser despite the full framework reporting zero failures; this is retained as a parsing limitation.
- **Netdata system info — first attempt fails.** Its public header could not compile the unchanged required test: label declarations and `RRDLABEL_SRC_AUTO` were missing. The prior runner suppressed that compiler error and skipped all 19 required cases. The separate header correction passes all 19 cases (105 assertions), and affected production files compile. Its rubric grade remains 0: one of 23 checks rejects migrated field access despite those alleged accesses appearing only in removed diff lines. The rating is preserved without rerolling.
- **MariaDB statistics — first attempt fails.** Both complete server builds succeeded after removing 15 empty build objects left by the interrupted VM. All three original baseline cases passed. The frozen implementation passed three of four required cases but lost persistent statistics for indexes added by `ALTER TABLE`, failing `gcol.innodb_virtual_stats`. All 18 rubric checks were evaluable; one rejection contradicts its own explanation. A separate one-line correction forces statistics recalculation after ALTER; rebuilding and rerunning the unchanged tests passes all four. It is recorded as test-verified, without replacing the initial failure or inventing a regrade.

## Verification boundaries

Original incomplete reports and raw ratings remain archived. Certain source failures are scored as failures while retaining `evaluation_valid: false`, `canonical_evaluation_valid: false`, and `failure_assessment_valid: true`; compilation failure already establishes that the attempt cannot pass. Grafana recoveries explicitly combine existing artifacts from identical frozen source and identical rubric inputs. This completes all 75 **local outcome assessments**, not 75 identical canonical invocations or the separate quota-blocked autonomous GPT-6 Luna multiturn/API run.

The task VM is stopped after verification. The unrelated default VM is unchanged.

[Full task table](../results/README.md) · [Machine-readable ledger](../results/summary.json) · [Compact outcomes](../results/summary.json)
