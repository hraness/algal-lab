# Cost-aware research memory: corpus and protocol gate

**Status: corpus decided by the owner (2026-10-08); protocol freeze next.** This is an evidence receipt,
not a preregistration, holdout result, or claim about model quality.

## Decision

On genuinely source-disjoint task families, can selective feedback improve
quality enough to offset retrieval and revision cost versus fixed instructions,
labeled examples, matched-byte recency or random retrieval, and unselected
feedback from the same eligible development pool?

The acceptance rule is fixed at the level of the question: preserve holdout
integrity; establish baseline headroom; require the candidate to be
noninferior on the primary quality endpoint and meet a prespecified total-cost
saving. Otherwise stop and retain the null result.

## Development gate receipt

- Repository source: `7ce4b68a3ebeab9e9756a1ae0d3bcd1848682d8e`.
- Runner discovery source is pinned to the same SHA; no paid discovery request
  was made.
- `bun run foundation verify-dataset runs/clinc150` passed. It identified
  `clinc150-full`, manifest digest
  `09035c10fc6caa16b596d281758e2cf885db8504e8fbedd924eba0209a4335e5`, and
  the recorded train/validation/test partitions (15,012/3,081/5,476 rows).
- `bun run foundation verify-baseline runs/clinc150 runs/clinc150-baseline`
  passed with digest
  `409a8e2e8f07d733a619d2b7a32a1049050fb3eb8b3aabbb8066c589b8163dde` and
  scope `development-only`. The recorded TF-IDF development control is
  193/302 (63.91%), versus 2/302 (0.66%) for majority/random. These are
  headroom and replay checks only; they are not confirmatory evidence.

The foundation checks pass, but the research gate does not. The public intent
fixture does not provide source or conversation-group provenance for a genuine
source-group split, and its test partition is not an authorized fresh holdout
for this question. The split access history, practical margins, paired
uncertainty plan, multiplicity policy, and full cost allowance therefore remain
unfrozen. No candidate search, holdout access, or paid model call is authorized.

## Required freeze before any search

1. Obtain a licensed or owner-authorized corpus with stable source-group
   identities and record immutable source and split digests.
2. Freeze development/validation access, an untouched task-family holdout,
   access history, and the independent unit before seeing final outcomes.
3. Compare fixed instructions, labeled demonstrations, recency retrieval,
   seeded random retrieval at matched context bytes, selective feedback, and
   unselected feedback from the same eligible development pool. Keep the task
   schema and evaluator fixed, and count preparation and selection separately.
4. Predeclare quality (including invalid and unwanted outputs), calls, tokens,
   retrieval/revision work, losing candidates, latency, and total estimated
   cost. Set the noninferiority and cost-saving margins before selection.
5. Freeze paired uncertainty, multiplicity and stopping rules, independent
   review, a second-machine reproduction, and the rule to stop on contamination
   or a missed margin.

The next falsifiable action is the corpus intake record and protocol freeze. Until
that is complete, the published synthetic fixture remains a regression control,
not research evidence.

## Corpus admission record still required

An intake record must name the owner or license and permitted use; immutable
corpus version and collection date; source/conversation-group key, how it was
constructed, and evidence that it denotes independent sources rather than
near-duplicate texts; group-level split manifests and cross-split duplicate
checks; prior access to labels or published outcomes; and the holdout custodian
and one-time release rule. If those facts cannot be established, neither CLINC150
nor a newly named dataset supplies a confirmatory holdout. Do not reconstruct
missing provenance by grouping on the labels the experiment predicts.

## Owner corpus decision (2026-10-08)

The owner delegated the corpus choice to the operator agent on 2026-10-08 and
it is recorded here as the owner decision:

