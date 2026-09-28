# A finite exclusion for seven Ramsey remainders

An exhaustive neighbourhood-cover search excludes the covered degree-six
extensions defined below for all seven inputs. These inputs represent all
595 ways to delete two vertices from one verified 35-vertex Ramsey graph.
The search closes after 1,712 branch nodes, and a separately written
implementation reproduces every case, complete candidate inventory, and
node count.

All seven necessary-condition SAT formulas are also UNSAT. Every exact
CNF was independently reconstructed, and every retained LRAT certificate
passed both Python RUP replay and the pinned `lrat-trim` checker. The
covering exclusion and the proof certificates support the same finite
conclusion.

The [structural note](STRUCTURAL-NOTE.md) gives the mathematical reduction
and the checked computation. The [independent review](REVIEW.md) records
the independent reconstruction and reviewed source identities. This is a
finite exclusion within the stated family, with no claim of novelty or a
new bound on `R(3,10)`.

## Exact scope

Suppose `G` is triangle-free on 40 vertices, has minimum degree 6 and
independence number at most 9, and contains a degree-six vertex `c`. Write
`A=N(c)` and `H=G−({c}∪A)`. We impose two further conditions:

- `H` is an induced two-vertex deletion of the verified source graph below.
- Every vertex of `H` has a neighbour in `A`.

No such extension exists. The second condition is centre coverage. It
holds in every maximal triangle-free graph with the specified centre and
remainder, because an uncovered vertex would permit adding an edge to
the centre without creating a triangle. Other remainders, other possible
minimum degrees, and extensions lacking centre coverage are outside this
exclusion.

