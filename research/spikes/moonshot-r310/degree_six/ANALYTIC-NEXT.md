# Degree-six reductions and the next finite experiment

Mathematical note, 2026-09-28. This is a proposal and a set of necessary
conditions. It records no additional solver run, Ramsey exclusion, or claim
of novelty. The running profile and its saved evidence were not changed.

The more informative next experiment is to fix a verified 33-vertex Ramsey
graph H and solve its attachment problem. This removes all uncertainty
about whether H itself has an independent nine-set. The external catalogue
has not been obtained; deleting pairs from the already verified 35-vertex
graph supplies a narrower, immediately available input family. If a further
general-formula experiment is considered, three small additions are sound:
the internal degree bound, an ordering of the six neighbour degrees, and
two limits on repeated attachment signatures. Together they add no variables
and 2,898 clauses to the reviewed v1 formula. They do not guarantee that
another general trial will finish.

## Assumptions and the exact independence condition

Let G be a maximal triangle-free graph on 40 vertices, with independence
number at most 9 and minimum degree 6. Choose a degree-six vertex 0, put
A = N(0), and let H = G minus ({0} union A). Thus A is independent,
|A| = 6, |H| = 33, and alpha(H) <= 8. Degrees in G lie between 6 and 9.
Every vertex of H meets A: otherwise its missing edge to 0 could be added.

For a in A, let S_a = N(a) intersect H. For v in H, let
K_v = N(v) intersect A and r_v = |K_v|. Write c = sum_v r_v for the
number of A--H edges and h = e(H). A signature is the nonempty set K_v.
Each S_a is independent, has size 5 through 8, and is maximal independent
in H. Column maximality follows because a missing edge a--v can be blocked
only by a common neighbour in S_a.

For every independent set T of H, the set T union (A minus N_A(T)) is
independent in G. Consequently

```text
|N_A(T)| >= |T| - 3.                                      (1)
```

Together with alpha(H) <= 8, condition (1) is also sufficient to exclude
an independent ten-set in G. Sets containing 0 have size at most 9; a set
not containing 0 has size at most |T| + 6 - |N_A(T)|.

## Internal degrees and edge bounds

For v in H, the graph H minus N_H[v] has independence number at most 7.
The established value R(3,8) = 28 therefore gives

```text
5 <= d_H(v) <= 8,              1 <= r_v <= 4.
```

The upper bound on d_H follows from alpha(H) <= 8. Combining it with
d_G(v) <= 9 gives r_v <= 9 - d_H(v).

Let P_a contain the vertices whose exact signature is {a}. Those vertices
are independent and have no A-neighbour outside a. By (1), |P_a| <= 4.
Thus at most 24 vertices have a singleton signature. Coverage of all 33
vertices requires at least nine extra incidences, and

```text
42 <= c <= 48,                2h + c <= 297.
```

The published lower bound e(3,9,33) = 118 then gives

```text
118 <= h <= 127,              166 <= e(G) = 6 + h + c <= 178.
```

The upper edge bound follows from
6 + h + c <= 6 + (297 + c)/2 <= 178.5 and integrality. These restrictions
apply to the stated maximal, minimum-degree-six case. They neither exclude
that case nor address minimum degrees seven through nine.

The 118-edge bound is in Goedgebeur--Radziszowski (2013), Table 4; the
general degree/edge inequality used by the earlier profile is in Table 5.
The established small Ramsey values are premises, not results recomputed
in this note.

## Only 50 signature-size distributions

Let N_j count vertices of H with |K_v| = j. Coverage, the internal-degree
bound and the preceding edge bounds give

```text
N_1 = 66 - c + N_3 + 2 N_4,
N_2 = c - 33 - 2 N_3 - 3 N_4,
N_3 + 2 N_4 <= c - 42,       18 <= N_1 <= 24.
```

The nonnegative integer possibilities are small:

| c | Number of signature-size distributions | Number of sorted column-size multisets |
| ---: | ---: | ---: |
| 42 | 1 | 7 |
| 43 | 2 | 5 |
| 44 | 4 | 4 |
| 45 | 6 | 3 |
| 46 | 9 | 2 |
| 47 | 12 | 1 |
| 48 | 16 | 1 |
| Total | 50 | 23 |

The last column counts sorted six-tuples from {5,6,7,8} with sum c. These
are arithmetic possibilities; they are not assertions that the corresponding
graphs exist.

