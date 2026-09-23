# Research direction and roadmap

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
2. **Replicated comparison (current stage).** Implemented in
   [`src/comparison.ts`](../src/comparison.ts),
   [`src/statistics.ts`](../src/statistics.ts), and
   [`src/topology.ts`](../src/topology.ts): protocol v2 host priming so every
   condition starts from identical seeded designs, counterbalanced condition
   order across replicates, held-out transfer budgets, paired inference over
   replicate seeds (exact sign-flip, percentile bootstrap, and Wilcoxon
   signed-rank) against a preregistered practical margin, and exact
   topology (isomorphism) classes tracked separately from labeled graphs.
   Scripted arms are controls; a live arm requires `--executor-command`. The
   frozen plan document for the first live comparison is still to follow, and
   no comparison result is claimed yet.
3. **Develop reusable scientific memory.** Add typed claims with supporting and
   contradicting experiments, exact lineage, failed hypotheses, and targeted
   replication requests. Separate a researcher's explanation from measured
   evidence and later confirmation. Evaluate retrieval quality before expanding
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
