# The next degree-six experiment

Research proposal, 2026-09-28. No implementation or solver run is recorded
here. The current structured trial is recorded separately.

Prefer a fixed 33-vertex graph experiment to another general SAT trial.
Start with the five published graphs having 118 edges, once the exact
catalogue bytes have been obtained and checked. Fixing these edges reduces
the undecided graph from 780 edge variables to 198 attachment variables.
Each completed case has a precise interpretation. A timeout has none of
the force of an exclusion.

This is an application of the published neighbourhood gluing method, not
a new construction method or a claim of priority. The reviewed sources do
not establish that the proposed 40-vertex cases remain untested by their
authors. Novelty would need a further literature check even after a result.

## Published catalogue scope and available files

Let H be triangle-free on 33 vertices with independence number at most 8.

| Source | Complete scope reported | Count |
| --- | --- | ---: |
| Goedgebeur–Radziszowski, 2013, Table 14 | e(H) = 118 | 5 |
| Goedgebeur–Radziszowski, 2013, Table 14 | e(H) = 119 | 69 |
| Angeltveit, arXiv v2, Section 3.3 | e(H) ≤ 121 | 14,395 |

The [2013 paper](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i1p30/pdf)
also establishes e(3,9,33) = 118 in Table 4. Its counts of at least 1,223
graphs with 120 edges and at least 13,081 with 121 edges are lower bounds,
not complete counts. The inspected PDF has SHA-256
`d2abf9b7c2c184869d6d1caa080e47e27cd75d918d8bd541698b2c311572b2cb`.
Appendix 1 points to House of Graphs for generated minimal and minimal-plus-one
graphs; Appendix 2 explicitly includes the collection with at most 119 edges
in its deletion-closure checks.

