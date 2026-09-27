# Retained knowledge transfer

This follow-up compares three frozen programs on new public synthetic messages:
the original fixed program, the earlier validation winner kept as an executable
procedure, and the fixed program with bounded guidance from an accepted feedback
revision. It never sends a message.

The procedure comes from the original optimizer's first portfolio entry, even
when that is a fixed or demonstration program. The lesson comes from the accepted
feedback candidate with the highest validation accuracy, with manifest digest as
a deterministic tie-break. Original holdout results do not choose either artifact.
If no accepted feedback revision exists, the run writes an explicit ineligible
result instead of inventing a lesson.

The knowledge artifact contains the original task for rollback, its exact digest,
the retained program, original source groups, training-only lesson provenance,
and separate learning and full-campaign costs. Its parser rejects unknown fields,
stale parents, changed budgets/routes/schemas, and non-training lesson sources.
There can be at most four lessons totaling 2,048 UTF-8 bytes. Every compiled prompt
must remain within 4,096 bytes. Learned text is data passed through the ordinary
task parameter interface; it cannot grant tools or change execution limits.

`FRESH_CORPUS` is frozen public study data: two calibration cases, eight validation
cases, and eight audit cases, all with source IDs distinct from the first study.
The runner rejects overlapping source groups and freezes corpus and program
digests before execution. It evaluates all three arms on validation, then saves
the selection before running any audit case. Replacement requires strictly better
validation accuracy without more invalid outputs or false responses. Ties keep
the prior task. Audit outcomes are reported for all three frozen arms and cannot
change that decision.

Campaign and artifact hashes establish content identity, not authorship or the
truth of a score. Reproduce the source campaign from its saved receipts before
using it as evidence; the earlier study's inspector supports that check.

Each audit uses the existing single-candidate foundry. Its calibration and
validation reruns are charged and reported, but cannot select another program.
The fixed corpus requires 78 fresh calls across the three arms. Costs of learning
the original lesson, the original whole campaign, and fresh evaluation remain
separate. Parse failures, total accuracy, accuracy conditional on a valid output,
and false responses are reported separately.

Credential-free mechanics run:

```sh
bun experiments/task-optimization/retention-run.ts \
  --from runs/task-study/11-feedback.json --out runs/retention-scripted
```

Explicit live comparison, with the same pinned Gateway model and configuration
as the original live study:

```sh
bun experiments/task-optimization/retention-run.ts \
  --from runs/task-gateway-seed11/11-feedback.json --out runs/retention-live \
  --live --max-calls 80 --max-usd 1
```

Provide Gateway credentials through the same environment mechanism as the first
study. The runner refuses an existing output directory and never retries a failed
remote request. It saves `knowledge.json`, the frozen evaluation plan, the decision
made before audit, receipts, full results, rollback task, and sanitized transport
observations. Do not commit generated runs or provider credentials.

Reproduce the full fresh selection, costs, and audits offline without calling a
provider:

```sh
bun experiments/task-optimization/retention-run.ts --inspect runs/retention-live
```

The inspector loads the recorded effects, reruns all three arms and their
validation/rollback decision, and compares the complete canonical result. Altered
metrics fail even when the outer result hash has been recomputed.

The cases measure a small hand-written policy, not production user benefit or
broad retained intelligence. A scripted run establishes execution and rollback
mechanics only. A live result can show whether this particular retained program
or lesson transfers under the recorded model, data, and limits; a null result is
an ordinary outcome.

## Observed transfer, September 27, 2026

The live follow-up to seed 11 completed 78 fresh calls using the same
`openai/gpt-6-luna` model through the OpenAI-only Gateway route. Temperature was
omitted, preserving the provider default; reasoning was disabled. All three arms
scored 8/8 on fresh validation and 8/8 on the separate audit, with no invalid
outputs or false responses. The frozen rule therefore kept the original task.
This run found no measurable transfer benefit from replacing it with the retained
program or adding the learned guidance.

The knowledge artifact held one 613-byte lesson. Original learning cost was
49 calls and 45,648 modeled work units; the full original campaign was 77 calls
and 67,962 units. Fresh evaluation cost was 78 calls and 61,752 units, with
21,632 input tokens and 1,170 output tokens. The fresh standard uncached price
estimate was **$0.0027482**, not an invoice reconciliation.

Offline inspection reproduced all 78 fresh receipts/effects and the complete
validation, rollback, cost, and audit result without provider calls. The local
archive is `runs/retention-live-seed11`; generated data is excluded from Git.
Canonical result digest:
`sha256:dce5c969236fa1bf18357c68d922fab68f8e9966d7fbcf99bc57f58bb7689138`.
SHA-256 of saved `result.json` bytes:
`72c668dca06ae06d0ac0bd9f8b035f34d3254a46657eee38cc9e6aba9c7e2dc5`.

One synthetic transfer set with a perfect baseline has a ceiling and little
power to detect improvement. It supplies a real null comparison and successful
rollback evidence, not proof that retained knowledge cannot help other tasks.
