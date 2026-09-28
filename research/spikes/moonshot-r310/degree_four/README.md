# A checked minimum-degree restriction for (3,10,40) graphs

Computational result, 2026-09-28. Every triangle-free graph on 40 vertices
with independence number at most nine has minimum degree at least five.
This restricts hypothetical Ramsey witnesses; it does **not** determine
whether any such graph exists or change the bounds 40 ≤ R(3,10) ≤ 41.
The proof uses the published uniqueness of the (3,9,35) graph and a finite
attachment problem verified by three separately implemented proof checkers.

The underlying neighborhood gluing method is established prior work.
No priority claim is made for this restriction. The bounded source review
found no degree-four exclusion for 40 vertices in the inspected 2013 and
2026 papers; that is not an exhaustive search of published or unpublished
computations. See the [frontier review](../frontier-review-20260928.md).

## Mathematical reduction

Let G be triangle-free, have 40 vertices, and have no independent set of
size ten. Every vertex has degree at most nine because its neighborhood is
independent. For any vertex v, its anti-neighborhood H = G − N[v] has no
independent nine-set: adding v would create an independent ten-set in G.
The known equality R(3,9) = 36 therefore forces deg(v) ≥ 4.

Suppose deg(v) = 4, with neighbors u₁,…,u₄. Then H has 35 vertices and is a
(3,9)-graph. Theorem 3 of
[Goedgebeur and Radziszowski (2013), EJC 20(1), P30](https://doi.org/10.37236/2824)
proves that this graph is unique up to isomorphism and is 8-regular. It is
the cyclic graph on Z/35 with differences ±{1,7,11,16}. Our representative
uses differences ±{8,12,14,17}; multiplication by 22 modulo 35 gives an
explicit isomorphism to the published representative.

Put Sᵢ = N(uᵢ) ∩ V(H). These sets are independent, since G has no triangle.
They are pairwise disjoint: each H-vertex already has eight neighbors in H
and can acquire at most one more in G. Conversely, any such four sets
determine a triangle-free extension by adding the independent vertices
u₁,…,u₄, their center v, and the specified attachment edges. No symmetry
of G or restriction on the placement of v is imposed.

Every independent set containing v has size at most 1 + α(H) = 9.
One omitting v and containing zero or one of the uᵢ also has size at most
nine. All remaining independent ten-sets are excluded exactly when:

- For each pair of uᵢ, their two attachment sets meet every independent
  eight-set of H.
- For each triple of uᵢ, their three attachment sets meet every independent
  seven-set of H.
- The union of all four attachment sets meets every independent six-set
  of H.

With variable xᵥᵢ meaning that vertex v belongs to Sᵢ, these are ordinary
positive clauses. Disjointness and independent attachment sets give binary
negative clauses. The resulting Boolean formula is equivalent to the
degree-four extension problem, not merely a collection of necessary tests.

## Exact instance and checked result

| Clause family | Number |
| --- | ---: |
| At most one attachment per H-vertex | 210 |
| Independent attachment sets | 560 |
| Cover 3,360 independent eight-sets for each of six pairs | 20,160 |
| Cover 13,760 independent seven-sets for each of four triples | 55,040 |
| Cover 22,995 independent six-sets | 22,995 |
| **Total** | **98,965** |

The instance has 140 variables, no auxiliary variables, and no symmetry
breaking. It contains no additional degree or cardinality assumptions.
An independently written audit checked the published graph isomorphism,
enumerated its independent sets, and matched every actual CNF clause
against the complete required set of 98,965 distinct clauses.

CaDiCaL 3.0.1 returned UNSAT in 30.517 CPU seconds and 39.999 wall seconds.
The run had a 60-second CPU limit, a 65-second wall limit, and a 256 MiB
per-file output limit. Its 20,723,074-byte textual LRAT proof contains
150,174 clause additions and 253,961 total lines.

Three implementations accepted the exact formula and proof:

1. `lrat.py`, a small independent semantic RUP checker, in 4.083 seconds.
2. A separate reviewer's set-based RUP replay, together with the exact CNF
   audit and source checks, in 3.744 seconds under `python3 -O`.
3. Armin Biere's established
   [lrat-trim](https://github.com/arminbiere/lrat-trim), version 0.2.0,
   commit `b30f400f4ee5c32b77ee566a7c006081b521534f`, in 0.132 seconds.
   `--no-trim` checked all 150,174 additions; it returned code 20 and
   `s VERIFIED`, using 38 MB of memory.

The local checker accepts only the RUP subset of textual LRAT. Negative
RAT hints and variables outside the input range are rejected. Each accepted
non-tautological clause is derived by unit propagation under its negation;
deletions only remove available clauses. Once a conflict has been proved,
unused remaining hints do not affect soundness. This is a semantic proof
check, not a certificate of strict LRAT grammar conformance. The established
checker supplies an additional independent implementation.

| Artifact | SHA-256 |
| --- | --- |
| DIMACS instance | `9891b6de6d529ce04ad69deb4f2936b1010dfd3f44efd84b05ae3ddf383cc81e` |
| Textual LRAT proof | `438b15ecf760a9afc17c5037d43ba9c9c96381971c9bc99f13a2ba42980767b4` |
| CaDiCaL binary used | `601c9fa8ba5d09fd81bb00c89b3e54832f138bccc3422bd8652e8cda4d74d1fa` |
| lrat-trim C source | `fdd3c1574ce2caef9e2ab2c08cd1919d7153f46682f9ed4c760706ab2bfc9944` |

The exact run remains in ignored `runs/moonshot-r310/degree-four-60s/`.
The release bundle preserves its formula, proof, portable receipt, source,
checker license and qualification evidence. Generated proof data are not
ordinary Git source files. Independent verification uses the saved proof;
it does not require trusting CaDiCaL or reproducing its search trajectory.

## Controls and reproduction

The seven automated controls compare fixed-size independent-set enumeration
against brute force for all 1,024 labeled graphs on five vertices; compare
the Boolean encoding against direct graph decisions for every small
attachment assignment, including overlapping sets; check the exact
35-vertex instance; exercise enumeration limits; and reject tampered or
incomplete proofs. Both small attachment families contain genuine SAT
examples. Separate live controls checked a CaDiCaL model for the five-cycle
and an emitted LRAT refutation. The established checker accepted a small
UNSAT proof, rejected that proof against a satisfiable altered formula,
and did not certify an empty proof.
The portable independent audit also rejected an empty proof and a substituted
CNF clause when their receipt hashes were consistently updated, under
`python3 -O`. Its verification therefore does not depend on assertions or
merely on stored hashes.

From the repository root:

```sh
python3 -m unittest discover -s research/spikes/moonshot-r310/degree_four -p 'test_*.py'
python3 research/spikes/moonshot-r310/degree_four/encode.py --output runs/moonshot-r310/degree-four-regenerated
shasum -a 256 runs/moonshot-r310/degree-four-regenerated/instance.cnf
python3 research/spikes/moonshot-r310/degree_four/lrat.py runs/moonshot-r310/degree-four-60s/instance.cnf runs/moonshot-r310/degree-four-60s/proof.lrat
python3 -O research/spikes/moonshot-r310/degree_four/independent_audit.py runs/moonshot-r310/degree-four-60s
```

The regenerated CNF must have the hash above. To perform a fresh bounded
solver run, with an approved installed CaDiCaL executable:

```sh
python3 research/spikes/moonshot-r310/degree_four/solve.py --solver /path/to/cadical --seconds 60 --checker-seconds 60 --output runs/moonshot-r310/degree-four-rerun
```

Each output directory must be new. A timeout or an unverified solver result
is recorded as incomplete, never as an exclusion. Different solver builds
may produce different valid proofs and runtimes for the same fixed formula.

The pinned established checker is a single C source file with an MIT
license. Its complete source and license are included with the evidence
bundle. Build and check from the extracted bundle root:

```sh
clang -std=c11 -O2 -Wall -Wextra third-party/lrat-trim/lrat-trim.c -o lrat-trim
./lrat-trim --no-trim evidence/instance.cnf evidence/proof.lrat
```

Success requires exit code 20 and `s VERIFIED`. Supplying the CNF is
essential: processing a proof without its formula is not this check.

## Remaining problem

All potential witnesses now have degrees between five and nine. The present
result has no claim about the degree-five case in arbitrary graphs.

An existence search can impose a stronger condition. Adding edges until a
triangle-free graph is maximal cannot increase its independence number.
Every two nonadjacent vertices of the resulting graph share a neighbor,
so it has diameter two. Theorem 3.6 of
[Pandey and Ravi (2026)](https://arxiv.org/html/2601.03572) gives minimum degree
at least six for these candidates. The following counting argument makes
the degree-five step explicit and corrects arithmetic errors in the preprint.

If v had five neighbors, each of the other 34 vertices would meet N(v).
There are at most 5 × 8 = 40 edges from N(v) to those vertices. Consequently
at least 2 × 34 − 40 = 28 of them meet N(v) exactly once. A neighbor of v
can have at most five such private neighbors: six of them together with
the other four members of N(v) would be independent. Thus there can be at
most 5 × 5 = 25, a contradiction. Degree four is already excluded here;
diameter two also excludes it by the elementary bound 1 + 4 + 4 × 8 < 40.

Accordingly, the next existence search starts with a saturated representative
of minimum degree at least six. This does not assert that every possible
witness already has minimum degree six, or that every such representative
has a vertex of degree exactly six. Degrees seven, eight and nine remain
separate cases. See the [current plan](../plan.md).
