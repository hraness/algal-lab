# Native local searches for the grid targets

Standalone C programs used in round 26 (September 2026). They are research
tools, not part of the evolution loop: they read a grid size, a target size, a
CPU-time budget, a seed, and optionally a starting point set, and print every
valid set they reach as one JSON line on stdout. Each program re-verifies a set
by brute force before printing it and aborts if that self-check fails. The
Python verifiers in `../verifiers/` remain the only judges of a claim.

```sh
cc -O3 -march=native -DMAXP=32768 -DMAXK=128 -o ls5x research/extremal/native/ls5x.c -lm
KMAX=48 ./ls5x 18 46 2400 908851045 start.txt > found.jsonl
```

| Program | Problem | Method |
| --- | --- | --- |
| `ls5x.c` | no five points of `[n]^3` on a sphere or plane | tabu search over `k`-sets with exact incremental counts of degenerate 5-subsets, an exact repair step, and growth to `KMAX` after each valid set |
| `sym5.c` | same | iterated local search over centrally symmetric sets that are kept valid (ruin and rebuild over antipodal pairs) |
| `iso2.c` | isosceles-free subsets of the `n x n` grid | tabu search with exact repair; `SYM=1` restricts to mirror-symmetric sets |

For a 4-subset `T` of the current set, `ls5x` and `sym5` enumerate the grid
points `q` with `det(T u {q}) = 0`: the circumsphere of `T`, the plane of `T`,
or, when `T` is collinear or concyclic, every grid point, because four
concyclic points and any fifth point lie on a common sphere. The repair step
removes up to three conflicting points and accepts only when the remainder is
already valid and the exact search finds conflict-free replacements.

Both caps are compile-time constants: `MAXP` bounds the grid (`n^3` for the
sphere programs, `n^2` for `iso2`) and `MAXK` bounds the set size. A run's
path depends only on its arguments, the starting file, and the environment
knobs; the CPU budget only decides when it stops, so a logged
`FOUND ... it=N` line is reproducible.

An earlier scratch version (`ls5h`, round 25 follow-up, never committed)
accepted a repair without checking the remainder and ignored concyclic
quadruples; six of eight sets it reported were invalid under the verifier.
`ls5x` fixes both and adds the brute-force self-check.
