# A small obstruction for seven fixed Ramsey remainders

Checked finite computation, 2026-09-28.

None of the seven remainders considered here admits the covered degree-six
extension defined below. An exhaustive search over maximal independent sets
rejects all seven inputs after 1,712 branch nodes in total. A separately
written search reproduces every case and node count. These seven inputs
represent all 595 ways to delete two vertices from one verified 35-vertex
Ramsey graph.

This is a finite exclusion, not a new bound on R(3,10). It does not cover all
33-vertex Ramsey graphs, other possible minimum degrees, or degree-six
extensions without the stated coverage condition. No claim of novelty is
made; previous work has also used fixed-graph gluing searches.

## The target and the input family

Suppose G is triangle-free on 40 vertices, has independence number at most
9 and minimum degree 6, and has a vertex c of degree 6. Write A=N(c), so A
is an independent set of six vertices, and H=G−({c}∪A), with |H|=33.
We require every H-vertex to have a neighbour in A. This coverage condition
holds when G is maximal triangle-free: otherwise a missing edge c−v could
be added without making a triangle.

Here H is fixed to a two-vertex deletion of the graph on Z/35 with
differences ±{8,12,14,17}. Multiplication by 22 maps these local labels to
the published circulant with differences ±{1,7,11,16}. The source graph is
8-regular, triangle-free and has no independent nine-set. Its directly
verified affine automorphisms put the 595 deleted pairs into seven orbits.
See [the catalogue](catalogue.py) and
[the input-family derivation](../degree_six/ANALYTIC-NEXT.md).

The pair labels throughout this note use the **local** differences
±{8,12,14,17}. The affine quotient need not be the full isomorphism quotient;
retaining redundant cases cannot lose an input.

## Why maximal independent sets suffice

For a∈A, let S_a=N(a)∩H be its attachment column. It is independent in H.
Add any further A−H edge that creates no triangle, and continue until no
such edge remains. This preserves H, c and its six neighbours, coverage,
and the upper bound on the independence number. Minimum degrees do not
decrease. Every degree remains at most 9, since the neighbourhood of a
vertex in a triangle-free graph is independent.

In this saturated extension, every S_a is maximal independent in H. A
missing a−v edge can form a triangle only through an H-neighbour already
in S_a. Thus an extension, if one exists, has a representative in which
each column is one of the enumerated maximal independent sets. This
argument does not require adding any H−H edges.

All maximal independent sets of these seven H have size 7 or 8. This fact
was checked by two different complete enumerations: increasing-vertex
independent-set enumeration and maximal-clique enumeration in the
complement using the Bron–Kerbosch algorithm. The search retains columns
of sizes 5 through 8, as allowed by the target's degree bounds; the absence
of sizes 5 and 6 is an observed property of these inputs.

## Private vertices force six distinct columns

A vertex of H is private to a when its only A-neighbour is a. Let P_a be
this private set. It is independent, so |P_a|≤4: five such vertices together
with A−{a} would make an independent ten-set.

Let N_1 be the number of private H-vertices and let q be the number of
A−H edges. The six columns each have size at most 8, so q≤48. Coverage
of all 33 H-vertices gives

```text
q ≥ N_1 + 2(33 − N_1) = 66 − N_1,
and hence N_1 ≥ 18.
```

If two columns S_a and S_b were equal, both P_a and P_b would be empty.
The other four private sets contribute at most 16 vertices, contradicting
N_1≥18. Therefore all six columns are distinct. This proof is needed before
representing the problem with a simple compatibility graph; pair tests
alone would not rule out repeated columns.

## A necessary covering problem

Let D be the H-vertices of internal degree 8. Each has exactly one
A-neighbour: coverage requires at least one, and the degree-nine upper
bound permits at most one. Consequently D∩S_a consists of private vertices,
and every candidate column contains at most four D-vertices.

The retained columns must satisfy these conditions:

1. Select six distinct maximal independent sets of H.
2. Cover every vertex of D exactly once.
3. Use an internal-degree-seven vertex at most twice and an
   internal-degree-six vertex at most three times.
4. For any two selected columns, their union must meet every independent
   eight-set of H. Otherwise that eight-set and the two corresponding
   A-vertices form an independent ten-set.

Conditions 1–4 are necessary, not sufficient, for a Ramsey extension. They
are already inconsistent for every input here. The implementation also
checks full H-coverage and all private-set caps at a completed selection;
neither final check is reached in these seven searches. The independent
implementation omits those two final checks and obtains the same negative
result.

There are 18, 19 or 21 vertices in D. Thus at most one of the six selected
columns could miss D altogether: four columns containing at most four
D-vertices cannot cover even the smallest D. The implementation nevertheless
handles an arbitrary number of D-empty columns in its general small
controls, rather than relying on that shortcut.

## Counts and checked search results

An entry x/y in the middle columns means x sets of size 7 and y of size 8.
The eligible counts apply the additional restriction |S∩D|≤4.

