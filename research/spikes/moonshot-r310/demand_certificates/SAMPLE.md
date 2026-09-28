# Degree-six obstructions for 113 sampled remainders

The expanded certificate file excludes **113 of 128 specified 33-vertex
graphs** as exact remainders `H = G − N[c]` of a maximal triangle-free graph
G with a degree-six vertex c. Fifteen sampled graphs remain unresolved by
these certificates. This is a finite-sample result, with no claim of a new
Ramsey bound, a complete graph catalogue, or mathematical novelty.

[sampled-certificates.json](sampled-certificates.json) contains all 128
graphs, 113 integer certificates, and the 15 remaining sample indices.
The graph identities are complete labelled adjacency arrays: bit v in
row u records the edge uv. Each array also has a SHA-256 identifier. Sample
indices identify these exact inputs; they are not catalogue indices.

## What changed from the nine-case version

The [original nine certificates](README.md), their data and their verifier
remain unchanged. Matching the full graph bytes places original classes
0–8 at sample indices 0–8. Those nine cases are included in the total of
113, rather than counted twice.

The expanded result combines three disjoint sets of sample indices:

| Certificate source | Excluded sample graphs |
|---|---:|
| Unit-weight demand screen | 15 |
| Original weighted selections outside those 15 | 6 |
| New weighted selections | 92 |
| Total | 113 |

Ninety-six certificates use only weight one. The remaining seventeen use
positive integer weights no larger than three. Every capacity bound is at
most four. Zero-weight demands are omitted from the compact file.

The remaining sample indices are:

`19, 22, 25, 31, 43, 52, 57, 72, 92, 98, 100, 103, 106, 108, 119`.

No certificate here excludes those fifteen graphs. Their lack of a
certificate does not establish a maximal extension or rule out another
weighted obstruction.

## Why integer weights give a proof

A demand is a nonadjacent pair of H vertices with no common neighbour in H.
In a maximal triangle-free extension, both endpoints of each demand must
belong to some independent attachment set `N(a) ∩ H`, where a is one of the
six neighbours of c. Give each selected demand a positive integer weight.
If every independent H-set contains demands of total weight at most M,
the six attachment sets can collectively cover total weight at most 6M.
Every certificate has total selected weight strictly greater than 6M.

The verifier proves the capacity bound without enumerating maximal
independent sets. It examines every inclusion-minimal subset of selected
demands whose weight is greater than M. Each subset's endpoint union must
contain an H edge. If an independent H-set had weight greater than M, it
would contain one of these subsets, whose endpoints would also be
independent—a contradiction.

For positive integer weights, a minimal overweight subset has at most M+1
members. It is minimal exactly when its total weight minus its smallest
weight is at most M. Thus the check is a finite enumeration of small demand
subsets. When all weights are one, it reduces to the original test of every
M+1 demands.

## Reproduce the verification

Use Python 3.10 or newer. The verifier uses only the standard library and
the unchanged `verify.py` in this directory. It needs no numerical package,
SAT solver, census file, network connection or credentials.

```sh
python3 research/spikes/moonshot-r310/demand_certificates/verify_sample.py
python3 -m unittest discover -s research/spikes/moonshot-r310/demand_certificates -p 'test_verify_sample.py' -v
```

The checker validates every graph, exact adjacency identity, sample index,
demand, integer weight and strict covering inequality. It rejects duplicate
labelled graph bytes and requires the certified and remaining indices to
partition the 128 inputs. The 113 proofs require **311,618 endpoint-union
checks** after considering 366,225 demand combinations. A shared allowance
of 500,000 combinations and ten CPU seconds bounds verification. Exceeding either limit returns
`unknown`, never a verified result.

The controls compare weighted capacities with direct independent-set
enumeration on all 75 labelled simple graphs through order four, with three
weight patterns per graph. They include a weighted six-cycle, a single
demand heavier than the alleged capacity, equality in the covering
inequality, zero weights, altered fields and identities, duplicate graphs,
incorrect sample partitions and exhausted limits. They also check the
original nine graphs and certificates against their unchanged files.

## Scope and provenance

Each proof concerns the exact induced H supplied in the file. Saturating
a nonmaximal extension may add edges inside H and change that remainder;
these certificates do not exclude such an extension. They do not require
a minimum-degree premise, an independence-number bound or distinct
attachment sets.

The fixture records hashes of the input sample, proposal records and
independent mathematical reviews. Those records helped find and check the
certificates. Replaying the proof depends only on the explicit graphs,
demands and integer weights supplied here. Neither floating-point
optimality nor the discovery method is part of the proof.

The earlier incomplete SAT runs remain inconclusive. A later counting
certificate does not complete a stopped SAT proof. The sample also does
not exhaust the published graph classes relevant to the Ramsey problem.
