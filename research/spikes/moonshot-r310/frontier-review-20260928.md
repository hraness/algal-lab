# R(3,10): frontier and next exact target

Agent review, 2026-09-28. This is a research plan and source audit, not a new
Ramsey bound or a claim of exhaustive literature coverage. No researcher was
contacted. The vertex-transitive census has its own implementation owner.

## Verified frontier and existing work

The best bound verified in primary text is **40 ≤ R(3,10) ≤ 41**.
[Angeltveit, EJC 32(4), P4.30 (2025)](https://arxiv.org/html/2401.00392v2),
Theorem 1.1, establishes the upper bound; Exoo's 1989 graph on 39 vertices
establishes the lower bound. Section 7 reports **43,146,537** known
(3,10,39) graphs after combining collections, including **43,117,868**
supplied by Goedgebeur and Radziszowski. Vertex deletion followed by all
one-point extensions was already used. Ordinary extension of these known
graphs is a control, not a new research strategy. The approximately
**150 billion** intermediate graphs in that proof were **(3,8)** graphs,
not (3,9) graphs.

[Pandey and Ravi, January 2026](https://arxiv.org/html/2601.03572), Section 3,
studies hypothetical (3,10,40) graphs and leaves minimum degree at least four.
Its abstract retains the obsolete upper bound 42; the introduction and
Authors' Note acknowledge Angeltveit's 41 bound. Use the latter statements.
A fresh arXiv search found this as the newest relevant indexed result, but
the capture was marked partial. No stronger bound was found; the search
does not certify the absence of a later result.

The existing lab plan already records circulant and Cayley exclusions and
prior extension searches. This review did not repeat their computations or
the running 1,963-action vertex-transitive census.

## Available source graphs

- [Exoo's author-hosted catalogue](https://cs.indstate.edu/ge/RAMSEY/) links
  the original [39-vertex matrix](https://cs.indstate.edu/ge/RAMSEY/r3.10.39).
  This is a useful independent positive control, not a new construction.
- [McKay's current catalogue](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html)
  states that the (3,9,35) graph is unique and links its
  [graph6 data](https://users.cecs.anu.edu.au/~bdm/data/r39_35.g6).
- Pandey–Ravi Lemma 1.2 explicitly states both uniqueness and 8-regularity,
  citing Theorem 3 of
  [Goedgebeur–Radziszowski (2013)](https://arxiv.org/abs/1210.5826).
  The [full original journal PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i1p30/pdf)
  was retrieved and its relevant statements checked today. Theorem 3, page 12,
  proves uniqueness and 8-regularity and identifies the cyclic graph with
  distances `{1,7,11,16}`, first found by Kalbfleisch in 1966. The lab's recovered
  distances `{8,12,14,17}` describe the same graph after multiplying labels
  by 22 modulo 35.

An independent agent decoded the pinned public mirror's 102-byte graph6
object using a separate parser and enumerated its independent sets directly.
The graph has 35 vertices, 140 edges, degree eight everywhere, no triangles
and independence number eight. The counts for sizes 0 through 9 are
`[1,35,455,2905,10150,20265,22995,13760,3360,0]`.
The bytes have SHA-256
`7f8d273023c1c2b5026627b3e69f7429b3e2995b9f54f9f6409141726adb1c50`.
The mirror is
[`LinXueyuanStdio/RamseyGraph`, commit `c36f59c1e4884d304e143ba62325930fc40c2b0e`](https://github.com/LinXueyuanStdio/RamseyGraph/blob/c36f59c1e4884d304e143ba62325930fc40c2b0e/raw_data/r39_35.g6),
Git blob `1d6472fd6906ea3f9828bcc2ebc406d4fe30341a`.
The independent enumeration took 0.027 seconds; this was a small input audit,
not a duplicate run of the main search.

## Next target: rule out a degree-four vertex

The construction below specializes the neighborhood gluing extension method
of Goedgebeur–Radziszowski, Section 3, pages 6–9; the method itself is not new.
Their Theorem 4, page 13, excludes this 35-vertex anti-neighborhood for
**42-vertex** candidates, whose expansion vertex has degree six. It does not
state the proposed degree-four exclusion on 40 vertices. Section 6, page 15,
reports unsuccessful attempts to construct a 40-vertex graph without claiming
that all degree-four candidates were excluded. No such exclusion was found
in the inspected 2013 and 2026 texts.

Let G be a (3,10,40) graph and v have four neighbors u₁,…,u₄. Then
H = G − N[v] is a (3,9,35) graph: an independent nine-set in H together with
v would be forbidden. Thus H is the unique 8-regular graph above.

Write Sᵢ = N(uᵢ) ∩ V(H). These four sets are independent, by triangle-freeness,
and pairwise disjoint: every H-vertex already has degree eight, while every
degree in G is at most nine because neighborhoods are independent. Each
|Sᵢ| ≤ 6; otherwise seven members of Sᵢ together with the other three uⱼ
would form an independent ten-set. No symmetry of G is assumed.

For these disjoint independent sets, the following conditions are
**necessary and sufficient** to exclude independent ten-sets in G:

- Every independent eight-set of H intersects at least three of the Sᵢ.
- Every independent seven-set of H intersects at least two of the Sᵢ.
- Every independent six-set of H intersects at least one of the Sᵢ.

Indeed, a forbidden set omitting v uses k = 2, 3, or 4 of its neighbors and
10 − k vertices of H, so its H-part misses at least k attachment sets. The
three conditions exclude exactly these cases. Sets containing v have size
at most 1 + α(H) = 9; those using zero or one uᵢ also have size at most nine.
Triangle-freeness follows from the independent Sᵢ. This gives 140 Boolean
attachment variables before auxiliary cardinality variables.

An optional pruning condition is |Sᵢ| + |Sⱼ| ≥ 10 for i ≠ j. Otherwise deleting
N[uᵢ] ∪ N[uⱼ] leaves at least 28 vertices, hence an independent eight-set by
R(3,8) = 28, which combines with uᵢ and uⱼ. Together with |Sᵢ| ≤ 6, this forces
all four sizes to be five or six, or the pattern (4,6,6,6). Their sum lies in
20…24. The initial encoding can omit this pruning for a simpler audit.

## Evidence required before claiming a result

Verify the source graph's bytes, order, degrees, triangle-freeness and
independence number. Record and independently check exhaustive counts of its
independent six-, seven- and eight-sets. Validate any SAT witness with an
independent graph checker. For UNSAT, require a proof-producing solver and
an independent proof checker, with the exact instance and proof retained.

A positive witness would prove R(3,10) = 41. A checked negative result would
prove minimum degree at least five for every (3,10,40) graph, without a
symmetry restriction. **Novelty remains provisional** beyond the inspected
2013 and 2026 papers: this bounded search does not establish priority against
all published or unpublished computational work. The 2026 paper's weaker
stated bound alone does not establish priority. Use the existing research
time budget and host scheduling requirements.
