# Independent review of the fixed-remainder experiment

Agent review, 2026-09-28. This records source review and independent
mathematical reproduction. It is not human peer review, a priority claim,
or a new Ramsey bound.

## Findings and scope

No blocker was found in the reviewed full-attachment encoding, its bounded
runner, or the necessary-column search. A separate implementation also
finds no six-column cover for all seven remainders. That independent search
uses a weaker relaxation: it omits coverage of the lower-degree rows and
the final cap on all private attachment classes.

The resulting finite exclusion concerns centre-covered extensions with a
degree-six centre and one of these pair-deletion remainders. In particular,
it includes maximal triangle-free graphs with such a centre and remainder.
It does not classify other 33-vertex remainders, unsaturated extensions
without centre coverage, or graphs of other minimum degrees. The separate
selector CNF has also passed source review. All seven exact real-case
formulas passed independent byte reconstruction, and every retained
UNSAT certificate passed both the independent Python RUP checker and
the pinned `lrat-trim` implementation. One case required a reviewed,
selector-only deletion-record limit correction; its original failed
attempt remains intact beside fresh successful replay receipts.

## Mathematical reduction

Write the graph as a centre, its six independent neighbours `A`, and the
fixed 33-vertex graph `H`. Every triangle-free graph with independence
number at most nine has maximum degree at most nine. Consequently an
internal-degree-eight vertex of `H` has exactly one attachment under centre
coverage, and other rows have capacity `9-d_H(v)`.

Each attachment column can be enlarged to a maximal independent set of
`H` by adding allowed `A–H` edges. This preserves `H`, the centre's degree,
triangle-freeness, the independence bound, minimum degree, and coverage.
Maximum degree nine then follows again from the independence bound. This
is an existence-preserving reduction, not a claim that every initial
extension already has maximal columns.

All maximal independent sets of these seven `H` have size seven or eight.
Every independent eight-set is therefore among the enumerated maximal
sets. An attachment column contains at most four private vertices: five
private vertices together with the five other vertices of `A` would be an
independent ten-set. In particular it contains at most four degree-eight
vertices of `H`.

The columns are distinct. Duplicate columns would each have no private
vertex, so the four other columns could account for at most sixteen
private vertices. There are at least eighteen degree-eight vertices in
each remainder, all private by exact coverage, giving a contradiction.
This shorter argument agrees with the alternative bound
`N_1 >= 66-c >= 18` from coverage and at most 48 attachment edges.

For two selected columns `S,T`, an independent eight-set disjoint from
both, together with their two vertices of `A`, would be independent of
size ten. The pair-compatibility test is therefore necessary. Exact
coverage of degree-eight rows, upper row capacities, this pair condition,
and six distinct eligible columns are necessary conditions. Failure of
these weaker conditions suffices for the stated finite exclusion.

## Search completeness

`column_cover.py` enumerates independent sets in increasing vertex order
and retains a set precisely when its closed neighbourhood covers every
vertex. Each maximal independent set appears once. The independent
implementation in `independent_cover.py` instead uses pivoted
Bron–Kerbosch on the complement and shares no imports with the research
runtime.

The production cover search branches on an uncovered degree-eight row
and retains every compatible column that covers it. It applies no global
increasing-index restriction after choosing a dynamic pivot. Such a
restriction would be unsound. Columns avoiding all degree-eight rows can
be postponed until those rows are covered: all current constraints are
invariant under column order and only remove options as columns are
selected. Both implementations support general completion with several
such columns, even though the production counts permit at most one.

The production search removes a column exactly when it is already
selected, conflicts with a selected column, or touches a saturated row.
Its negative-tree replay independently recomputes eligibility from the
entire selected path and checks every option, terminal reason, and child.
It rejects missing, duplicate, cyclic, and unreachable tree nodes.

## Independent reproduction

The independent implementation constructs the published circulant with
differences `±{1,7,11,16}` and transports its matrix using multiplication
by 22 into the local labeling. The following pairs use local labels.

| Deleted pair | Maximal sets of size 7 / 8 | Eligible columns | Columns missing all degree-eight rows | Cover nodes |
| --- | ---: | ---: | ---: | ---: |
| `(0,1)` | 31 / 1,996 | 1,416 | 36 | 300 |
| `(0,2)` | 27 / 2,032 | 1,332 | 18 | 244 |
| `(0,4)` | 23 / 2,089 | 1,023 | 6 | 114 |
| `(0,5)` | 40 / 2,009 | 1,300 | 18 | 235 |
| `(0,7)` | 21 / 2,022 | 1,427 | 54 | 314 |
| `(0,8)` | 139 / 1,824 | 1,236 | 18 | 261 |
| `(0,14)` | 114 / 1,824 | 1,222 | 18 | 244 |

