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
