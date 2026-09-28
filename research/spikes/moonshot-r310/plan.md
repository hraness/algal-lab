# Moonshot: a 40-vertex (3,10) Ramsey graph

Status, 2026-09-28: the vertex-transitive class and the degree-four case are
excluded by complete, checked computations. No witness was found and the
Ramsey number remains unresolved. Both independently reviewed degree-six
SAT formulations reached their cut limits without a witness or an exclusion.
Their final graphs still contain verified independent ten-sets.
The separate [fixed-remainder search](fixed_remainder/README.md) excludes
centre-covered degree-six extensions of all 595 two-vertex deletions of
the published 35-vertex graph, represented by seven checked cases.
The independently reviewed [demand certificates](demand_certificates/README.md)
exclude a further nine exact 33-vertex remainders for maximal triangle-free
extensions with a degree-six centre. Their integer proofs require 150,902
endpoint-union checks and no SAT solver. This finite sample includes two of
the five published 118-edge classes; it does not exclude nonmaximal
extensions or settle the unrestricted problem.

## Target and present evidence

A triangle-free graph on 40 vertices with independence number at most 9
would prove R(3,10) = 41. The current bounds are 40 ≤ R(3,10) ≤ 41. Exoo's
39-vertex construction proves the lower bound. Angeltveit's 2025 result,
[R(3,10) ≤ 41](https://arxiv.org/abs/2401.00392), proves the upper bound.

The search has low prospects: prior work already found tens of millions of
39-vertex Ramsey graphs, without a successful extension. A negative search
within a special class is useful evidence, but cannot settle the unrestricted
problem. No numerical probability of success has been calibrated.

The [dated frontier review](frontier-review-20260928.md) records authoritative
sources, corrected census counts, the degree-four reduction, and the bounded
comparison with the original 2013 construction work. No publication-priority
claim is made for either exclusion or the next experiment.

## Completed work

| Work | Result | Status |
| --- | --- | --- |
| Circulants on C40 | 2,921 triangle-free connection sets, no witness | Reproduced independently by the new enumerator |
| All Cayley presentations of order 40 | 28 semidirect presentations, 9,034,972 tested unions, no witness | Complete construction with duplicates retained |
| Eight selected nonregular actions | 395 tested unions, all rejection witnesses replayed | Control family, not a census |
| Minimal transitive actions of degree 40 | All 1,963 actions; 2,138,937 tested unions; every rejection replayed | Complete relative to TransGrp's published classification |
| Minimal transitive actions of degree 39 | All four actions; 1,317 tested unions; every rejection replayed | Complete relative to the same classification |
| Positive control on 35 vertices | 8-regular circulant with independence number 8 recovered and independently checked | Suitable representative for the next reduction |
| A degree-four vertex in any 40-vertex candidate | Exact 140-variable, 98,965-clause attachment formula is unsatisfiable | LRAT proof accepted by three separate implementations; every candidate has minimum degree at least five |

Counts are labelled orbit unions, with repetitions across actions. The full
order-40 search covers degrees 4 through 9. Smaller degrees cannot qualify
by the greedy independent-set bound; larger degrees cannot qualify because
neighbourhoods in triangle-free graphs are independent.

The [enumerator report](vertex_transitive/README.md) gives the completeness
argument, input and binary digests, exact degree counts, controls, limitations,
sources, and reproduction commands. Generated archives, manifests,
certificates, and complete run summaries remain in ignored `runs/`.
The [degree-four report](degree_four/README.md) gives the mathematical
reduction, formula and proof hashes, published uniqueness premise, exact
controls, portable audit and reproduction commands.
The [immutable degree-four proof release](https://github.com/hraness/algal-lab/releases/tag/r310-degree-four-proof-20260928)
was published on 2026-09-28 after PR #89 merged as
`5a47c4e7558b5a99f041f4fc9e4f7e0adbd2b8a8` and main's required check passed.
A fresh release download matched archive SHA-256
`7df0a45dbe16d9be94494e5dd054337c8bac049acc0146737b5bb0a9e54daf0d`.
All 24 manifest entries, exact formula regeneration, seven focused tests,
the project LRAT checker, the independent audit and `lrat-trim` passed.

## Correction to the previous record

The earlier Cayley log treated 14 distinct element-order profiles as proof
that all 14 isomorphism types had been covered. That implication is not
justified: an element-order profile is not a complete group invariant. The
fresh search instead retains every homomorphism from each order-8 group to
Aut(C5), avoiding the unsupported deduplication step. The complete
vertex-transitive search also subsumes the Cayley result.

The earlier literature note misidentified the roughly 150 billion graphs
as (3,9)-graphs; Angeltveit's paper attributes that scale to its (3,8) stage.
The frontier review distinguishes the stages and records the larger
43,146,537-member 39-vertex collection described by the current source.
Prior claims that a search was unprecedented have been removed pending a
proper novelty review.

## A complete reduction for existence searches

If any witness exists, adding edges until it is maximal triangle-free
preserves its order and cannot increase its independence number. Any two
nonadjacent vertices must then have a common neighbor; otherwise their edge
could be added. Thus it is enough to search diameter-two representatives.
This argument is about existence, not a claim that every witness is maximal.

[Pandey and Ravi (2026)](https://arxiv.org/html/2601.03572), Theorem 3.6, gives
minimum degree at least six for this class. Here is the degree-five step
with its counting made explicit. If deg(v) = 5, all 34 vertices outside N[v]
meet N(v), and at most 5 × 8 = 40 edges join these parts. At least
2 × 34 − 40 = 28 outside vertices therefore meet N(v) exactly once. Yet
each of the five neighbors can have at most five private outside neighbors,
because six together with the other four neighbors would form an independent
ten-set. This gives at most 25, a contradiction. Diameter two also rules out
degree four since 1 + 4 + 4 × 8 = 37 < 40. Lower degrees are already excluded
by R(3,9) = 36. This repairs arithmetic slips in the preprint's proof without
changing its stated result.

## Current pilot: incremental SAT with a degree-six vertex

Search on all 40 labelled vertices with no assumed automorphisms. Fix one
vertex and its six neighbors by relabelling, require degrees between six
and nine, forbid triangles, and require every remaining vertex to meet that
fixed neighborhood. A saturated candidate with a degree-six vertex satisfies
all these conditions. Full diameter-two constraints can be omitted initially;
doing so enlarges the searched family and cannot exclude a real candidate.
The cases of minimum degree seven, eight and nine remain outside this pilot.

Use an incremental SAT solver and add required independent-ten-set clauses
when an exact graph check finds a counterexample in a proposed model.
Every ten-set must contain an edge, so each added clause is valid for the
entire target class. The graph checker decides when a model is a true witness;
a SAT assignment to a partial clause set is not one. Preserve the exact
accumulated formula, cuts, settings and a candidate or stop reason.

Before a ten-minute, single-core pilot, obtain an independent review of the
encoding and reduction, compare the cardinality encoding and small graph
models against brute force, and recover known Ramsey graphs as positive
controls. No symmetry pruning beyond the fixed neighborhood is admitted
without its own proof and review. A reported UNSAT must be followed by a
fresh proof-producing solve of the final formula and independent proof
verification before supporting an exclusion. A timeout or unchecked UNSAT
changes neither Ramsey bound. This approach is a research pilot, not a claim
of algorithmic or publication novelty.

The reviewed baseline reached its 100,000-cut limit after 6,251 models,
using 281.690 CPU seconds, 376.928 wall seconds and 90,488,832 peak bytes.
Every recorded mask and corresponding 45-literal clause passed replay.
The final model satisfied all recorded cuts, but an independent check found
the ten-set {0,7,8,9,10,18,19,23,29,30}. This remains an unresolved search.
Its source was frozen separately from the next implementation.

The opt-in [stronger profile](degree_six/PROFILE.md) uses the published
e(3,9,33) = 118 bound, sorts outside-neighborhood signatures without
assuming automorphisms, and limits each private-neighbor class to four.
It has 17,933 variables and 78,702 initial clauses; its independent edge
recount and exhaustive small controls pass. The unchanged baseline remains
the default. The combined 26-test suite passes, including isolated-source
execution and interruption recovery; three additional independent controls
also pass. The reviewed comparison stopped at 100,000 cuts after 6,251
models, using 153.808 total CPU seconds. Its final graph still contains
the independently verified ten-set {0,7,8,9,10,22,26,27,33,36}. Both runs
remain inconclusive; their [report](degree_six/RESULTS.md) records the exact
coverage and formula checks.

## Budget and reporting

The [fixed-remainder reduction](fixed_remainder/STRUCTURAL-NOTE.md) has a
complete 1,712-node branch enumeration, independent reconstruction of all
candidate sets and search outcomes, and saved branch trees. It applies to
the specified remainders and centre coverage, rather than to every possible
degree-six remainder. Its proof files and separate Boolean encoding provide
another verification route, documented with their original and fresh checks.

The recovered session authorized at most 72 CPU-hours. The present work uses
small serial experiments with explicit time, node, and output limits, after
coordination with the integration owner about host scheduling. It does not
authorize paid services, new infrastructure, or an unbounded search.

The full vertex-transitive run took 338.644 seconds of wall time, including
orbit construction, certificate replay, and summary writes. The C search
itself used 2.028 CPU seconds; that number is not the total cost. The earlier
Cayley control took 45.510 seconds of wall time. The remaining budget is far
larger than these completed experiments require; it should be spent only on
reviewed, decisive subproblems rather than repeated searches of exhausted
classes. Stop a computational experiment at its declared bounds and report
its exact coverage, even if the overall research objective remains open.

The degree-four solve used 30.517 CPU seconds and 39.999 wall seconds.
Its three proof checks took about eight seconds in total, plus small controls
and packaging checks. The retained proof has 20,723,074 bytes. Each completed
SAT pilot had a separate ceiling of 600 CPU seconds on one core, with wall
time, memory, iteration and output bounds fixed before it started. Together,
the two pilot supervisors and their workers recorded 435.498 CPU seconds;
this subtotal excludes controls, independent audits and earlier experiments.