All seven searches completed with no necessary cover. The preserved run
used Python 3.14.6, took 2.236 CPU seconds, and had cooperative limits of
25 CPU seconds, 40 wall seconds, and one million nodes per enumeration
or cover search. The command-line process also had CPU limits of 29/30
seconds and a four-MiB output-file limit.

```sh
python3 research/spikes/moonshot-r310/fixed_remainder/independent_cover.py \
  --output runs/moonshot-r310/fixed-remainder-independent-cover-20260928.json
```

The output must be new. Its SHA-256 was
`37b942ab60909b3f089983d317353f70c83424b4bd9b681f98252c7adbab4eae`.
It records graph and sorted-column inventory hashes for comparison with
the other implementation. Generated run files remain outside Git.

The production archive at
`runs/moonshot-r310/fixed-column-cover-20260928-r2/evidence/` contains all
seven problem instances and negative branch trees, its source snapshot,
and a catalogue. Its summary SHA-256 is
`4a2449e3906dc465f25e31c1d36d1b09b96ec8a7d7c7acaf0591b0c0d1e52b41`.
Independent readback checked every source and artifact hash, reconstructed
every adjacency matrix, and compared the complete maximal-set, eligible
column, and independent-eight-set inventories. Every compatibility bit
and row capacity agreed with direct independent reconstruction. This took
2.081 CPU seconds under a 29/30-second process CPU limit. The 1,712 tree
nodes reach maximum selected-column depths `2,3,2,2,2,3,2`; the owner's
replay passed for every tree.

Eight production-search controls passed, including all 1,099 simple
graphs through order five, all 1,143 small column/slot/capacity combinations,
200 deterministic random constraint combinations, and adversarial tree
mutations. The recorded supervised run used 3.174 wall seconds, 3.191
child CPU seconds including memory sampling, and 35.8 MB sampled peak
memory. Its 30-CPU-second / 40-wall-second / one-GiB limits were respected
and its child was collected.

An additional bounded ablation set every non-degree-eight row's capacity
to six, retained the same columns, exact degree-eight coverage and pair
compatibility, and called the independent `exact_cover` implementation.
All seven results remained negative with exactly the same node counts.
The run took 0.936 CPU seconds; every case had a three-CPU-second /
100,000-node bound inside a 29/30-second process limit. Its record is
`runs/moonshot-r310/fixed-remainder-cap-ablation-20260928.json`.
Thus the lower-degree row capacities are unnecessary for this particular
obstruction. The other reductions and the finite-family scope still apply.

Five independent controls passed in 0.023 seconds:

```sh
python3 -m unittest discover \
  -s research/spikes/moonshot-r310/fixed_remainder \
  -p test_independent_cover.py -v
```

They compare maximal-set enumeration against all subsets of every
four-vertex graph; compare 160 small cover instances against every column
subset; retain a witness needing decreasing column indices after a dynamic
pivot; complete a witness with multiple zero-required-row columns; and
verify that exhaustion of a bound raises an unresolved result rather than
returning an exclusion.

## Full-attachment instrument

The full-attachment formula has exactly one variable for each possible
`H–A` edge plus cardinality auxiliaries. Negative binary clauses exclude
triangles, and every independent `(10-k)`-set of `H` is paired with every
`k`-subset of `A`, for all `k=1..6`. These clauses cover every possible
independent ten-set omitting the centre. A centre-containing set is
excluded by the independently checked `alpha(H)<=8`. The formula has no
unsafe relabeling restriction or unproved maximal-column assumption.

The implementation owner reported twelve controls passing in 3.828
seconds, including all 73,728 attachment assignments over all eighteen
eligible labelled four-vertex remainders. The actual SAT/UNSAT control was
rerun successfully in 0.342 seconds after result-metadata clarification.
The reviewed tests also exercise proof/model tampering, interrupted
construction, exact-child interruption and collection, memory observation
failure, wall expiry, and forced collection of an unresponsive child.
These results were inspected rather than duplicated without cause.

The runner snapshots its source, uses one owned child per stage, leaves
timeouts unresolved, and audits an actual SAT graph independently of the
CNF. The RUP proof reader checks the archived formula rather than trusting
a solver exit code. A large-instance negative conclusion still requires
review of its exact formula and replay of its retained proof, including
an established independent checker. No full-attachment 40-vertex case was
run by this reviewer.

## Necessary-column selector instrument