The source is the circulant on `Z/35` with differences `±{8,12,14,17}`.
Multiplication by 22 maps it to the representative `±{1,7,11,16}` in
Goedgebeur and Radziszowski,
[EJC 20(1), P30 (2013), Theorem 3](https://doi.org/10.37236/2824).
Construction rechecks its degree 8, triangle-freeness, absence of an
independent nine-set, and the map to the published labels.

The catalogue checks every proposed affine permutation against every
edge and nonedge. Exactly 210 permutations survive, with multipliers
`{1,11,16,19,24,34}`. Their orbits cover all 595 unordered deletion pairs:

| Case | Local deleted pair | Labelled pairs | Remainder edges | Eligible columns | Cover nodes |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | `(0,1)` | 105 | 124 | 1,416 | 300 |
| 1 | `(0,2)` | 105 | 124 | 1,332 | 244 |
| 2 | `(0,4)` | 105 | 124 | 1,023 | 114 |
| 3 | `(0,5)` | 105 | 124 | 1,300 | 235 |
| 4 | `(0,7)` | 35 | 124 | 1,427 | 314 |
| 5 | `(0,8)` | 105 | 125 | 1,236 | 261 |
| 6 | `(0,14)` | 35 | 125 | 1,222 | 244 |
| **Total** | | **595** | | | **1,712** |

All seven covering results are negative. The catalogue retains a checked
33-vertex isomorphism for every deletion pair. It does not need to identify
the full automorphism group or prove that the seven representatives are
pairwise nonisomorphic: redundant representatives cannot omit a case.

## Why this finite computation is sufficient

In any extension satisfying the conditions above, add allowed `A–H` edges
until each attachment set is maximal independent in `H`. This preserves
`H`, the centre, coverage, triangle-freeness, and the independence bound.
Every degree remains at most 9 because each neighbourhood is independent.
Complete enumeration shows that every maximal independent set of these
seven remainders has size 7 or 8.

The six attachment sets must be distinct. Each can contain at most four
vertices attached privately to its vertex of `A`; five private vertices
and the other five vertices of `A` would be independent. Centre coverage
and at most 48 attachment edges require at least 18 private vertices.
Two identical columns would leave only four columns able to have private
vertices, contributing at most 16, a contradiction.

Every internal-degree-eight vertex of `H` has exactly one attachment,
and each column contains at most four such vertices. Furthermore, the
union of any two columns must meet every independent eight-set of `H`.
The exhaustive search finds no selection of six eligible columns with
these necessary properties. Its additional valid capacity limits on
internal-degree-six and internal-degree-seven vertices are unnecessary:
an independent run omitting them gives the same seven negative results.

The search stores a complete branch tree. Replay recomputes candidates
from each selected path and checks every branch and terminal reason.
Small controls compare enumeration and search with exhaustive direct
checks, including cases that would fail under unsafe ordering shortcuts.
A separate implementation uses complement-clique enumeration and a
set-based covering search, sharing no imports with the research runtime.
Independent agent review checked the reduction, encodings, process
controls, and retained artifacts; this is computational review, not human
peer review.

## Reproduce the covering result

From the repository root, first run the focused controls:

```sh
python3 -m unittest discover \
  -s research/spikes/moonshot-r310/fixed_remainder \
  -p 'test_column_cover.py' -v
python3 -m unittest discover \
  -s research/spikes/moonshot-r310/fixed_remainder \
  -p 'test_independent_cover.py' -v
```

The [structural note](STRUCTURAL-NOTE.md#retained-run-and-reproduction)
provides the bounded command to reconstruct and replay all seven branch
trees. It uses 30 CPU seconds, 40 wall seconds, a 1 GiB memory threshold,
and a 16 MiB per-file limit, with a five-second cooperative budget per case.
The recorded run completed in 3.174 wall seconds, replayed all seven trees,
and collected its owned child. Its source snapshot, catalogue, branch
trees, hashes, and process receipt are retained together.

Follow the repository and host execution controls. If memory observation
is denied, preserve the stopped attempt and use the supported approval
route. A timeout, missing artifact, or unresolved case is not an exclusion.

## Additional SAT and LRAT confirmation

The [selector profile](SELECTOR-PROFILE.md) chooses six distinct eligible
columns, requires exact coverage of internal-degree-eight vertices, caps
the remaining rows, and excludes incompatible column pairs. Its seven
formulas have 31,230–42,209 variables and 550,012–1,080,366 clauses.
UNSAT proves failure of these necessary conditions. SAT produces only a
necessary cover, which still needs the remaining graph constraints.

One invocation attempts one case, with a new output directory:

```sh
python3 research/spikes/moonshot-r310/fixed_remainder/selector_run.py \
  --solver /path/to/installed/cadical \
  --lrat-trim /path/to/installed/lrat-trim \
  --case 0 --output runs/moonshot-r310/selector-case0
```

Add `--construct-only` to stop after construction. The limits are 60 CPU
seconds for construction and 90 CPU seconds each for solving, Python RUP
replay, and `lrat-trim`, with 30 extra wall seconds per stage. The explicit
proof profile permits at most 60,000 variables, 1,500,000 clauses, 32 MiB
of DIMACS and 256 MiB of textual LRAT. The memory threshold is 1 GiB.
Memory observation is cooperative on macOS; Linux also applies an
address-space limit. Every stage supervises and collects only its owned
child, and incomplete stages remain unresolved.

The runner records source and tool hashes, emits textual LRAT with
factoring disabled, and accepts UNSAT only after Python RUP replay and
`lrat-trim --no-trim` both pass. The second checker must return status 20
and print `s VERIFIED`. The exact constructed formula and its catalogue
premise also require independent review before a mathematical conclusion
is reported.

## Reproduce the released certificates

Download the archive and SHA-256 file from the
[fixed-remainder proof release](https://github.com/hraness/algal-lab/releases/tag/r310-fixed-remainder-proof-20260928).
Verify the published digest, extract the archive, and run:

```sh
cd r310-fixed-remainder-proof
python3 -B source/fixed_remainder/package.py verify . \
  --lrat-trim /path/to/verified/lrat-trim --output ../r310-replay
```

Use Python 3.11 or newer on Linux or macOS and a verified build of the
included pinned `lrat-trim` source. The bundle README documents a separate
C11 build under the host's native-build controls if needed. The verifier
does not launch a compiler. Its output directory must be new and outside
the extracted bundle. It verifies every manifest entry and records the
checker's version and executable identity, reconstructs all seven CNFs,
replays every proof with both checkers, verifies the catalogue and branch trees,
and repeats the separate finite cover calculation. It does not invoke
a SAT solver. All child stages have explicit CPU, wall, memory and file
limits; host execution controls still apply.

The successful result in the new directory's `verification.json` is
`all_seven_proofs_formulas_and_branch_evidence_replayed`. Failed or
interrupted stages remain incomplete. The archive includes both source
snapshots and preserves the original attempt records through explicit
public projections whose original digests are retained.

Case four originally failed the proof reader's one-million-byte line
limit. Its unchanged certificate has a 1,331,144-byte deletion record.
The reviewed update permits selector deletion records up to 2 MiB,
including their newline; all other bounds and proof rules remain in
force. The follow-up passed both checkers on those exact original bytes,
without a solver rerun. Its successful result is separate from the
preserved failed attempt. The command above uses the updated verifier;
the original source snapshot accurately retains the earlier limit.

Proof replay establishes UNSAT for each formula. The mathematical
reduction, verified catalogue maps and independent byte-for-byte formula
reconstruction connect those certificates to the stated finite family.

## Full attachment instrument and focused controls

`run.py` retains a full graph encoding with 198 attachment variables. It
requires degrees 6–9, centre coverage, triangle-freeness, and a covering
clause for every independent `(10-k)`-set of `H` and every `k`-subset of
`A`, for `k=1..6`. Its satisfying assignments are precisely the stated
extensions; a reported SAT graph also undergoes a direct graph audit.
The full graph encoding has not supplied the covering exclusion above.

The full-attachment controls check all 73,728 assignments over all 18
eligible labelled four-vertex remainders. Selector controls check all
96,000 assignments over 375 small formulas, compare all seven complete
column inventories with independent enumeration, and exercise actual
SAT/UNSAT runs through both proof checkers. Run the full focused suite
with the native and independent-evidence inputs enabled:

```sh
CADICAL_LIBRARY=/path/to/libcadical \
CADICAL_BINARY=/path/to/cadical \
LRAT_TRIM=/path/to/lrat-trim \
SELECTOR_INDEPENDENT_CENSUS=/path/to/independent-census.json \
python3 -m unittest discover \
  -s research/spikes/moonshot-r310/fixed_remainder -p 'test_*.py' -v
```

Missing optional inputs produce explicit skips. Those skips do not count
as completed verification.
