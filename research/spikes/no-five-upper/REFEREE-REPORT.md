# Referee report: Round 27, upper bounds for no-five-on-a-sphere in `[n]^3` (Memo B)

Memo reviewed: `memo.md` in this directory (502 lines), with `src/` and `out/`.
Referee: an independent adversarial check, 2026-09-25. I did not edit the memo, commit or push.
My scratch scripts are in `/tmp/referee/` (throwaway, not committed): `common.py`, `c3.py`,
`c4.py`, `lp.py`, `sphmax.py`.

## Verdict

**Accept as a research memo after minor revision.**

I found no mathematical error in any item labelled Theorem, Lemma, Corollary or Proposition.
Every proof checks line by line, and every threshold and constant I recomputed holds.
The claim that the LP optimum is "exactly 4n" is real: `x ≡ 4/n²` is feasible and reaches
`4n`, and the `n` axis-plane constraints give the matching upper bound. The memo also claims
no bound below `4n`, and nothing in it contradicts that. The problems below are all in glosses
and summaries that say more than the theorems prove, plus a few stale or internally
inconsistent numbers.

## Numbered problems

**1. (Moderate, wording/scope.) Summary item 3, the remark after Theorem 3.5, and §6.1 item 3
make the Thiele transfer sound stronger than Proposition 4.3.1 proves.**
Lemma 3.3 holds for parallel lines of *any* direction `v`, not just axis directions. So the
statement that the mechanism "only constrains pairs on axis-parallel lines" is false as
written. The witness `S_n` also violates the non-axis instances. For every `n ≥ 4` the plane
`x = 0` contains the four collinear points `(0,j,j)`, `j = 0..3`. With `v = (0,1,1)`, the pairs
`{(0,0,0),(0,3,3)}` and `{(0,1,1),(0,2,2)}` have equal sums, which is exactly what Lemma 3.3
and Lemma 3.1(a) forbid. Proposition 4.3.1 as stated, restricted to Corollary 3.3.1 with
`v ∈ {e₁,e₂,e₃}`, is correct.
*Fix:* restrict the gloss to the axis-parallel instance, which is what Thiele's column
argument actually uses. Alternatively, strengthen the result as follows. For `|v|₁ ≥ 2`, the
directional counting bound `Σ_{L∥v} C(k_L,2) ≤ 2(n−1)|v|₁+1` holds automatically for any
`4n`-point set with no three collinear points. In such a set the pairs on lines of one
direction form a matching, so there are at most `2n ≤ 4n−3` of them. A `4n`-point witness with
four points on every axis plane, no axis-parallel pair and no three collinear points would
therefore make the whole directional trapezoid mechanism vacuous. `S_n` is not such a witness.
Also, "saturated" does not apply to the coaxial lemma: the memo itself says (line 152) that
lemma is an injectivity constraint, not a counting one.

**2. (Minor, overclaim.) Summary item 2 says "any argument that only uses the restriction of
`S` to slabs of bounded thickness proves nothing below 4n."** Corollary 4.2.2 proves this only
for *partitions* into slabs. Overlapping or sliding windows are not covered, because a union
bound over all windows fails: the total failure probability is `≈ 4·C(4k,5)`, which is not
below 1.
*Fix:* restate the item as in Corollary 4.2.2. Optionally, extend it with the Lovász Local
Lemma (variable version), which I checked:
- Take the `4n` points `(X_{c,j}, Y_{c,j}, c)` with independent uniform coordinates.
- The bad events are `D_T = 0` for 5-subsets `T` of z-span `< k` (probability `≤ 4/n`) and
  coincidences inside a plane (probability `1/n²`).
- Each event shares variables with at most `d = 5(C(8k−5,4)+3)` other events.
- So `e·(4/n)·(d+1) ≤ 1` holds once `n ≥ 4e(5·C(8k−5,4)+16)`.

For such `n` there is a `4n`-point set with four points on every plane `z = c` in which every
five points of z-span `< k` are in general position. This covers sliding windows too.

**3. (Minor, false edge case.) "Thus `C(n) ≤ 4n − 4` for `n ≤ 4`" (line 39) and "true for
`n ≤ 4` with `c = 4`" (line 51) are false at `n = 1`,** since `C(1) = 1 > 0`. At `n = 4` the
claim also rests on `C(4) = 11`, which comes from the other lane and is not verified here.
The memo's own LP gives only `C(4) ≤ 13`.
*Fix:* write `2 ≤ n ≤ 3` (proved here), and state `n = 4` separately as conditional on the
exact lane.

