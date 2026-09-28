# Vertex-transitive search for a (3,10,40)-graph

On 2026-09-28, the search exhausted all 1,963 minimal transitive actions of
degree 40 supplied by GAP's TransGrp 3.6.5 catalogue. It found no triangle-free
graph with independence number at most 9. Every one of the 2,138,937 tested
orbit unions has a separately replayed independent set of size 10.

This excludes vertex-transitive witnesses, conditional on the published
transitive-group classification and the correctness of the enumeration. It
does **not** decide R(3,10), exclude asymmetric graphs, or establish that the
exclusion is new. The individual rejection witnesses are directly checkable;
the enumeration's completeness is supported by source review and exhaustive
small controls, not by a formal proof assistant.

## Why the search covers this class

For a triangle-free graph with independence number at most 9, every vertex
has degree at most 9: its neighbourhood is independent. In a graph of maximum
degree at most 3, repeatedly selecting a vertex and deleting its closed
neighbourhood yields an independent set of size at least ceil(40/4) = 10.
A vertex-transitive graph is regular, so only degrees 4 through 9 remain.

Every finite transitive permutation group contains a subgroup minimal with
respect to transitivity. Any vertex-transitive graph can therefore be
relabeled so that one of the catalogue's minimal transitive actions preserves
its edges. An invariant graph's edge set is a union of that action's orbits
on unordered vertex pairs. Enumerating all such unions covers the graphs in
question, with duplication allowed.

`orbits.py` obtains the pair orbits from explicit permutation generators.
`search.c` enumerates their unions with degree and triangle pruning. Its
independent-set search branches directly on vertices. A negative decision
includes a 10-vertex witness. `run.py` reconstructs each rejected graph from
its orbit selection and checks the witness by direct adjacency tests; it also
checks the record count, degree counts, and strict traversal ordering. A
positive decision is checked again by `checker.py`, which uses complement
colouring and a different search procedure.

The TransGrp importer parses a limited data grammar without executing GAP
code. It checks the complete degree-40 index range 1 through 315,842, all
selected IDs, permutations, transitivity, duplicate IDs, and the pinned
archive digest. The selected set has the 1,963 actions reported by Holt and
Royle. Matching a count alone would not establish catalogue completeness;
the coverage argument uses TransGrp's `MinimalTransitiveIndices` data and
the catalogue's published classification.

## Recorded result

| Degree | Triangle-free orbit unions | Replayed rejection witnesses |
| --- | ---: | ---: |
| 4 | 27,079 | 27,079 |
| 5 | 88,249 | 88,249 |
| 6 | 224,140 | 224,140 |
| 7 | 437,444 | 437,444 |
| 8 | 650,847 | 650,847 |
| 9 | 711,178 | 711,178 |
| Total | 2,138,937 | 2,138,937 |

These are labelled orbit unions counted once per action, not isomorphism
classes. All 1,963 actions reported exhaustion, with no timeout, node-limit
termination, or candidate. C search time totalled 2.028 CPU seconds. Import,
orbit construction, certificate replay, and repeated summary writes account
for most of the 338.644-second measured search wall time; C time alone is
not the total computational cost.

The canonical action-array SHA-256 is
`9c44acf28d3075aacc57b86809d61c86fa65c368ea20829a3fec96a1871663c5`.
The executed C binary SHA-256 is
`d37f2b6c9d2f76b2c318e777a7494f3aa651303539dd7f715cee443d1538a2b0`.
Compiler-dependent binary hashes are recorded for provenance, not required
to reproduce the mathematical result.

The same search also checked all four minimal actions of degree 39. Its
1,317 tested graphs in degrees 4 through 9 all had independent 10-sets.
The known 39-vertex Ramsey witnesses therefore require a different starting
class for extension. The same degree bounds apply, since ceil(39/4) = 10.
The order-40 conclusion does not depend on that auxiliary run.

## Earlier search audit

The earlier unpublished Cayley prototype selected representatives by
element-order profiles. An element-order profile is not a proof of group isomorphism, so
the earlier claim that 14 profiles established complete group coverage was
unsupported by that code alone. It also relied on an independence routine
without the present positive and exhaustive small controls.

