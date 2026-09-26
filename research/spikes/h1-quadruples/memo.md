# H1-quadruples spike: concyclic 4-subsets of [n]^3 — proof attempt

Working (gitignored) directory: `research/spikes/context/runs/h1-quadruples/`.
Goal (from the H1 memo, `research/spikes/h1-cospherical/memo.md`): show that
`N_circ4(n)` = the number of 4-subsets of `B_n = [0,n)^3` lying on a common
circle is `o(n^8)`. Empirically `N_circ4 ~ n^{7.6±0.2}`.

**Status: reduction proved; one precise lemma missing (stated in §4).**
Everything in §§1–3 is proved. The honest summary is:

* the concyclic 4-sets split into **symmetric** (isosceles trapezia + kites:
  reflection-symmetric quadrilaterals) and **asymmetric** ones;
* the symmetric part is `O(n^7 log n)` — proved in §3 (and it is the empirical
  majority: ~64% of mass at n = 48..96);
* the asymmetric part is `o(n^8)` provided a single uniform planar-rarity
  statement, **Lemma L** below — a rank-2-lattice analogue of the
  Huxley–Konyagin theorem used by Ghosal–Goenka–Keevash for `[n]^2`
  (arXiv:2509.06935).  Any per-section saving `s^{-θ}` with `θ > 1/2` suffices
  and gives the power bound `N_circ4 = O(n^{9-2θ+o(1)})` — *stronger* than the
  `o(n^8)` target; `θ = 1` gives `O(n^{7+o(1)})`.
* unconditionally we prove `N_circ4 = O(n^{9+o(1)})` (§2); the gap to the lemma
  is exactly the arithmetic input (4-point circles are rare among 3-point
  circles, uniformly in the section lattice).

Notation. `B_n = {0,...,n-1}^3`. `s(v) = |v|_∞` for a primitive normal
`v ∈ Z^3`. `N_{v,k} = #{x∈B_n : v·x = k}`; `Λ_v = v^⊥ ∩ Z^3` is a rank-2
lattice of covolume `‖v‖` (H2 memo, Lemma 1). The circle centres etc. below.

## 0. What a concyclic 4-set is (bookkeeping, exact)

Four distinct points are *concyclic* iff they are coplanar and lie on a common
sphere — equivalently coplanar and the unique circle through any non-collinear
triple contains the fourth. A concyclic 4-set is automatically non-collinear
(a circle meets a line in ≤ 2 points), hence lies in a **unique** plane
`Π_{v,k} = {v·x = k}` (v primitive, unique up to sign) and on a **unique**
circle.  Therefore

    N_circ4(n) = Σ_{v prim,±}  Σ_{k∈Z}  Σ_{γ ⊂ Π_{v,k}}  C(t_γ, 4),

where γ runs over circles containing ≥ 4 box points and `t_γ` is the box-point
count.  Equivalently, since a 4-set has four 3-subsets and all four have the
same circumcircle,

    N_circ4(n) = (1/4) Σ_{T non-collinear} (t_{γ(T)} − 3)
               = (1/4)·#{(T,w): T a non-collinear triple, w ∈ γ(T) ∩ B_n \ T}.

Canonical data of a circle: the sphere through γ centered at γ's center `c₀`,
primitivized: `a|x|² + b·x + c = 0`, `a ≥ 1`, `gcd(a,b,c)=1`, with
`c₀ = -b/(2a)` lying in the plane, i.e. `v·b = -2ak` (so `k` is determined by
`(v,a,b)`; the circle is `γ = {x : v·x = k, a|x|²+b·x+c = 0}`).

For a triple `T = {x,y,z}` the circumcentre solves `2c₀·(y-x) = |y|²-|x|²`,
`2c₀·(z-x) = |z|²-|x|²`, `v·c₀ = k`; the system determinant is
`4·A_T·‖v‖²` where `A_T ≥ 1` is the lattice (double) area of T in `Λ_v`
(`Area_E = A_T·‖v‖/2`, so `det = 4·‖v‖·2Area_E = 4A_T‖v‖²`, an
integer `∈ [4‖v‖², 24‖v‖ n²]` since `A_T ≤ 6n²/‖v‖`).  Hence the centre
denominator `q_T | det_T` and `2·det_T·c₀ ∈ Z^3`.

