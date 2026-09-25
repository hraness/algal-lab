# H1 computational spike: expected extra cospherical points E(n)

Committed copy: `research/spikes/h1-cospherical/` (sources alongside this memo).
Raw run data (~600 MB: per-sample sphere coefficients and extras TSVs, per-sphere
circle censuses) lives in the gitignored `research/spikes/context/runs/h1-cospherical/`
and regenerates from `src/` sources (paths there are labelled `e<n>.{spheres,extras}.tsv`,
`an<n>.txt`, `circ<n>.txt`, `data/`).  Compiled copies of the `src/` files are at the
top level of this directory.

## Setup and method

For G_n = {0,..,n-1}^3 we draw 4 uniform random points, reject coplanar or
non-distinct quadruples (counted as `degen`), compute the *exact* sphere
a|p|^2 + b.p + c = 0 (primitive integer coefficients via a 3x3 determinant /
adjugate in `__int128`), and count grid points exactly by solving a quadratic in
z for each (x,y).  `k = total - 4` is the "extra" count; E(n) = E[k].

Exactness was cross-checked by an independent Python `Fraction` implementation
(`src/xcheck.py`): 700 sampled spheres with extras at n=8, 64, 128 gave
**0 mismatches** (after fixing an adjugate-transpose bug in the checker).

A separate exact brute-force census at n=3 (`src/brute.py`, all C(27,4) and
C(27,5) subsets) verified the decomposition identity used below:
sum_bases k = 4*Z_circ + 5*Z_irr exactly (36624 + 22980 = 59604), where

- Z_circ = # 5-subsets containing a concyclic 4-subset ("circle+point"),
- Z_irr  = # non-coplanar cospherical 5-subsets with NO concyclic 4-subset
           ("irreducible"),
- Z_sphere = Z_circ + Z_irr  (any non-coplanar cospherical 5-subset lies on a
  unique sphere; at most one 4-subset can be concyclic since two circles on a
  sphere share <=2 points).

A circle+point 5-subset {K,x} has exactly 4 valid (non-coplanar) bases {3K,x};
an irreducible one has 5.  Hence E*B = 4 Z_circ + 5 Z_irr with
B = # valid bases = C(n^3,4)*(1 - r4), r4 = coplanar-4 rate.

## Files

- `src/esamp.c`   exact sampler (deterministic xorshift64;
                  `esamp n samples seed prefix`; main runs used seed 1).
                  Emits `e<n>.spheres.tsv` (a b1 b2 b3 c det k) and
                  `e<n>.extras.tsv` (full point list per extras sample).
- `src/zplane.c`  coplanar-5-subset MC (K* sanity check).
- `src/circ4.c`   MC count of concyclic 4-subsets (left-kernel consistency
                  test; verified against exact brute force at n=3).
- `src/circles.c` per-sphere circle census over extras files (all planes
                  through point triples; sampled mode for t>70).
- `src/analyze.py`, `src/circsum.py`, `src/fit.py`, `src/xcheck.py`,
  `src/brute.py` -- aggregation, independent checking, exact small-n census.
- `data/summary.txt` per-run sampler output; `data/zplane_*.txt`,
  `data/circ4_*.txt`; `out/an<n>.txt`, `out/circ<n>.txt`.

## Measured E(n)

Samples, E, standard error (both iid and batched estimators agree), products:

| n   | samples   | E(n)     | se      | n*E    | n^2*E  | n^2 E/(ln n)^2 | P(k>=1) | E[k|k>=1] | max k | share_circ |
|-----|-----------|----------|---------|--------|--------|----------------|---------|-----------|-------|------------|
| 8   | 1,000,000 | 3.727270 | 0.00732 | 29.82  | 238.5  | 55.2           | 0.633   | 5.89      | 68    | 0.329      |
| 12  | 1,000,000 | 2.668888 | 0.00739 | 32.03  | 384.3  | 62.2           | 0.486   | 5.49      | 116   | 0.279      |
| 16  | 1,000,000 | 2.030376 | 0.00733 | 32.49  | 519.8  | 67.6           | 0.390   | 5.20      | 164   | 0.240      |
| 20  | 1,000,000 | 1.586429 | 0.00712 | 31.73  | 634.6  | 70.7           | 0.320   | 4.95      | 212   | 0.221      |
| 24  | 1,000,000 | 1.272137 | 0.00674 | 30.53  | 732.8  | 72.6           | 0.271   | 4.70      | 220   | 0.216      |
| 32  | 800,000   | 0.885481 | 0.00698 | 28.34  | 906.7  | 75.5           | 0.203   | 4.36      | 344   | 0.196      |
| 40  | 800,000   | 0.674646 | 0.00701 | 26.99  | 1079.4 | 79.3           | 0.159   | 4.25      | 436   | 0.180      |
| 48  | 600,000   | 0.508868 | 0.00720 | 24.43  | 1172.4 | 78.2           | 0.129   | 3.96      | 548   | 0.174      |
| 64  | 500,000   | 0.334722 | 0.00714 | 21.42  | 1371.0 | 79.3           | 0.0899  | 3.72      | 620   | 0.164      |
| 96  | 250,000   | 0.175020 | 0.00742 | 16.80  | 1613.0 | 77.4           | 0.0537  | 3.26      | 566   | 0.158      |
| 128 | 150,000   | 0.109487 | 0.00905 | 14.01  | 1793.8 | 76.2           | 0.0345  | 3.17      | 640   | 0.144      |

`share_circ` = fraction of extras lying on the circle through a base triple
(exactly the fraction of E-mass arising from circle+point 5-subsets).

## Decay rate

Successive log-log slopes drift upward: 0.82, 0.95, 1.11, 1.21, 1.26, 1.22,
1.55, 1.46, 1.60, 1.63 between consecutive n.  A pure power law is therefore
*not* stable over the window:

- log-log fit on n>=32: E ~ 152.7 n^{-1.48}  (residuals drift to -0.07 at 128)
- **fit of n^2 E vs (ln n): n^2 E ~ 79.2 (ln n)^{1.99}**, residuals <= 0.03
  over all of n in [32,128]; i.e. the data are consistent with

        E(n) ~ 79 (ln n)^2 / n^2 ,   Z_sphere ~ const * n^10 (ln n)^2 .

  (The local exponent at n~110 is 2 - 2/ln n ~ 1.6, matching the observed 1.6.)

**Verdict: the data strongly support E(n) = o(1/n) (H1):** n*E(n) falls like
~(ln n)^2 / n (from 32.5 at n=16 to 14.0 at n=128), i.e. E ~ n^{-2+o(1)}.
Equivalently Z_sphere(n) ~ n^{10} (ln n)^{~2} - one power of n below the
critical n^11 needed for H1.  A bare power n^{-1.5} also fits the window, so the
honest statement is a in [1.4, 2], most consistent with a = 2 up to a log^2.

## Coplanar sanity check (zplane.c, 3e8 draws each)

Z_plane(n)/n^11 estimates: 0.0658 (n=16), 0.0683 (24), 0.0739 (32), 0.0749 (48),
0.0764 (64), SEs 0.5%-8%.  Consistent with the memo's K* ~ 0.072 bracket
(finite-size approach from below modulo ~2σ at large n).

Concyclic 4-subsets (circ4.c, corrected and brute-verified):
N_circ4 / n^8 = 0.105, 0.095, 0.084, 0.070, 0.061, 0.048, 0.038, ~0.015 at
n = 8, 12, 16, 24, 32, 48, 64, 96 (n=96 has only 5 hits, SE ~45%; the rest have
SE < 15%).  => N_circ4 ~ n^{7.6±0.2}, Z_circ ~ n^3 N_circ4 ~ n^{10.6±0.2}
and its share of Z_sphere falls steadily.