`selector.py`, `selector_proof.py`, `selector_run.py`, and their controls
were independently read after stabilization. No blocker was found for a
bounded real-case attempt. The selector independently enumerates every
independent set of sizes zero through eight, retains the maximal ones,
checks the observed size-seven/eight property, and records sorted
inventory hashes. It chooses six distinct eligible columns, constrains
degree-eight rows to exact coverage, caps other rows, and forbids pairs
whose union misses an independent eight-set. These are precisely the
necessary conditions above, omitting full coverage of the lower-degree
rows and the final private-class cap.

Its separate proof profile allows at most 60,000 variables, 1,500,000
clauses, and 32 MiB of DIMACS. It does not raise the original attachment
proof reader's limits. Both readers use the reviewed independent RUP
checker, and the selector also requires the established `lrat-trim`
checker to exit with code 20 and an explicit `s VERIFIED` line. Each
checker has its own bounded process stage. A SAT result is checked against
every archived clause and directly against the selection conditions,
then reported as a necessary cover, never as a Ramsey graph.

The implementation owner reported all eight focused selector controls
passing in 2.070 seconds with the actual CaDiCaL library, solver, and
`lrat-trim` enabled. The controls exhaust all 96,000 selector assignments
over 375 small formulas, compare all seven real-case maximal-set and
eligible-column hashes with the independent reproduction, reject invalid
profiles and tampered proofs, and run actual positive and negative
end-to-end controls. All owned children were collected. These focused
results were inspected rather than needlessly rerun.

The seven archived formulas at
`runs/moonshot-r310/fixed-remainder-selector-case{0..6}-20260928/` were
then reconstructed independently. The audit derives H from the published
circulant, re-enumerates all maximal independent sets with the separate
Bron–Kerbosch implementation, and reconstructs the canonical threshold
counters and every independent-eight-set pair clause without importing
the selector or attachment encoder. It also exhaustively checks the
sixteen Boolean assignments for the threshold-cell identity. Every
complete DIMACS file matched byte for byte, covering 264,236 variables
and 6,118,685 clauses across the seven formulas.

The first case-zero audit took 0.716 CPU seconds. After making the auditor
portable, all seven audits together took 4.790 CPU seconds; each had a
19/20-second process limit and a 15-second cooperative CPU budget. The
read-only script is retained at
`runs/moonshot-r310/independent-selector-formula-audit.py`. It takes a
case directory and an optional `--independent-source` path to the pinned
`independent_cover.py`; by default it uses the case's source snapshot.
It refuses Python optimization and emits no private absolute paths.

## Retained selector certificates

| Case | Deleted local pair | Variables | Clauses | Verified RUP additions |
| ---: | --- | ---: | ---: | ---: |
| 0 | `(0,1)` | 41,671 | 1,061,033 | 52,553 |
| 1 | `(0,2)` | 39,688 | 937,386 | 35,694 |
| 2 | `(0,4)` | 31,230 | 550,012 | 22,367 |
| 3 | `(0,5)` | 38,642 | 895,064 | 51,590 |
| 4 | `(0,7)` | 42,209 | 1,080,366 | 58,595 |
| 5 | `(0,8)` | 35,654 | 805,904 | 31,093 |
| 6 | `(0,14)` | 35,142 | 788,920 | 28,059 |

Independent readback checked every original source and artifact hash,
all per-stage log hashes, each exact-child collection receipt, both
available proof-result bindings, and the recorded solver/checker
identities. Cases 0, 1, 2, 3, 5 and 6 originally completed both proof
checks. Case 4 correctly remained `selector_unsat_unverified`: one LRAT
deletion record at line 67,617 was 1,331,144 bytes, exceeding the original
one-million-character input guard. The old result was not promoted or
rewritten. The readback record is
`runs/moonshot-r310/independent-selector-artifact-readback-20260928.json`,
SHA-256 `7c61ffed8842e240843b1b1478a5c028227da2aed5a462a92dfba602e4b4d18b`.
It includes all seven complete CNF and proof digests.

The reviewed repair changes only the selector proof profile. A bounded
binary read permits at most two MiB for a numeric-ID deletion record;
ordinary records retain the one-million-byte limit. Both a preliminary
file-size check and cumulative input accounting retain the 256-MiB total
bound. The CNF reader and original attachment proof reader are unchanged,
as are all semantic RUP and deletion checks. Four focused controls passed
in 0.024 seconds with this command from `fixed_remainder/`:

```sh
python3 -m unittest -v test_selector.SelectorProofControls
```

Those controls accept the exact boundary, reject one additional byte,
reject oversized ordinary/comment records and malformed deletion
terminators, retain the total-file limit, and verify that the original
reader still rejects the larger deletion record. The source and controls
were independently read before the real proof was replayed.

The fresh replay at
`runs/moonshot-r310/fixed-remainder-selector-case4-replay-20260928/`
binds the repaired source to the original CNF and proof digests:

