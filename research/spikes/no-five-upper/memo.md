# Round 27 — upper bounds for the no-five-on-a-sphere problem in `[n]^3`

Written on branch `research/no-five-upper`; committed together with the lower-bound memo
`research/spikes/no-five-theorem/memo.md` and the exact small-values lane `research/spikes/no-five-exact/`.
Run directory: `research/spikes/no-five-upper/` (`src/` code, `out/` results).
Date: 2026-09-25.  Revised after the referee report `REFEREE-REPORT.md` (minor revision); the changes
are listed in Section 9.  All statements below are labelled **Theorem/Lemma** (complete proof given
here), **Computed** (exact computation, command and hash given), **Numerical** (Monte Carlo or
solver output that is not a certificate), or **Conjecture/Heuristic** (not proved).

## 0. Summary

Let `C(n)` be the largest size of `S ⊂ {0,…,n−1}^3` such that no five points of `S` lie on a
common sphere or plane (exact criterion: every 5-subset of lifted rows `(x, y, z, x²+y²+z², 1)`
has non-zero determinant).  Known: `C(n) ≥ n − o(n)` (Dong–Xu), empirically `≈ 5n/2`, trivial
upper bound `C(n) ≤ 4n`.

**Outcome of this round: no rigorous improvement of `C(n) ≤ 4n` valid for all `n` was found,
and none is claimed.**  What the round establishes rigorously is *why* the natural proof
strategies cannot give one, plus exact small cases:

1. **Theorem 4.1 (linear counting is stuck at 4n).**  The linear relaxation that uses all
   plane/sphere (`≤ 4`) and line/circle (`≤ 3`) cardinality constraints (and `0 ≤ x_p ≤ 1`; other
   valid cardinality constraints exist and are not included, see §4.1) has optimum exactly `4n` for
   all `n ≥ 8100` (explicit, crude
   threshold from an elementary lattice-point lemma), and exactly `4n` for all `n ≥ 2` when
   sphere and circle constraints are dropped.  Certified values for small `n` (constraint
   generator cross-checked by brute force and against the census, §4.1): `LP(3) = 10`,
   `LP(4) = 40/3`, `LP(5) = 20 = 4n` (linear counting beats `4n` at `n = 3, 4` but not at `n = 5`; `LP(6)` was not computed, §4.1).
2. **Theorem 4.2 (slab windows are stuck at 4k).**  Let `W(k,n)` be the maximum of a no-five
   set inside `[n]² × [k]`.  Then `W(k,n) = 4k` for every `n ≥ 4·C(4k,5) + 6k + 1`
   (Schwartz–Zippel).  Hence any argument that only uses the restrictions of `S` to the slabs of a
   *partition* of `[n]` into sets of bounded size (in one axis direction) proves nothing below `4n`
   (Corollary 4.2.2).  Overlapping or sliding windows are not covered by the union bound; for `n`
   larger still, a Lovász Local Lemma argument (Proposition 4.2.3, from the referee report) covers
   them too.  Computed exactly:
   `W(2,3) = 7`, `W(2,n) = 8` for `4 ≤ n ≤ 8`, `W(3,3) = C(3) = 8` (CP-SAT, §4.2).
3. **Theorem 3.5 / Proposition 4.3 (the axis-parallel instance of Thiele's mechanism is vacuous
   in 3D).**  The isosceles-trapezoid mechanism that gives Thiele's `(5n−3)/2` in the plane
   transfers to 3D (Lemma 3.3, for parallel lines of *any* direction).  Its axis-parallel instance,
   which is what Thiele's column argument uses, only constrains pairs on axis-parallel lines; for
   `n ≥ 4` there are `4n`-point sets with four points on every axis plane and no axis-parallel pair,
   so that instance yields no bound below `4n`.  (The witness does violate non-axis instances; see
   the remark after Proposition 4.3.1.)
4. **Computed exact values.**  `C(2) = 4` (proved, §6.3) and `C(3) = 8` (CP-SAT with lazy exact
   clauses, proved optimal, verified from scratch).  Thus `C(n) ≤ 4n − 4` for `2 ≤ n ≤ 3`
   (at `n = 1`, `C(1) = 1 > 0`).  The exact lane `research/spikes/no-five-exact/` proves `C(4) = 11`
   (an 11-point certificate plus a cadical UNSAT proof for 12 points, LRAT-checked); this lane's own
   verification run did not finish and its LP gives only `C(4) ≤ 13`, so `C(4) ≤ 4·4 − 5` holds
   conditional on the exact lane.  **No argument is known that gives `4n − c` for all `n`, for any
   `c ≥ 1`.**
5. **Computational obstruction evidence.**  Exact censuses of degenerate 5-subsets in the full
   grid (`n ≤ 7`) and in random plane-4-regular sets (`n ≤ 96`), an exact Monte Carlo estimate
   of `E(n)` = expected number of further grid points on the circumsphere of four random grid
   points (`n ≤ 128`), and sphere statistics (§5).  In random 4-regular sets the (non-axis)
   coplanar count grows roughly linearly, while the cospherical count grows *sublinearly* in the
   measured range (cospherical/n falls from `≈ 210` at `n = 32` to `≈ 120` at `n = 96`: counts
   grow about ×1.7 while `n` grows ×3); `n²·E(n)` varies slowly (`≈ 900–1600`) for
   `32 ≤ n ≤ 128`, i.e. `E(n) ≈ c/n²` there, which makes the expected
   number of cospherical 5-subsets of a *uniformly random* `4n`-subset of the grid `O(1)` while
   the expected number of coplanar ones grows linearly (§6, **heuristic**).

The honest status: (a) `C(n) ≤ (4 − ε)n` — **open**; (b) `C(n) ≤ 4n − c` for all `n` —
**open**; true with `c = 4` for `2 ≤ n ≤ 3` (proved here) and for `n = 4` (given the exact lane's
`C(4) = 11`), false for `n = 1`; (c) the obstruction analysis in §6 is rigorous where labelled and is
the deliverable of this round.

## 1. Problem and notation

`[n] = {0,…,n−1}`.  For `p = (x,y,z) ∈ Z³` put `u_p = (x, y, z, x²+y²+z², 1) ∈ Z⁵`.  Five
points `p_1..p_5` lie on a common sphere or plane iff `det(u_{p_1},…,u_{p_5}) = 0` (a sphere or
plane is the zero set of `a(x²+y²+z²) + bx + cy + dz + e` with `(a,b,c,d) ≠ 0`; the determinant
vanishes iff such a non-trivial linear form kills all five lifted rows).  A set with no such
5-subset is a **no-five set**.  `C(n)` is the largest no-five subset of `[n]³`.

The 5×5 determinant equals the 4×4 determinant of the lifted differences `u_{p_i} − u_{p_1}`
(`i = 2..5`); each of its 24 terms is a product of one entry of absolute value `≤ 3(n−1)²` and
three of absolute value `≤ n−1`, so `|det| ≤ 72·n⁵ < 2.5·10¹²` for `n ≤ 128`, and the `int64`
arithmetic in `count5.c` is exact there (intermediate cofactors are bounded by `18 n⁴`);
`spheres.c` and `mc_extra.c` use `__int128`.

