# A stronger degree-six SAT profile

The optional `degree-six-structure-v1` profile adds necessary edge bounds
and an ordering of interchangeable labels. It retains a representative of
every qualifying graph in the degree-six case. The default remains
`baseline`; its formula, edge map and structural metadata match the frozen
baseline exactly. Neither profile covers minimum degrees seven through nine.

## The 33-vertex edge bound

Write A = N(0), H = V(G) minus N[0], and c for the number of edges from A to H.
Here |A| = 6 and |H| = 33. If H contained an independent nine-set, adding
vertex 0 would give an independent ten-set. Thus H is a (3,9;33)-graph.

Goedgebeur and Radziszowski,
[*New Computational Upper Bounds for Ramsey Numbers R(3,k)*, EJC 20(1), P30 (2013)](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i1p30/pdf),
Table 4, page 11, establishes e(3,9,33) = 118. We therefore require
e(H) ≥ 118. This uses a published numerical theorem; the pilot does not
re-enumerate its underlying 33-vertex catalogue. The inspected source PDF
has SHA-256
`d2abf9b7c2c184869d6d1caa080e47e27cd75d918d8bd541698b2c311572b2cb`.
Table 5, page 12, separately gives e(3,10,40) ≥ 161.

The degree counters already contain exact bits for degree at least 7, 8
and 9. Let T_A and T_H be their sums over A and H. Since every degree lies
between 6 and 9 and A is independent,

```text
c = 30 + T_A
2 e(H) = 198 + T_H - c = 168 + T_H - T_A.
```

Consequently e(H) ≥ 118 is exactly T_H - T_A ≥ 68. Encode this by requiring
at most 31 true literals in the 117-input sequence consisting of the
negated H threshold bits followed by the positive A threshold bits.
The counter uses 3,248 auxiliary variables and 12,844 clauses.

## Label ordering and private neighbors

For each vertex of H, its signature is the six adjacency bits to vertices
1 through 6, with vertex 1 most significant. Order these signatures
lexicographically. Any graph can be relabelled this way by permuting H;
all its other constraints are invariant under that permutation. Equal
signatures retain arbitrary relative order. This requires no automorphism.

For adjacent signatures x and y, forbid x_i = 1 and y_i = 0 when their
earlier bits agree. Expanding every possible shared prefix needs 63 clauses
per pair, or 2,016 clauses for the 32 pairs, with no auxiliary variables.
The expansion is small because signatures have only six bits.

Let P_a contain the vertices of H adjacent to exactly one member a of A.
P_a is independent, since all its vertices share neighbor a. It has no
edges to A minus {a}; those five vertices are also independent. Thus
|P_a| ≥ 5 would give an independent ten-set, and |P_a| ≤ 4 is necessary.
Equal signatures form a consecutive block after sorting. Forbid every
five-vertex window from being five copies of any one-bit signature.
The resulting 6 × 29 = 174 clauses each have 30 literals and need no
auxiliary variables. This window encoding relies on the sorting clauses.

There are at most 24 vertices in all the P_a. Coverage gives every remaining
H vertex at least two neighbors in A, so c ≥ 2 × 33 - 24 = 42. Together
with c = 30 + T_A, this requires T_A ≥ 12: at most six of the 18 A threshold
bits may be false. A second counter adds 105 variables and 396 clauses.

Finally e(G) = 6 + c + e(H) ≥ 166. The profile therefore implies the
published global lower bound of 161 without a separate global counter.
These are necessary conditions and routine encodings, with no novelty claim.

## Formula cost and verification

| Addition | Auxiliary variables | Clauses |
| --- | ---: | ---: |
| e(H) ≥ 118 | 3,248 | 12,844 |
| Ordered H signatures | 0 | 2,016 |
| At most four copies of each private signature | 0 | 174 |
| c ≥ 42 | 105 | 396 |
| Total addition | 3,353 | 15,430 |
| Complete initial profile | 17,153 | 78,702 |

There are also 780 edge variables, making 17,933 variables in total.
The worker and supervisor use the same selected profile when constructing
and reconstructing the formula. Metadata records its name, bounds,
ordering and source. Every returned model is checked by recounting graph
edges, signatures and private neighbors independently of the SAT counters.
An UNSAT answer still requires a saved proof and independent replay; its
graph interpretation also depends on the published 118-edge premise.

The full focused suite passed 26 tests in 16.788 seconds on 2026-09-28.
New controls cover all 4,096 pairs of six-bit signatures, 4,095 short
signature sequences, 4,589 signed-cardinality cases, 192 assignments for
returned threshold bits, and 3,072 five-vertex graphs with edge-bound
settings. Known Ramsey graphs on 5, 8, 13 and 35 vertices retain a sorted
representative. A one-second isolated source copy preserves the selected
profile in its reconstructed formula and collects its worker. The earlier
interruption, recovery, graph-checker and positive controls also pass.

The copied source includes sibling directories `degree_six` and
`vertex_transitive`; only `checker.py` from the latter is required at runtime.
The checker is loaded from that exact path, without changing the module
search path. The installed solver library remains an explicit external input.
The [independent review](PROFILE-REVIEW.md) confirms the preservation arguments,
checks the frozen baseline and exact source identities, and adds three
full-size boundary and import-isolation controls.

Run after independent review, with the same budget and batch size as the
baseline and a new output directory:

```sh
python3 research/spikes/moonshot-r310/degree_six/run.py --library /path/to/libcadical.dylib --output runs/moonshot-r310/degree-six-structured-pilot --seconds 600 --batch 16 --cuts 100000 --models 20000 --memory-mib 1024 --seed 0 --profile degree-six-structure-v1
```

The comparison run stopped at its 100,000-cut limit after 6,251 models,
using 153.808 total CPU seconds. The saved formula and all recorded cuts
passed reconstruction; the final model still contains an independent
ten-set. See [the complete report](RESULTS.md). This unresolved result
changes neither Ramsey bound.
