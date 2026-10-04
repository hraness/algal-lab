# Research direction and roadmap

## Research objective

Prioritize computer-science results that change how a useful computation is
performed: a proved algorithm or limitation, a certified optimization method,
a reproducible systems result, or a measured improvement to research itself.
A result needs separate answers to **is it correct**, **what differs from prior
work**, and **who can use it under which assumptions**. A high score or a new
finite construction answers none of those questions by itself.

The executable [research agenda](../examples/research-agenda.json) identifies
four proposed tracks, in starting order. Inspect it without running experiments:

```sh
bun run discovery doctor
bun run discovery agenda
bun run discovery agenda cost-aware-research-memory
```

The agenda checker requires a question, proposed contribution, existing evidence,
baselines, metrics, next experiment, independent confirmation, primary-source
comparison, stopping rule, and existing repository references for every track.
Its commands are displayed as instructions, never executed from JSON. A valid
agenda is a research proposal, not an approved experiment or a novelty verdict.

| Track | Practical question | First decision to resolve |
| --- | --- | --- |
| Cost-aware research memory | Can selective feedback improve assistants enough to pay for retrieval and revision? | Establish headroom on source-disjoint tasks against labeled examples and cheap retrieval. |
| Certified resource allocation | Can workers or replicas be assigned efficiently under useful constraints? | Find a workload-supported constraint that the existing exact reductions do not already solve. |
| Failure-aware execution | Can long jobs recover without repeating uncertain effects? | Specify and test the persistence and ownership failure model before optimizing recovery cost. |
| Certificate-guided search | Can reusable obstructions reduce exact search cost? | Prove reuse is sound and include learning and proof checking in the total cost. |

These are application hypotheses. The softmax objective is not a validated model
of a production scheduler, the host fixture is not a distributed service, and
synthetic assistant cases are not user traffic. Each track must earn its
application claim through the separate consumer test below.

## What can run today

| Component | Delivered behavior | Limit |
| --- | --- | --- |
| Network studies | Matched conditions, frozen selection, independent numerical checks, offline reproduction. | Toy connectivity objectives; the one recorded live comparison is not a general sharing result. |
| Resumable discovery | Finite local graph search, saved predictions/failures, optional explicitly enabled providers, one final evaluation, offline score and selection verification. | One writer on one host; the runner does not select research questions, prove theorems, or coordinate distributed owners. |
| Observation interface | Registered predictions, measurement joins, source identities, and frozen evaluation for reviewed adapters. | An interface does not validate a new domain or authorize arbitrary code. |
| Study claims and evidence | Typed run-local claims cite supporting or contradicting records; outcomes and support levels are derived and checked offline. | The study projection grants replay evidence, not novelty or utility. This is not shared cross-campaign retrieval. |
| Exact research | Mathematical arguments, finite certificates, independent verifiers, and scoped result articles. | Proof, computational coverage, priority, and usefulness require different evidence. |
| Task and host experiments | Replayable task comparisons and local crash/recovery controls. | Historical outcomes do not qualify a new strategy, model, or deployment. |
| Outer research agent | The [discovery skill](../.agents/skills/algal-discovery/SKILL.md) directs source comparison, finite experiments, reviews, and handoff. | No unattended scheduler, cross-campaign budget service, or shared claim database is implemented. |

Do not build a second simulator or activate generated code to fill those limits.
Reuse an existing fixed evaluator where its assumptions fit. Add another as
reviewed repository code with small analytical controls, an independent check,
explicit resource bounds, and a versioned input contract.

## Starting datasets and tools