Exact verifier for a point set: `research/extremal/verifiers/no_five_on_sphere.py` (main
checkout).  All code in this round uses the same criterion (`det5 == 0`).

## 2. Literature (as consulted; arXiv abstracts fetched with `curl` from export.arxiv.org)

* Thiele, *The no-four-on-circle problem*, JCTA 71 (1995) — planar bound `≤ (5n−3)/2` for
  subsets of `[n]²` with no four on a circle or line (proof reconstructed in Theorem 3.5).
* Ghosal, Goenka, Grebennikov, Keevash, Kwan, Pham, arXiv:2607.05255 — no-`(k+1)`-in-line
  in `[n]²` is exactly `kn` for `k ≥ 3` and large `n`; a `2n − o(n)` no-four-on-circle
  construction.  Ghosal–Goenka, arXiv:2609.20447 — extensible no-four-on-circle sets.
* Suk–White, arXiv:2412.02866 — for fixed `d ≥ 3`, subsets of `[n]^d` of size `n^{3/(d+1)−o(1)}`
  with no `d+2` points on a sphere or hyperplane (improving Thiele's `Ω(n^{1/(d−1)})`);
  superseded for `d = 3` by Dong–Xu.
* Dong–Xu, arXiv:2506.18113 — subsets of `[n]^d` of size `n − o(n)` with no `d+2` points on a
  sphere or hyperplane, for every `d ≥ 2` (for `d = 2` improving Thiele's `n/4`, for `d ≥ 3`
  Suk–White); for `d = 3` this `C(n) ≥ n − o(n)` is the best published lower bound.
* No published upper bound below `4n` for `d = 3` was found (consistent with the round-26
  notes `demonstrandum-WRITEUP.md`, which list "adapt Thiele's `d = 2` argument" as the open
  citable target).

## 3. Structural lemmas (complete proofs)

Throughout, `S ⊂ R³` is a no-five set with `|S| ≥ 5`.  (For `n ≥ 3` every extremal subset of
`[n]³` has at least five points: `(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,2)` has lifted
determinant `2 ≠ 0`, computed in §5.)

**Lemma 3.1 (kill lemma).**  (a) No four points of `S` are collinear.  (b) No four points of
`S` are concyclic.  Consequently every line contains at most three and every circle at most
three points of `S`.

*Proof.*  (a) Four collinear points together with any fifth point of `S` span at most a plane.
(b) Let `A,B,C,D ∈ S` lie on a circle `γ` with plane `Π`, centre `O`, radius `r`, unit normal
`ν`, and let `E ∈ S` be a fifth point.  If `E ∈ Π` the five points are coplanar.  Otherwise
the spheres containing `γ` are exactly the spheres with centre `O + tν` and radius²
`r² + t²`, `t ∈ R` (a sphere contains `γ` iff its centre lies on the axis of `γ` and it passes
through one point of `γ`).  `E` lies on the sphere with parameter `t` iff
`|E − O|² − 2t (E − O)·ν + t² = r² + t²`, i.e. `t = (|E−O|² − r²) / (2 (E−O)·ν)`, which is
well defined because `(E−O)·ν ≠ 0`.  So `A,B,C,D,E` are cospherical.  ∎

**Lemma 3.2 (trivial bound and plane-extremal structure).**  `C(n) ≤ 4n`.  If `S ⊂ [n]³` is a
no-five set with `|S| = 4n − t`, then in each of the three axis directions all but at most `t`
of the `n` axis planes contain exactly four points of `S`, and no axis plane contains five.

*Proof.*  Five points in a common axis plane are coplanar; sum over the `n` planes `x = c`.  ∎

**Lemma 3.3 (isosceles trapezoid lemma, 3D).**  Let `L ≠ L'` be parallel lines with common unit
direction `v`, `A ≠ B` on `L`, `C ≠ D` on `L'`.  If `(A+B)·v = (C+D)·v` then `A,B,C,D` are
concyclic.

*Proof.*  `L` and `L'` span a plane `Π`.  Let `ℓ ⊂ Π` be the line through `M = (A+B)/2`
perpendicular to `v`.  Since `A, B ∈ L` are symmetric about `M` along `v`, `ℓ` is the
perpendicular bisector of `AB` inside `Π`.  The midpoint `M' = (C+D)/2` lies on `L'` and
satisfies `M'·v = M·v`, so `M' ∈ ℓ`; as `CD` is parallel to `v` and hence perpendicular to `ℓ`,
`ℓ` is also the perpendicular bisector of `CD` inside `Π`.  The segment `AC` is not parallel to
`v` (its endpoints are on different parallel lines), so its perpendicular bisector in `Π` is not
parallel to `ℓ` and meets `ℓ` in a point `P`.  Then `|PA| = |PB|`, `|PC| = |PD|`, `|PA| = |PC|`,
so the four (distinct) points lie on the circle in `Π` with centre `P`.  ∎

**Corollary 3.3.1 (distinct pair sums).**  Let `S ⊂ [n]³` be a no-five set with `|S| ≥ 5` and
`v ∈ {e₁, e₂, e₃}`.  For each line `L` of direction `v` let `k_L = |S ∩ L| ≤ 3`.  Then the map
`{A,B} ↦ (A+B)·v` is injective on the set of pairs of points of `S` that lie on a common line of
direction `v`; its values lie in `{1,…,2n−3}`; hence `Σ_L C(k_L,2) ≤ 2n − 3`.
Moreover `k_L + k_{L'} ≤ 4` for any two distinct lines `L, L'` of direction `v`.

*Proof.*  Two pairs on distinct parallel lines with equal sums are concyclic (Lemma 3.3),
contradicting Lemma 3.1(b).  Two distinct pairs on the same line with equal sums are disjoint
(if they share a point they are equal), giving four collinear points, contradicting 3.1(a).
`(A+B)·e₁ = x_A + x_B` with `x_A ≠ x_B` in `[0, n−1]` lies in `[1, 2n−3]`.  Two parallel lines
are coplanar, so `k_L + k_{L'} ≥ 5` would give five coplanar points.  ∎

**Lemma 3.4 (coaxial lemma).**  Let `A,B,C ∈ S` lie in the plane `x = c` on a circle with
centre `O = (c, o₂, o₃)`, and let `D, E` lie in the plane `x = c'`, `c' ≠ c`, with
`|D − O'| = |E − O'|` where `O' = (c', o₂, o₃)`.  Then `A,B,C,D,E` are cospherical.

*Proof.*  The spheres through the circle of `A,B,C` have centres `(t, o₂, o₃)` and radius²
`r² + (t−c)²`.  `D` lies on the sphere with parameter `t` iff `|D−O'|² + (c'−t)² = r² + (t−c)²`,
i.e. `|D−O'|² + c'² − c² − 2t(c' − c) = r²`, a linear equation in `t` with non-zero
coefficient, hence solvable, and the solution depends on `D` only through `|D − O'|²`, so the
same sphere contains `E`.  ∎

*Consequence.*  For every triple `T` of points of `S` in an axis plane `x = c` and every other
plane `x = c'`, the points of `S ∩ {x = c'}` have pairwise distinct distances from the
orthogonal projection of the circumcentre of `T`; equivalently, no such projected circumcentre
lies on a perpendicular bisector of a pair of points of `S` in another parallel plane.  This is
an injectivity constraint on rational numbers of unbounded height, not a counting constraint
(see §6).

**Theorem 3.5 (Thiele's planar bound, reconstructed).**  If `T ⊂ [n]²` contains no four points
on a common circle or line, then `|T| ≤ (5n − 3)/2`.

*Proof.*  Columns (lines `x = c`) contain at most three points of `T`.  Let `a`, `b`, `c` be the
numbers of columns containing exactly 3, 2, 1 points; `|T| = 3a + 2b + c` and `a + b + c ≤ n`.
Two points `(x, y₁), (x, y₂)` in the same column form a pair with sum `y₁ + y₂ ∈ [1, 2n−3]`.
Two distinct pairs with the same sum are either disjoint pairs in the same column (four
collinear points) or pairs in different columns, which are concyclic by Lemma 3.3 applied in
the plane (two parallel lines, equal projections of the midpoints); both are excluded.  So the
number of pairs satisfies `3a + b ≤ 2n − 3`.  Therefore
`|T| = 3a + 2b + c = ½(3a + b) + (3/2)(a + b + c) − ½c ≤ ½(2n−3) + (3/2)n = (5n−3)/2`.  ∎

*Remark (why the axis-parallel instance does not transfer).*  In `[n]³` the same argument,
applied to lines of direction `e₁`, gives `Σ_L C(k_L,2) ≤ 2n − 3` (Corollary 3.3.1), but the
points of `S` are distributed over `n²` lines, so for `n ≥ 4` the constraint is satisfiable with
`k_L ≤ 1` for all `L` and `|S| = 4n` (Proposition 4.3.1).  The planar argument bites only because
`[n]²` has just `n` columns.  Lemma 3.3 itself holds for parallel lines of any direction; the
non-axis instances are discussed after Proposition 4.3.1.

## 4. Rigorous obstruction theorems

### 4.1 The linear relaxation has value `4n`

Every constraint used below is valid for every no-five set `S` with `|S| ≥ 5` (Lemma 3.1 and
the definition), so the optimum of the following LP is an upper bound for `C(n)` (`n ≥ 3`).  It
contains all plane/sphere (`≤ 4`) and line/circle (`≤ 3`) cardinality constraints, not every valid
cardinality constraint: for example `Σ_{p ∈ v+[3]³} x_p ≤ 8 = C(3)` is valid for every translate
`v + [3]³ ⊂ [n]³`, and at `n = 3` it alone cuts the LP value from 10 to 8.

```
LP(n) = max Σ_p x_p   over  x : [n]³ → [0,1]  subject to
        Σ_{p∈Π} x_p ≤ 4 (every plane Π),   Σ_{p∈σ} x_p ≤ 4 (every sphere σ),
        Σ_{p∈ℓ} x_p ≤ 3 (every line ℓ),    Σ_{p∈γ} x_p ≤ 3 (every circle γ).
```

**Lemma 4.1.1 (lattice points on circles and spheres; elementary).**  Let `γ ⊂ R³` be a circle
of radius `R`.  (i) `|γ ∩ Z³| ≤ 2 + 10 R^{2/3}`.  (ii) `|γ ∩ [n]³| ≤ 12 + 20 n^{2/3}` for every
`n ≥ 1`.  (iii) Every sphere `σ` satisfies `|σ ∩ [n]³| ≤ 12n + 20 n^{5/3}`.

*Proof.*  (i) If `|γ ∩ Z³| ≤ 2` there is nothing to prove.  Three lattice points on `γ` are
non-collinear, so they span the plane `Π` of `γ`,
which is therefore a rational plane `{p : ν·p = d}` with primitive `ν ∈ Z³`; `Π ∩ Z³` is a
translate of the two-dimensional lattice `ν^⊥ ∩ Z³`, whose covolume is `|ν| ≥ 1`.  Hence a
triangle with vertices in `Π ∩ Z³` has area `≥ 1/2`.  If the three points lie on an arc of length
`ℓ`, the side lengths are `≤ ℓ` (chord ≤ arc) and the area is `abc/(4R) ≤ ℓ³/(4R)`; thus
`ℓ ≥ (2R)^{1/3}`, i.e. an arc of length `< (2R)^{1/3}` contains at most two lattice points.
Cut `γ` into `m = ⌊2πR/(2R)^{1/3}⌋ + 1` half-open arcs of equal length `< (2R)^{1/3}`:
`|γ ∩ Z³| ≤ 2m ≤ 2 + 4πR/(2R)^{1/3} = 2 + 2^{5/3}π R^{2/3} < 2 + 10 R^{2/3}`.
(ii) If `R ≤ n`, (i) gives `≤ 2 + 10 n^{2/3}`.  If `R > n`, let `K = Π ∩ [0,n−1]³`, a convex
polygon with at most six sides (or a segment or a point) and diameter `≤ (n−1)√3 < 2n < 2R`,
so `γ ⊄ K`.  `γ ∩ K` is a closed subset of `γ` whose connected components are closed arcs,
possibly single points; every component has its endpoints in `γ ∩ ∂K`, which has at most two
points per side, hence at most `12` points.  So if `a` components have positive length, at
most `12 − 2a` components are single points (each with at most one lattice point), and `a ≤ 6`.
A component of positive length has chord `≤ diam K < √3·R` and cannot contain two antipodal
points of `γ` (they are `2R > diam K` apart), so it is a minor arc with central angle `θ`
satisfying `2R sin(θ/2) < √3 R`, i.e. `θ < 2π/3`, and its length is
`Rθ = chord·(θ/2)/sin(θ/2) ≤ 1.2092·(n−1)√3 < 2.095 n`.  Covering it by
`⌊ℓ/(2R)^{1/3}⌋ + 1` consecutive sub-arcs of equal length `< (2R)^{1/3}` (half-open, except that the
last piece is closed so that the closed arc is covered; each piece still has length
`< (2R)^{1/3}`, so the count is unaffected) shows it contains at most
`2 + 2ℓ/(2R)^{1/3}` lattice points.  Altogether
`|γ ∩ [n]³| ≤ (12 − 2a) + a(2 + 2·2.095 n/(2R)^{1/3}) ≤ 12 + 6·4.19 n/(2n)^{1/3} < 12 + 20 n^{2/3}`.
(iii) `σ ∩ {z = c}` is a circle, a point or empty, for each of the `n` values `c ∈ [n]`.  ∎

**Lemma 4.1.3 (circles, from the referee report).**  For `n ≥ 1` every circle contains at most
`2n` points of `[n]³`; for `n ≥ 3` this is `≤ 3n²/4`.

*Proof.*  If the circle does not lie in a plane `x = c`, it meets each of the `n` planes `x = c`
in at most 2 points.  If it lies in a plane `x = c`, it meets each of the `n` lines
`{x = c, y = c'}` in at most 2 points.  Finally `2n ≤ 3n²/4` iff `n ≥ 8/3`.  ∎  (This is consistent
with the computed maximum of `8 ≤ 10` points on a circle at `n = 5`.)

**Theorem 4.1.2.**  (a) For every `n ≥ 2` the LP with only the plane and line constraints has
optimum exactly `4n`.  (b) For `n ≥ 3`, `LP(n) = 4n` whenever every sphere contains at most `n²`
points of `[n]³` (the circle condition needed by the uniform point holds automatically by
Lemma 4.1.3); in particular `LP(n) = 4n` for all `n ≥ 8100`, and (**Computed**) for `n = 5`.  (c) (**Computed, certified**) `LP(3) = 10`, `LP(4) = 40/3`, so
`C(3) ≤ 10`, `C(4) ≤ 13`.

*Proof.*  Upper bound `4n` in all cases: add the `n` constraints of the axis planes `x = c`.
(a) `x ≡ 4/n²` is feasible: a plane not parallel to some axis direction `e_i` meets each of the
`n²` lines of direction `e_i` in at most one point, so it contains `≤ n²` grid points and gets
weight `≤ 4`; a line contains `≤ n` points and gets `4/n ≤ 3`.  (b) The same point gives every
sphere weight `≤ 4·n²/n² = 4` under the hypothesis, and every circle weight `≤ 4·2n/n² = 8/n ≤ 3`
by Lemma 4.1.3.  For `n ≥ 8100` Lemma 4.1.1(iii) gives `4(12n + 20n^{5/3})/n² = 48/n + 80/n^{1/3} ≤ 4`
(slicing alone, with Lemma 4.1.3, would only give `2n²` per sphere, so Lemma 4.1.1 is still needed
for spheres).  For `n = 5` the hypothesis holds: `spheres.c` enumerates all `539 397` spheres with
`≥ 5` grid points that contain a non-coplanar 5-subset (completeness checked against the census,
see below) and the maximum occupancy is `24 < 25`; a sphere all of whose grid points are concyclic
carries at most `2n = 10` of them (Lemma 4.1.3).  (The circle generator of `lp_bound.py` reports a
maximum of 8 points on a circle at `n = 5`, cross-checked by brute force, in line with Lemma 4.1.3.)  Independently `lp_bound.py 5` (with all `570 042` constraints) returns primal
value `20` with an exact dual certificate of value `20`.
(c) `lp_bound.py 3`, `lp_bound.py 4`: GLOP primal `10` and `13.333…`, exact dual
certificates `10` and `40/3` (dual multipliers rounded to rationals with denominator `≤ 10⁶`,
bound evaluated exactly as `Σ rhs·y + Σ_p max(0, 1 − Σ_{c∋p} y_c)`, which is a valid bound for
every `y ≥ 0`).  ∎

*Verification of the constraint generator.*  Validity and completeness are checked separately.
Validity (all that the upper bounds `C(n) ≤ LP(n)` need): `lp_bound.py` recomputes the lifted
affine rank of every constraint's point set with exact integer arithmetic and aborts unless every
rhs-4 set has rank `≤ 3` (a genuine plane or sphere) and every rhs-3 set rank `≤ 2` (a genuine
line or circle).  Completeness (needed for the claim that the certified value *is* `LP(n)`):
`src/xcheck_circles.py` regenerates every circle and line with `≥ 4` grid points by brute force —
the closures of all 4-subsets of lifted rank `≤ 2` — and, for `n = 3`, every sphere and plane
with a non-coplanar 5-subset as the closures of all 5-subsets of rank exactly `3`; the sets agree
exactly with the generator's (`364` and `948` at `n = 3`, `3848` circles/lines at `n = 4`,
`out/xcheck-n3.txt`, `out/xcheck-n4.txt`).  `src/xcheck_spheres.py` checks the sphere lists of
`spheres.c` against the independent census of `count5.c`: every listed sphere is cospherical,
maximal (equal to its closure) and distinct, and `Σ_S C(m_S,5) − Σ_G C(|G|,5)·#{S ⊇ G}` (sum over
listed spheres `S` with `m_S` grid points and circles `G` with `≥ 5` grid points) equals the census
count of cospherical non-coplanar 5-subsets, so no sphere carrying a non-coplanar 5-subset is
missing (`out/xcheck-n3.txt`, `out/xcheck-n4.txt`, `out/xcheck-n5.txt`; spheres all of whose grid
points lie on one circle are omitted by construction and are redundant for the LP).  An earlier
version of the generator keyed circles by plane and centre only and silently dropped concentric
circles (`45` of the `364` at `n = 3`); the brute-force comparison caught it, and the certified
values `10`, `40/3`, `20` did not change after the fix (the bounds were valid throughout, since
validity does not depend on completeness).

*Remarks.*  (1) Sphere occupancy exceeds `n²` for `n = 2,3,4,6` (`8, 12, 24, 48` points on one
sphere: `{0,1}³`, `|p − (1,1,1)|² = 2`, `|p − (1.5,1.5,1.5)|² = 2.75`, `|p − (2.5,2.5,2.5)|² =
8.75`), so the uniform point is infeasible there; the threshold `8100` in (b) is crude and is
where the elementary Lemma 4.1.1 first beats `n²`; classical bounds on `r₃(m)` give
`O(n^{1+ε})` occupancy but with no explicit constant, which is why they are not used.
For `n = 6` the sphere enumeration finished (`4 975 281` spheres with `≥ 5` grid points, maximum
occupancy `48`), but the LP with that many constraints was stopped after 15 minutes because of
host memory pressure, so `LP(6)` is **not computed** (it may be below `24`, since the uniform
point is infeasible there).  (2) The LP value equals `4n` at `n = 5` already, although the exact values `C(3) = 8`,
`C(4) = 11` give no hint that the gap `4n − C(n)` closes at `n = 5`; **any proof of `C(n) < 4n` must therefore use non-linear (interaction) information,
not cardinality constraints on planes/spheres/lines/circles alone.**

### 4.2 Slab windows: `W(k,n) = 4k` for large `n`

**Definition.**  `W(k,n)` = maximum size of a no-five subset of `[n]² × [k]` (points with
`z ∈ {0,…,k−1}`).  Trivially `W(k,n) ≤ 4k`, and `W(k,n)` is non-decreasing in `n`.

**Theorem 4.2.1.**  Let `k ≥ 1`, `n ≥ n₀(k) := 4·C(4k,5) + 6k + 1`, and let `Z ⊆ [n]` be any
set of `k` values.  Then there is a no-five subset of `[n]³` with exactly four points on each
plane `z = c`, `c ∈ Z`, and no other points.  In particular `W(k,n) = 4k` (take `Z = [k]`), and
the same holds for any `k` planes in any one axis direction, consecutive or not.

*Proof.*  For each `c ∈ Z` take four points `P_{c,1..4} = (X_{c,j}, Y_{c,j}, c)` with all
`8k` coordinates `X_{c,j}, Y_{c,j}` independent and uniform in `[n]`.  Fix a 5-subset `T` of
the index set.  Its lifted determinant `D_T` is a polynomial in the `10` coordinates of `T`
with the `z`-entries fixed.  *Degree:* each term of the `5×5` expansion takes one entry from each
column; the columns `x, y, z, x²+y²+z², 1` contribute degrees `1, 1, 0, 2, 0`, so
`deg D_T ≤ 4`.  *Non-vanishing:* the five `z`-values of `T` are not all equal (at most four
indices per plane), so one can choose four of the five points with at least two distinct
`z`-values, one at a time, each outside the affine span of the previous ones: this is possible
because if all previous points lie in the plane of the next one there are at most two of them
(at most three of the four chosen points share a `z`-value), so their span is a point or a
line, and otherwise the span meets that plane in a set of dimension `≤ 1`.  The four points
are then non-coplanar, their circumsphere is unique, and
the fifth point can be chosen in its plane `z = const` off that sphere (a plane meets a sphere in
at most a circle).  At this real point `D_T ≠ 0`, so `D_T` is a non-zero polynomial.  By the
Schwartz–Zippel lemma `Pr[D_T = 0] ≤ 4/n`.  Two indices in the same plane give the same point
with probability `1/n²`; there are `6k` such index pairs.  A union bound gives
`Pr[some D_T = 0 or some coincidence] ≤ 4·C(4k,5)/n + 6k/n² ≤ (4·C(4k,5) + 6k)/n < 1`
for `n ≥ n₀(k)`, so the required `4k`-point no-five set exists.  ∎

**Computed** (CP-SAT with lazy exact clauses, `src/window_max.py`; "proved optimal" means the
final CP-SAT solve on the accumulated clause relaxation reached `OPTIMAL`, which is a rigorous
upper bound, and the returned set was re-verified from scratch, a rigorous lower bound): the
full table is in §5.  `W(2,3) = 7`; `W(2,n) = 8` for `4 ≤ n ≤ 8`; `W(3,3) = C(3) = 8`.  The runs
for `W(3,4)` and `W(4,4) = C(4)` did not finish (`out/windows.txt`); `C(4) = 11` is taken from the
exact lane `research/spikes/no-five-exact/`.

So the thickness-2 slab is saturated (`W = 4k = 8`) from `n = 4` on, far below `n₀(2) = 237`.

**Corollary 4.2.2 (slicing is stuck).**  Fix `k` and `n ≥ n₀(k)`.  Any bound on `C(n)` obtained
by partitioning `[n]` into sets `Z_1, …, Z_m` of size `≤ k` (intervals or not) and using only
that each `S ∩ ([n]² × Z_i)` is a no-five set is `≥ Σ_i 4|Z_i| = 4n`.  The same holds for
partitions in any one axis direction (`x`, `y` or `z`).  This covers *partitions* only: for
overlapping or sliding windows the union bound over all windows fails (the total failure
probability is `≈ 4·C(4k,5)`, not below 1).  (Arguments that combine the four-per-plane structure
in *several* directions are not covered either: the random slab construction has only `4k` points
and says nothing about sets that are four-per-plane in all three directions.)

**Proposition 4.2.3 (sliding windows; Lovász Local Lemma, from the referee report).**  Let `k ≥ 1`
and `n ≥ 4e(5·C(8k−5,4) + 16)`.  Then there is a `4n`-point set in `[n]³` with exactly four points on
every plane `z = c`, `c ∈ [n]`, in which every five points of z-span `< k` are in general position
(no five on a sphere or plane).  Hence no argument that only uses the restrictions of `S` to windows
of `k` consecutive planes `z = c` (overlapping or not) proves anything below `4n` for such `n`.

*Proof (variable version of the LLL).*  Take the points `(X_{c,j}, Y_{c,j}, c)`, `c ∈ [n]`,
`j = 1..4`, with all coordinates independent and uniform in `[n]`.  Bad events: `D_T = 0` for each
5-subset `T` of z-span `< k`, which has probability `≤ 4/n` by the degree and non-vanishing argument
of Theorem 4.2.1; and the coincidence of two points in the same plane, probability `1/n² ≤ 4/n`.  An
event is determined by the coordinates of at most five points.  A given point lies in at most
`C(8k−5, 4)` of the 5-subset events (the other four points come from the at most `4(2k−1) − 1 = 8k−5`
other points in planes at z-distance `< k`) and in 3 coincidence events, so each event shares
variables with at most `d = 5(C(8k−5,4) + 3)` others.  The symmetric LLL condition
`e·(4/n)·(d+1) ≤ 1` is `n ≥ 4e(5·C(8k−5,4) + 16)`; then with positive probability no bad event occurs.
Any five points in a window of `k` consecutive planes have z-span `≤ k−1`.  ∎

### 4.3 The axis-parallel instance of Thiele's mechanism is vacuous in three dimensions

**Proposition 4.3.1.**  For every `n ≥ 4` the set
`S_n = {(x, y, x + y mod n) : x ∈ [n], (y − x) mod n ∈ {0,1,2,3}}`
has `4n` points, exactly four points on every axis plane, and no two points on a common
axis-parallel line.  Consequently the constraints of Lemma 3.2 (`≤ 4` per axis plane) and
Corollary 3.3.1 (`Σ_L C(k_L,2) ≤ 2n−3`, `k_L + k_{L'} ≤ 4`, `k_L ≤ 3`) admit a `4n`-point
solution, and no bound below `4n` can follow from them.

*Proof.*  `S_n` is a set of cells `(x,y)` of the cyclic Latin square `L(x,y) = x + y mod n`
with symbol `z = L(x,y)`.  Two points on an axis-parallel line would share two coordinates: the
same `(x,y)` is impossible (one symbol per cell), the same `(x,z)` or `(y,z)` is impossible
because a symbol occurs once per row and once per column.  Row `x` contains the four cells
`y = x + j`, `j = 0..3`, distinct since `n ≥ 4`; column `y` contains the four cells `x = y − j`.
Symbol `z` occurs in the cells with `x + y ≡ z`, `y − x ≡ j`, i.e. `2y ≡ z + j (mod n)`: for odd
`n` exactly one `y` per `j`, four cells; for even `n` two solutions for each of the two values
`j ∈ {0,1,2,3}` with `z + j` even, again four cells.  ∎

(`S_n` itself is of course far from a no-five set — it lies on two planes — the point is only
that the *counting* consequences of the axis-parallel trapezoid lemma (Corollary 3.3.1 with
`v ∈ {e₁,e₂,e₃}`) are already satisfied by a `4n`-point configuration, so they cannot be the engine
of a proof that `C(n) < 4n`.  The coaxial Lemma 3.4 is an injectivity constraint, not a counting
constraint, and Proposition 4.3.1 says nothing about it.)

*Remark (non-axis directions).*  Lemma 3.3 holds for parallel lines of *any* direction `v`, and
`S_n` violates the non-axis instances: for every `n ≥ 4` the plane `x = 0` contains the four
collinear points `(0,j,j)`, `j = 0..3`, and with `v = (0,1,1)` the pairs `{(0,0,0),(0,3,3)}` and
`{(0,1,1),(0,2,2)}` have equal sums, which Lemma 3.3 and Lemma 3.1(a) forbid.  So Proposition 4.3.1
does not show that the full directional mechanism is vacuous.  What can be said (referee's
observation): for primitive `v ∈ Z³` with `|v|₁ ≥ 2` the directional counting bound
`Σ_{L ∥ v} C(k_L,2) ≤ 2(n−1)|v|₁ + 1` (the number of possible values of `(A+B)·v`) holds
automatically for any `4n`-point set with no three collinear points, because then the pairs on lines
of one direction are disjoint, so there are at most `2n ≤ 4n − 3` of them.  Hence a `4n`-point set
with four points on every axis plane, no axis-parallel pair and no three collinear points would make
the whole directional counting mechanism vacuous.  `S_n` is not such a set, and we have not
constructed one.

## 5. Computations (exact unless stated; commands in §8, hashes of committed files in `out/SHA256SUMS`)

All degenerate-5-subset counts are exact integer computations (`count5.c`, `int64`, verified
against an independent pure-Python Bareiss determinant census on the `n = 3` grid —
`1134 / 1140 / 13752` — and on a random 40-point set — `258 / 410 / 2870`, `out/xcheck40.txt`).
"Random plane-4-regular set" = `{(i, σ_j(i), τ_j(i)) : i ∈ [n], j = 1..4}` for four independent
uniformly random pairs of permutations, resampled until the `4n` points are distinct
(`rand4reg.py`, seeds 1–3); every axis plane then contains exactly four points, so all
degenerate 5-subsets are "other coplanar" or "cospherical".

<!-- TABLES -->
The tables are in `research/spikes/no-five-upper/out/tables.md` (rendered by `src/make_tables.py`;
its LP-constraint column was corrected by hand in the revision, see the note in that file).

Reading the tables:

* Full grid: cospherical (non-coplanar) 5-subsets outnumber coplanar ones about `8 : 1` at
  `n = 7`; between `n = 3` and `n = 7` the cospherical count grows like `n^{12.4}` and the
  non-axis coplanar count like `n^{12.8}` (both still far from their asymptotic exponents, which are
  heuristically `≤ 10 + ε` and `11`).
* Random plane-4-regular sets: cospherical violations per unit `n` range over `≈ 120–230` for
  `8 ≤ n ≤ 96`, but the trend is *sublinear* from `n = 32` on (cospherical/n `≈ 210` at `n = 32`,
  `≈ 175` at `n = 48, 64`, `≈ 120` at `n = 96`: counts grow about ×1.7 while `n` grows ×3), consistent
  with `n²·E(n)` varying slowly; (non-axis) coplanar violations are `≈ 16–51 · n`; the prediction `8.53·n²·E(n)` from the
  Monte Carlo (last column of the `E(n)` table, derived from `C(4n,5)·E(n)/n³`) matches the
  cospherical counts within `≈ 15 %` for `n ≥ 32`.
* `E(n)`: `n·E(n)` peaks near `n ≈ 12–16` (`≈ 32`) and then decreases; `n²·E(n)` is roughly
  flat, `≈ 900–1600`, for `32 ≤ n ≤ 128` (the `n = 128` value rests on `10⁴` samples with a
  heavy-tailed histogram, so its standard error is of order `10 %`).  **Numerical.**
* Violating spheres at `n = 32` (seed 1; `sphere_stats.py`, exact rational circumspheres): the
  `6812` cospherical 5-subsets lie on `6107` distinct spheres, `5981` of which carry exactly five
  set points (`121` carry six, `5` carry seven); centre denominators: `q = 2` for `1606`
  spheres, `q = 1` for `214`, even `q ≤ 24` dominate, and about `2500` spheres have `q > 25`.
  The violations are spread over many "generic" spheres, not concentrated on few symmetric
  ones.
* `C(3) = 8` (`W(3,3)`, proved optimal by CP-SAT on the accumulated exact clauses, incumbent
  re-verified by a full census).  `LP(3) = 10`, `LP(4) = 40/3`, `LP(5) = 20 = 4n`.

## 6. Obstruction analysis

### 6.1 What any proof of `C(n) < 4n` must do (rigorous consequences of §4)

Let `S ⊂ [n]³` be a hypothetical no-five set with `|S| = 4n`.  By Lemma 3.2 it has exactly four
points on every axis plane in all three directions.  A proof must derive a contradiction from
this, and by §4:

1. it cannot be a weighted sum of cardinality constraints on planes, spheres, lines and circles
   (Theorem 4.1.2: such sums give `≥ 4n` for `n = 5` and for all `n ≥ 8100`; at `n = 3, 4` the
   uniform point `x ≡ 4/n²` is infeasible because some spheres there carry more than `n²` grid
   points — by Theorem 4.1.2(b) and Lemma 4.1.3 that is the only way it can fail for `n ≥ 3` — and
   the LP values there are `LP(3) = 10`, `LP(4) = 40/3`; at `n = 5`, where no sphere does,
   `LP(5) = 20`);
2. it cannot look only at the points on a bounded number of planes in one axis direction,
   consecutive or not (Theorem 4.2.1), nor combine such restrictions over a partition into
   bounded slabs (Corollary 4.2.2), nor, for `n ≥ 4e(5·C(8k−5,4)+16)`, over all windows of `k`
   consecutive planes (Proposition 4.2.3);
3. it cannot rest on the counting consequences of the axis-parallel trapezoid lemma alone
   (Corollary 3.3.1 with axis directions; Proposition 4.3.1): those are satisfied by the
   Latin-square configurations `S_n`, which have four points per axis plane and no axis-parallel
   pairs.  (Non-axis directions and the coaxial injectivity constraint are not covered by this.)

So the contradiction must come from the *joint* four-per-plane structure in all three
directions interacting with the sphere condition, through constraints that are non-linear in
the indicator vector and global in position.  The available rigid constraints of that kind
(Lemmas 3.1, 3.3, 3.4) are all *injectivity* statements: for every non-collinear triple
`T ⊂ S` the sphere-pencil parameter `t(q) = (|q − O_T|² − r_T²) / (2 (q − O_T)·ν_T)` is
injective on `S \ plane(T)`; for triples in axis planes this is the coaxial form (distinct
distances from projected circumcentres); for axis-parallel pairs it is the pair-sum form.  Only
the last of these takes values in a set of size `O(n)`, and it needs axis-parallel pairs, which
`S` need not have.  The general pencil parameters are rationals whose denominators are
unbounded in `n` (already the circumcentre denominators in the `n = 32` sample spread over
`> 25` values with a long tail), so no pigeonhole argument is available from them without a
new idea that controls their heights.

### 6.2 What the computations say about the two possible truths

Two scenarios are consistent with everything known:

**(A) `C(n) = 4n − o(n)`.**  Then no `(4 − ε)n` bound exists.  Support: (i) the Monte Carlo
gives `E(n) ≈ 1300/n²` for `32 ≤ n ≤ 128`, so a *uniformly random* `4n`-subset of the grid has
`≈ C(4n,5)·E(n)/n³ ≈ 8.5·n²·E(n) ≈ 10⁴` expected cospherical 5-subsets, varying slowly with `n`,
against `Θ(n)` coplanar ones (the plane-4-regular samples confirm both orders of magnitude);
(ii) in the planar no-`(k+1)`-in-line problem the trivial bound `kn` is attained for `k ≥ 3`
and large `n` (Ghosal et al.), via pseudorandom hypergraph matchings, a deletion step for the
few "heavy" lines and a randomised switching step; the obvious analogue here is "no five in a
plane in `[n]³`", whose trivial bound is the same `4n`, and if that analogue holds with a
sphere-generic construction, `C(n) = 4n − o(n)` follows.  **Heuristic.**

**(B) `C(n) ≤ (4 − ε)n`.**  Support: the empirical values `C(n) ≈ 5n/2` for `n ≤ 26`
(round 26), and the exact values `C(3) = 8` (this lane) and `C(4) = 11` (exact lane
`research/spikes/no-five-exact/`), gaps `4, 5` from `4n`.  These are
small-`n` data; in scenario (A) the gap `4n − C(n)` would still be large at such `n` because the
switching/deletion constructions only work for large `n`.  No mechanism for (B) is known.

The computations cannot discriminate between (A) and (B).  What they do suggest (**numerical**)
is that in random-like sets the cospherical obstruction grows *sublinearly* in the measured range
(counts ×1.7 for `n` ×3 between `n = 32` and `96`), while the coplanar one grows roughly linearly.
If that persists, a proof of (B) — if true — must exploit the coplanar structure at least as much
as the sphere structure, i.e. it must first prove the (open, to our knowledge) statement that no
`4n − o(n)` points of `[n]³` avoid five coplanar points, or else use spheres in a way that
random-like sets do not "see".

*Cross-memo note (lower bounds).*  The same data bear on the lower-bound memo
`research/spikes/no-five-theorem/memo.md`.  Writing `Z_sphere(n)` for the number of degenerate,
non-coplanar 5-subsets of `[n]³`, one has `Z_sphere(n) ≤ C(n³,4)·E(n) ≤ 5·Z_sphere(n)`, so
`Z_sphere(n)/n^{11} ≈ n·E(n)/120`, which falls from `0.27` at `n = 16` to `0.084` at `n = 128`
(table of §5).  That memo's Proposition P shows that `Z_sphere(n) = o(n^{11})` together with a
rigorous coplanar count `Z_plane(n) ≤ (K + o(1)) n^{11}`, `K ≈ 0.072`, would give
`C(n) ≥ (1.03 − o(1)) n` by plain random deletion.  Both hypotheses are open; the `E(n)` data here
support the first, and support the `n^{10+o(1)}` heuristic of §6.4 rather than a `Θ(n^{11})` count.

### 6.3 Constant improvements

* `C(2) = 4 = 4n − 4` (all eight points of `{0,1}³` are cospherical, so `C(2) ≤ 4`; any 4 points
  have no 5-subset).
* `C(3) = 8 = 4n − 4` (**Computed**, this round; agrees with the exact lane).
* `C(4) = 11 = 4n − 5` (exact lane `research/spikes/no-five-exact/`: an 11-point certificate
  and a cadical UNSAT proof at 12 points, LRAT-checked; not re-verified in this lane, whose run
  `window_max.py 4 4` did not finish and whose LP gives only `C(4) ≤ 13`).
* `n = 1`: `C(1) = 1`, so no bound of the form `4n − 4` holds there; the `4n − 4` statements
  above are for `2 ≤ n ≤ 3` (proved) and `n = 4` (via the exact lane).
* `n = 5`: linear counting gives only `C(5) ≤ 20 = 4n`.
* No argument giving `C(n) ≤ 4n − 1` for all `n` is known.  The natural candidate — "a
  plane-4-regular set in all three directions cannot be a no-five set" — is exactly the
  statement that the LP/Latin obstructions do not address; deciding it for `n = 5, 6` is a
  finite SAT question (the exact lane's target).

### 6.4 Heuristic asymptotics of degenerate 5-subsets (not proved)

* Coplanar 5-subsets of `[n]³`: `Θ(n^{11})` (five points on a plane with `Θ(n²)` grid points;
  the axis-plane count alone is `3n·C(n²,5) − 3n²·C(n,5) ≈ n^{11}/40`; summing over all lattice
  planes gives the heuristic constant `K_* ≈ 0.072`, see the lower-bound memo's Lemma K).
* Cospherical, non-coplanar 5-subsets: `E(n)·C(n³,4)/5 ≈ E(n)·n^{12}/120`; with
  `E(n) ≈ 1300/n²` this is `≈ 11·n^{10}`, i.e. `O(n^{10+ε})` if `E(n) = O(n^{−2+ε})`, which is
  what lattice-point heuristics for spheres with rational centres of denominator `q` predict
  (`≈ R/q`-type counts averaged over the denominator distribution).  The measured `n = 7` value
  `4.79·10⁸ ≈ 1.7·7^{10}` is still above the asymptotic regime.
* For a random plane-4-regular set: coplanar `≈ 50n` (measured), cospherical `≈ 8.5·n²·E(n)`
  (measured to `±15 %`), the latter bounded if `E(n) = O(n^{−2})`.

## 7. What could work next (not attempted here, or attempted and abandoned)

1. **The plane-only problem.**  Determine whether the largest subset of `[n]³` with no five
   coplanar points has size `4n − o(n)`.  A `(4−ε)n` upper bound there would transfer to `C(n)`
   verbatim; a `4n − o(n)` construction there (by the Ghosal et al. machinery: heavy planes
   are the axis planes and the `O(n²)`-point rational planes) would settle scenario (A) up to
   making the construction sphere-generic, which the `E(n)` data suggests costs only `O(1)`
   deletions per heavy-sphere family.  This is the decisive sub-question.
2. **Height control for pencil parameters.**  The injectivity constraints of §6.1 become
   counting constraints if the pencil parameters of a triple `T` restricted to `S` can be shown
   to lie in a set of size `< |S| − 3` (for instance if the circumcentres of all triples in a
   fixed axis plane could be forced to have bounded denominators).  Nothing of this kind is
   true for arbitrary sets; it would have to be extracted from the four-per-plane structure.
3. **Finite certificates.**  `C(5)`, `C(6)` by SAT with DRAT proofs (exact lane).  If the gap
   `4n − C(n)` keeps growing (`4, 4, 5, …`) that is weak evidence for (B); if it stalls, for (A).
4. **Abandoned here:** a `4n − c` argument from corner/boundary planes (the boundary planes
   are not geometrically special for spheres); Schwartz–Zippel over permutation-structured
   families (the coordinates are dependent, so no polynomial-identity bound applies); random
   deletion from plane-4-regular sets (needs `Θ(n)` deletions for the coplanar violations
   alone, giving nothing beyond the known `5n/2` heuristics).

## 8. Reproduction

Environment: a Python 3.12 environment with numpy, sympy, ortools and pysat, and `cc -O3`.  All runs under `nice -n 15`, at most three concurrent.  From the run
directory:

```
cc -O3 -o src/count5 src/count5.c; cc -O3 -o src/spheres src/spheres.c; cc -O3 -o src/mc_extra src/mc_extra.c
for n in 3 4 5 6 7; do ./src/count5 grid $n; done                     # full-grid census (n=7: 336 s wall)
for n in 8 12 16 24 32 48 64 96 128; do for s in 1 2 3; do python src/rand4reg.py $n $s out/r4-n$n-s$s.txt; done; done
for f in out/r4-n*-s*.txt; do ./src/count5 file $f; done               # random-set census (n=96: 750 s wall)
./src/count5 file out/r4-n32-s1.txt out/r4-n32-s1-spheres.txt          # dump cospherical 5-subsets
python src/sphere_stats.py out/r4-n32-s1.txt 32 out/r4-n32-s1-spheres.txt
for n in 3 4 5 6 8 12 16 24 32 48 64 96 128; do ./src/mc_extra $n SAMPLES 7; done   # samples as in the table
python src/window_max.py N K 900                                       # W(K,N); (3,3) takes ~12 min
./src/spheres N 5 > out/spheres-nN.txt; python src/lp_bound.py N out/spheres-nN.txt   # N = 3,4,5,6
python src/xcheck_circles.py N out/spheres-nN.txt                     # N = 3,4 (run inside src/)
python src/xcheck_spheres.py N out/spheres-nN.txt CENSUS [SAMPLE]         # N = 3,4,5; CENSUS = sphere count of count5
python src/make_tables.py                                              # regenerates the tables of §5
shasum -a 256 src/* out/*.txt out/*.log > out/SHA256SUMS
```

Files: `src/count5.c` (census), `src/rand4reg.py` (random plane-4-regular sets),
`src/sphere_stats.py` (exact circumspheres of dumped 5-subsets), `src/mc_extra.c` (exact
Monte Carlo for `E(n)`), `src/window_max.py` (CP-SAT window maxima), `src/spheres.c` (all
spheres with `≥ 5` grid points), `src/lp_bound.py` (LP + exact dual certificate),
`src/xcheck_circles.py`, `src/xcheck_spheres.py` (brute-force / census cross-checks of the
constraint generator), `src/make_tables.py`.  Results: `out/*.txt`.  The large sphere lists
`out/spheres-n5.txt` and `out/spheres-n6.txt` are larger than 1 MB, are not committed, and are
reproducible from the commands above; `out/SHA256SUMS` lists the committed files only.  Compiled
binaries (`src/count5`, `src/spheres`, `src/mc_extra`) are not committed.  Because the sphere lists
are absent, re-running `make_tables.py` on the committed files drops the `n = 5, 6` rows of the last
table; `out/tables.md` is therefore kept as generated, with a hand correction noted in the file.

## 9. Revision response (referee report `REFEREE-REPORT.md`, verdict: minor revision)

| # | Referee item | Change in this revision |
|---|---|---|
| 1 | Thiele transfer overstated; "saturated" misapplied to the coaxial lemma | Summary item 3, the remark after Theorem 3.5, the §4.3 heading and §6.1 item 3 now speak of the *axis-parallel instance*; Lemma 3.3 is stated to hold for every direction; a remark after Proposition 4.3.1 records that `S_n` violates the non-axis instance (`(0,j,j)`, `v = (0,1,1)`) and the referee's observation that for `|v|₁ ≥ 2` the directional count is automatic in sets with no three collinear points; the coaxial lemma is described as an injectivity constraint that Proposition 4.3.1 does not address. |
| 2 | Slab claim covers partitions only | Summary item 2 and Corollary 4.2.2 restricted to partitions, with the reason the union bound fails for sliding windows; new Proposition 4.2.3 (the referee's LLL extension, arithmetic re-checked: `d = 5(C(8k−5,4)+3)`, `n ≥ 4e(5·C(8k−5,4)+16)`) covers sliding windows for larger `n`; §6.1 item 2 updated. |
| 3 | `n = 1` false; `n = 4` rests on the exact lane | `C(n) ≤ 4n − 4` now stated for `2 ≤ n ≤ 3` (proved); `n = 4` stated as conditional on the exact lane `research/spikes/no-five-exact/`, which proves `C(4) = 11` with an LRAT-checked UNSAT proof; `C(1) = 1` noted (§0 items 4 and (b), §4.2, §6.3). |
| 4 | Inconsistent growth descriptions | §0 item 5, the §5 reading and §6.2 now say: coplanar roughly linear, cospherical *sublinear* in the measured range (×1.7 for `n` ×3), `n²E(n)` varying slowly; no `Θ(n)` claim for the cospherical count. |
| 5 | "every valid cardinality constraint" | Replaced by "all plane/sphere (≤ 4) and line/circle (≤ 3) cardinality constraints" (§0, §4.1), with the sub-cube constraint `≤ C(3) = 8` as an example of a valid constraint not in the LP. |
| 6 | Stale `out/tables.md` LP-constraint column | Corrected by hand to 1312, 37658, 570042 with a note in the file (regeneration needs the uncommitted >1 MB sphere lists); `out/SHA256SUMS` regenerated for the committed files. |
| 7 | Circle hypothesis automatic for `n ≥ 3` | New Lemma 4.1.3 (a circle carries `≤ 2n ≤ 3n²/4` grid points); Theorem 4.1.2(b) now needs only the sphere hypothesis; the computed circle check is kept as a consistency remark; Lemma 4.1.1 kept for spheres. |
| 8 | "only because" in §6.1 item 1 | Rephrased: the uniform point is infeasible at `n = 3, 4` because some spheres carry more than `n²` points. |
| 9 | Half-open covering in Lemma 4.1.1(ii) | One clause added: the last piece is closed; the count is unaffected. |
| — | Cross-memo note | §6.2 now relates the `E(n)` data to the lower-bound memo's conditional Proposition P; §6.4 cites its coplanar constant. |
| — | Local path in §8 | Replaced by a generic environment description. |

No theorem, lemma or computed value changed.  No bound below `4n` is claimed.
