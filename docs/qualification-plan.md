# Qualification plan, 2026-09-22

This plan is frozen before observing the qualification results. Its purpose is
to decide whether Algal Lab is an honest, useful experimental substrate. A
positive effect of sharing is not a pass condition. Do not tune this plan until
sharing wins. Later experiments require a new plan and new search seeds.

## Decision

| Approach | What it resolves | Cost and limitation | Decision |
| --- | --- | --- | --- |
| Keep the demo and add more agent messages | Exercises execution | Mixed evaluation and portfolio selection still obscure usefulness | Insufficient |
| Keep ALGAL and qualify the instrument, controls, and selection | Tests the existing architecture with independent numerical evidence | Still a toy graph domain | Adopt |
| Add another orchestration layer or Valhalla now | Could enable federation | Does not resolve the local measurement questions | Defer |

ALGAL remains responsible for typed execution and receipts. The lab owns
experimental admission, instruments, candidate retention, and interpretation.
Reconsider that boundary if a concrete experiment requires a missing runtime
guarantee; no such gap has been established.

## Numerical and baseline qualification

Independently check the existing simulator against a reference connectivity
implementation and exhaustive small graphs. Add an exact random-failure oracle:
after k uniform removals, average largest-component service over all k-node
removed subsets, then integrate those expectations over the failure horizon.
The oracle must agree with analytical cases and explicit removal permutations.
It evaluates the full failure distribution, including states encountered during
discovery; it is not exclusively held-out data or a real-world network model.

Use the following three regimes: (nodes, edges, failure steps) = (8,10,3),
(8,12,3), and (10,14,4). Each has 16 predeclared search seeds, two researchers,
four rounds, and all three information-sharing conditions. Compare the existing
adaptive scripted policy with independently sampled connected graphs using the
same proposal seeds and eight proposal slots per condition/replicate. The
random generator is biased and is not advertised as uniform graph sampling.

Search seeds: 107, 223, 349, 487, 613, 761, 887, 1019, 1151, 1289, 1433,
1567, 1709, 1871, 1999, 2143. Discovery schedules: 41, 83, 167, 331. Sampled
holdout schedules: 1009, 2017, 4027, 8053, 16111, 32213, 64433, 128879.
These schedules are retained for continuity; the exact oracle is the primary
qualification measurement.

Before evaluation, each condition freezes one champion: highest mean discovery
AUC, breaking ties by canonical graph digest. All candidate artifacts remain
available. Report the champion's exact expected random-failure AUC and targeted
control separately. Also evaluate a fixed ring with deterministic opposite-node
chords at each graph budget, without selecting it from observed outcomes.

Primary descriptive contrast: adaptive shared-artifacts minus adaptive isolated,
paired by search seed within a regime. Secondary contrasts: adaptive isolated
minus random isolated; adaptive shared-artifacts minus random shared-artifacts.
Report every paired difference, mean, minimum, maximum, wins, ties, and losses.
No significance or superiority claim follows from these descriptive statistics.
The message-blind scripted policy's two shared conditions must remain identical;
random search must remain identical across all conditions. Invalid proposals
consume their slots. Report failures and duplicate designs.

The fixed 0.75 coverage threshold from the demo is not an acceptance criterion.
Even perfect surviving connectivity has AUC ceiling 1 - steps/(2*nodes), which
can be below that threshold. Portfolio size and exploration also affect its
meaning. Population evaluation and a frozen champion resolve the primary
qualification question more directly.

## Live model smoke

When an admitted application executor is available, run one seed, two
researchers, two rounds, and three conditions: at most 12 model calls. Use fresh,
stateless, tool-free requests with no repository access. Remove condition names
from the model-visible context; information content can still reveal a treatment.
Keep provider/model/settings and usage evidence, failed calls, predictions,
measurements, and complete receipts. Never silently fall back to scripted search.

Acceptance requires retained outcomes for all calls, valid measured proposals,
offline archive reproduction, and at least one valid changed design that cites
a visible earlier peer artifact. Such inheritance demonstrates the mechanism;
it does not establish causal benefit or transferable scientific discovery.
If the provider cannot be qualified or the smoke fails, report the exact limit.

## Confidence and next claims

Confidence in this approach means numerical agreement, uncontaminated selection,
working controls, reproducible evidence, and an operational research loop. It
does not require sharing to outperform isolated search. A future superiority
claim requires a new frozen confirmatory plan with a practical effect margin,
paired uncertainty analysis, fresh replicates, and another regime or relabeling
check. A discovery of a structural rule additionally needs a rule stated before
successful tests on new graph configurations.
