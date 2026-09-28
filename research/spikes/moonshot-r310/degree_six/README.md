# A bounded degree-six SAT pilot

This experiment searches for a triangle-free graph on 40 vertices with no
independent ten-set, a vertex of degree six, and all degrees between six
and nine. It assumes no graph automorphism. The baseline stopped at 100,000
cuts after 6,251 models, using 281.690 CPU seconds and 376.928 wall seconds.
Its final model still has an independent ten-set. No witness was found;
the Ramsey number remains open.

## Exact scope

If a Ramsey witness exists, adding edges until it is maximal triangle-free
cannot increase its independence number. Such a graph has diameter two.
The credited counting argument in the [plan](../plan.md) shows that its
minimum degree is at least six; the usual independent-neighborhood argument
gives maximum degree at most nine. The cases of minimum degree seven, eight
and nine remain separate and are not covered by this pilot.

For the degree-six case, choose such a vertex and relabel it 0 and its
neighbors 1 through 6. Every other vertex meets this neighborhood, since
the graph has diameter two. This fixes labels without losing any graph in
that case. The default baseline adds no further ordering rule.
We omit the remaining diameter-two constraints initially. Omitting a
necessary condition enlarges the family and cannot remove a real witness.

The optional [stronger profile](PROFILE.md) orders outside-neighborhood
signatures and adds published and derived edge bounds. Its complete
initial formula has 17,933 variables and 78,702 clauses. Its completeness
arguments, source, exact costs and controls are documented separately.
The baseline formula and structural metadata are preserved unchanged.

The initial formula has 780 edge variables, 13,800 auxiliary variables,
and 63,272 clauses:

| Constraint | Clauses |
| --- | ---: |
| No triangle, for every vertex triple | 9,880 |
| The fixed neighborhood of vertex 0 | 39 |
| Every outside vertex meets that neighborhood | 33 |
| Every degree lies in 6 through 9 | 53,320 |

The degree encoding uses unary prefix counters. A cell means that at least
j of the first i incident edges are present. Each cell is equivalent to
the previous cell in its column or the current edge together with the
previous cell in the preceding column. Full equivalence makes both the
lower and upper degree bound exact.

## Incremental constraints and acceptance

CaDiCaL proposes a graph satisfying the constraints accumulated so far.
A separate [graph checker](../vertex_transitive/checker.py) verifies its
structure and searches exactly for an independent ten-set. Each such set
adds the 45-literal clause saying that at least one of its pairs is an edge.
Every clause is required of every Ramsey witness, so counterexample-based
selection cannot discard a real witness. A second bounded enumeration
collects up to 256 such sets per model and checks every one before use.
That enumeration never certifies the absence of a set.

A graph is accepted as a candidate only when the exact checker finishes
without finding an independent ten-set. Satisfying the current partial
formula is insufficient. Interrupted graph checks preserve the last model
and report an unresolved result. Any candidate still receives an independent
review before a claim about R(3,10).

An incremental UNSAT result is labelled `unverified_unsat`. It needs a fresh,
proof-producing solve of the saved final CNF and an independent proof check
before supporting any exclusion. The driver does not turn an unchecked
negative result into a theorem. Even a checked negative result would cover
only the degree-six family above.

## Resource and evidence limits

Each reported run used one solver thread, a 600 CPU-second budget, a 660-second
supervisor wall limit, at most 20,000 models and 100,000 independent-set cuts.
Search stops cooperatively at 590 process CPU seconds, leaving time to save
results; the worker also has a 595-second operating-system CPU limit. Its
1 GiB peak-memory threshold is checked cooperatively, not an operating-system
hard memory cap. Files have a 256 MiB operating-system size limit. Exact
graph checks have their own two-second and one-million-node limits.

The supervisor owns the worker it starts and terminates only that process.
SIGINT and SIGTERM stop and collect that worker, save an unresolved result
and the complete recorded formula, and preserve the signal in the exit code.
It saves a formula containing all complete recorded cut batches even after
an interrupted worker. Such a final batch might not all have reached the
solver; every included clause is still valid for the target problem.
An incomplete log line is discarded and disclosed. Normal exits preserve
the precise complete input. Formula, cut log, local solver library and
source hashes are recorded, along with models, time, memory and stop reason.
All generated files remain in ignored `runs/`.

No new package or network service is needed. `native.py` links an existing
installed CaDiCaL static library into a local shared library. `native.py`
uses the published C/IPASIR interface and preserves solver learning between
rounds. This initial implementation does not perform dynamic isomorphism
rejection or use a graph-specialized propagator.

## Prior work and expected difficulty

This is not a new SAT method. In particular,
[Li, Duggan, Bright and Ganesh, IJCAI 2025](https://www.ijcai.org/proceedings/2025/292)
report SAT plus computer-algebra certificates for R(3,8) and R(3,9), with
plain CaDiCaL timing out after seven days on their R(3,8) comparison.
[SAT Modulo Symmetries](https://sat-modulo-symmetries.readthedocs.io/en/latest/)
already supports graph generation and learning from counterexamples.
The [dated frontier review](../frontier-review-20260928.md) records what was
inspected and the limits of that comparison.

A ten-minute trial measures whether this simple formulation reaches useful
models and how quickly its independent-set constraints accumulate. There
is no expectation that a brief negative search decides the Ramsey number.

## Controls and commands

The focused controls exhaust 2,815 cardinality assignments through six
inputs, compare structural formulas against all labelled graphs on five
vertices, compare batched independent sets against all those graphs, recover
small Ramsey witnesses, and check the known 35-vertex graph. A fixed six-cycle
must produce independent-set clauses and then an explicitly unverified UNSAT.
Stops and partial-formula models must never be reported as witnesses.
The independent review adds controls for native interruption and callback
failure, an interrupted exact graph check, real SIGINT/SIGTERM delivery to
the supervisor, forced child cleanup, and recovery of a truncated cut log.
See [the review record](REVIEW.md) for the baseline inspection and results.
The stronger profile adds exhaustive ordering and edge-bound controls and
an isolated source-copy run. The implementation suite passed 26 tests;
three additional checks passed in the [independent profile review](PROFILE-REVIEW.md).

With an already installed static library, use local paths for the following:

```sh
python3 research/spikes/moonshot-r310/degree_six/native.py /path/to/libcadical.a runs/moonshot-r310/native-cadical
CADICAL_LIBRARY=/path/to/linked/libcadical.dylib python3 -m unittest discover -s research/spikes/moonshot-r310/degree_six -p 'test_*.py' -v
python3 research/spikes/moonshot-r310/degree_six/run.py --library /path/to/linked/libcadical.dylib --output runs/moonshot-r310/degree-six-pilot --seconds 600
```

Use `.so` on a supported Linux installation; its static library must be
built with position-independent code (`./configure -fPIC` for CaDiCaL).
CI builds release 3.0.1 at commit
`c60730422e758ef1cebe7aeddf2dda31c996bf04` and runs all native controls.
Without `CADICAL_LIBRARY`, unittest reports those controls as skipped.
Follow the repository's host scheduler when one is installed.

Both long runs and their post-run checks are complete. Each stopped at
100,000 cuts after 6,251 models; neither supplies a witness or exclusion.
See [the results](RESULTS.md) for resource use, retained hashes and explicit
independent ten-sets in the final models.
