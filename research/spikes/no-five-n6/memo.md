# C(6) layer enumeration (n=6 decision attempt)

Port of `research/spikes/no-five-exact/layer_enum5.c` to n=6, with an
incremental optimization: the per-node rebuild of future-layer forbidden
masks `blockf[k]` (O(C(m,4)) random lookups into the 4.2GB degenerate-set
table per node) is replaced by per-edge delta propagation — `add_delta`
applies exactly the 4-subsets meeting a newly placed layer set (1-of-C via
per-position deltas accumulated during the `Mp` build, plus small loops for
2/3/4-of-C). Validation: identical node counts to the original binary on 30
consecutive orbits (e.g. orbit 0: 3,620,318 nodes both ways), ~6x faster.

Corrected C(5)-era prune retained: future-layer bound
`low = K - m - 4*(NZ-1-j)` counts all unplaced layers (the pre-fix C(5)
prune dropped layers j..k-1; see the no-five-exact memo erratum).

Run (in progress): `./layer_enum6 16 <deadline> 19 0 8133` decides whether
a 19-set exists in [6]^3 — a verified 18-set certificate already gives
C(6)>=18 (no-five-exact/certificates/n6_18_ls5x.json), so `found=0` over
all 8,133 canonical layer-0 orbits would establish C(6)=18.

Sphere table: C(216,4)x6 u64 masks ≈ 4.23GB, built once per run (~23s) and
self-tested against direct evaluation (0 mismatches). Orbit-complete logs
under `runs/c6-enum/` (gitignored); resumable via the rep-range arguments
([lo,hi) on canonical reps).
