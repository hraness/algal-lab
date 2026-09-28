# R(3,10): frontier, certified case, and search restrictions

Agent review, 2026-09-28. This is a research note and source audit, not a new
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
studies hypothetical (3,10,40) graphs and leaves the unrestricted minimum
degree at least four. Its Theorem 3.6 gives the stronger bound six when the
diameter is two; the argument can be checked directly as explained below.
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

## Completed target: rule out a degree-four vertex

The construction below specializes the neighborhood gluing extension method
of Goedgebeur–Radziszowski, Section 3, pages 6–9; the method itself is not new.
Their Theorem 4, page 13, excludes this 35-vertex anti-neighborhood for
**42-vertex** candidates, whose expansion vertex has degree six. It does not
state the degree-four exclusion on 40 vertices. Section 6, page 15,
reports unsuccessful attempts to construct a 40-vertex graph without claiming
that all degree-four candidates were excluded. Angeltveit (2025), Section 3.3,
also reports gluing the unique 35-vertex graph, in a calculation whose target
has 41 vertices. Section 6 reports unsuccessful extensions of many 38-vertex
graphs to 40 vertices, without stating a complete exclusion of this case.
No explicit unrestricted degree-four exclusion was found in these three texts.

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
Triangle-freeness follows from the independent Sᵢ. The completed encoding uses
140 Boolean attachment variables and no auxiliary or symmetry variables.

An optional pruning condition is |Sᵢ| + |Sⱼ| ≥ 10 for i ≠ j. Otherwise deleting
N[uᵢ] ∪ N[uⱼ] leaves at least 28 vertices, hence an independent eight-set by
R(3,8) = 28, which combines with uᵢ and uⱼ. Together with |Sᵢ| ≤ 6, this forces
all four sizes to be five or six, or the pattern (4,6,6,6). Their sum lies in
20…24. The initial encoding can omit this pruning for a simpler audit.

The known small-graph edge bounds further reduce the possible size patterns.
Write r = Σ|Sᵢ|, so e(G) = 144 + r. For a neighbor uᵢ with |Sᵢ| = s, every
vertex in Sᵢ has total degree nine, and deleting N[uᵢ] removes exactly 4 + 9s
edges. The values e(3,9,34) = 129 and e(3,9,33) = 118 in the 2013 paper's
Table 4 exclude s = 4 and require r ≥ 23 when s = 5. Thus only
`(5,6,6,6)` and `(6,6,6,6)` survive these edge counts, giving 167 or 168 edges.
The bound e(3,10,40) ≥ 161 in its Table 5, repeated in the 2026 paper's
Section 3, does not itself contradict these cases.

## Completed certificate checks

The degree-four formula has 98,965 clauses. A proof-producing solver returned
UNSAT, and three implementations checked the certificate: the lab's RUP
checker, a separately authored independent audit, and the established
`lrat-trim` 0.2.0 checker. The independent audit also reconstructed the base
graph from the published distances, enumerated the independent sets, and
checked exact equality between the required constraints and the actual CNF.
It verified all 150,174 proof additions and the empty clause. This proves that
every (3,10,40) graph, if one exists, has minimum degree at least five, using
the cited classification of the 35-vertex anti-neighborhood.

The independently authored [portable audit](degree_four/independent_audit.py)
does not import the encoder or its proof checker. It accepts one run-directory
argument and does not require the original repository path or solver binary.
A complete replay passed under `python3 -O`; tampering controls with consistently
updated hashes still rejected both an empty proof and a substituted CNF clause.

- CNF SHA-256: `9891b6de6d529ce04ad69deb4f2936b1010dfd3f44efd84b05ae3ddf383cc81e`.
- Proof SHA-256: `438b15ecf760a9afc17c5037d43ba9c9c96381971c9bc99f13a2ba42980767b4`.

This is a structural restriction, not a determination of R(3,10). **Novelty
remains provisional**: this bounded source audit does not establish priority
against all published or unpublished computational work. Neither the 2026
paper's weaker unrestricted bound nor an unsuccessful web search establishes
priority.

## Saturation makes degree-five enumeration unnecessary for existence

Any triangle-free graph can be extended, on the same vertices, to a graph
maximal under adding edges while preserving triangle-freeness. Adding edges
cannot increase its independence number. In the resulting graph every
nonadjacent pair has a common neighbor, since otherwise their edge could be
added. Thus any 40-vertex witness can be saturated to diameter two.

The diameter-two minimum-degree bound in Pandey–Ravi Theorem 3.6 has an
elementary proof that also resolves arithmetic slips in its printed argument.
Let v have degree d, put A = N(v), and let H contain the n − d − 1 remaining
vertices in a triangle-free graph with independence number less than k.
Every vertex of H meets A. Each vertex of A has at most k − 2 neighbors in H,
so c = e(A,H) ≤ d(k − 2). Let p count vertices of H meeting exactly one member
of A. Then c ≥ 2(n − d − 1) − p. For any u in A, its private neighbors in H,
together with A minus u, form an independent set. Consequently u has at most
k − d private neighbors, and p ≤ d(k − d). Combining these bounds gives

    2(n − 1) ≤ d(2k − d).

With n = 40 and k = 10, every degree is at most nine and this inequality forces
d ≥ 6. Explicitly, for d = 5 the cross-edge upper bound is 40, so at least
28 of the 34 outside vertices would have to meet A exactly once. But the five
members of A can have at most five private neighbors each, allowing only 25.
The contradiction does not require a census of (3,9,34) graphs.

This is a lossless restriction for an **existence search** after saturation.
It does not prove that every unsaturated candidate already has minimum degree
six. A search may therefore focus on maximal triangle-free 40-vertex graphs
with degrees six through nine, while keeping the separate nine-regular case.

## Related SAT work inspected on 2026-09-28

The official [IJCAI 2025 proceedings page](https://www.ijcai.org/proceedings/2025/292)
for Li, Duggan, Bright and Ganesh, *Verified Certificates via SAT and Computer
Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems*, reports checked
SAT+CAS certificates and a cube-and-conquer extension. Its abstract reports
59 hours for R(3,8), or 11 hours with the colors reversed, while its SAT-only
CaDiCaL comparison timed out after seven days. This is a concrete warning
that a short direct-SAT pilot is only a feasibility experiment. The abstract
does not address the degree-six (3,10,40) case; the full paper was not
inspected in this pass.

The [SAT Modulo Symmetries documentation](https://sat-modulo-symmetries.readthedocs.io/en/latest/)
describes graph generation modulo isomorphisms, custom graph constraints,
and co-certificate learning. Those established techniques should be compared
before attributing originality to a graph-SAT implementation or a lazy
independent-set exclusion loop.

The official [abstract of Przybocki, Mackey, Heule and Subercaseaux (2026)](https://arxiv.org/abs/2604.21187)
reports a SAT/LLM study of doubly saturated Ramsey graphs and formally checked
infinite families. It is relevant methodological precedent. The full-text
extraction was unusable, so this review makes no claim about its detailed
encodings or whether it treats the current degree-six case. No specific
earlier SAT treatment of that case was established by this bounded pass.

## Requirements for further computational claims

Verify the source graph's bytes, order, degrees, triangle-freeness and
independence number. Record and independently check exhaustive counts of its
independent six-, seven- and eight-sets. Validate any SAT witness with an
independent graph checker. For UNSAT, require a proof-producing solver and
an independent proof checker, with the exact instance and proof retained.

A positive 40-vertex witness would prove R(3,10) = 41. Any further negative
claim must specify the full class covered and preserve a checkable certificate
or an equally explicit completeness argument. Use the existing research time
budget and host scheduling requirements.