- **Corpus:** Super-NaturalInstructions, English track
  ([allenai/natural-instructions](https://github.com/allenai/natural-instructions);
  Wang et al. 2022, arXiv:2204.07705). Pin the repository commit and record the
  digest of every task file at intake.
- **Source group:** the union of each task's `Source` entries (split on `;`),
  merged across name variants and derived datasets by a rule recorded at intake.
  Tasks in one merged group are one independent unit.
- **Development pool:** the official English training split
  (`splits/default/train_tasks.txt`: 756 tasks at the pinned commit; the paper
  reports 757).
- **Evaluation split (not a fresh holdout):** the official English test split
  (119 tasks). The authors excluded training tasks sourced from the same dataset
  as any test task, but the split is not source-disjoint by the `Source` field
  (test task249 and training tasks 275-276 share enhanced_wsc) or by derivation
  (for example SQuAD 1.1/2.0, eQASC/QASC, WSC variants). At intake, split
  multi-valued `Source` entries, merge names that denote the same or derived
  datasets into one group across both splits, and run the cross-split duplicate
  check; drop any test task whose group touches the development pool from the
  evaluation split before freeze. This repository has never read its instances; record that
  access history now. Until the protocol below is frozen and independently
  reviewed, read only test-task metadata (`Source`, categories, instance
  license), never instances or outputs; then release it once.
- **Rights:** task definitions are Apache-2.0; instances carry each source's
  license in the task's `Instance License` field. Admit only tasks whose
  instance license permits research reuse and record the license per task;
  drop tasks with an unknown license instead of guessing.
- **Known limit:** the test split is public and its labels may be in model
  training data, so under AGENTS.md it is not a fresh holdout. This repository
  has not read it, so after the intake merge it serves as a source-disjoint, repository-untouched
  evaluation split, and results are a paired relative comparison between arms
  under that exposure, not confirmatory fresh-holdout evidence or absolute
  quality. The stop-on-contamination rule applies to repository-side exposure
  (holdout content in prompts, retrieval indexes, tuning, stopping or
  selection); the protocol freeze records each model's published training-data
  disclosures.
- **Access history:** on 2026-10-08 an independent reviewer read the first
  1,500 bytes of each test-task file to extract `Source` strings only; those
  bytes may include `Definition` text and never reached `Instances`.
- **Questions the freeze settles:** whether a test task's `Definition` and
  `Positive Examples` count as schema available to all arms (they contain
  outputs); how many instances per task are evaluated (the paper used 100);
  and a metadata-only reader for `Instance License`, which follows `Instances`
  in each file.
- **Spending:** paid calls only through the host runner's existing discovery
  budget, with the reserved, consumed and remaining allowance recorded in the
  freeze, and only after it.

Next: build the intake record above for this corpus, then freeze the numerical
protocol values listed below. CLINC150 stays a regression control.

## Structural commitments recorded before corpus authorization

These controls are frozen now, but do **not** substitute for the missing corpus
or numerical protocol values:

- The independent unit is a source group/task family. Repeated calls, seeds, or
  reordered demonstrations on one item are not additional units.
- Selection and revision may read development/validation records only. The
  untouched task-family holdout, its labels, and any derived outcome remain out
  of prompts, retrieval indexes, tuning, stopping, and model selection.
- The comparison has six named arms: fixed instructions, labeled
  demonstrations, recency retrieval, seeded random retrieval at matched context
  bytes, selective feedback, and unselected feedback. The feedback arms draw
  from the same eligible development pool; every arm uses the same task schema
  and fixed evaluator. The historical training-feedback arm is not evidence
  for a new matched-pool comparison.
- The primary quality record includes correct decisions, invalid outputs, and
  unwanted actions. The cost record includes selection, candidate and losing
  calls, input/output tokens, retrieval, revision, evaluation, latency, and
  declared provider or hardware charges.
- Promotion requires the selected arm to meet the frozen quality
  noninferiority rule **and** the frozen total-cost saving rule. A quality win
  without the cost saving, or a cost saving with a missed quality margin, is a
  null result for this question.

The following values remain explicit blanks rather than post-hoc choices:
corpus version pin and intake digests, the source-group merge rule, split/access
ledger, independent-unit count, quality and cost margins, uncertainty and
multiplicity method, stopping rule, reviewer identities, reproduction target,
and reserved/consumed/remaining allowance. No search starts until that table is
completed and independently reviewed.

## Control receipts on 2026-10-08

- `bun run discovery doctor` returned `ready: true`, Bun `1.3.14`, and the four
  proposed tracks. It did not qualify optional tools or providers.
- `bun run discovery agenda cost-aware-research-memory` returned `status:
  proposed`; its next experiment is the same source-group corpus and
  headroom gate. Agenda text is a proposal, not spending authority.
- `.herd-live/STATUS.json` reported no active runs and `$0.40/$500` spent. The
  existing `runner-smoke-*` records are transport smokes, not research
  evidence. This step made no paid request and consumed no new allowance.

This receipt records a corpus decision and a still-unfrozen protocol rather than a quality,
novelty, practical-value, or LLM-intelligence claim.
