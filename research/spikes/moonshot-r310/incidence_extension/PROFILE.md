# Six attachment columns over a fixed remainder

This experiment asks whether one specified 33-vertex graph H extends to a
maximal triangle-free graph G on 40 vertices with independence number at
most nine, minimum degree six, and a distinguished vertex of degree six.
An exclusion applies only to that input and those conditions. A graph
meeting the conditions would be a candidate for a new R(3,10) lower bound
after separate independent verification.

The initial experiment uses index 19 of the independently checked sample
of 128 remainders. Its adjacency SHA256 is
`159658dd5992a1c1ab00a12917328c9d216cd7ab99e4cc76d5b6d5c6a0ec0fb3`.
This is one of 15 inputs left unresolved by the accepted demand-cover
exclusions. The successful six-color demand check establishes compatible
independent endpoint sets; it does not establish an extension.

## Variables and graph conditions

Number the centre c as vertex zero, its six neighbours A as vertices one
through six, and H as vertices seven through 39. Fix every edge within H,
join c to all of A, and make A independent. The remaining edges are the
198 variables y[a,v], one for each attachment a in A and vertex v in H.
Column S_a consists of the vertices with y[a,v] true.

The initial formula imposes these conditions:

- Every column is independent in H. This prevents every possible triangle
  involving A; H itself is checked to be triangle-free.
- Every H vertex is covered, and
  `max(1, 6 - d_H(v)) <= sum_a y[a,v] <= 9 - d_H(v)`.
  The lower degree bound follows from minimum degree six. The upper bound
  follows because a vertex's neighbours are independent in a triangle-free
  graph. A degree-five H vertex may meet four attachments.
- Every column has size between five and eight. Its attachment has one
  additional neighbour c, and `{c} union S_a` is independent.
- Every column is maximal independent in H. For each v, its clause says
  `y[a,v] or any(y[a,w] for w in N_H(v))`. Thus every missing A-H edge has
  a common neighbour and cannot be added without a triangle.
- Every H nonedge whose ends have no common H neighbour has both ends in
  at least one column. Each possible attachment witness is an AND gate
  encoded by full equivalence.

Coverage handles the missing c-H edges, and c handles all A-A nonedges.
The last two conditions handle the remaining nonedges. Together they are
exactly maximality for this fixed layout. Minimality or a census of the
columns is not assumed. The eight-set upper bound for H is checked from
its raw adjacency with a finite independent-set search.

The degree-six condition is part of the target. Excluding a fixed H under
maximality does not exclude nonmaximal extensions of that H: completing
such a graph can change H or the centre's degree.

## Permutations and independence cuts

The only symmetry rule sorts adjacent columns lexicographically, with H
vertex zero as the first and most significant membership bit. Equal columns
are allowed. Permuting A preserves all graph conditions and all cuts, so
each admissible graph has a sorted representation. H vertices are never
permuted by this rule. Prefix-equality gates use full equivalence.

After a satisfying assignment, the program reconstructs all 40 adjacency
rows, checks the saved CNF model, and checks graph layout, degrees, triangles
and maximality. An independent-set search either proves that no ten-set
exists or returns one. A ten-set cannot contain c because H has independence
number at most eight. Let T be its H vertices. Then `4 <= |T| <= 8`.

For every subset B of A with `|B| = 10 - |T|`, add the clause

```text
OR(y[a,v] for a in B for v in T).
```

If all these incidences were absent, B together with T would be an
independent ten-set. The clauses therefore hold in every target graph.
Adding every B preserves attachment-label symmetry. Each cut saves T, the
rejected adjacency matrix, its six columns, and its independent ten-set.
Two implementations check this evidence before the cut is used.

The initial formula and any finite collection of these cuts are necessary
conditions. Unsatisfiability excludes the target for this H. Satisfiability
requires the full 40-vertex check; it does not itself establish a Ramsey
graph.

## Separate reconstruction and proof checking

`encode.py` produces the clauses. `audit.py` imports no encoding producer;
it reads the raw adjacency as a Boolean matrix and rebuilds the formula
with its own threshold counters, AND gates, prefix gates and cut checks.
The reconstructed DIMACS bytes must match the saved formula exactly.

Exploration writes no proof. If it finishes UNSAT, reconstruction must
pass before a separate proof-producing solve of the same CNF. That solve
uses CaDiCaL text LRAT with factoring disabled. A Python RUP checker and
`lrat-trim` must both validate the saved proof. The latter must exit 20 and
print `s VERIFIED`. An unsupported RAT step, changed artifact, incomplete
replay, or missing empty clause cannot support an exclusion.
Reconstruction and proof replay keep separate hash records, and both must
match the original CNF hash again at final acceptance.

Seven focused control groups precede any solve on index 19. They compare
the producer and reconstruction against 4,204 complete incidence assignments
on 20 tiny graph configurations, exhaust small cardinality and symmetry
relations, check a witnessed cut against all incidence patterns on its
subset, and reject malformed models, proofs, reviews and limits. They use
no solver subprocesses. The control report names the source hashes it tested.

## Input identities and finite limits

The run manifest fixes the raw-input acceptance record, its 128-graph result,
the independently accepted 15-case demand-coloring result, every source file
and dependency, and the Python, CaDiCaL and `lrat-trim` executables. An
independent source review must bind that manifest and those source hashes.
The program saves copies of these inputs and sources in a new output
directory. Solver environment overrides are rejected.

| Resource | Maximum for this pilot |
| --- | ---: |
| Inputs solved | One, index 19 |
| Aggregate CPU | 60 seconds |
| Elapsed time | 80 seconds |
| Child RSS threshold | 896 MiB |
| Driver RSS threshold | 96 MiB |
| Additional memory reserve | 32 MiB |
| Output files combined | 256 MiB |
| One proof | 128 MiB |
| One CNF | 2 MiB |
| Variables / clauses | 10,000 / 60,000 |
| Solver rounds / independent-subset cuts | 64 / 63 |
| Independent-set search nodes per call | 500,000 |

The shared CPU account includes controls, construction, all solver rounds,
all verification, and process-supervisor sampling. Each stage receives only
the remaining allowance after a five-second completion reserve. A child
also has a CPU limit and a per-file limit. RSS sampling is cooperative on
macOS; the report records its observations without treating an unsampled
short process as using zero memory. The supervisor signals and collects
only its own child. The combined disk check reserves space for the next
stage's log and proof before it starts.

Any resource limit or unfinished verification produces `unknown`. A locally
checked graph or exclusion is recorded as pending independent result review.
The driver never changes the accepted exclusion count or declares a new
Ramsey bound. The parent research task owns any later run or publication.