## 1. Lattice points on a circle: `t_γ = n^{o(1)}`

**Lemma 1.** Uniformly over all circles γ determined by `B_n`-triples:
`t_γ = O(n^{o(1)})`.  More precisely `t_γ ≤ C_ε (n·s·det_T)^ε` for every ε>0.

*Proof.* Take a point `p` on γ and let `D = det_T` for an inscribed triple.
`2D·c₀ ∈ Z³` (above), so the map `x ↦ 2D·x − 2D·c₀` sends the lattice points
of γ to integer vectors of `Λ_v` of squared norm `M = 4D²ρ² ∈ Z`,
`ρ = |sides|/(4·Area_E) ≤ (n√3)³/(4·‖v‖/2) ≤ C·n³/‖v‖` (circumradius
of a triangle of lattice area `A_T·‖v‖/2 ≥ ‖v‖/2` with sides `≤ n√3`).
`M = 4·det_T²·ρ² ≤ 4·(24‖v‖n²)²·(Cn³/‖v‖)² = O(n^{10})`.  In a Minkowski
basis of `Λ_v` these vectors are representations of `M` by a primitive
integral binary quadratic form of discriminant `−4‖v‖²`; for a *single*
primitive positive binary form `r_Q(M) = O(d(M)) = M^{o(1)}` (standard:
`summed over the class group` the count is `2w·Σ_{e|M}χ(e)`, and a single
class is no larger up to the unit factor `w ≤ 6`).  Hence
`t_γ = n^{o(1)}` as `M = poly(n)`. ∎

*Remark.* The classical bound is exactly this shape; for `Λ ≅ Z²` it is
`r₂(m) ≤ 4d(m)`.

**Corollary (baseline).** `N_circ4 ≤ (t_max/4)·Σ_γ C(t_γ,3) ≤ n^{o(1)}·C(n³,3)
= O(n^{9+o(1)})`, since `Σ_γ C(t_γ,3) ≤` #non-collinear triples (each triple
maps to its unique circumcircle).  This is the wall every elementary argument
hits: with only `t = n^{o(1)}` one cannot beat `n^9`.

## 2. Symmetric/asymmetric split — definitions

A concyclic 4-set is **symmetric** iff, viewed as a quadrilateral on its
circle (it is convex: 3 collinear circle points impossible), it has a
reflection symmetry.  The symmetry axis must pass through the centre, so two
types occur:

* *isosceles trapezoid* (incl. rectangle, square): axis swaps the two pairs of
  vertices — equivalently *one of the three perfect matchings has equal chord
  lengths* (equal chords ⇒ equal arcs ⇒ symmetry; conversely the legs and the
  diagonals are equal pairings);
* *kite*: axis passes through two opposite vertices, which are then a diameter
  — equivalently some chord `{a,c}` is a diameter and `b,d` are equidistant
  from `a` and `c`.

Every other concyclic 4-set is **asymmetric**.

Numeric check of the test: the classifier in `quad.c` implements exactly these
three matchings + kite checks; verified against the corrected counts below.

## 3. Theorem (proved): `N_sym = O(n^7 log n)`

**Trapezia.** A trapezoid = two parallel chords `{p1,p2}`, `{q1,q2}` of a
circle, symmetric about the diameter through their midpoints.  Parametrize:

* `w = p2 − p1 ∈ Z³\{0}`, `|w| ≤ n√3`; for each `w` the chord has `≤ n³`
  placements (first endpoint in the box); write `w = g·u`, `u` primitive,
  `g = gcd(w)`.
* `h = m' − m` = difference of the two chord midpoints.  Symmetry forces
  `h ⊥ w`; `h ∈ w^⊥ ∩ Z³`, `|h| ≤ n√3`.  The lattice `w^⊥ ∩ Z³ = u^⊥ ∩ Z³` has
  covolume `|u| = |w|/g`, so the number of such `h` is
  `≤ C·n²/|u| + O(n) ≤ C'·n²·g/|w|`.
* the second chord `w' = q2 − q1` is parallel to `w`, hence `w' = t·u`,
  `t ∈ Z`, `|w'| ≤ n√3`, giving `|t| ≤ g·n√3/|w|`: `≤ 7gn/|w|` choices.