**4. (Minor, internal inconsistency.) The memo describes cospherical growth in random-like sets
in three incompatible ways.** §0 item 5 says "Θ(n) degenerate 5-subsets of both types in the
accessible range", and §5 says "≈ 120–230·n". But §6.2 says "the cospherical obstruction,
unlike the coplanar one, is *not* growing with n". The table supports neither extreme:
`cospherical/n` falls from 213 (n = 32) to 120 (n = 96), so counts grow about ×1.7 while `n`
grows ×3.
*Fix:* describe the growth as sublinear in the measured range, consistent with `n²E(n)`
varying slowly. Do not call it `Θ(n)`.

**5. (Minor, wording.) Summary item 1 says the LP uses "every valid cardinality constraint".**
Other valid cardinality constraints exist and are not in the LP. For example,
`Σ_{p ∈ v+[3]³} x_p ≤ 8 = C(3)` is valid for every translate, and at `n = 3` it alone cuts the
LP from 10 to 8.
*Fix:* say "all plane/sphere (≤ 4) and line/circle (≤ 3) cardinality constraints", as §4.1
already does.

**6. (Minor, stale table.) The "LP constraints" column of `out/tables.md` (1267, 36908, 563650)
predates the concentric-circle fix.** The files `out/lp-n3.txt`, `lp-n4.txt` and `lp-n5.txt`
report 1312, 37658 and 570042. My independent generator gives exactly 1312 at `n = 3`
(948 rhs-4 + 364 rhs-3) and 37658 at `n = 4` (33810 + 3848).
*Fix:* regenerate `tables.md`, then update `out/SHA256SUMS`.

**7. (Minor, simplification.) The circle hypothesis in Theorem 4.1.2(b) holds automatically for
`n ≥ 3`.** Suppose a circle does not lie in a plane `x = c`. Then it meets each of the `n`
planes `x = c` in at most 2 points. If it does lie in such a plane, it meets each line
`{x = c, y = c'}` in at most 2 points. Either way a circle carries at most `2n ≤ 3n²/4` grid
points, which also explains the computed maximum of 8 at `n = 5`.
*Fix:* use this bound instead of the computed circle check, and keep Lemma 4.1.1 only for
spheres. Slicing alone gives spheres only `≤ 2n²`, so the lemma is still needed there.

**8. (Nit.) §6.1 item 1 says `LP(3)`, `LP(4) < 4n` are possible "only because" some spheres
carry more than `n²` points.** This is correct only as a contrapositive of 4.1.2(b), given that
circles satisfy the bound (problem 7).
*Fix:* phrase it as "the uniform point is infeasible there because ...".

**9. (Nit.) Lemma 4.1.1(ii): the covering of a closed arc by half-open sub-arcs should leave
the last piece closed.** Each piece still has length `< (2R)^{1/3}`, so the count is
unaffected. Say so in one clause.

## What I verified independently, and how

All determinant tests use my own exact fraction-free Bareiss 5×5 determinant (Python integers),
or `numpy` 4×4 determinants of small-integer matrices rounded to integers, which is exact at
these sizes.

**Computations.**
- **`C(3) = 8`.** I enumerated all 80730 5-subsets of `[3]³` and found 16026 degenerate ones.
  This equals the census total 1134 + 1140 + 13752. CP-SAT with one clause per degenerate
  5-subset returned `OPTIMAL 8`, bound 8. The optimal set
  `{002, 020, 100, 111, 121, 201, 212, 220}` has zero degenerate 5-subsets on re-check.
- **`LP(3) = 10`, `LP(4) = 40/3`, from my own constraint generator.**
  - Planes and spheres: I took the unique hyperplane through every lifted-rank-4 4-subset and
    kept those with ≥ 5 grid points.
  - Lines and circles: I took the closure of every triple and kept those with ≥ 4 grid points.
  - Counts: 948/364 at `n = 3` and 33810/3848 at `n = 4`, identical to `out/lp-n*.txt`.
  - Upper bounds: GLOP, then an exact dual certificate (multipliers rounded to denominator
    ≤ 10⁶, evaluated in `Fraction`), gave exactly `10` and `40/3`.
  - Lower bounds: I symmetrised under the cube group (orbits by number of interior
    coordinates) and checked exactly feasible primal points against every constraint:
    - `n = 3`: corners ½, edge-midpoints ⅓, face centres ⅙, centre 1, total 10.
    - `n = 4`: corners ½, all other points ⅙, total 40/3.

  So both values are certified from both sides.
- **Theorem 4.1.2(a) at `n = 3`.** The planes+lines LP has value 12 = 4n (exact primal and
  dual).