```text
CNF   ea78f3ce5571944380011c8b79c24f6b67fdb6bb25b96c4e486d7736801cf4ad
proof 5113aa3ba973dd0d5e86e1e276bb455fee48ccd64a78d4141c4e996b4e42e559
```

The independent Python checker verified all 58,595 additions and the
empty clause in 4.121 child CPU seconds. The pinned `lrat-trim` returned
20 with `s VERIFIED` in 0.195 child CPU seconds. Both CPU measurements
include the exact-child RSS sampler. The stages used 30/35 and 15/20
CPU/wall-second bounds respectively, with one-GiB sampled memory limits;
the highest observed RSS was 307,085,312 bytes. Both children were
collected and neither stage had an external stop. Original and replayed
certificate bytes, source snapshots, and the original failed result were
checked again after verification. No solver was rerun. The fresh result
SHA-256 is
`4154563772f3aed969e54544a2479155349a376a00caa534122b4a02f13fa6b8`.

These certificates verify the necessary selector formulas. Combined with
the checked orbit coverage, maximal-set inventories and mathematical
reduction, they establish the finite-family exclusion stated above.
They do not supply a Ramsey graph, a complete 33-vertex remainder census,
or a new bound on `R(3,10)`.

## Reviewed source identities

Paths below are relative to `research/spikes/moonshot-r310/`. New source
or dependencies require a corresponding review update; these hashes do
not substitute for the repository's final integration checks.

```text
fixed_remainder/catalogue.py 36cd3106076dbd9abd06fe7687f085bb7391745fa9be64c7b625ce1f6497b3bf
fixed_remainder/encode.py e2b2a24e014e7bc3390053a3b86fdb65f37e88b075457b4c88157ebb67b284c1
fixed_remainder/shared.py 122fd7b2457517e0bdbb8b961cebb2333c2f52a215394fbf2bdd3b841a8b330a
fixed_remainder/process.py 72f269e0506a2ea57bb3f73d2ae622aeb51470410ce4319de8586fe410bbbc76
fixed_remainder/proof.py fe9926768991bf4b9bf6788b75eba4aba9726cce192b76c07443dc8f56470c10
fixed_remainder/run.py befd7acecff740aa1357bb9a59b266bd7a3a7913580819e3b6a09c19269c27f6
fixed_remainder/test_fixed.py 3d2fb6e4d34870885b2984a826344563ba0cba4d40f47bf4e15428ff11c9fb4c
fixed_remainder/test_process.py 7900c097e4216858c24a770fb6f30c70470296d062566b996f634057ccbf0a58
fixed_remainder/column_cover.py cb0db18c850c63e32d206a07af614fa833ba649d5905a034ef7be3e8af1b94d4
fixed_remainder/test_column_cover.py f9c12832467d8b7bfc8897bf6507076612c5081fcd1f1383921c279976b138f5
fixed_remainder/independent_cover.py 700e185c0c9b6cc6786faebbafccb90e7b341741083327a021dccaf74b210e44
fixed_remainder/test_independent_cover.py b6dcdab2355bcf6632e18f590387628cb76501c01c4dc8a562a49f2e61575da5
fixed_remainder/selector.py 4ca818c9aac0ea55393e43e32d4a7295ab7b8561a1256a8bda181075aee24091
fixed_remainder/selector_proof.py e1305057f7413a73816df6ccf9e5041511e5ce73e45c5b469205e160417f1df6
fixed_remainder/selector_run.py e668e198cb3e7d7212a03a1f72c7251f766e08ac6ec5aac52bcaecedc7e551d3
fixed_remainder/test_selector.py 56dc59df689a0260974d6310a684703be31e5c557f45080e12d028d1c93c802b
degree_six/encoding.py 525808c8cb36924c35b5c35cc47055a11976dc20465a22b4be04c921edc6545b
degree_six/native.py 6581f3ab805375de34e83236459363d00d98af3ee75401be97ad083fd8958777
degree_four/lrat.py 8db2970f7a97494c605cadd53f6b5b417ccad1974f58c296d175e086b857ff4a
vertex_transitive/checker.py aecfd40ba0e6cda88b72a66c8c03431e1d07301fc4f1665739b7f8e2c0ac5bf1
```

The original seven run snapshots retain the earlier selector reader
`1892433aa5c8b35141b61ec75ab2a1b5e3d39611687e9357fefc8795bce3dd3f`
and tests
`0916f73b31e11ce817d58cb21a1fd73aa5d2dd6517201297560335f1e31fba39`.
Those identities describe the six initially successful certificates and
the preserved case-four failure; the fresh case-four replay uses the
repaired identities listed above.