The current [House of Graphs catalogue](https://houseofgraphs.org/meta-directory/minimal-ramsey)
links the five graphs with 118 edges to this exact file:

<https://houseofgraphs.org/data/ramsey/minramsey/Ramseygraphs_3_9_33_e118_some.g6>

The filename ends in `_some`, although the page labels the link with the
published count of five. Do not infer completeness from the filename or
page alone. Decode the file, verify all graph properties, and establish
that it contains five pairwise nonisomorphic graphs. Those checks, together
with the published classification, would establish the intended input scope.
The current page does not link the 119-edge collection.

The [newer paper](https://arxiv.org/html/2401.00392v2) reports a complete
14,395-graph collection with at most 121 edges. Section 6 exhausts its
extensions to 41 vertices. Its additional 38-to-40 checks start from
“a large number” of graphs, which is not a statement that all 40-vertex
extensions of this collection were exhausted. No data archive or code link
was found in the inspected article.

As of this proposal, no bytes from any of these three catalogue scopes have
been obtained. Supported public page capture could read the catalogue but
could not capture the `.g6` download. The installed public-file request
route requires a control application that is not available. No control
bypass, global installation, or substitute download route was attempted.
Bounded public GitHub searches found no source-owned repository for these
data: exact `Ramseygraphs_3_9_33` and `Ramseygraphs_3_9` code queries had no
hits; author/problem and research-organization repository searches did not
locate an archive. This is a discovery limit, not evidence that none exists.

The first executable step therefore remains obtaining the observed source
file through an available supported route. Do not invent an `e119` URL by
changing its filename or adopt an unverified third-party mirror as the
published catalogue.

## Fixed-H formulation

Write V(G) = {0} ∪ A ∪ V(H), where |A| = 6. Join 0 to all of A, make A
independent, and leave 0 nonadjacent to H. Fix every H edge. The only
decisions are x[a,h], the 6 × 33 = 198 edges between A and H. Let
S_a = {h : x[a,h] = 1}.

The target is the same maximal triangle-free, minimum-degree-six case as
the current pilot. Minimum degrees seven through nine remain separate.
For this target:

- Every S_a is independent. This gives 6e(H) binary triangle clauses:
  708 clauses when e(H) = 118, or 714 when e(H) = 119.
- Each S_a has size 5 through 8, so a has degree 6 through 9 in G.
- Every h meets A. Its total degree is d_H(h) + sum_a x[a,h] and must lie
  between 6 and 9.
- Each S_a is maximal independent in H. For every a and h, include
  x[a,h] ∨ OR_{u in N_H(h)} x[a,u]. These are 198 clauses.
- If an H nonedge has no common neighbour inside H, full maximality of G
  requires a common neighbour in A. These additional constraints apply to
  the stated maximal-graph target; do not silently use them for a broader
  claim about all extensions of a fixed H.

Saturating only the A–H edges preserves H and the degree of 0. It cannot
increase the independence number, and a triangle-free graph with independence
number at most 9 automatically has maximum degree at most 9. Thus restricting
the S_a to maximal independent sets is also valid for a broader extension
problem that already imposes coverage and minimum degree six. By contrast,
adding H edges to force full maximality changes the fixed input H.

The exact independence condition is

```text
alpha(H minus union_{a in B} S_a) <= 9 - |B|   for every B subset A.
```

Only |B| = 2, 3, 4, 5 need separate checks: the cases of size zero or one
follow from alpha(H) ≤ 8; size six follows from coverage. Equivalently,
for every independent (10 − b)-set I of H and every b-subset B of A,
require at least one attachment in B × I. If I_j(H) counts independent
j-sets, the full positive-clause family has

```text
15 I_8(H) + 20 I_7(H) + 15 I_6(H) + 6 I_5(H)
```

clauses before duplicate removal. Without coverage, add I_4(H) clauses
for b = 6. These counts must be measured from the actual graph files;
they are not estimated here.

The equivalent formulation in [the analytic note](ANALYTIC-NEXT.md) uses
maximal independent sets M and w[h,B] = OR_{a in B} x[a,h]. For every M
and B require

```text
sum_{h in M} w[h,B] >= |M| + |B| - 9
```

whenever the right side is positive. It is sufficient because every
independent set of a residual induced subgraph extends to a maximal
independent set of H. Merely testing the size of the union of A-neighbours
of maximal sets is not equivalent; smaller independent subsets can violate
the condition while their maximal extension passes.

Permuting A is safe. Arbitrary permutations of a fixed labelled H are not:
the general profile's H-signature ordering must not be copied into this
formula. Any reduction based on H permutations must use verified
automorphisms of that particular input graph.

## Staged limits and evidence

Use the repository's required host scheduling and the supervisor's owned
process cleanup. The following are proposed ceilings, not measured runtime
predictions or authorization to start an unreviewed implementation.

1. Obtain and check the five-graph file. Freeze its source URL, acquisition
   date, SHA-256, decoded records and per-record hashes. Independently check
   n = 33, e = 118, triangle-freeness, alpha ≤ 8, and pairwise nonisomorphism.
   Record the published completeness premise separately from these local
   checks. Allow 60 CPU seconds and 256 MiB for this first admission step;
   an incomplete check stops the experiment.
2. Build one case, selected as the first record in the frozen source file.
   Measure maximal independent sets, I_5 through I_8, generated variables,
   clauses and construction cost. Allow 60 CPU seconds, 1 GiB of memory,
   and 128 MiB of CNF. If complete materialization exceeds the cap, report
   that result before selecting an incremental formulation.
3. Run one solver thread for at most 300 CPU seconds and 330 wall seconds,
   with a 1 GiB memory threshold. Reserve a separate 300 CPU seconds and
   330 wall seconds for proof replay. Cap each proof at 256 MiB and total
   case artifacts at 512 MiB. State which limits the operating system
   enforces and which the supervisor measures. Any exceeded limit produces
   an unresolved result and collected child processes.
4. Continue to the other four records only after the first case has a
   completed independent graph check or checked exclusion. Retain the same
   per-case ceilings. Across five cases, the maximum solve-plus-replay
   allocation is 3,000 CPU seconds, apart from construction and input checks.
   A failed or unresolved first case calls for a diagnosis, not an automatic
   74- or 14,395-case launch.

Before the first scientific run, compare the attachment encoding with direct
enumeration on small graphs, including cases with and without coverage,
repeated attachment sets, false maximality assumptions and known positive
extensions. Verify that A ordering preserves a representative. Cross-check
the maximal-set residual constraints against exhaustive independent sets
on these small controls. Check stop and proof-file-limit behavior with the
same supervisor that will own the real run.

Any returned 40-vertex graph must pass an independent exact triangle and
independent-ten-set check on its saved edge list. An UNSAT answer needs a
saved exact CNF, a proof-producing solve and independent proof replay. A
solver status or a run with no output is insufficient. If a final CNF is
built from incremental independent-set cuts, independently verify every
cut and reproduce that exact formula before checking its proof.

Excluding the five admitted inputs would exclude only the stated degree-six
maximal-graph case with e(H) = 118. If the complete 74 inputs through 119
edges were later admitted and excluded, the same case would require
e(H) ≥ 120. Excluding the complete 14,395 through 121 would give e(H) ≥ 122
in that case. Neither conclusion determines R(3,10), covers larger e(H),
or covers minimum degrees seven through nine.

## A modest general-profile alternative

If catalogue acquisition remains unavailable, the clearest necessary
condition to add is d_H(h) ≥ 5. Indeed, H minus N_H[h] has independence
number at most 7, since an independent eight-set there could be joined
by h. As R(3,8) = 28, that residual graph has at most 27 vertices. Hence
32 − d_H(h) ≤ 27.

Let t7, t8 and t9 be the existing exact degree threshold bits for h and
a_h its number of A-neighbours. Then

```text
d_H(h) = 6 + t7 + t8 + t9 - a_h.
```

The existing threshold bits are exact and ordered. Therefore the bound can
be encoded directly: any two attachments imply t7, any three imply t8,
any four imply t9, and any five attachments are forbidden. For one H
vertex this uses 15 + 20 + 15 + 6 = 56 clauses and no auxiliary variables.
Across H it adds 1,848 clauses. This is the preferred encoding from
[the analytic note](ANALYTIC-NEXT.md); it has not been implemented or solved.

For comparison, the same condition is at most four true literals among
the six positive attachment literals and the three negated threshold
literals. A read-only construction check of that generic counter allocated
35 auxiliary variables and 127 clauses per H vertex. Its 1,155-variable,
4,191-clause total is unnecessary given the existing ordered thresholds.

| Proposed addition to v1 | Added variables | Added clauses |
| --- | ---: | ---: |
| d_H ≥ 5 for all 33 vertices | 0 | 1,848 |
| Complete v1 plus d_H ≥ 5 | 17,933 total | 80,550 total |
| Optional within-signature row ordering | 1,152 | 6,720 |
| Complete v1 with both additions | 19,085 total | 87,270 total |

The row-ordering cost is provisional. For each adjacent pair of equal
six-bit H signatures, compare their H adjacency rows with the two mutual
positions deleted. A lexicographically least upper-triangle representation
under permutations within equal-signature blocks satisfies that ordering.
An explicit encoding can use six signature-equality prefix variables and
30 row-equality prefix variables per pair, with 29 + 150 + 31 clauses.
Across 32 pairs this gives the displayed cost. This argument and encoding
still need exhaustive small-graph controls and independent review before
implementation. It does not apply unchanged when H is fixed.

The d_H bound is inexpensive and justified. Neither proposed addition
guarantees that another general trial will escape the independent-set cut
limit. A verified fixed-H input offers the more informative next experiment.