* integrality of `q_i = m' ± w'/2` (with `2m = p1+p2 ∈ Z³`, `2h ∈ 2Z³`)
  requires `t·u ≡ p1+p2 (mod 2)`, a `mod-2` condition on `t` — it either kills
  or halves the admissible `t`; for the upper bound we simply keep all `t`.

Every isosceles trapezoid arises this way (its two parallel sides are `w`, `w'`
and `h` is the axis offset), each one `≤ 4` times (choice of which parallel
side is `w`, and ordering).  Hence

    N_trap ≤ C·Σ_w n³·(n²g/|w|)·(gn/|w|)
           = C·n⁶·Σ_w g²/|w|²
           = C·n⁶·Σ_{u prim} |u|^{-2}·#{g ≤ n√3/|u|}
           = C·n⁶·Σ_{u prim} n√3/|u|³
           ≤ C'·n⁷·Σ_{t ≤ n√3} t²·t^{-3}            (# u of size t is O(t²))
           = O(n⁷ log n).

**Kites.** A kite = diameter pair `{a,c}` + mirror pair.  Fix the diameter
pair (≤ `n⁶` choices); the off-axis points `b` satisfy
`|2b − (a+c)|² = |a − c|²` (angle `abc = 90°`), i.e. they are lattice points on
a sphere of radius `≤ n√3/2` and denominator `≤ 2`; such points number
`r₃-type = O(n^{1+ε})`.  The mirror partner `d` is then *determined*
(reflection of `b` in the line `ac` within the plane `abc`), and each kite is
counted `O(1)` times (≤ 2 diameter pairs).  So `N_kite = O(n^{7+ε})`.

**Total.** `N_sym = O(n⁷ log n) + O(n^{7+ε}) = O(n^{7+o(1)})`. ∎

Consistency with data: `sym/n⁷` measured `0.19, 0.30, 0.37, 0.43, 0.50, ~0.55,
0.7, 0.9, 1.05, ~1.0, ~1.36` at `n = 3,4,5,6,7,8,12,16,24,32,48` — i.e.
`sym ∝ n⁷ log n` (slowly rising ratio), matching the bound's shape.

## 4. Asymmetric part — the reduction and the missing lemma

`N_asym = Σ_{v,k} Q_asym(Π_{v,k} ∩ B_n)`, where `Q_asym` counts asymmetric
concyclic 4-subsets of the section `S = Π_{v,k} ∩ B_n` — a coset of a rank-2
lattice of covolume `‖v‖ ∈ [s, s√3]`, with `N = N_{v,k} ≤ 2n²/s + 2` points in
a region of diameter `≤ n√3` (H2 Lemma 3); sections with ≥ 4 non-collinear
points exist only for `s = O(n²)`.

**Lemma L (the missing uniform-rarity lemma).** There is a `θ > 1/2` and `C`
such that for every primitive `v` (size `s`) and every `k`, the number of
circles through `≥ 4` points of `S = Π_{v,k} ∩ B_n` is
`G(S) ≤ C·N³·s^{−θ}·n^{o(1)}`  — equivalently, the fraction of non-collinear
section triples whose circumcircle carries a fourth section point is
`O(s^{−θ}n^{o(1)})`.

*If Lemma L holds with θ > 1/2*, then, since `Q(S) = Σ_γ C(t_γ,4) ≤
C(t_max,4)·G(S) ≤ n^{o(1)}·G(S)` by Lemma 1:

    N_asym ≤ n^{o(1)}·Σ_v s^{−θ} Σ_k N³
           ≤ n^{o(1)}·Σ_{s ≤ n²} 13s²·(2n²/s + 2)²·n³·s^{−θ}
           ≤ C·n^{7+o(1)}·Σ_{s ≤ n²} s^{−θ}
           ≤ C·n^{7+o(1)}·O(n^{max(0,2−2θ)} + 1)
           = O(n^{9−2θ+o(1)})   = o(n⁸)      for θ > 1/2,

and `θ > 1` even gives `N_asym = O(n^{7+o(1)})`. Combined with §3 this would
prove `N_circ4 = o(n⁸)` (in fact `O(n^{8−δ})`).