Let n_i count vertices of H of internal degree i. The capacities
r_v <= 9 - d_H(v) give the additional necessary conditions

```text
N_4 <= n_5,
N_3 + N_4 <= n_5 + n_6,
n_8 <= N_1,
3 n_5 + 2 n_6 + n_7 = 264 - 2h.
```

For example, h = 127 permits only the following four combinations of these
integer data. This is a useful diagnostic boundary, not an existence result.

| c | (n_5,n_6,n_7,n_8) | (N_1,N_2,N_3,N_4) |
| ---: | --- | --- |
| 42 | (0,0,10,23) | (24,9,0,0) |
| 43 | (0,0,10,23) | (23,10,0,0) |
| 42 | (0,1,8,24) | (24,9,0,0) |
| 43 | (0,1,8,24) | (24,8,1,0) |

## Repeated signatures and the c = 42 boundary

Suppose m vertices have exact signature K, with |K| = r >= 2. For any
a in K, those vertices together with P_a are independent and have all
their A-neighbours in K. Condition (1) implies

```text
|P_a| + m <= r + 3.                                      (2)
```

This yields two useful universal limits:

- A two-element signature occurs at most four times. Five copies would
  force both associated private sets to be empty, giving N_1 <= 16,
  whereas N_1 >= 18.
- A three-element signature occurs at most three times. Four copies would
  give at most two private vertices for each of its three elements, so
  N_1 <= 18. But N_3 >= 4 forces N_1 >= 22.

More precisely, a two-element signature occurs at most
floor((c - 40)/2) times. For m >= 2, (2) gives N_1 <= 26 - 2m; combining
this with N_1 >= 66 - c proves the bound. Cases m <= 1 satisfy it directly.
The weaker universal bounds above are convenient for a small SAT addition.

At c = 42, there are exactly four private vertices per a, nine two-element
signatures, and no larger signatures. Equation (2) makes all nine pairs
distinct. Regard those pairs as a simple support graph B on A. Then

```text
e(B) = 9,             d_B(a) = |S_a| - 4 in {1,2,3,4}.
```

Only six sorted degree sequences of B occur:

```text
(1,2,3,4,4,4), (1,3,3,3,4,4), (2,2,2,4,4,4),
(2,2,3,3,4,4), (2,3,3,3,3,4), (3,3,3,3,3,3).
```

The apparent seventh column-size pattern (5,5,8,8,8,8) would require
degrees (1,1,4,4,4,4), which are not graphical: the four degree-four vertices
would need degree sum 16, but their internal edges contribute at most 12
and the two remaining vertices at most 2. A direct enumeration finds
3,700 labelled nine-edge support graphs with degrees 1 through 4. No claim
that any of these support graphs extends to a valid G is made.

## A small possible addition to the general SAT profile

In the reviewed formula, t7(v), t8(v), t9(v) are the exact, ordered bits
for d_G(v) >= 7, 8, 9. For v in H, d_H(v) >= 5 is equivalent to

```text
r_v <= d_G(v) - 5.
```

It can be encoded without auxiliary variables:

- For each pair of its six attachment variables, selecting both implies t7.
- For each triple, selecting all three implies t8.
- For each four-set, selecting all four implies t9.
- No five of the six attachment variables may all be selected.

This uses 15 + 20 + 15 + 6 = 56 clauses per vertex, or 1,848 total.
All 256 combinations of a degree in {6,7,8,9} and an attachment bitmask
were checked against the arithmetic inequality; they agree exactly.

The six vertices of A may also be ordered by nondecreasing G-degree.
For consecutive a_i,a_{i+1}, include t_k(a_i) implies t_k(a_{i+1}) for
k = 7,8,9: 15 binary clauses. This is compatible with ordering H by its
attachment signatures: first permute A by degree, then sort the H rows.
Permuting H does not change any A-degree.

Since the current general profile sorts H by its six-bit signature, all
copies of a signature are contiguous. For each of the 15 two-element
signatures, prohibit every window of five consecutive rows from all having
that signature: 15 times 29 = 435 clauses. For each of the 20 three-element
signatures, prohibit windows of four: 20 times 30 = 600 clauses. A window
clause is the disjunction of the bit mismatches with its nominated signature;
it has 30 or 24 literals respectively. No new variables are needed.