## Who dominates E: sphere-side decomposition

For each sampled sphere, primitive equation a|p|^2 + b.p + c = 0, center
-u/det with denominator Dc, radius R.

*Primitive quadratic coefficient a (equivalently center denominator):*
E-mass is carried overwhelmingly by SMALL a, spread roughly log-uniformly
across dyadic classes up to a ~ n^3, with a slowly decaying per-class weight:

- a = 1 spheres: sample share falls like ~n^{-2.4} (0.048@16 -> 3e-4@128) yet
  carry mean k ~ 0.55 n at every n (19.6@16 -> 72.9@128 extras, i.e. mean
  t ~ 0.57n lattice points) -> share of E = 0.47, 0.35, 0.28, 0.22 at
  n = 16, 32, 64, 128.
- mean extras per sampled sphere ~ n * a^{-0.6} approximately (see table below).
- Dc = 1 (integer centers): 5.0% of E at n=32, 1.7% at n=128; Dc = 2
  (half-integer centers) carry ~20-30% of E.  All denominators up to ~n^3
  contribute; the dyadic tail decays ~x0.6 per doubling.
- det (6x area of the base tetrahedron): E-contrib concentrated in the broad
  middle band det ~ n^3 (2^13..2^22 at n=128), i.e. the bases are *generic*
  4-tuples, not special small-volume ones.
- radius: R/n ~ 1 bucket (0.7n..1.4n) carries ~85-90% of E at all n; larger
  spheres contribute progressively less (they hit fewer box points / larger
  denominators).
- no sphere is sampled twice at n>=32 (all 500k spheres at n=64 distinct;
  at n=8, 6.8% of samples collide); the mass is spread over many spheres.

*Rich vs sparse:* the k-histogram is heavy-tailed.  At n=64, P(k>=1) = 0.090,
E[k|k>=1] = 3.72, max k = 620; ~50% of E comes from spheres with k >= 12.
Per-circle census (circles.c + circsum.py): the points of a rich sphere sit on
lattice circles with low-height normals -- dominant normals (sorted |v|):
(0,0,1) axis planes first, then (0,1,1),(1,1,1),(0,1,2),(1,1,2),(1,2,2)...
with contribution decaying in |v|_inf.  Max circle load cmax = 4-8 typically;
the richest spheres (t~600 at n=64-128) carry coordinate-plane circles of
~24-32 points (cmax/t ~ 0.05).

## Mechanism split at the 5-subset level

Estimated Z_sphere = Z_circ + Z_irr two independent ways (extras attribution
via share*E*B/4 vs per-sphere cp/N census); they agree:

| n   | extras-share_circ | circsum cp-share of Z_sphere | Z_sphere/n^11 (census) | nE/120 (sampler) |
|-----|-------------------|------------------------------|----------------------|------------------|
| 8   | 0.329             | 0.379                        | 0.259                | 0.248            |
| 12  | 0.279             | 0.325                        | 0.282                | 0.267            |
| 16  | 0.240             | 0.290                        | 0.287                | 0.271            |
| 20  | 0.221             | 0.268                        | 0.279                | 0.264            |
| 24  | 0.216             | 0.255                        | 0.268                | 0.254            |
| 32  | 0.196             | 0.235                        | 0.248                | 0.236            |
| 40  | 0.180             | 0.215                        | 0.235                | 0.225            |
| 48  | 0.174             | 0.210                        | 0.212                | 0.204            |
| 64  | 0.164             | 0.195                        | 0.186                | 0.179            |
| 96  | 0.158             | 0.188                        | 0.145                | 0.140            |
| 128 | 0.144             | 0.174                        | 0.121                | 0.117            |

(The small census-vs-sampler offsets are the (1 - r4) factor and sampled-mode
bias on the largest spheres; agreement is 3-5%.)