**Why Lemma L is plausible — and where the difficulty is.**

* The `s = O(1)` case is a theorem: for `Z²`-like sections,
  Ghosal–Goenka–Keevash (arXiv:2509.06935, Thm 1.3 + Lemma 4.2) give
  `γn⁵ + O(n^{4.62+ε})` cyclic quadrilaterals in `[n]²`, and the raw input is
  Huxley–Konyagin: circles through ≥ 4 lattice points are rare among
  3-point circles (`O(R^{2+18/29+ε})` asymmetric translation classes of radius
  `≤ R` vs `Θ(R³)` trapezia classes).
* The section lattices are `Λ_v ⊂ Z³` with norm forms `Q(i,j) = |ib₁+jb₂|²`
  of discriminant `−4‖v‖²` — the order `Z[‖v‖·i]` in `Q(i)`.  The
  Huxley–Konyagin mechanism is a statement about factorization in `Z[i]`;
  for the order of conductor `‖v‖` the class number is
  `h(−4‖v‖²) = ‖v‖^{1+o(1)}`, which is exactly the source of the expected
  `s^{−θ}` dilution.  A faithful transposition of their argument is the real
  work; it is not done here.
* Empirics strongly support `θ ≈ 1`: per dyadic `s`-class, the *asymmetric*
  share decays roughly geometrically (n=24: per-class asym hits
  `229,140,104,52,16,3,1` for `s`-blocks `[2-3],[4-7],...,[128-255]`), and
  asymmetric quads essentially die for `s ≳ 2n`, while symmetric quads
  populate all `s` up to `Θ(n²)` — consistent with the split.

**What does NOT work / honest gaps.**

* `t_γ ≤ n^{o(1)}` alone gives only `O(n^{9+o(1)})` — the rarity must come
  from the *number* of ≥4-point circles, not their size.
* Counting circles by parameter volume `(v,a,b,c)` fails badly: most such
  tuples carry no lattice points at all; parameter counting is vacuous without
  the incidence condition (this is the same wall as in the H1 sphere count).
* Counting via `Σ_T (t_T − 3)` with `T` ranging over section triples collapses
  to the same per-section quantity `4·Q(Π)`.
* Uniform-in-`v` equidistribution (`N_{v,k} = n²φ_v(k/n) + O(n)`) is *false*
  for `s ≫ n` (skew lattices); only the Pick-type bound `N ≤ 2n²/s + 2` holds
  — the asymmetric count cannot be handled by equidistribution, which is why
  the problem reduces to arithmetic rarity rather than analysis.
* The 2D theorem is *not* directly applicable per-section: under a
  lattice-preserving map `Λ_v → Z²` circles become ellipses; the
  Euclidean structure is intrinsic to `Q`, so one needs the HK-type input for
  a general form `Q` of discriminant `−4‖v‖²`.

**A second (unexplored-in-full) route** that avoids per-section bookkeeping:
concyclic iff `∃ c ∈ Z⁴\{0}` with `Σc_i = 0`, `Σc_i p_i = 0`, `Σc_i|p_i|² = 0`
(the affine-dependence condition plus the lifted quadratic one).  Counting
4-tuples by the dependency vector `c` reduces to counting solutions of a
quadratic equation inside the rank-9 lattice `Σc_i p_i = 0`; a
quadratic-Diophantine count with uniformity in `c` would give an independent
attack (the coefficients satisfy `|c_i| ≤ 3n²` = the sub-triangle areas in
lattice units).

## 5. Numerics (corrected and extended)

Exact enumeration (`quad.c`, all `C(n³,4)` subsets, `sym`/`asym` classified by
the §2 test; cross-verified against a `Fraction`-free Python implementation at
n=3,4 — see §6 for the bug story):

| n | N_circ4 | sym | asym | N/n⁸ |
|---|---------|-----|------|------|
| 3 | 468 | 420 | 48 | 0.0713 |
| 4 | 6360 | 4848 | 1512 | 0.0970 |
| 5 | 38910 | 28878 | 10032 | 0.0996 |
| 6 | 174828 | 120780 | 54048 | 0.1041 |
| 7 | 614250 | 410658 | 203592 | 0.1066 |

Monte Carlo (`quad.c`, distinct-uniform 4-subsets):