The [foundation setup](../CONTRIBUTING.md#prepare-tools-and-datasets) supplies a
licensed, hash-pinned CLINC150 development corpus with cheap retrieval controls,
a reproducible exact allocation suite, and optional local builds of CI-pinned
SAT/proof tools. Run `bun run foundation doctor` to distinguish available tools
from missing optional profiles. Keep the existing small assistant fixtures as
regression tests.

These preparations do not close the research gaps: public intent data lacks
conversation-group provenance and may appear in model training; allocation
instances are synthetic; local crash fixtures do not model distributed failures.
The corpus cannot be substituted into the binary Textbutler policy task. Each
track still needs its task definition, source/instance-family split, frozen
protocol, appropriate baseline, and practical workload validation before a
scientific comparison. Native setup runs short controls, not another moonshot
search or a release of held findings.

## Run a finite research campaign

1. **Choose a decision, not a topic.** Recover the current evidence and exclusions.
   State the falsifiable question, proposed contribution, intended consumer,
   and the observation that would change the next action. Prefer an unresolved
   question with a strong cheap baseline over an easy unoccupied record cell.
2. **Test the likely rediscovery first.** Build a claim-to-source table with
   exact versions, theorem/proof or experiment locations, hypotheses,
   substitutions, conclusions, and differences. Search alternate terminology
   and citations in both directions. Record inaccessible sources and uncertainty.
   A source saying something differs from independently reproducing it.
3. **Freeze the protocol before search.** Record source/data identities,
   development and regression cases, final cases and access rules, primary
   endpoint, practical margin with units, experimental unit, uncertainty method,
   multiplicity policy, baselines, ablations, full allowance, and stopping rule.
   Count pilot selection, failed runs, losing candidates, retrieval, evaluation,
   and certification costs. A new folder or machine does not reset that allowance.
4. **Qualify the measurement cheaply.** Reproduce analytical or exhaustive
   small cases, adversarial cases, infeasible inputs, and deliberately corrupted
   certificates. Check that the baseline has headroom. Stop a saturated study
   rather than searching for a flattering metric after seeing results.
5. **Search only development evidence.** Record predictions, parents, realized
   inputs, all failures, and strategy versions. Keep the evaluator fixed and
   model-generated commands inert. Development scores are selection evidence,
   not confirmatory evidence. Retrieved memory must record its split and source;
   do not bring prior holdout results back into a continuing experiment.
6. **Try to refute the candidate.** Test the smallest counterexample, boundary
   cases, relabelings, perturbations, and stronger known baselines. Isolate each
   proposed mechanism with an ablation. An obstruction to one proof or search
   family is not a counterexample to the broader claim.
7. **Review correctness and novelty separately.** Give independent reviewers
   the frozen inputs, source revision, exact claim and assumptions, proof or
   protocol, negative results, and source comparisons. Resolve findings in
   recorded evidence. AI review is not human peer review; a passing test is not
   a proof or a literature search.
8. **Confirm a frozen selection once.** Use fresh source/instance families and
   paired comparisons at the independent task or replicate level. Seeds that
   only reorder the same examples do not create independent examples. Report
   intervals, effects in task units, all prespecified comparisons, timeouts,
   and invalid outputs. Account for multiple hypotheses and any sequential
   stopping; do not repeatedly inspect a holdout until a threshold passes.
9. **Test the application.** Freeze an adapter to one named public or
   owner-authorized workload. Compare against the best appropriate simple and
   established implementations. Include preprocessing, learned-state storage,
   checking, latency, memory, and integration cost. State where model assumptions
   fail. Synthetic, trace-based, and live evidence remain distinct; no production
   activation follows from a synthetic win.
10. **Replicate and preserve the result.** A second machine or independent
    implementation repeats the computation at the recorded source/tool versions.
    Transfer the private run separately, verify its contents, preserve consumed
    allowances, and distinguish numerical reproduction from a new stochastic
    model run. Do not silently rerun uncertain paid operations.
11. **Publish only the supported scope.** Separate theorem, finite certificate,
    empirical result, conjecture, rediscovery, and unresolved priority. Refresh
    dated record tables before reporting a new bound. Release a minimal verifier,
    inputs or a lawful data-access recipe, exact commands, limitations, and review
    identity. Respect the field-audit correction and author-response hold; do not
    export its withdrawn counts or contact authors as part of routine delivery.
12. **Continue from the negative results too.** Leave the strongest supported
    claim, disproved approaches, remaining allowance, unresolved operations,
    assigned next test, and who holds the run. Stop when the declared allowance
    ends, a required assumption fails, a baseline subsumes the candidate, or the
    practical margin is missed. A null result can close a question.

For theory, statistical holdouts do not establish universal quantifiers. Require
a proof with independent review, and use numerical tests to find mistakes and
check finite witnesses. For empirical work, a proof of the evaluator does not
establish generalization or practical value.

## Portfolio and next work

Prefer one active primary question and one cheap replication or refutation at a
time. This is a scheduling recommendation, not permission for new compute or
spending. Promote a strategy only after matched-budget comparisons including the
cost of generating that strategy. Retain diverse alternatives when objectives
conflict rather than selecting a post-hoc winning score.

Before more inference, address these evidence gaps:

- Replicate the [network.v2 transfer finding](live-comparison-v2-findings.md)
  under its frozen plan if a live allowance is authorized. The original run
  found degradation; it does not establish the proposed diversity-collapse
  mechanism. Distinguish a same-plan stochastic replication from a fresh-seed
  generalization study. A mechanism experiment needs its own preregistration.
- The [task study](../experiments/task-optimization/FINDINGS.md) found labeled
  examples as accurate as costlier feedback on the same small audit set. Freeze
  a harder source-disjoint corpus before attributing value to selective memory.
- Finish primary-source comparisons for a small number of useful allocation or
  grouping results before adding more related theorem claims. Keep
  [novelty-ledger.md](novelty-ledger.md) as the source record, not model memory.
- Refresh an extremal target's source and inspect its unseeded-control status
  before treating it as a promising new campaign. Finite improvements and a
  general search-method advantage are separate outcomes.

Reuse [the existing study evidence and claims](architecture.md#artifact-boundary)
where their contracts fit: `src/evidence.ts` projects completed `lab study`
archives, and `src/claims.ts` checks run-local supporting and contradicting
citations. A claim asking for stronger support remains insufficient when its
records only establish replay. These commands do not accept resumable
`discovery` directories or establish literature priority. Extending them to
other instruments needs a reviewed evidence mapping, not a second claim format.

The graph runner enforces run-local reservations and selection order. The outer
agent connects those records to the campaign-wide ledger, source comparisons,
and cross-machine ownership record. Automating that ledger or adding
federated workers is follow-up work: it must prevent duplicate assignment and
budget renewal, keep holdouts out of retrieval, and pass crash/transfer controls
before use. Population size is not a substitute for these checks.

## Historical foundation and sources

The sections below describe the original staged network-lab design and its
checkpoints, rather than the current work queue. Later result notes supersede
open questions where linked.

Algal Lab explores a concrete research loop: build a reliable instrument,
generate testable proposals, record predictions, measure consequences, preserve
competing artifacts, and use accumulated evidence to choose the next experiment.
The first implementation fixes the instrument and tests a small part of that
loop. It does not claim recursive scientific intelligence.

## Sources and design choices

Markus J. Buehler's [Recursive Meta-Intelligence](https://www.linkedin.com/pulse/recursive-meta-intelligence-markus-j-buehler-umx8c)
motivates treating an executable research environment as a durable product of
earlier research. It connects instrument construction with later populations of
investigators. This is the inspiration for the project direction, not evidence
that Algal Lab has reproduced the article's results.

The [MetaMaterialsDiscovery archive](https://huggingface.co/lamm-mit/MetaMaterialsDiscovery/blob/main/README.md)
preserves three agent-built laboratories and distinguishes their original runs
from later human-directed studies. Its recorded discrepancy between a requested
geometry control and the realized geometry motivates retaining both here. Its
[shared prompt](https://huggingface.co/lamm-mit/MetaMaterialsDiscovery/blob/main/data/Run%201/prompt.md)
calls for numerical checks, competing hypotheses, failed results, controlled
comparisons, and predictions before later simulations. Those requirements are
more actionable for this lab than scaling an agent population first. The graph
instrument here does not implement those archived mechanics solvers.

The [SwarmWorld paper, version 1](https://arxiv.org/html/2608.26081v1) and
[source repository](https://github.com/lamm-mit/SwarmWorld) motivate separating
shared artifacts from explicit communication. The paper reports that reuse often
starts through physical observation and that cultural mechanisms have
metric-dependent benefits; the strongest individual artifact need not come from
the richest social condition. Our three local conditions ask a related, narrower
question. They are not a reproduction of SwarmWorld's spatial environment,
population, action system, or results.

These sources were inspected on 2026-09-22. An archive, a prompt, and a paper
support different claims. Preserve that distinction when citing this project's
motivation or comparing future outcomes.

## First delivery

The initial scope is a headless network-resilience lab with strict bounded
contracts, a deterministic simulator, ALGAL receipts, a content-addressed
experiment archive, three sharing conditions, pre-measurement predictions,
frozen portfolios, unseen random schedules, and repeated targeted controls. The
default executor is scripted and credential-free; an operator can explicitly
supply a model wrapper. The scripted
policy ignores message text, so the demo is not an experiment on LLM
communication benefits.

This provides a reproducible application substrate. It does not establish a
collective advantage, novel scientific discovery, or model-provider performance.
The [research method](research-method.md) defines what the measurements mean.

## Proposed follow-up stages

The [initial qualification plan](qualification-plan.md) now supplies an
independent exact oracle, exhaustive instrument checks, discovery-selected
champions, matched random search, and paired descriptive comparisons. See
[qualification findings](qualification.md) for measured results and the
[first](gateway-smoke-findings.md) and [second](gateway-smoke-v2-findings.md)
Gateway smoke findings for the live-model status. These are acceptance evidence
for a research substrate, not completion of the scientific claims below.

1. **Qualify the research protocol.** Status of each sub-item:
   - Done: more independent study seeds (16 search seeds per regime in the
     qualification; 8 replicate seeds in the comparison plan).
   - Done: recorded inference usage for model runs (Gateway token counts and
     reported cost in both smokes; XCB usage explicitly unavailable).
   - Done: comparison with random search and a predeclared fixed reference
     under matched proposal seeds and budgets.
   - Done: preregistered outcomes (frozen qualification plan; frozen comparison
     plan with a practical margin), with null results retained.
   - Partly done: whether sharing concentrates search or adds diversity is now
     measured as topology-class counts per portfolio; no verdict yet.
   - Not done: a relabeling or tie-policy sensitivity study. The instrument
     probe documents label sensitivity of targeted failure; no study varies it.
   - Done: artifact-only and message-enabled conditions stay separate.
2. **Replicated comparison (initial network stage).** Implemented in
   [`src/comparison.ts`](../src/comparison.ts),
   [`src/statistics.ts`](../src/statistics.ts), and
   [`src/topology.ts`](../src/topology.ts): protocol v2 host priming so every
   condition starts from identical seeded designs, counterbalanced condition
   order across replicates, held-out transfer budgets, paired inference over
   replicate seeds (exact sign-flip, percentile bootstrap, and Wilcoxon
   signed-rank) against a preregistered practical margin, and exact
   topology (isomorphism) classes tracked separately from labeled graphs.
   Scripted arms are controls; a live arm requires an admitted executor
   (`--executor-command`, or the pinned Gateway route in
   [`gateway-compare.ts`](../examples/gateway-compare.ts)). The headroom spike
   showed the network.v1 objective saturated at the registered budgets, so the
   first live run registers the heterogeneous-failure instrument
   (`network.v2`, `src/heterogeneous.ts`: weighted random removal,
   value-fraction service, exact subset-DP oracle, seeded per-replicate
   environments) in the [v2 plan](comparison-plan-v2.md) at sparse budgets
   that clear the preregistered 0.03 headroom bar. The v1
   [frozen plan](comparison-plan.md) remains the scripted-control baseline.
   The first live run under the v2 plan is recorded in
   [live-comparison-v2-findings.md](live-comparison-v2-findings.md): a
   competent but not dominant live arm, a small within-margin sharing
   trend at primary, and a measured negative transfer effect — one run,
   no strong claim.
3. **Develop reusable scientific memory.** Partly delivered by the run-local
   `src/claims.ts` and `src/evidence.ts` contracts for supporting/contradicting
   evidence and insufficient outcomes. Cross-campaign retrieval, literature
   comparisons, and targeted replication scheduling remain outer-agent work.
   Separate a researcher's explanation from measured evidence and later
   confirmation. Evaluate retrieval quality and split isolation before expanding
   memory indefinitely.
4. **Broaden the instrument family.** Add another validated domain through an
   explicit instrument interface. Require analytical examples, independent
   implementation or reference checks, documented assumptions, and fresh
   reproduction before comparing outcomes. Keep domains with different units and
   objectives separate.
5. **Admit proposed instrument and generator changes.** Let researchers suggest
   changes as artifacts first. A separate admission process must qualify code,
   resource limits, reference fixtures, control realization, and compatibility
   before activation. Freeze the evaluator for a study; a candidate must not
   improve its reported score by changing its own judge. Arbitrary generated
   code execution and recursive instrument evolution are not implemented now.
6. **Federate independently owned laboratories when needed.** Valhalla could
   exchange signed artifact references, attribution, replication requests, and
   verification outcomes across owners. Algal would still run local experiments
   under local authority. This requires a maintained work-room adapter and
   domain-specific verification; Valhalla's room directory and bounded Platonik
   replay are not a joined research conversation or universal scientific
   verifier. Local studies do not depend on this integration.

Each stage needs its own acceptance evidence and reviewed scope. Population
size, richer conversation, and recursion are experimental variables, not
substitutes for a validated instrument or an honest comparison.

## Structural discovery checkpoint

The [weighted-tree continuation](weighted-tree-discovery.md) now establishes
two exact design rules, a four-node phase diagram, and a counterexample to
unrestricted star optimality. These are proved for the stated mathematical
model and independently checked with rational arithmetic; their literature
priority remains unresolved. A separate frozen experiment tests evolution of
bounded reusable construction/search parameters. It does not activate arbitrary
generated code, change the instrument, or establish recursive LLM improvement.

Use the proved cases as controls. Concentrate further design search on
conflicting value/reliability profiles and budgets outside those cases. The
evaluator must remain fixed while the generator evolves, and the cost of
selecting a generator must be reported separately from deployment search.

A separate [terminal-tree study](terminal-tree-discovery.md) develops the
two-survivor endpoint: a proved dominance-frontier construction, exact
integer-rate evaluation, and a sampled construction with a checked confidence
bound on regret. It provides a tractable setting for measuring the work/error
tradeoff against a known optimum. It does not replace the AUC objective or
establish literature priority or an advantage from model-generated proposals.

The [ordered-survival continuation](ordered-survival-discovery.md) proves a
four-point joint-inclusion law at every fixed horizon and derives probability-free
pairing rules for cooperative and redundant pairs. This broadens the mathematical
result to successive-sampling inclusion probabilities and a distinct additive
service objective. A small-model pilot found no feedback advantage over its
no-feedback arm, while a zero-model enumeration control found both additive
laws. Prefer exact enumeration within a small admitted grammar; future model
experiments should test useful grammar expansion or proof construction with
fresh questions, not count investigator-supplied laws as model discoveries.

The [next result](rank-selection-and-triples.md) moves to general independent
rank selection under a reversed-hazard condition and identifies a tractability
boundary after two weighted failures: sorting solves intact equal-size groups,
but exact majority-triple optimization is strongly NP-complete. A quadratic
spread bound certifies small additive regret near uniform rates. Exact
counterexamples delimit stochastic-order and order-only generalizations.
Full-source novelty checks and specialist comparison remain higher priority
than further inference in the old conjecture grammar; the
[source ledger](novelty-ledger.md) makes those gaps explicit. The subsequent
[all-horizon theorem](intact-groups-all-horizons.md),
[stochastic-order theorem](stochastic-intact-groups.md), and
[mixture-family theorem](mixture-rank-grouping.md) supersede the original open
intact-group question within their stated assumptions. Check those results and
their priority limits before proposing another version of that question.