| Prospective addition | Additional variables | Additional clauses |
| --- | ---: | ---: |
| d_H >= 5 | 0 | 1,848 |
| Ordered A-degrees | 0 | 15 |
| Two-element signature multiplicity <= 4 | 0 | 435 |
| Three-element signature multiplicity <= 3 | 0 | 600 |
| Total addition | 0 | 2,898 |
| Reviewed v1 plus these additions | 17,933 total | 81,600 total |

These are prospective counts against v1's 78,702 clauses. No modified
formula was generated or solved here. A future implementation needs tests
of the emitted literals, symmetry preservation, and proof reconstruction.
In particular, these additions do not themselves enforce alpha(H) <= 8.
If a saved independent-ten-set cut contains 0, it already excludes a
particular independent nine-set in H after the fixed 0--H edges are removed.

## Fixed H: an exact and smaller attachment problem

For a verified H, use 198 primary Boolean variables x[a,v]; cardinality or
other encodings may introduce auxiliaries. Include the independent-column,
coverage, degree and column-maximality constraints. Triangle-freeness uses
6h binary clauses. Column maximality uses 198 clauses

```text
x[a,v] OR OR_{u in N_H(v)} x[a,u].
```

Because H is fixed, its maximal independent sets can be enumerated once.
Each S_a can instead be selected from the maximal independent sets of
size 5 through 8. This is an alternative encoding, not a reduction in the
number of mathematical cases without implementation evidence.

The complete remaining independence condition is

```text
alpha(H minus union_{a in B} S_a) <= 9 - |B|,   for B subset A.       (3)
```

Only |B| = 2,3,4,5 need explicit constraints: alpha(H) <= 8 handles sizes
zero and one, and coverage handles size six. For b = |B|, one direct
encoding includes a positive clause on B times T for every independent
(10 - b)-set T of H. Its clause count is

```text
15 I_8(H) + 20 I_7(H) + 15 I_6(H) + 6 I_5(H).
```

Alternatively define w[v,B] = OR_{a in B} x[a,v]. For every maximal
independent set M of H, condition (3) is equivalent to

```text
sum_{v in M} w[v,B] >= |M| + |B| - 9                       (4)
```

whenever the right side is positive. Necessity is immediate. For
sufficiency, any independent set in a residual graph extends to a maximal
independent set M of H; (4) bounds the number of uncovered vertices of M.
Only maximal sets of size at least 5 matter. If coverage and |P_a| <= 4 are
encoded separately, the b = 5 case follows and only b = 2,3,4 remains.

It is not sufficient merely to impose (1) on maximal sets M. For example,
a six-subset can have only two A-neighbours while two other vertices bring
its maximal eight-set's neighbour union to all six. The eight-set passes
that scalar test but its six-subset fails. Formulation (4) checks residual
coverage for every B and avoids this loss of information.

Column maximality is valid even for a broader fixed-H extension search:
add only allowed A--H edges until no further such edge can be added. This
preserves H, the degree of 0, triangle-freeness, and the independence bound.
Minimum degrees cannot decrease, and maximum degree nine follows from the
independence bound in a triangle-free graph. This argument does not justify
forcing missing H edges to be blocked: full graph maximality can require
adding H edges and thereby changing the prescribed H.

Do not copy the general H-signature row ordering into a fixed labelled H.
That ordering uses arbitrary permutations of H, which would generally
change its fixed edge matrix. Permutations of A remain safe; H reductions
must use verified automorphisms of the actual input.

## What a finite exclusion would establish

Goedgebeur--Radziszowski (2013), Table 14, gives complete counts of five
33-vertex graphs with 118 edges and 69 with 119 edges. Its next two counts
are lower bounds. Angeltveit's arXiv v2, Section 3.3, reports a complete
14,395-graph collection through 121 edges. The newer paper's Section 6
exhausts a 41-vertex gluing problem; its separate 38-to-40 tests use
"a large number" of starting graphs. That phrase does not establish a
complete 40-vertex result.

See [NEXT-PROFILE.md](NEXT-PROFILE.md) for the exact source links,
acquisition limits, and proposed staged experiment. No catalogue graph
bytes were available to this analysis. Once the five-graph input has been
obtained and verified, a fixed-H pilot is preferable to another unrestricted
trial because every completed case has an exact scope.