- **`n = 5` sphere occupancy.** Scanning the hyperplanes through all 9.76M 4-subsets of `[5]³`
  gives a maximum of 24 grid points on a sphere and 25 on a plane. At `n = 4` the maximum is
  24 on a sphere. With problem 7, this proves `LP(5) = 20` without trusting the LP solve.
- **Window values.** `W(2,3) = 7` (CP-SAT OPTIMAL, 2048 degenerate 5-subsets) and
  `W(2,4) = 8` (OPTIMAL).
- **Determinant for `(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,2)`.** It is 2, as stated in §3.
- **Coplanar census.** My exact sum over lattice planes of `C(N,5)` equals the census
  coplanar totals at `n = 3` (2274) and `n = 4` (109680).

**Proofs checked by hand.**
- Lemma 3.1: the sphere pencil through a circle.
- Lemma 3.3: the two perpendicular bisectors in `Π` are non-parallel because `AC ∦ v`.
- Corollary 3.3.1: the range `[1, 2n−3]`, and `k_L + k_L' ≤ 4` because parallel lines are
  coplanar.
- Lemma 3.4: the linear equation in `t` has coefficient `−2(c'−c) ≠ 0`.
- Theorem 3.5: the identity `3a+2b+c = ½(3a+b) + (3/2)(a+b+c) − ½c`.
- Lemma 4.1.1, all constants:
  - `2^{5/3}π = 9.97 < 10`
  - `θ < 2π/3` from `chord < √3R`, together with "no antipodal pair", so the arc is minor
  - `1.2092·√3 = 2.0944`
  - `6·4.19/2^{1/3} = 19.95 < 20`
  - the covolume of `ν^⊥ ∩ Z³` is `|ν|`, so a lattice triangle has area `≥ ½`
- Theorem 4.1.2 thresholds at `n = 8100`:
  - `48/n + 80/n^{1/3} = 0.0059 + 3.984 ≤ 4`
  - spheres: `12/n + 20/n^{1/3} = 0.9975 ≤ 1`
  - at `n = 8000` the sphere inequality fails, so 8100 is where this lemma first works.
- Theorem 4.2.1:
  - `deg D_T ≤ 4` (column degrees 1, 1, 0, 2, 0)
  - `D_T ≢ 0` by the sequential choice (at most three of the four chosen points share a
    z-value)
  - Schwartz–Zippel over the set `[n]` of size `n`
  - the union bound `(4·C(4k,5)+6k)/n < 1`
  - for `k = 1`, `n₀ = 7` is fine.
- Proposition 4.3.1: the counting for odd and even `n`.

**Literature.** I fetched the arXiv abstracts. Dong–Xu 2506.18113 gives `n − o(n)` for all
`d ≥ 2` and improves Thiele's `n/4` for `d = 2`. Suk–White 2412.02866 gives `n^{3/(d+1)−o(1)}`.
Ghosal–Goenka–Grebennikov–Keevash–Kwan–Pham 2607.05255 show exactly `kn` for `k ≥ 3` and large
`n`. Ghosal–Goenka 2609.20447 is the extensible no-four-on-a-circle paper. All match the
memo's descriptions. Thiele's `(5n−3)/2` agrees with Dong–Xu's introduction.

## What I could not check

- **`C(4) = 11`.** My CP-SAT run found and re-verified an 11-point set, so `C(4) ≥ 11`. It did
  not prove `C(4) ≤ 11` within an 8-minute cap: the bound stayed at 16, and the host load was
  about 55. The census count of 714936 degenerate 5-subsets was reproduced exactly.
- **Not recomputed:**
  - the `n = 5..7` full-grid census
  - the random plane-4-regular censuses
  - the `E(n)` Monte Carlo
  - the `n = 32` sphere statistics
  - `W(3,3)`, which equals `C(3)` and so is covered indirectly.

## Cross-memo note

The sibling lower-bound memo (`theorem-lower/.../no-five-theorem/memo.md`) conjectures
`Z_sphere(n) = Θ(n^{11})` (its Conjecture 3). This memo's `E(n)` table implies
`Z_sphere/n^{11} ≈ n·E(n)/120`, which falls from 0.27 (n = 16) to 0.084 (n = 128). That is
evidence against Conjecture 3 and supports the `n^{10+o(1)}` heuristic in §6.4. It matters: the
exact plane-count constant is ≈ 0.072, below the deletion threshold 0.0819 (see that memo's
referee report). So `Z_sphere = o(n^{11})` would give `C(n) ≥ 1.03n` by plain deletion. The
authors of the two memos should reconcile §6.2/§6.4 here with §3.7/§4.4 there.
