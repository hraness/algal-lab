# Moonshot: a 40-vertex (3,10) Ramsey graph

Status, 2026-09-28: the vertex-transitive class is exhausted. No witness was
found. The Ramsey number remains unresolved; the next experiment examines
the degree-4 case without imposing symmetry on the 40-vertex graph.

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
sources, corrected census counts, the degree-4 reduction, and comparison with
the original 2013 construction work. We have not established
publication novelty for either the symmetry exclusion or the next experiment.

## Completed work

| Work | Result | Status |
| --- | --- | --- |
| Circulants on C40 | 2,921 triangle-free connection sets, no witness | Reproduced independently by the new enumerator |
| All Cayley presentations of order 40 | 28 semidirect presentations, 9,034,972 tested unions, no witness | Complete construction with duplicates retained |
| Eight selected nonregular actions | 395 tested unions, all rejection witnesses replayed | Control family, not a census |
| Minimal transitive actions of degree 40 | All 1,963 actions; 2,138,937 tested unions; every rejection replayed | Complete relative to TransGrp's published classification |
| Minimal transitive actions of degree 39 | All four actions; 1,317 tested unions; every rejection replayed | Complete relative to the same classification |
| Positive control on 35 vertices | 8-regular circulant with independence number 8 recovered and independently checked | Suitable representative for the next reduction |

Counts are labelled orbit unions, with repetitions across actions. The full
order-40 search covers degrees 4 through 9. Smaller degrees cannot qualify
by the greedy independent-set bound; larger degrees cannot qualify because
neighbourhoods in triangle-free graphs are independent.

The [enumerator report](vertex_transitive/README.md) gives the completeness
argument, input and binary digests, exact degree counts, controls, limitations,
sources, and reproduction commands. Generated archives, manifests,
certificates, and complete run summaries remain in ignored `runs/`.

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

## Next experiment

If a qualifying 40-vertex graph has a degree-4 vertex v, deleting v and its
four neighbours leaves the unique 35-vertex (3,9)-graph H. H is 8-regular.
Let S1 through S4 be the neighbours in H of the four deleted neighbours.
Each Si is independent, and the Si are pairwise disjoint: a vertex of H
already has degree 8 and cannot gain two neighbours when maximum degree is 9.

The remaining forbidden-independent-set conditions can be encoded exactly
on 140 Boolean attachment variables. For each choice of k deleted neighbours,
every independent (10−k)-set in H must meet at least one of their attachment
sets. Only k = 2, 3, 4 adds constraints, because H has independence number 8.
The representative recovered here has 3,360 independent 8-sets, 13,760
independent 7-sets, and 22,995 independent 6-sets. These can all be enumerated
directly, without approximating the constraints or the independence bound.

Before a solve, compare the encoding against exhaustive small controls and
obtain an independent source review. A SAT result must yield a directly
verified graph. An UNSAT result must have a separately checked proof before
supporting an exclusion. A timeout changes neither Ramsey bound. Any claimed
novelty still requires comparison with the 2013 graph-extension work.

## Budget and reporting

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
