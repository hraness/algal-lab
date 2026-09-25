# Round 27: exact values of C(n) for small n via certified SAT and CP-SAT

Status: C(3) = 8, C(4) = 11 and **C(5) = 14** are complete. The n = 5 decision
is by exhaustive layer enumeration (`layer_enum5.c`, 2026-09-25): after fixing
z-layer 0 to one canonical subset per D4 orbit (1,905 orbits of
within-layer-valid subsets of [5]², sizes 1–4), the DFS over layers 1–4 visited
~292 M nodes and found no 15-subset (`records/enum_n5_k15.log`). The same
binary run at K = 14 found a 14-set in ~2 s (positive control; verified by the
repository verifier and an independent 5×5 determinant check), and the
layer-candidate table was cross-checked by brute force (826 of the 12,650
4-subsets of [5]² are concyclic/collinear; the enumerator keeps exactly
11,824). A cube-and-conquer LRAT UNSAT proof at k = 15 (`cube_solve.py`) is
still running as an independent second witness; completeness of the
enumeration is argued + spot-checked, not yet machine-certified.

n = 6: `certificates/n6_18_ls5x.json` gives C(6) ≥ 18 (the seed-82 ls5x run,
initialised from the n = 6, k = 17 witness; a second certificate from an
independent seed also verifies). Local search at k = 19 stalls far from zero
degeneracies (best ~5–6), so C(6) = 18 is plausible but unproved; n = 6's
hypergraph is too large (~5.0 M maximal degenerate sets) for the current SAT
encoding.
Large files (CNF, LRAT proofs, hypergraph dumps) are not committed; their SHA-256 are in
the logs under `records/` and they regenerate from the scripts.

C(n) = largest subset of the grid {0, …, n−1}³ with no five points on a common
sphere or plane (AlphaEvolve problem 60). Exact criterion: every 5-subset of
lifted rows (x, y, z, x²+y²+z², 1) has a nonzero determinant.

The scripts write their outputs to `runs/` (gitignored); `records/` holds the frozen copies of the small logs and JSON records that this memo cites.

## Summary

| n | C(n) | lower bound (certificate) | upper bound | certification |
|---|---|---|---|---|
| 3 | 8 | `certificates/n3_8.json` | CP-SAT optimal; cadical UNSAT at k = 9 with and without symmetry breaking, LRAT proofs checked | complete |
| 4 | 11 | `certificates/n4_11.json` | CP-SAT optimal (symmetry-broken model); cadical UNSAT at k = 12 with and without symmetry breaking, LRAT proofs checked | complete |
| 5 | 14 | `certificates/n5_14_ls5x.json` | exhaustive layer enumeration (`layer_enum5.c`); LRAT corroboration in progress | complete* |
| 6 | ≥ 18 | `certificates/n6_18_ls5x.json` | none (trivial 4n = 24; k = 19 search stalls) | lower bound only |

\* the enumeration's completeness is argued in `layer_enum5.c` and spot-checked;
a machine-checkable UNSAT proof (cadical/kissat LRAT) is still being computed —
if one exists it supersedes the enumeration witness.

## Method

### Exact hypergraph (`hypergraph.py`)

Five points lie on a common sphere or plane iff their lifted vectors
L(p) = (x, y, z, x²+y²+z², 1) are linearly dependent. For a generalized sphere
Σ (sphere or plane) with at least five grid points, the set P ∩ Σ is a
*degenerate set*; a 5-subset is forbidden iff it lies inside one such set, so
the exact constraint is

> at most 4 chosen points in every inclusion-maximal degenerate set.

Two distinct generalized spheres meet in a circle, a line, a point or nothing,
so a degenerate set with ≥ 5 points can be contained in another one only if it
is entirely concyclic or collinear; only those are tested for a superset.

