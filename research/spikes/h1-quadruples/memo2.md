# memo2.md — second pass on N_circ4(n) = o(n^8): bounded sections done, tail reduced to one clean bound

Continuing `memo.md` (same directory; all notation as there: `B_n = [0,n)^3`,
`v` primitive up to sign, `s = |v|_∞`, `Λ_v = v^⊥∩Z³` of covolume `‖v‖ ∈ [s, s√3]`,
`S = Π_{v,k}∩B_n`, `N = N_{v,k} ≤ 2n²/s + 2`, `G(S)` = #circles through ≥4
points of `S`, `Q(S)` = #concyclic 4-subsets, `Q_asym` = asymmetric part).

## What this memo proves / adds

* §1 (Task 1, COMPLETE): the reduction to a fixed-`Q` 2D problem is written out
  with explicit constants; the bounded-covolume contribution is settled — and in
  fact the *trivial* bound already handles `s ≤ n^{1−δ}` (any fixed `δ > 0`), a
  much bigger free range than `s = O(1)`. The 2D theorem (GGK) is needed only to
  sharpen the exponent, not for `o(n⁸)`.
* §2 (Task 2): the tail arithmetic is done exactly. New proved results:
  - **Theorem A**: `s > 3√3n²/2` ⇒ no concyclic 4-set at all (hard cutoff).
  - **Theorem B**: `s > 3√3n²/4` ⇒ every concyclic 4-set is a *parallelogram*,
    hence a rectangle, hence symmetric ⇒ `N_asym(s) = 0`.
  - More generally the affine-dependency vector `c` of a concyclic 4-set
    satisfies `|c_i| ∈ [1, K(s)]`, `K(s) = ⌊3√3n²/(2s)⌋` — a free extra
    parameter that shrinks like `1/s` and classifies the shapes at the top.
  - The two crude tail bounds proposed do NOT work: `G(S) ≲ n⁴/s²` summed over
    sections gives `Θ(n⁹)` (arithmetic below, plus numeric confirmation at
    `n = 64`: `≈ 0.77·n⁹`); `C(N,3)/3` is exactly the trivial `Θ(n⁹)` bound.
    The crude-bound threshold that would suffice is `G(S) ≲ n⁴·s^{−5/2−δ}`.
  - §2.5 reformulates Lemma L as a *zeros-of-a-quadratic-form on a rank-7
    lattice* bound `Z(c,v) ≤ C_ε n^{5+ε}Δ_{c,v}^{−α}`: the computation shows
    `α > 3/5` suffices for the whole theorem. The parallelogram `c`'s are the
    only visible obstruction (they belong to `N_sym` anyway).
* §3: scoreboard. Remaining open range: `s ∈ [n^{1−o(1)}, (3√3/4)n²]` — and in
  that range `N_{v,k} ≤ 2n^{1+o(1)}`, i.e. the difficulty is concentrated on
  *sparse sections* (`N ≪ n²`). Unconditional bound stays `O(n^{9+o(1)})`.

## 0. The master inequality (recap, with constants)

For each primitive `v` (up to sign), `Σ_k N_{v,k} = n³` (every box point lies on
exactly one `(v,·)`-section). Hence, writing `M_s = 2n²/s + 2`,

    Σ_k N_{v,k}³ ≤ (Σ_k N)·max_k N² ≤ n³·M_s² .

The number of primitive `v` (up to sign) with `|v|_∞ = s` is
`≤ ½((2s+1)³−(2s−1)³) = 12s² + 1`.

By Lemma 1 of memo.md (`t_γ = n^{o(1)}` uniformly),
`Q(S) ≤ Σ_γ C(t_γ,4) ≤ ((t_max−3)/4)·Σ_γ C(t_γ,3) ≤ n^{o(1)}·C(N,3) ≤ n^{o(1)}N³`
(the `n^{o(1)}` is `C_ε n^ε`; the point is only `o(n)` powers are lost).

Hence for a dyadic block `s ∈ [S, 2S)`:

    Block(S) := Σ_{s∈[S,2S)} Σ_{v} Σ_k Q(S_{v,k})
             ≤ n^{o(1)}·Σ_{s<2S} (12s²+1)·n³·(2n²/s+2)²
             ≤ n^{o(1)}·Σ_{s<2S} (12s²+1)(4n⁴/s² + 8n²/s + 4)·n³
             ≤ C·n^{o(1)}·(n⁷S + n⁵S² + n³S³).                (0.1)

The three terms are, in order: sections with `N ~ n²/s` (`s ≪ n` regime), the
crossover, and `N = O(1)` sections (`s ≫ n` regime). Each is `Θ(n⁸)` at
`S ~ n`, `S ~ n^{3/2}`, `S ~ n^{5/3}` respectively — the trivial bound is
`Θ(n⁹)` overall (memo §1 baseline).

**Uniform saving needed.** With a per-section saving `s^{−θ}` (Lemma L),
`Block(S) ≤ n^{o(1)}(n⁷S^{1−θ} + n⁵S^{2−θ} + n³S^{3−θ})`, and all three terms
are `o(n⁸)` per block at `S ≤ Θ(n²)` iff `θ > 1/2` (at `θ = 1/2` each term is
exactly `n⁸`, logarithmically over). Consistent with memo §4.

## 1. Task 1 — the bounded-covolume case, done rigorously

### 1.1 The reduction lemma (explicit constants)

**Lemma R (reduction).** Let `v` be primitive, `s = |v|_∞`, and let
`S = Π_{v,k}∩B_n` be nonempty. Then there is a `Z`-linear map
`Ψ: Z² → Λ_v`, `u ↦ x_0 + u_1b_1 + u_2b_2` (`x_0` any point of the section
coset, `(b_1,b_2)` a Gauss-reduced basis of `Λ_v`), such that

(i) `S' := Ψ⁻¹(S − x_0) ⊂ Z²` is contained in a polygon `P` which is an affine
    image of the box-slice `{v·x = k}∩[0,n)³`; `P` has at most **6** sides
    (a plane meets a cube in ≤ 6 edges), Euclidean area `≤ 3πn²/4` (a diameter-`d`
    planar set has area `≤ πd²/4`; `d ≤ n√3`), lattice area `A_P ≤ 3πn²/(4‖v‖)`,
    and `Q`-diameter `≤ n√3`, i.e.
    `S' ⊂ Z² ∩ {u : Q(u − u_*) ≤ 3n²}` for some `u_*`;
(ii) `Q(u) := |u_1b_1 + u_2b_2|²` is a primitive integral binary quadratic form
    of discriminant `−4‖v‖²` (after dividing by `gcd`, the reduced
    representative has coefficients `≤ (2/√3)‖v‖`), and `Ψ` is an **isometry**
    `(R², Q) → (Π_0, |·|_E)`. Therefore circles in `Π` correspond bijectively
    to `Q`-ellipses `{Q(u − c) = ρ²}`, and

        Q(S) = # 4-subsets of S' lying on a common Q-ellipse := F_Q(S').

Moreover `Ψ` preserves the symmetric/asymmetric classification (it is a
similarity of the intrinsic metric).

*Proof.* `Λ_v = v^⊥∩Z³` has covolume `‖v‖` (H2 Lemma 1). Gauss reduction gives
`b_1, b_2` with `⟨b_1,b_2⟩ ≤ |b_1|²/2` (angle ≥ 60°) and
`λ_1λ_2 = |b_1||b_2| ≤ (2/√3)‖v‖`; `λ_1 ≥ 1` since `Λ_v ⊂ Z³`. `Ψ` is a
`Z`-isomorphism `Z² ≅ Λ_v` and an isometry for `Q` by definition of `Q`;
circles pull back to `Q`-ellipses. The slice `{v·x = k}∩[0,n)³` is a convex
polygon with ≤ 6 sides and Euclidean diameter `≤ n√3`; its image `P = Ψ⁻¹(·)`
has the same `Q`-metric diameter and lattice-area `= E-area/‖v‖ ≤ 3πn²/(4‖v‖)`. ∎

### 1.2 The 2D input

**Input (2D, fixed `Q`).** For a fixed primitive positive binary form `Q` and
fixed convex polygon `P_0`, the number of 4-subsets of `Z²∩n·P_0` on a common
`Q`-ellipse is `O(n^{5+o(1)})`; for `Q = x²+y²`, `P_0 = [0,1]²` this is
GGK Thm 1.3 (arXiv:2509.06935): `γn⁵ + O(n^{4+18/29+ε})`, whose raw input is
Huxley–Konyagin (`P_4(R) = cR³ + O(R^{76/29+ε})`, Acta Arith. 138 (2009)).

*Uniformity caveat (honest).* GGK prove the statement for `Q = x²+y²`
(Z[i]-factorization drives the error term). For a fixed general `Q` the same
argument transposes — representations by `Q` in the order `Z[‖v‖·i]` of
discriminant `−4‖v‖²` — with a constant `C_ε(Q)` depending on `Q` a priori.
For `s ≤ s_0` **fixed** there are finitely many forms, so uniformity is free;
for `s_0` growing one would need `C_ε(Q) = O(|disc Q|^{κ})` for some `κ` —
*not* currently extracted from their proof (this is the only point where the
2D transplant is not already a theorem). None of this is needed for the
`o(n⁸)` conclusion (see 1.3a).

### 1.3 The summation over bounded-covolume sections

**(a) Unconditional (trivial per-section bound).** Directly from (0.1):

    Σ_{s ≤ s_0} Σ_v Σ_k Q(S_{v,k})
        ≤ n^{o(1)}·(53n⁷s_0 + 50n⁵s_0² + 18n³s_0³).

For `s_0 = n^{1−δ}`, `δ > 0` fixed: `= O(n^{8−δ+o(1)}) = o(n⁸)`.
**So the whole range `s = O(n^{1−δ})` is handled by the trivial bound.**
(`s_0 = n^{o(1)}` a fortiori; the boundary is genuinely `s_0·n^{o(1)} = o(n)` —
the first term `n⁷s_0` is the binding one.)

**(b) Sharp form (fixed `s_0`, using the 2D input).** For each fixed `v`,
`Q(S) = F_Q(S') ≤ F_Q(Z²∩B_Q(0,2n)) = O(n^{5+o(1)})` by §1.2 (ball version of
the fixed-`Q` count; `Q`-balls have `O(n²)` lattice points). With
`#k ≤ 3ns + O(1)` levels and `O(s_0²)` normals:

    Σ_{s≤s_0}Σ_k Q(S) ≤ C(s_0)·Σ_{s≤s_0}12s²·(3ns+O(1))·n^{5+o(1)}
                      = O(n^{6+o(1)})                (s_0 fixed)

(and the `s_0`-dependence is `O(s_0^{4+κ})` if the 2D constant is polynomial —
then `s_0 = n^{o(1)}` still gives `O(n^{6+o(1)})`).

**Verdict on Task 1:** bounded covolumes contribute `o(n⁸)` — in fact
`O(n^{6+o(1)})` via GGK transplant, `O(n^{7+o(1)})` elementarily — and the free
range extends to all `s ≤ n^{1−δ}`. Nothing in the final theorem needs GGK here;
what GGK/HK *do* show is the *shape* of the truth (per-section `Θ(N^{5/2})`-scale
counts) and, via the class-number dilution `h(−4‖v‖²) ~ ‖v‖^{1+o(1)}`, the
*mechanism* that must be made uniform to cover `s → ∞`.

## 2. Task 2 — the tail

### 2.0 A hard cutoff and a free parameter (NEW, proved)

**Lemma (dependency vector).** Every concyclic 4-set `X = {x_1,..,x_4}` in a
section `(v,k)` is in convex position (no 3 collinear), so its affine dependence
is 1-dimensional: a primitive `c ∈ Z⁴` up to sign with `Σc_i = 0`,
`Σc_ix_i = 0`, `Σc_i|x_i|² = 0`. The coefficients satisfy `|c_i| = A_i/g` where
`A_i ≥ 1` is the lattice double-area of the triangle `X∖{x_i}` in `Λ_v` and
`g = gcd(A_1,..,A_4)`. Every triangle in the slice has Euclidean area
`≤ (√3/4)(n√3)² = 3√3n²/4` (max triangle in a diameter-`d` set is equilateral,
area `√3d²/4`), so `A_i ≤ 2·(3√3n²/4)/‖v‖ ≤ 3√3n²/(2s)`. Hence

    |c_i| ∈ [1, K(s)],   K(s) = ⌊3√3n²/(2s)⌋.                 (2.1)

**Theorem A (hard cutoff).** `s > 3√3n²/2` ⇒ `K = 0` ⇒ no concyclic 4-set.
(Also: `S` then has no non-collinear triple at all.) `□`

**Theorem B (asymmetric cutoff).** `s > 3√3n²/4` ⇒ `K ≤ 1` ⇒ every `|c_i| = 1`
⇒ `c ∈ {±1}⁴` with `Σc_i = 0` ⇒ two entries `+1`, two `−1`, i.e. (after relabel)
`x_a + x_b = x_c + x_d`: a pair-partition with coincident midpoints ⇒ `X` is a
parallelogram ⇒ cyclic parallelogram = **rectangle** ⇒ isosceles trapezoid ⇒
**symmetric**. Therefore `N_asym(s) = 0` for `s > (3√3/4)n² ≈ 1.299n²`. `□`

**Classification at `K ≤ 2`** (`s ∈ ((√3/2)n², (3√3/4)n²]`): primitive `c` with
entries in `{±1,±2}`, all nonzero, `Σc_i = 0` are, up to sign and permutation:
`{1,1,−1,−1}` (parallelogram ⇒ rectangle ⇒ symmetric) or `{1,2,−1,−2}` (the
unique other multiset: `{2,2,−2,−2}` is nonprimitive, `{2,2,−1,−3}` and
`{1,1,1,−3}` violate the bound, `(2,−1,−1,0)` has a zero). So every asymmetric
quad in that band satisfies `x_a + 2x_b = x_c + 2x_d` ("2:1 diagonals") —
a 1-shape family.

More generally (2.1) says: *the shape complexity of a concyclic 4-set in a
covolume-`s` section is `O(n²/s)`* — as `s` grows the admissible dependency
vectors thin out (`Θ(K³)` of them). Empirics note: the observed death of
asymmetric quads near `s ≈ 2n` is still far sharper than the proved cutoff
`1.3n²`; plausible mechanism: for `s ≳ n` most `Λ_v` have `λ_2 ~ s` and no
orthogonal short vectors at all, which already excludes *rectangles* for most
`v` (the surviving large-`s` hits in `sp24.txt` are isolated `s`-values,
presumably `v`'s with special relations).

### 2.1 What the tail needs, exactly

The free range is `s ≤ n^{1−δ}` (§1.3a); the zero range is `s > 1.3n²` (Thm B
for asym). The open range is therefore

    s ∈ (n^{1−o(1)}, (3√3/4)·n²],  where  N_{v,k} ≤ 2n^{1+o(1)} :

**all remaining difficulty lives in sections with `N ≪ n²` points** — Lemma L is
needed only on sparse sections. Per-block requirement (0.1):
`n^{o(1)}(n⁷S^{1−θ} + n⁵S^{2−θ} + n³S^{3−θ}) = o(n⁸)` ⇔ `θ > 1/2`; the three
terms bind at `S ~ n²`(`term1` needs `S^{1−θ} = o(n)`), `S ~ n²`(`term2` needs
`S^{2−θ} = o(n³)`), `S ~ n²`(`term3` needs `S^{3−θ} = o(n⁵)`) — all three pinch
exactly at the top `S ~ n²`, i.e. on `O(1)`-point sections. Restated: Lemma L's
content at the top is "*at most an `s^{−θ}`-fraction of the `Θ(s²·n³)`
four-point `(v,k)`-sections is concyclic*".

### 2.2 The proposed crude bounds fail

* `G(S) ≲ n⁴/s²` per section does **not** suffice: with
  `#k ≤ min(3ns, n³/4)` per `v`,
      Σ_v Σ_k n⁴/s² = Σ_s (12s²+1)·min(3ns, n³/4)·n⁴s⁻²
      ≈ 36n⁵·Σ_{s≤n²/12} s + 3n⁷·#{s ≤ 1.3n²}
      ≈ n⁹/8 + 3.9n⁹ = Θ(n⁹).   (Numeric check at n=64: ≈ 1.38e17 ≈ 0.77·n⁹.)
  The crude-bound threshold that would suffice is `G(S) ≲ n⁴·s^{−5/2−δ}`
  (then `36n⁵Σ s^{1/2−δ} ~ n^{8−2δ}` and `3n⁷Σ s^{−1/2−δ} ~ n^{8−2δ}`).
  Equivalently in `N`-language the needed bound at `s ≥ n` is sharper than
  "`N³`-times-`s^{−θ}`": it must use that sections are `O(1)`-point.
* `G(S) ≤ C(N,3)/3`-type is exactly the trivial `N³` bound ⇒ `Θ(n⁹)` (§0).
* Every elementary reparametrization collapses to the same `N³`:
  `Σ_T(t_{γ(T)}−3)` over triples; `(x,y)`-pair bisectors; the inversion map
  (fix `p`, invert: `Q(S∋p)` = #collinear triples of an `N−1`-point set `S_p*`
  whose lines are all `n^{o(1)}`-rich-bounded since a line through `m` inverted
  points is a circle through `p` with `m+1` points ≤ `t_max`). The last form is
  useful *conceptually*: what is needed is "at most an `s^{−θ}`-fraction of the
  pairs of `S_p*` lie on ≥3-rich lines" — and point sets where *all* pairs lie
  on rich lines exist (elliptic-curve cosets; cf. Green–Tao on ordinary lines).
  So pure incidence geometry cannot supply `s^{−θ}`; the input is genuinely
  arithmetic, as memo.md predicted.

### 2.3 The `c`-counting attempt — and where it lands

Sum over the dependency vector `c` (admissible: primitive, `Σc_i = 0`, all
`c_i ≠ 0`, `|c_i| ≤ K = Θ(n²/s)` — `Θ(K³)` values). For fixed `v,k,c`, count
solutions `u_1,u_2,u_3 ∈ U = Ψ⁻¹(S)` of `R_c := c_4Σ_{i≤3}c_iQ(u_i) +
Q(Σ_{i≤3}c_iu_i) = 0` with `u_4 := −(Σ_{i≤3}c_iu_i)/c_4 ∈ Z²∩U`. For fixed
`u_1,u_2` this is a **nondegenerate `Q`-ellipse** in `u_3` (its `u_3`-quadratic
part is `c_3(c_3+c_4)Q` — degenerate only if `c_3(c_3+c_4) = 0`), and lattice
points on a `Q`-ellipse are `n^{o(1)}` uniformly (Lemma 1: representations of
one value by one form). Hence

    N_c ≤ N²·n^{o(1)}   per (v,k,c),
    Q(S) ≤ Θ(K³)·N²·n^{o(1)} ≤ C(n²/s)³·N²·n^{o(1)}.          (2.2)

vs the needed `N³s^{−θ}`: (2.2) beats `N³` iff `N ≳ (n²/s)³` — which requires
`s ≥ n²/√2` where `N = O(1)` — **never** usable. Effective `θ_eff(s)` is
nonpositive throughout the open range. **Verdict: the `c`-partition alone is
vacuous; its value is structural (§2.0), and as the right parametrization for
the next bound (2.4).**

### 2.4 The rank-7 quadratic-form bound (the clean sufficient input)

Forget `k`: for fixed `(v,c)` count directly in `B_n⁴`:

    Z(c,v) = #{(x_1,..,x_4) ∈ B_n⁴ : Σc_ix_i = 0, v·x_1 = ··· = v·x_4,
                                     Σc_i|x_i|² = 0, x_i distinct}.

Every asymmetric quad is counted exactly `O(1)` times (unique `v`, `c` up to
sign, `24` orderings), so `N_asym ≤ Σ_v Σ_c Z(c,v)`.

*The constraint lattice has rank 7, not 6.* The 6 functionals
`{Σc_ix_i ∈ R³; v·(x_i − x_1), i = 2..4}` always satisfy one relation:
`Σ_{i≥2}c_i(v·x_i − v·x_1) = v·(Σc_ix_i)` identically (since `Σc_i = 0`); and
this is the *only* relation (a second relation would force `c_i = 0` for some
`i ≥ 2` — impossible). So `L_{c,v} := {Σc_ix_i = 0, v·x_i equal} ∩ Z^{12}` has
rank `12 − 5 = 7`.

*Its covolume is `Δ_{c,v} = 2‖v‖³`, independent of `c`.* First
`L_v := {x ∈ Z^{12}: v·x_i all equal}` = kernel of `M: Z^{12} → Z³`,
`x ↦ (v·(x_i − x_1))_{i≥2}`, which is surjective (`v` primitive ⇒ `∃w`,
`v·w = 1`); `MM^T = ‖v‖²(I_3+J_3)`, `det = 4‖v‖⁶`, so
`covol(L_v) = √det MM^T = 2‖v‖³`. On `L_v` the map `x ↦ Σc_ix_i` lands in
`v^⊥` (since `v·Σc_ix_i = kΣc_i = 0`), i.e. in `Λ_v`, and its image is
`d·Λ_v` with `d = gcd(c_2,c_3,c_4)`; but `d | c_1` too (as `Σc_i = 0`), so
`d | gcd(c) = 1` ⇒ `d = 1`, image `= Λ_v`, index `[L_v : L_{c,v}] = 1`, and
`Δ = 2‖v‖³`. (The `v·Σc_ix_i = 0` component of the c-equations is automatically
satisfied on `L_v` — that is the rank-drop above.)

`Σc_i|x_i|²` restricted to `L_{c,v}` is a quadratic form in `7` variables;
heuristically its zeros in the box number `~ n^{7−2}·Δ^{−α} = n⁵·(2s³)^{−α}`
— zeros of a form in `m` variables in box `n` number `~n^{m−2}`, and the
index-`Δ` sublattice dilutes by `Δ^{−α}` (α = 1 = naive equidistribution).

    N_asym ≤ Σ_{v,c} Z(c,v) ≤ C_ε n^{5+ε} Σ_s 13s²·s^{−3α}·Θ(K³)
           = C' n^{11+ε} Σ_{s≤1.3n²} s^{−1−3α}
           = C'' n^{11+ε}·s_0^{−3α}   (s_0 = n^{1−δ})
           = O(n^{11−3α+3αδ+ε}).

So this route needs `3α(1−δ) > 3`, i.e. `α > 1` strictly — *beyond* the
equidistribution expectation `α = 1`, which lands exactly on `n⁸` up to the
`n^{3δ}` slack. **The two completed bounds miss each other by an `ω(1)`-factor
at `s ~ n`**: the trivial bound is `o(n⁸)` only for `s_0 = o(n)`, while the
`c`-lattice bound even at full strength `α = 1` covers only `s = ω(n)` —
the seam `s ≍ n` (which is also the empirical centre of the asymmetric mass) is
where both arguments are exactly `Θ(n⁸)`-tight. Closing it needs either a
fractional extra saving inside the `c`-count (e.g. exploiting that only
`Θ(K³)` `c`'s occur *and* that their zeros correlate) or a sharper small-`s`
bound than `N³` (e.g. the 2D transplant with `s^{κ}`-uniform constants:
`Q(S) ≤ N^{5/2}s^{κ}n^{o(1)}` summed over `s ≤ n` gives `O(n^{15/2+κ+o(1)})` —
under `n⁸` iff `κ < 1/2`, i.e. a **polynomial-uniformity extension of GGK
suffices on the `s ≤ n` side** to shrink the gap to `s ∈ [n, 1.3n²]`).

The excluded parallelogram `c`'s — where `Z(c,v) ~ n⁵` at `Δ ~ O(1)` and the
bound is genuinely false — are exactly the symmetric (rectangle) cases counted
in `N_sym`; the lemma is needed only for `c` with some `|c_i| ≥ 2`. Caveat:
for `s ≳ n^{5/3}` the expectation `n⁵Δ^{−1} < 1` means the bound must be read
as `≤ C_ε(n^{5+ε}Δ^{−α} + n^{floor})` with floors controlled on a sparse
exceptional set — the delicate bookkeeping point.

### 2.5 Equivalent formulations collected (for the writeup)

The following are each sufficient for `N_asym = o(n⁸)` (hence, with §3 of
memo.md, for `N_circ4 = o(n⁸)`):

- (L1) `G(S) ≤ CN³s^{−θ}n^{o(1)}`, `θ > 1/2`, `s ≤ 1.3n²` — the original lemma.
- (L2) per-block: `Block(S) = o(n⁸)` for `S ∈ [n^{1−o(1)}, 1.3n²]` — `θ > 1/2`
  on each dyadic scale.
- (L3) sparse-section form: only sections with `N ≤ n^{1+o(1)}` matter.
- (L4) `Z(c,v) ≤ n^{5+o(1)}(‖v‖³|c|²)^{−α}`, `α > 3/5`, away from parallelogram
  `c` and an exceptional locus (§2.4).
- (L5) inverted-incidence form: for the `N−1`-point set `S_p*`, pairs on
  ≥3-rich lines ≤ `N²s^{−θ}n^{o(1)}` (§2.2) — ruled out by hand because
  elliptic-type point configurations defeat pure incidence arguments.

## 3. Scoreboard / exact remaining range

| range of s | status | bound |
|---|---|---|
| `s ≤ n^{1−δ}` (any fixed δ) | **PROVED** (trivial bound, §1.3a) | `O(n^{8−δ+o(1)})` |
| fixed `s_0` | sharp count via fixed-`Q` GGK transplant | `O(n^{6+o(1)})` |
| `(n^{1−o(1)}, (√3/2)n²]` | OPEN — needs L (θ > 1/2) | — |
| `( (√3/2)n², (3√3/4)n²]` | structurally: only `{±1}` (rectangles) and `{±1,±2}`-dependency quads | — |
| `s > (3√3/4)n²` | **PROVED**: only rectangles ⇒ `N_asym = 0` (Thm B) | 0 |
| `s > (3√3/2)n²` | **PROVED**: no concyclic 4-set (Thm A) | 0 |

**Strongest achieved combined bound:** `N_circ4 = O(n^{9+o(1)})` unconditionally
(memo baseline), with the asymmetric contribution now confined *provably* to
`s ∈ [n^{1−o(1)}, 1.299n²]`, the shape complexity `|c| ≤ 3√3n²/(2s)` proved,
and the missing input isolated as Lemma Z (`α > 3/5` on a rank-7 lattice) or
Lemma L (`θ > 1/2` on sparse sections). Any one of L1/L4 suffices; L4 is the
most "finite" statement to attempt (a uniform zeros bound, α-threshold known).

## 4. Numerical verifications run for this memo

* `quad2.c` (new): exact enumeration at `n = 4..8` recomputing totals
  (`6360, 38910, 174828, 614250, 1761672` — n≤7 match memo §5 exactly; n=8 is a
  new exact value `N_circ4(8) = 1,761,672`), with per-quad primitive normal
  `s`, symmetric flag, and the four sub-triangle lattice areas `A_i`:
  - `|A_i| ≤ K(s)` held for every quad (`badK = 0` at all n): verifies (2.1);
  - no quad with `s > 3√3n²/4` failed the parallelogram conclusion (vacuous at
    n≤8 since `maxs_all ≈ 5n < 0.87n²` — the check verifies the *bound*, the
    implication itself is proved);
  - `max s` of an *asymmetric* quad: `1,3,4,8,15` at `n = 4..8` — consistent
    with the empirical `asym` death at `s ≲ 2n`, far below the proved `1.3n²`.
* Crude-tail check (python): `Σ_v Σ_k n⁴/s²` with `#k ≤ min(3ns, n³/4)` at
  `n = 64` evaluates to `1.38e17 ≈ 0.77·n⁹` — confirms the `Θ(n⁹)` failure of
  the `n⁴/s²` hypothesis (§2.2).
