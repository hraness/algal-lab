# Independent enumeration of sphere-and-plane-free grid sets

`independent_enum.c` is a separate, bounded decision procedure for the existence
of a K-point subset of {0, …, n−1}³, for 1 ≤ n ≤ 6, with
no five points on a common sphere or plane. It uses an independent determinant
oracle and does not load `layer_enum5.c`'s precomputed masks or use its recursive
symmetry reductions. A partial run does not establish an upper bound.

## Reproduction

```sh
cc -O3 -std=c11 -Wall -Wextra -Werror independent_enum.c -o /tmp/independent-enum
python3 -m unittest -v test_independent_enum.py
/tmp/independent-enum --n 3 --target 8 --seconds 30
/tmp/independent-enum --n 3 --target 9 --seconds 30
```

The executable prints one JSON object. `found` includes a witness checked over
every five-point subset using the direct determinant. `exhausted` means every
initial orbit was searched and no witness exists. `unknown` means a deadline,
node budget or interrupt stopped the search. `inspected` performs internal
checks and lists initial-layer coverage without searching. The corresponding
exit codes are 0, 1, 124 and 0; invalid input or an internal inconsistency exits
2. The `complete` field refers specifically to exhaustive exclusion.

`--seconds` includes setup and is capped at 600; deadline polling may overshoot
by the work between adjacent checks. `--max-nodes` adds a deterministic bound.
`--cache-bits` controls the number of cache slots (0–20; default 18): the cache
uses 14 MiB by default and at most 56 MiB. A colliding entry is replaced, so a
full cache affects speed only. The program uses one CPU thread.

All layer-zero subsets of size zero through four are represented. D4 symmetry
reduces them to one representative per square-symmetry orbit. The empty layer
and singleton orbits are retained. `--no-symmetry` disables this reduction and
the last-layer size restriction. `--inspect` reports counts by subset size;
for n = 3 and K ≥ 5 they are `[1,3,8,16,18]`, totaling 46 orbits.

## Why the search is complete

Every coordinate layer contains at most four chosen points: any five in that
layer are coplanar. Initial subsets and subsequent layer subsets are generated
by a terminating lexicographic combination iterator. When K ≥ 5, a
four-point subset with dependent lifted rows cannot occur in a valid solution,
because any fifth row gives a zero determinant. For K ≤ 4, the search keeps
these subsets.

An isometry in the D4 group maps any first-layer subset to its canonical
representative without changing the no-five property. Reflection across the
midplane exchanges the first and last layers, so at least one orientation has
last-layer size at most first-layer size. These two reductions keep at least
one image of every feasible set.

For each four-subset of points already placed, the signed minors of its lifted
matrix give an exact linear form. Every grid point where that form vanishes is
forbidden as an additional point. If all minors vanish, **every** additional
point is forbidden. Each remaining layer contributes at most the smaller of
its allowed-point count and its layer capacity. Summing those bounds can only
overestimate the possible extension, so failing the target is a sound prune.

For a proposed new layer, all bad five-subsets containing one new point have
already been removed by the forbidden masks. The search explicitly checks
every five-subset containing two, three or four new points with the direct
determinant. There are never five new points. Thus every extension satisfies
the intended geometric predicate.

## Checks and limits

The regression suite independently computes D4 orbit counts in Python, using a
Leibniz determinant expansion to exclude dependent four-tuples. It verifies
positive and negative controls for n = 1, 2, 3, checks every returned witness,
and repeats the n = 3 decision with symmetry disabled and with a one-slot
cache. It also verifies that node limits and deadlines produce `unknown`.

On every invocation, the C program compares cached masks against direct 5×5
determinants for 200 deterministic random four-tuples and every grid point.
It explicitly tests a concyclic four-tuple and checks combination counts and
validity for all sizes up to four on sets of size up to ten. These tests support
the implementation; they are not a machine-checked proof of the code.

The 28 September 2026 controls reproduce C(3) = 8: a valid eight-point set is
found, and all 46 initial orbits at target nine are exhausted (814 search
nodes). They also reproduce C(4) = 11: a valid eleven-point set is found, and
all 315 initial orbits at target twelve are exhausted (283,490 search nodes;
22.468 seconds on the recorded machine). The eleven-point witness also passes
a Python Leibniz-expansion check of all 462 five-subsets.

The [small controls](records/independent-enum-controls.json),
[n = 4 positive control](records/independent-enum-n4-k11.json) and
[n = 4 exclusion](records/independent-enum-n4-k12.json) record source hashes,
compiler identity, arguments and full results; the latter two also hash the
exact executable. These are independent computational reproductions, not new
mathematical records.

The [n = 5, target 15 run](records/independent-enum-n5-k15.json) reached its
600-second limit and returned `unknown`, exit code 124, with `complete: false`.
It completed six initial orbits, visited 2,280,083 search nodes and considered
109,200,492 candidate layer subsets. Its one-thread cache used 56 MiB. All
25,000 setup comparisons with the direct determinant passed. There is no
exclusion result in this receipt, and six completed orbits is not a useful
estimate of the fraction of total search time completed.

For n = 5 this implementation lists 1,906 initial orbits, with counts
`[1,6,49,319,1531]` for sizes zero through four. The existing enumerator's
1,905-orbit count excludes the empty first layer; the extra orbit here is an
explicit coverage choice, not an extra nonempty configuration.

The existing C(5) = 14 enumeration and any proposed C(6) = 18 upper bound
remain unconfirmed by this independent program. They require their own
complete runs. No such result follows from compiling the checker, passing its
controls, reproducing the smaller grids, or stopping at a deadline.