Four points whose lifted vectors have rank ≤ 3 (four concyclic or four collinear
points) lie on a pencil of generalized spheres that covers the whole space, so
any fifth grid point completes a degenerate 5-subset. For |S| ≥ 5 (always the
case here, C(n) ≥ 8 for n ≥ 3) the constraint

> at most 3 chosen points on every circle or line with ≥ 4 grid points

is implied and is added as a redundant strengthening (it is what the earlier
note called "at most 3 on any grid circle" and "no four collinear").

Enumeration: for every non-collinear triple T = (i, j, k) the null vector of
the 4×5 matrix [L_i; L_j; L_k; L_q] is v_c = (−1)^c det(minor omitting column c),
linear in L_q (v = D(T) L_q with D(T) built from the ten 3×3 minors of the
triple). Normalising v by gcd and sign gives a canonical key per generalized
sphere; v = 0 identifies q as concyclic with T. A key seen for ≥ 2 points q
outside T names a sphere/plane with ≥ 5 grid points, whose full point set is
then evaluated exactly (L v = 0 over the grid). Lines come from pairs. All
arithmetic is int64 numpy on entries bounded by 24·(n−1)²·3(n−1)² (< 2²⁰ for
n ≤ 7), with gcd/sign normalisation in exact integers; `--selftest` compares
the D(T)-matrix null vectors with direct Python-int cofactor expansions and
checks the rank criterion against 5×5 determinants.

### Independent verification of the hypergraph (`bruteforce_check.c`)

A separate C program enumerates every 5-subset of the grid and classifies it
exactly (int64 4×4 determinant of lifted differences), and every 4-subset
(rank ≤ 3 iff all four 3×3 minors vanish). Against the emitted family it checks
soundness (a 5-subset inside a bound-4 set is degenerate; a 4-subset inside a
bound-3 set is rank-deficient) and completeness (every degenerate 5-subset lies
in a bound-4 set; every rank-deficient 4-subset lies in a bound-3 set). A third
opinion, `bruteforce_count.py`, is a pure-Python Laplace expansion of the raw
5×5 matrix with no shortcuts.

| n | 5-subsets | degenerate (C) | degenerate (pure Python) | rank-deficient 4-subsets | verdict |
|---|---|---|---|---|---|
| 3 | 80,730 | 16,026 | 16,026 | 468 | HYPERGRAPH EXACT |
| 4 | 7,624,512 | 714,936 | 714,936 | 6,436 | HYPERGRAPH EXACT |
| 5 | 234,531,275 | 10,301,543 | (not run) | 39,539 | HYPERGRAPH EXACT |
| 6 | not run | | | | |

The construction therefore reproduces the complete degenerate-5-subset relation
at n = 3, 4 (where the earlier CP-SAT proofs of C(3) = 8 and C(4) = 11 used the
complete 5-subset hypergraph) and at n = 5, and it is invariant under all 48
cube symmetries at every n (checked as a set equality of the whole family).

### Hypergraph statistics (inclusion-maximal sets)

| n | spheres (≥ 5 pts) | planes (≥ 5 pts) | circles (≥ 4 pts) | lines (≥ 4 pts) | size range | build time |
|---|---|---|---|---|---|---|
| 3 | 849 | 99 | 364 | 0 | 5–12 | 1 s |
| 4 | 32,964 | 846 | 3,772 | 76 | 5–24 | 31 s |
| 5 | 539,397 | 6,597 | 23,855 | 193 | 5–25 | 1,181 s (loaded host) |
| 6 | not run | | | | | |

No non-maximal set had to be dropped at n ≤ 5 (every sphere/plane set with ≥ 5
grid points is already maximal). Size histograms are in the `stats` block of
each `records/hg{n}.json`.

### Models

*CP-SAT* (`solve_cpsat.py`, OR-tools 9.15): Boolean x_p per grid point,
Σ_{p∈A} x_p ≤ 4 per maximal degenerate set, Σ_{p∈B} x_p ≤ 3 per circle/line,
Σ x_p ≥ 5 (so the circle/line bounds are valid), maximise Σ x_p; 4 workers.

