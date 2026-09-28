# Nine finite certificates for degree-six extensions

These certificates rule out nine specified 33-vertex graphs as the exact
remainder `H = G − N[c]` of a maximal triangle-free graph G with a degree-six
vertex c. They do not establish a global Ramsey bound or exhaust a graph
catalogue. A nonmaximal extension can acquire edges inside H when saturated,
changing its remainder, so it is not excluded by these certificates.

The complete inputs are in [certificates.json](certificates.json). Each
graph is supplied as 33 integer adjacency masks; bit v of row u records
the edge uv. The local class labels identify this finite sample. They are
not catalogue indices. The file also gives a small selected demand set P
and an integer attachment-capacity bound M for each graph.

Independent source and data review is recorded in [REVIEW.md](REVIEW.md).

| Local class | H edges | Selected demands | Capacity bound M | Six-set capacity |
|---|---|---|---|---|
| 0 | 118 | 26 | 4 | 24 |
| 1 | 119 | 15 | 2 | 12 |
| 2 | 119 | 16 | 2 | 12 |
| 3 | 119 | 14 | 2 | 12 |
| 4 | 118 | 26 | 4 | 24 |
| 5 | 120 | 8 | 1 | 6 |
| 6 | 119 | 27 | 3 | 18 |
| 7 | 120 | 14 | 2 | 12 |
| 8 | 120 | 7 | 1 | 6 |

## Why the certificates work

A demand is a pair of nonadjacent H vertices with no common neighbour in H.
Since G is maximal triangle-free, every missing edge of G has a common
neighbour. For a demand uv, that neighbour must lie in `A = N(c)`: neither
c nor any H vertex can supply it. Thus the six sets `N(a) ∩ H`, for a in A,
must collectively contain both endpoints of every selected demand.
Each attachment set is independent because G is triangle-free.

The certificate proves that an independent H-set contains at most M selected
demands. To check this, take **every subset of M+1 selected demands** and
form the union of its endpoints. Each union must contain an H edge. If an
independent set contained M+1 demands, their entire endpoint union would be
independent, contradicting that check. No maximal-independent-set enumeration
or numerical optimization is needed to verify this argument.

The six attachment sets can therefore cover at most 6M selected demands,
including any overlaps. Every row in the table has `|P| > 6M`, giving the
required contradiction. The argument permits repeated attachment sets and
does not require a minimum-degree or independence-number premise.

## Reproduce the verification

Use Python 3.10 or newer. No packages, network access, credentials, SAT
solver, or SciPy installation are required.

```sh
python3 research/spikes/moonshot-r310/demand_certificates/verify.py
python3 -m unittest discover -s research/spikes/moonshot-r310/demand_certificates -p 'test_verify.py' -v
```

The verifier checks the file format, exact graph order, integer masks,
symmetry, absence of loops and triangles, and each labelled adjacency hash.
Every selected demand must be distinct, nonadjacent in H, and have no common
H-neighbour. It then checks the strict covering inequality and all endpoint
unions. Successful output lists each exact adjacency hash and the scope of
its conclusion. The nine certificates require **150,902 endpoint-union
checks**, with a fixed total allowance of 200,000 and a ten-CPU-second limit.
A limit produces `unknown`, never a verified certificate.

The controls compare the subset test against direct independent-set
enumeration on all 75 simple labelled graphs through order four. They also
check a six-cycle, altered capacities, equality in the covering inequality,
false demand pairs, duplicate pairs, malformed graphs, altered identities,
unknown fields, nonfinite/duplicate JSON values, and exhausted limits.

## Provenance and scope

The raw adjacencies are the nine representatives from the original finite
pruning sample. Classes 0, 4, and 6 use all common-neighbour demands. The
other six use demand subsets selected from independently checked numerical
proposals. Although an LP helped find those subsets, every final coefficient
is zero or one and the proof verification above uses only exact integers.

The fixture retains SHA-256 identifiers for the source census and proposal
records. Those identifiers preserve provenance; the verifier's mathematical
conclusion depends on the full graphs and selected demand pairs supplied
here. It does not depend on trusting an LP answer or obtaining another file.
The earlier source records, partial SAT proof streams, and inconclusive SAT
results remain unchanged. A later, separately checked counting certificate
does not convert an unfinished SAT run into a completed proof.

These are finite certificates for the stated exact remainders, with no claim
of catalogue completeness or mathematical novelty. In particular, the
sample covers only two of the five published 118-edge classes mentioned
in the research record; the other classes require their own analysis.