| Deleted pair | e(H) | D vertices | All maximal sets, 7/8 | Eligible columns, 7/8 | Branch nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| (0,1) | 124 | 18 | 31/1,996 | 19/1,397 | 300 |
| (0,2) | 124 | 19 | 27/2,032 | 2/1,330 | 244 |
| (0,4) | 124 | 21 | 23/2,089 | 7/1,016 | 114 |
| (0,5) | 124 | 19 | 40/2,009 | 14/1,286 | 235 |
| (0,7) | 124 | 18 | 21/2,022 | 10/1,417 | 314 |
| (0,8) | 125 | 19 | 139/1,824 | 14/1,222 | 261 |
| (0,14) | 125 | 19 | 114/1,824 | 23/1,199 | 244 |
| **Total** | | | | | **1,712** |

All seven results are negative. No branch selects six columns; the deepest
selected paths have lengths 2, 3, 2, 2, 2, 3 and 2 respectively. Ordinary
six-cliques in the pair-compatibility graph do exist for all seven inputs,
so pair compatibility by itself is insufficient. Covering D exactly once
supplies an additional obstruction. An independent ablation removed the
capacity limits on internal-degree-six and internal-degree-seven vertices
and obtained the same seven negative results and node counts. Those two
limits are valid but unnecessary for this finite exclusion.

## How the exhaustive search is checked

[column_cover.py](column_cover.py) selects an uncovered D-vertex with the
fewest available columns, then branches on **every** column containing it.
Any valid exact cover has exactly one of those columns, making the pivot
complete. A new column removes pair-incompatible columns and columns that
would exceed a saturated row's capacity. There is no ascending column-index
restriction. Such a restriction after an adaptive pivot could silently
discard valid covers. Once D is covered, explicit branches handle any
remaining D-empty columns.

Each negative result includes a branch tree. Its replay recomputes every
available column directly from the selected path, without trusting the
search's incremental candidate updates. An omitted column must be already
selected, pair-incompatible, or prohibited by a row capacity. The replay
checks every pivot option, every child, every terminal reason, and the
absence of cyclic or unreachable nodes.

[test_column_cover.py](test_column_cover.py) contains eight passing controls:

- Maximal-set enumeration agrees with direct subset inspection for all
  1,099 simple graphs on one through five vertices.
- Cover search agrees with direct subset selection for 1,143 small column
  problems, plus 200 fixed-seed cases with compatibility edges, private
  caps and optional full coverage.
- Explicit positive cases require a lower column index after a higher one
  and require more than one D-empty completion column.
- Replay rejects omitted branches or candidates, unjustified candidates
  and terminal reasons, cyclic branches, and unreachable nodes.
- Node limits return an incomplete computation, never a negative result.

A separate implementation constructed H from the published circulant,
used complement-clique enumeration and a set-based covering search, and
reproduced the seven candidate inventories and branch counts. This is
independent computational review, not human peer review.

## Retained run and reproduction

The recorded run is under the ignored directory
`runs/moonshot-r310/fixed-column-cover-20260928-r2/`. It contains the source
snapshot, the complete 595-pair catalogue with induced isomorphisms, seven
case files with branch trees, a summary, and the process record. Generated
runs remain outside Git.

The supervisor allowed 30 CPU seconds and 40 wall seconds for the whole
seven-case command, with a 1 GiB memory threshold and 16 MiB per-file limit.
Each case also had a five-second cooperative CPU budget. The run completed
in 3.174 wall seconds; child CPU time including the memory sampler was
3.191 seconds, and the maximum sampled RSS was 35,799,040 bytes. Exit status
was zero, all seven trees replayed, and the owned child was collected.
An earlier attempt stopped when the sandbox prevented its memory monitor
from running; that attempt produced no mathematical result.

| Retained object | SHA-256 |
| --- | --- |
| `column_cover.py` | `cb0db18c850c63e32d206a07af614fa833ba649d5905a034ef7be3e8af1b94d4` |
| `test_column_cover.py` | `f9c12832467d8b7bfc8897bf6507076612c5081fcd1f1383921c279976b138f5` |
| `evidence/summary.json` | `4a2449e3906dc465f25e31c1d36d1b09b96ec8a7d7c7acaf0591b0c0d1e52b41` |
| `evidence/catalogue.json` | `edc0608bfe564c6c2919dab99fe75afda73d4cb4a92febd1a70e532be3f58cc5` |
| `process.json` | `c0f341519820da26b82dbf69741c50359046c643e76110b00f067ecac3d37962` |

From this directory, run the focused controls with:

```sh
python3 -m unittest -v test_column_cover.py
```

The following invokes the existing process supervisor and requires a new
output directory. The supervisor must be able to inspect its own child;
if the host denies that operation, retain the stopped attempt and use the
host's supported approval route.

```sh
python3 - <<'PY'
from pathlib import Path
import sys
from process import run_process

output = Path('../../../../runs/moonshot-r310/column-cover-reproduction').resolve()
output.mkdir(parents=True, exist_ok=False)
result = run_process(
    [sys.executable, 'column_cover.py', '--output', str(output / 'evidence'), '--seconds', '5'],
    output / 'run.log', output / 'process.json',
    cpu_seconds=30, wall_seconds=40, memory_mib=1024, file_bytes=16 * 1024**2,
)
print(result)
if result['returncode'] != 0 or result['external_stop'] is not None:
    raise SystemExit('The supervised computation did not complete.')
PY
```

The resulting summary must report all selected cases as negative, and each
case file must report a successful replay. A stopped run, a necessary
cover found by the relaxation, or a receipt without the underlying
mathematical checks would not establish this exclusion.