*SAT* (`encode_sat.py`, `solve_sat.py`): the same constraints as clauses. A
cardinality constraint "at most b of m" with C(m, b+1) ≤ 60 is written as its
explicit forbidden (b+1)-subsets (one 5-clause per 5-point sphere, six per
6-point sphere, …); larger ones use pysat's sequential counter. "At least k" is
a totalizer. cadical 3.0.1 (`--lrat --no-binary`) writes an LRAT proof for every
UNSAT answer; the proof is checked by `lrat-check` (marijnheule/drat-trim,
commit 2e3b2dc, built from source; the build is not committed), an independent checker
that re-derives every proof step by unit propagation from the hinted clauses.

### Symmetry breaking and its justification

The hyperoctahedral group of the cube (coordinate permutations × reflections
x ↦ n−1−x, order 48) acts on grid points and maps spheres to spheres, planes to
planes, circles to circles and lines to lines, so it permutes the hypergraph
(verified computationally). For every non-identity element π the lex-leader
constraint (x_0, …, x_{N−1}) ≤_lex (x_{π(0)}, …, x_{π(N−1)}) is encoded with the
standard prefix-equality chain (e_i ← e_{i−1} ∧ (x_i = x_{π(i)}),
e_{i−1} → (x_i ≤ x_{π(i)}); fixed points of π are skipped). Soundness: the
lexicographically smallest member of any orbit satisfies all 47 constraints
simultaneously, so every orbit of feasible sets keeps at least one
representative; in particular the optimum is unchanged. Empirical check: with
and without the constraints CP-SAT returns 8 at n = 3 and cadical is UNSAT at
k = 9 (n = 3) and k = 12 (n = 4) in both variants, while the optimum 11 at
n = 4 is found by both CP-SAT variants (the unbroken model does not close the
bound within an hour; the broken one proves optimality in 109 s).

### Certificates

`verify_certificate.py` checks every point set three ways: an independent
pure-Python Laplace expansion of the raw 5×5 lifted matrix over every 5-subset,
the repository verifier `research/extremal/verifiers/no_five_on_sphere.py`, and
the hypergraph constraints.

### Layer enumeration (`layer_enum5.c`, n = 5)

A second, non-SAT decision procedure for k = 15. Every valid set S has at most
4 points per axis layer; a 15-set therefore meets all five z-layers, and at
least one axis's extreme layer holds ≥ 2 points (otherwise that axis's five
layers hold ≤ 14). Orient that extreme to z = 0 and quotient by the D4
stabiliser of the z-axis: layer 0 can be restricted to 1,905 canonical
candidates (subsets of [5]² of size ≤ 4 with no concyclic/collinear 4-subset —
11824 of the 12650 4-subsets qualify, confirmed by an independent Python count).
Layers 1–4 are then extended by DFS with a precomputed table SPH[T][layer] =
the grid points lying on the generalised sphere through each 4-subset T
(9.69 M entries, ~194 MB, self-tested against an independent det evaluator),
applying the implied constraints as point-forbidding masks, the size bounds
needed to reach 15, the z-flip prune |L4| ≤ |L0|, and canonical augmentation
under stab(L0) at each node. Exhaustion: 1905/1905 orbits, ~292 M extension
nodes, ~192 s wall — no 15-set exists.

Completeness argument: any 15-set S has an axis whose two extreme layers are
not both ≤ 1, hence an orientation with |L0| ≥ 2 and |L0| ≥ |L4|; a D4
element sends S's layer 0 to its orbit representative, and the recursive
extension enumerates every remaining layer set, so an isomorphic copy of S is
searched. The positive control (K = 14 finds a verified 14-set after 35
orbits) and the 826/11824 candidate cross-count are the independent checks;
the cube-and-conquer LRAT pipeline remains the planned fully-mechanical
corroboration.