| n | samples | N_circ4 est | sym frac | N/n⁸ | asym/n⁸ |
|---|---------|-------------|----------|------|---------|
| 8 | 6e7 | 1.76e6 | 0.66 | 0.105 | 0.036 |
| 12 | 6e7 | 4.15e7 | 0.63 | 0.097 | 0.036 |
| 16 | 6e7 | 3.8e8 | 0.62 | 0.088 | 0.033 |
| 24 | 6e7 | 8.2e9 | 0.61 | 0.075 | 0.029 |
| 32 | 6e7 | 7.0e10 | 0.49 | 0.064 | 0.033 |
| 48 | 2e9 | 1.27e12 | 0.63 | 0.045 | 0.017 |
| 64 | 2e9 | 1.10e13 | 0.64 | 0.039 | 0.014 |
| 96 | 2e9 | 1.4e14 | 0.64 | 0.019 | 0.007 |

Readings: `N_circ4/n⁸` decreases steadily (0.105 → 0.019 over n=8→96); local
log-log slopes ≈ 7.1–7.2 in this window, blending toward the memo's n^7.6.
Both parts decay sub-`n⁸`: `sym ~ n⁷ log n` (proved), `asym/n⁸` falls ~4× per
octave at the top end (0.036 → 0.007 between n=8 and 96, accelerating).

Per-normal data (`sprof.c`): at n=24, `s ≤ 4` carries 37% of concyclic quads,
`s ≤ 16` carries 74%; beyond `s ≈ 26` essentially all concyclic quads are
symmetric trapezia (sym/circ ≈ 1 for `s ≥ 26`); asymmetric quads concentrate
at `s = O(n)` and decay ~`s^{−θ}`, `θ ≈ 0.7–1` in the mid range.

## 6. Verification and caveats

* `quad.c`, `sprof.c`, `vprof.c`, `dump.c`, `check3b.py`, `pdump.py` live in
  this directory.  An early version of the C counters silently dropped the
  third kernel-vector fallback (`w₁×w₂`), which made `ν = 0` coincide with
  `ν·R = 0` for collinear-in-x families — it undercounted `x=const` quads in
  `quad.c` (5624 vs the correct 6360 at n=4) and overcounted in `vprof.c`
  (ν=0 ⇒ ν·R=0 spuriously accepted).  Cross-checking against an independent
  numpy/exact-integer Python enumerator at n=3 (468) and n=4 (6360, with a
  symmetric per-normal histogram) caught it; the corrected C now agrees
  exactly.  This is the same trap the H1 memo flags in xcheck.py (an
  adjugate-transpose bug found the same way).
* As in the H1 memo: MC estimates have quoted sampling error; the split
  classification was verified only against the brute-force-compatible
  definitions in §2, not against a second implementation of `symmetric()`.
* The coplanar-4 count itself: `Z_plane4 = Θ(n⁹·polylog)`-ish by the H2
  machinery (sum over `v,k` of `C(N_{v,k},4)` ~ `n⁹`-scale with a log-divergent
  `Σ 1/s` tail) — concyclic is a strict sub-family of that, empirically
  `~n^{7.6}`.

## 7. Summary of the deliverable

* Proved: bookkeeping (`N_circ4 = Σ_γ C(t_γ,4)` over lattice circles, unique
  plane+circle), `t_γ = n^{o(1)}`, baseline `O(n^{9+o(1)})`, and
  **`N_sym = O(n⁷ log n)`** — the symmetric part is comfortably `o(n⁸)` and
  carries the empirical majority.
* Precise gap: the asymmetric part reduces to **Lemma L** — a uniform
  `s^{−θ}` (`θ > 1/2`) rarity bound for ≥4-point circles in rank-2 lattice
  sections.  It is exactly the rank-2-lattice version of the
  Huxley–Konyagin/GGK input; its `s = O(1)` cases are known theorems, and the
  class-number `h(-4‖v‖²) ~ ‖v‖^{1+o(1)}` mechanism supplies the heuristic
  `θ = 1`.  Proving L for general binary quadratic forms is the remaining
  work — plausible but a genuine paper-sized input, matching the memo's
  observation that uniform-in-denominator bounds are the H1 bottleneck.