The new Cayley control avoids that deduction. The Sylow 5-subgroup of a
group of order 40 is normal, and Schur-Zassenhaus supplies a complement of
order 8. `actions.py` constructs all homomorphisms from each of the five
groups of order 8 into Aut(C5) = C4. It retains all 28 resulting semidirect
presentations, including isomorphic duplicates. This covers every group of
order 40. All 9,034,972 tested triangle-free orbit unions in degrees 0 through
9 were rejected in the fresh run. That run did not retain individual
certificates; the stronger complete TransGrp run above supplies such
certificates and subsumes the Cayley exclusion.

Eight explicitly constructed nonregular actions contributed a separate
395-graph control, with all rejection witnesses replayed. Those eight
actions by themselves are not a census of non-Cayley graphs. A graph
invariant under a nonregular action can still be Cayley under another group.

## Reproduction

Dependencies are Python 3.10+ and a C11 compiler. There are no Python package
dependencies, GAP execution, provider credentials, or paid inference calls.
Obtain the public TransGrp 3.6.5 archive linked below through an authorized
download route. The importer requires exactly SHA-256
`6f2ec142a004f9d5e3b28bfa03246472fee93ceb12837206960bcb560eb72376`
(59,054,123 bytes), and reads its compressed data without extracting it.
The archive and generated records remain outside Git in ignored `runs/`.

From the repository root, using new output directories:

```sh
python3 -m unittest discover -s research/spikes/moonshot-r310/vertex_transitive -p 'test_*.py'
mkdir -p runs/moonshot-r310
clang -std=c11 -O2 -Wall -Wextra -Werror research/spikes/moonshot-r310/vertex_transitive/search.c -o runs/moonshot-r310/vt-search
python3 research/spikes/moonshot-r310/vertex_transitive/import_transgrp.py runs/moonshot-r310/dependencies/transgrp3.6.5.tar.gz --output runs/moonshot-r310/transgrp40-reproduction
python3 research/spikes/moonshot-r310/vertex_transitive/run.py --manifest runs/moonshot-r310/transgrp40-reproduction/actions.json --binary runs/moonshot-r310/vt-search --output runs/moonshot-r310/vt40-reproduction --min-degree 4 --max-degree 9 --target 10 --seconds 1 --node-limit 50000000 --wall-seconds 2100 --certificates
```

Observe the active host's required scheduling controls when running the full
reproduction. The driver enforces per-action CPU and node limits plus an
overall wall limit. An interrupted action never counts as an exclusion.
For a slower host, explicitly choose a larger bounded per-action allowance;
the driver accepts at most 300 CPU seconds per action. All output directories
must be new, so a rerun cannot overwrite earlier evidence.

The controls compare the independent-set checker with every labelled graph
on five vertices, compare complete small cyclic searches against direct
subset enumeration, check positive Ramsey graphs, compare C40 with direct
modular arithmetic, enumerate every homomorphism by an independent finite
reference, compare the eight selected nonregular actions against full Boolean
cubes, reject malformed input, and verify that interrupted searches remain
incomplete. The graph6 reader can inspect a separately obtained local graph
collection, but explicitly makes no catalogue-completeness inference.

## Sources and attribution

- Derek F. Holt and Gordon F. Royle, *A census of small transitive groups and
  vertex-transitive graphs*, [arXiv:1811.09015](https://arxiv.org/abs/1811.09015).
  Tables 1 and 2 report 315,842 transitive groups and 1,963 minimal transitive
  groups of degree 40.
- Alexander Hulpke and the TransGrp authors,
  [Transitive Groups Library](https://www.math.colostate.edu/~hulpke/transgrp/),
  [version 3.6.5 archive](https://www.math.colostate.edu/~hulpke/transgrp/transgrp3.6.5.tar.gz).
  Package licensing is Artistic-2.0 and GPL-2.0-only or GPL-3.0-only. The
  importer records the archive's license text with its private run evidence;
  this repository does not redistribute the catalogue.
- The dated [frontier review](../frontier-review-20260928.md) records the
  current Ramsey bounds and the limits of the publication-novelty check.