So ~80% of Z_sphere at large n is *irreducible* cospherical 5-subsets --
4+ points on a low-denominator sphere in generic position -- while the
"circle+point" degeneracy is ~20% and falling (~n^{10.6} vs n^{10}log^2).
Note the contrast with the sphere-level statistic "has some concyclic
4-subset": 62% of extras-spheres at n=48 (88% k-weighted) have one, but those
circles generate only a minority of the degenerate 5-subsets.

## What a proof needs to bound

E*B = 4 Z_circ + 5 Z_irr, and Z_irr <= sum over spheres s of C(t_s,5).
Everything observed is consistent with the following picture, which is what
a proof of H1 should establish:

1. Split spheres by the primitive leading coefficient a (or center
   denominator).  Empirically the per-sphere point count is t ~ 0.6 n / a^{1/2}
   at bounded ratio, i.e. lattice points on a sphere of radius ~n concentrate
   as ~(n / sqrt(a))^{1+o(1)} -- this is the arithmetic input (a bound of
   r_3-type / lattice points on spheres with controlled denominator).
2. The number of spheres with a in [A,2A) carrying >=4 points times their
   degenerate-5-subset count gives a dyadic contribution ~ n^{10}/a^{alpha}
   with alpha ~ 0.5-1; summing log-many classes produces the observed
   n^{10} (ln n)^2.  A sufficient theorem: for primitive a <= poly(n),
   the number of cospherical non-coplanar 5-subsets on spheres of class a is
   <= n^{10+o(1)} * a^{-c} for some c > 0; summing over a gives
   Z_sphere = n^{10+o(1)} = o(n^{11}).  The data suggest the bound is nearly
   tight: the true rate has a log^2 numerator.
3. The circle+point subfamily separately: Z_circ = sum_K (n^3 - q_K) over
   concyclic 4-subsets K ~ n^{10.6} measured; a bound like
   N_circ4 = O(n^8) would already give Z_circ = O(n^{11}) which is NOT enough
   for H1 on its own -- it needs the slightly sharper N_circ4 = o(n^8) or
   n^{8-eps}; measured coefficient falls ~n^{-0.4}.  But since Z_circ is only
   ~1/5 of Z_sphere and falling, the irreducible class is the essential one.
4. The coplanar piece Z_plane ~ K* n^11 with K* ~ 0.072 (verified
   independently here) bounds the "all on a circle" subfamily separately.

The dominant 4-tuples themselves are unremarkable: det ~ n^3 (bulk), radius
~n; what distinguishes them is landing on a low-denominator sphere.
Equivalently: the smallest algebraic-complexity spheres (a = 1,2,4; integer
and half-integer centers, e.g. center (37.5,35.5,35.5) with ~600 points at
n=128) supply a quarter of E with ~0.03% of samples, and the residual is
spread log-uniformly over denominators up to ~n^3.

## Honest caveats

- All E(n) are Monte Carlo estimates with quoted SEs; the log^2/n^2 fit is
  empirical (fit residuals <3% for n>=32, and it explains the drifting local
  exponent naturally).  It is evidence, not a proof.
- circsum's per-sphere census is exact for t <= 70 and sampled-triple mode
  for t > 70 (flagged ~; a few hundred spheres per n, all included in the
  totals shown).
- The sampler's `degen` count conflates coplanar with duplicate-point draws
  (~6/n^3 extra); accepted samples are still uniform over distinct
  non-coplanar 4-subsets, so E is unbiased.  r4 values used for B come from
  the distinct-only circ4 counter.

## Compute cost

Roughly 30 CPU-minutes total on this machine (18 cores, all jobs `nice -n 10`):
esamp ~7M accepted samples (~30k samples/s at n=64), circ4 ~9.7e9 draws
(~15M/s), zplane 1.5e9 draws, circles census ~8 CPU-min, python analysis
~4 min.  Wall time ~40 min with parallelism.
