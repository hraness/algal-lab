# Moonshot: a 40-vertex (3,10) Ramsey graph

Status: chosen 2026-09-27, not started. Time-boxed with a stopping rule.

## Target

A triangle-free graph on 40 vertices with independence number at most 9. One
such graph proves R(3,10) = 41. The bounds are 40 ≤ R(3,10) ≤ 41: the lower
bound is Exoo's 39-vertex graph (1989), the upper bound is Angeltveit,
"R(3,10) <= 41", Electron. J. Combin. 32(4) P4.30 (2025), arXiv:2401.00392.
R(3,10) and R(4,6) are the smallest unknown classical Ramsey numbers.

## Why this one

- A single object decides it, and anyone can check it.
- It has not been swept by the recent CP-SAT and agent wave. The alternative
  we considered, 2n-point no-three-in-line sets, was pushed to every n ≤ 60 in
  2026 (arXiv:2602.07751), and the no-five-on-a-sphere records are crowded.

## Honest odds

Low, likely a few percent at most. Angeltveit's partial census holds tens of
millions of (3,10,39)-graphs, and his one-point extension checks found no
40-vertex graph. He calls R(3,10) = 40 the obvious conjecture, while noting he
is not confident in it because the 39-vertex class is so large. A 40-vertex
graph, if one exists, would have to avoid everything those checks covered.

## Literature pass (done 2026-09-27)

- Bounds: 40 <= R(3,10) <= 41. Upper bound is Angeltveit (arXiv:2401.00392,
  EJC 32(4) 2025): ~150 billion (3,9)-graphs enumerated, ~3 CPU-years, no
  (3,10,41)-graph found. Lower bound is Exoo's (3,10,39)-graph (1989).
- Failed searches already in the record: 37M+ (3,10,39)-graphs with
  161 <= e <= 175 (Goedgebeur/Radziszowski catalog ~50M colorings) do not
  extend to a (3,10,40)-graph; a simulated-annealing run found 810 pairwise
  non-isomorphic colorings of K_40 with exactly ONE monochromatic triangle
  (Exoo et al., "On Some Small Classical Ramsey Numbers"). So a 40-vertex
  graph, if it exists, is outside all generated 39-vertex classes.
- Structural constraints on a hypothetical (3,10,40)-graph Omega
  (arXiv:2601.03572 sec.3): Delta = 9; delta >= 4; e >= 161; no vertex has
  two neighbours with degree sum <= 11; for any v and v1,v2 in N(v),
  |N(v1) u N(v2)| >= 11; diam(Omega) in {2,3}; if 9-regular then diam = 2;
  a degree-4 vertex has |Omega_2(v)| in [19,24], |Omega_3(v)| in [11,17].
- No published exhaustive symmetry-class search of (3,10,40)-graphs was
  found: circulants on Z_40, Cayley graphs on the groups of order 40, and
  vertex-transitive graphs on 40 vertices are not known to be excluded.
  Circulants are ~2^20 distance sets, enumerable in minutes; the
  vertex-transitive census at order 40 is available (Holt/Royle) and can be
  filtered directly.
- Assessment unchanged: the obvious conjecture is R(3,10) = 40, and finding
  a 40-vertex witness is a needle in a space already probed heuristically.
  The search proceeds under the existing time box; circulants/Cayley/VT
  classes first because they are cheap and independently checkable.

## Log

- 2026-09-27, circulants (`circulants.py`): every circulant on Z_40 of
  degree <= 9 checked exhaustively (10,072 candidates; degree > 9 is
  impossible since a vertex's neighbourhood is an independent set and
  alpha <= 9). 2,921 are triangle-free; none has alpha <= 9. No circulant
  (3,10,40)-graph exists — unconditional, no e-value bound needed. Likely
  folklore; we found no published exclusion.
- 2026-09-28, Cayley (`cayley/`): all 14 groups of order 40 enumerated as
  C5 ⋊ P (normal C5 by Sylow; split by Schur-Zassenhaus; P ranging over
  the five groups of order 8, all homs into Aut(C5)=C4; deduped by
  element-order profile — 14 distinct profiles = the full census).
  Every inverse-closed connection set of size <= 9 enumerated with
  incremental triangle-free pruning (`cayley40.c`); alpha computed exactly
  by Tomita max-clique on the complement. ~2.1 M triangle-free connection
  sets tested in seconds; ZERO hits. C40 count (2,921 tf sets)
  cross-checked against circulants.py; group tables verified independently
  (associativity, C5 normality, order profiles).
  **No Cayley graph on any group of order 40 witnesses R(3,10) >= 41.**

## Approach

1. Literature pass: which symmetry classes of (3,10,40)-graphs are already
   excluded (circulants, Cayley graphs on groups of order 40, graphs with an
   automorphism of prime order p).
2. Exhaustive search within classes not yet excluded, using orbit matrices,
   with triangle-freeness checked on orbit representatives and independence
   number by exact clique search in the complement.
3. Any hit ships with its adjacency list and a checker written independently of
   the search.

## Time box and stopping rule

- At most 72 CPU-hours on this machine after the C(6) run finishes, and at most
  two agent sessions.
- Stop when the time box runs out or the declared classes are exhausted.
- If step 1 shows those classes were already searched, switch to a shortlist of
  open problems from erdosproblems.com that reduce to finite search, under the
  same time box.
- Report exhausted classes as a certified negative result only if no one has
  published them.