Checked exclusions of the five inputs would exclude h = 118 for the stated
maximal, minimum-degree-six target. Exclusions of the 74 inputs through 119
would give h >= 120 in that target; the complete collection through 121
would give h >= 122. None settles R(3,10) or covers minimum degrees seven
through nine. A returned 40-vertex graph, independently checked, would be
a much stronger outcome. Prior use of gluing and the possibility that these
particular cases have already been tested must remain explicit.

## An available input family: pairs deleted from the 35-vertex graph

The base graph already used for the degree-four certificate is isomorphic
to the published circulant on Z/35 with differences +/-{1,7,11,16}. Its
local representative has differences +/-{8,12,14,17}; multiplication by
22 gives the stated isomorphism. Deleting any two vertices preserves
triangle-freeness and alpha <= 8, yielding a valid 33-vertex H.

A fresh independent construction from the published differences was
transported to the local labeling by the verified map v -> 22v mod 35.
The pairs below use that local labeling; their published labels are
included to make the distinction explicit. Checking all affine maps
v -> av+b in the local labeling gives exactly the six multipliers

```text
1, 11, 16, 19, 24, 34
```

preserve adjacency; all 35 translations are allowed. Each of the resulting
210 permutations was checked directly on the edge matrix. Their action
partitions the 595 unordered vertex pairs into the following seven orbits.

| Deleted pair (local labels) | Pair (published labels) | Pairs in orbit | h | Common neighbours of deleted vertices | (n_6,n_7,n_8) |
| --- | --- | ---: | ---: | ---: | --- |
| (0,1) | (0,22) | 105 | 124 | 1 | (1,14,18) |
| (0,2) | (0,9) | 105 | 124 | 2 | (2,12,19) |
| (0,4) | (0,18) | 105 | 124 | 4 | (4,8,21) |
| (0,5) | (0,5) | 105 | 124 | 2 | (2,12,19) |
| (0,7) | (0,14) | 35 | 124 | 1 | (1,14,18) |
| (0,8) | (0,1) | 105 | 125 | 0 | (0,14,19) |
| (0,14) | (0,28) | 35 | 125 | 0 | (0,14,19) |

The orbit coverage was checked in both directions: every pair has one of
these representatives, and applying the verified maps to each representative
reproduces exactly its listed orbit. This establishes coverage of all pair
deletions from this graph. It does not assert that the full automorphism
group is affine or that the seven remainders are pairwise nonisomorphic.
A finer-than-necessary quotient remains complete for this input family.

The degree counts also have a direct check. For a deleted pair with
adjacency indicator epsilon and k common neighbours,

```text
h = 124 + epsilon,
n_6 = k,       n_7 = 16 - 2 epsilon - 2k,
n_8 = 17 + 2 epsilon + k.
```

There are no internal-degree-five vertices, so all attachment signatures
have size at most three. For the two adjacent-pair cases there are no
degree-six vertices either, so all signatures have size at most two.

A completed exclusion of these seven representative cases would cover
only maximal, minimum-degree-six candidates whose H is one of these pair
deletions. It would not cover all 33-vertex Ramsey graphs with 124 or 125
edges, other edge counts, or other minimum degrees. A verified positive
extension would still give a 40-vertex Ramsey witness. This is a sensible
first fixed-H experiment, not a general Ramsey classification.

## Checks completed for this note

- Read the original 2013 Table 14 on PDF page 25 and checked the exact versus
  lower-bound notation against the newer source review.
- Enumerated all 50 integer signature-size distributions and all 23 sorted
  column-size multisets with a small Python program. Checked all compatible
  internal-degree multisets and the four h = 127 boundary rows above.
- Enumerated all 5,005 nine-edge subsets of the 15 possible support edges;
  exactly 3,700 have every degree between one and four, with exactly the six
  displayed degree sequences.
- Exhausted the 256 degree/attachment assignments for the proposed
  56-clause local degree rule. Every result matched r_v <= d_G(v) - 5.
- Independently checked the fixed-H mathematical section of
  [NEXT-PROFILE.md](NEXT-PROFILE.md), including scope, residual constraints,
  and permutation restrictions.
- Independently constructed the base circulant from the published
  differences and checked all 210 affine maps, all 595 deleted pairs,
  their seven orbits, and every displayed remainder degree histogram.

The bounded arithmetic check completed in under one second with Python
3.14. It is not a solver validation or a substitute for tests of a future
encoding. No runtime source, running worker, frozen source snapshot, or
existing result was changed.
