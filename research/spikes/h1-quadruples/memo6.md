# memo6.md — the flat-shell attempt: exact reduction, honest envelope, and the precise obstruction

Continues `memo.md` … `memo5.md` (same notation). Task this pass: close
`N_circ4(n) = o(n⁸)` via the **flat per-shell bound** — show that for every
dyadic `m ≤ 2.6n^{1+δ}`, the number of concyclic quads with `|c|∞ ∈ [m,2m)` is
`O(n^{7+ε})` (no `m`-decay needed; `O(log n)` shells; the `m ≥ 2.6n^{1+δ}` tail
is proved, memo4 §5.1).

**Verdict: flat is not closed.** But the reduction goes through a new, much
cleaner formulation (Lemma K below) in which the per-shell problem becomes a
single sentence — *zeros of a nondegenerate rank-6 quadric on a covolume-`m³`
lattice, summed over the `~m²` primitive directions `k`* — and the obstruction
is located exactly: the honest (provable) envelope is `min(n^{7+ε}m², n^{9+o(1)}/m)`,
which peaks at `n^{25/3}` around `m ~ n^{2/3}`; the flat target `n^{7+ε}`
requires an `m²`-factor of covolume-dilution *averaged over the direction
`k`* — the same input as memo5's Lemma D at roughly half strength (`m^{−1}`
rather than `m^{−3/2−δ}`). Empirically the flat bound holds with huge margin
(`shell(m) ≤ 0.28·4n⁷`, decaying `~m^{−1}`); it is a true but currently
unprovable statement.

## 1. Lemma K (new, proved): the dependency vector is the kernel vector

Let `x_4` be the point paired with coefficient `c_4 = −(c_1+c_2+c_3)` and set
`w_i = x_i − x_4 ∈ Z³` (`i ≤ 3`), `W = [w_1|w_2|w_3]` (a `3×3` integer
matrix, columns `w_i`).

* `Σ_{i≤3} c_i w_i = Σ_{i≤4} c_i x_i = 0` — so `c' := (c_1,c_2,c_3)` lies in
  the *right kernel* of `W`. For a non-collinear quad `rank(W) = 2`, so the
  kernel is 1-dimensional: `c' = λ·K(w)` where `K(w)` is the primitive
  generator (`K_i = ±` `2×2`-minors of `W`, primitivized).
* `Σ_{i≤4} c_i|x_i|² = Σ_{i≤3} c_i|w_i|²` (using `x_i = x_4 + w_i`,
  `Σc_i = 0`, `Σc_iw_i = 0`) — so the concyclicity condition is
  `Ψ(w) := Σ_i K_i(w)·|w_i|² = 0` (homogeneous in `λ`, hence a condition on
  `w` alone).
* Primitivity of `c` forces `|λ| = 1`: `gcd(c_1,c_2,c_3,c_4)` =
  `|λ|·gcd(K_1,K_2,K_3, ΣK_i)` = `|λ|` (since `gcd(K) = 1` and
  `ΣK_i ≡ ... ` — precisely `gcd(K_1,K_2,K_3,K_1+K_2+K_3) = gcd(K) = 1`).

So **`c = ±(K(w), −ΣK_i(w))`** and

    |c|∞ = max(|K_1|,|K_2|,|K_3|, |K_1+K_2+K_3|) =: |K⁺(w)|.

*Verified*: `quadc.c` recomputes `c` for all concyclic quads at `n = 6,7` via
the `adj(M)`-row construction (cofactors `C_{j,s}` of the `4×4` matrix
`[1|x_i]`, first nonzero column `s`); the multiset histograms match the exact
shell counts from `chist2/chist3` (`4·N_circ4` bookkeeping) with `0`
discrepancies.

## 2. The master reduction in its cleanest form

Since each ordered tuple maps to `(x_4, w_1,w_2,w_3)` with `x_4 ∈ B_n`
(`≤ n³` translates per `w`):

    Σ_{|c|∞~m} W(c)  ≍  n³ · M(m),

    M(m) := #{w ∈ (−n√3,n√3)⁹ : rank W = 2,  Ψ(w) = 0,  |K⁺(w)| ∈ [m,2m)}
        =  Σ_{k prim, |k⁺|~m} Z_L(k),

    Z_L(k) := #{w ∈ L_k ∩ box : G_k(w) := Σ_i k_i|w_i|² = 0, w_i ≠ 0, distinct},

where `L_k = {w ∈ Z⁹ : Σ_i k_i w_i = 0}` is a rank-6 lattice of covolume
`|k|₂³ ~ m³` (the map `w ↦ Σk_iw_i` is a surjection `Z⁹ → Z³` since
`gcd(k_1,k_2,k_3) = gcd(c) = 1`; `TT^T = |k|²I₃`), and `G_k|_{L_k}` is a
**nondegenerate** 6-variable quadratic form (the only radical direction of
`G_k` on `R⁹` is the diagonal `(t,t,t)`, which lies in `L_k` iff
`t·Σk_i = −k_4t = 0` — excluded since `c_4 ≠ 0`).

**The flat bound is therefore exactly:**

    (LEMMA M, sufficient)   Σ_{k prim, |k⁺|~m}  Z_L(k)  ≪  n^{4+ε}      (∀m ≤ 2.6n^{1+δ})

— zeros of a fixed nondegenerate quadric, on a family of `~m²` explicit
index-`~m³` sublattices of `Z⁹`, in one box, with no further structure needed.

This is the same object as memo5's Lemma D / memo3's `Z_eff`-sum, but now
manifestly a statement about *one quadric on many lattices*: the naive bound
`Z_L(k) ≪ n^{4+ε}` (dimension-growth for a nondegenerate 6-var quadric,
coefficient-uniform, hence lattice-oblivious) summed over `m²` directions
gives `n^{4+ε}m²` — the entire problem is the missing `m²` of averaged
dilution, i.e. equidistribution `Z_L(k) ~ n⁴·m^{−3}` on average.

## 3. The honest envelope: every provable bound is the same two bounds

For `shell(m) := Σ_{|c|~m} W(c)`:

**(A) Per-form dimension bound.** `Z_L(k) ≪ n^{4+ε}` (nondegenerate quadric,
`6−2 = 4` net variables) summed over `O(m²)` primitive `k` in the shell:

    shell(m) ≪ n³ · m² · n^{4+ε} = n^{7+ε}m².
    ⟹ handles m ≤ n^{1/2−δ} honestly.          (hitherto unused free range!)

**(B) The `s`-dual (covolume) bound.** `|c|∞ ≥ m` forces the carrying section
lattice `Λ_v` (covolume `ν = ‖v‖`) to satisfy `ν ≤ Cn²/m`
(`c_i = A_i/g`, `A_i ≤ 3√3n²/(2ν)` — memo2 (2.1)). Counting `w`-triples on
planes with `ν ≤ Cn²/m` via `u_3` on the circumcircle through `0,u_1,u_2`
(Lemma 1: `t_γ ≤ n^{o(1)}`):

    M(m) ≲ n^{o(1)} · Σ_{ν ≤ Cn²/m} (#N ~ ν²)·P_ν²,   P_ν ≤ 2n²/ν + 2,
         = n^{o(1)} · (4n⁴V + 4n²V² + (4/3)V³)|_{V = Cn²/m}
         = O(n^{6+o(1)}/m),
    shell(m) ≪ n^{9+o(1)}/m.
    ⟹ handles m ≥ n^{1+δ} (equivalent to memo4 §5.1).

**(C) Equidistributed bookkeeping (heuristic, not proved):** `n^{7+ε}m`
(memo5 §3).

Honest envelope `min(n^{7+ε}m², n^{9+o(1)}/m)`: crossover at `m ~ n^{2/3}`,
worst-case value `n^{7+4/3+ε} = n^{25/3}` ≈ `n^{8.33}`. **The flat bound
`n^{7+ε}` needs an improvement of `m²` over (A) — or `m·n^{-2}` over (B) —
exactly in the range `m ∈ [n^{1/2}, n^{1+δ}]` where both honest bounds are
vacuous.** The seam `m ~ n` of all previous attempts (Lemma L's `s ~ n`,
the `θ = 1/2` threshold) reappears here as the `m ~ n^{2/3}..n` stretch.

### 3.1 Why the two proposed levers are the same object

* *Lever 1 (`x_4` on a `1/m`-grid, integrality `c_4 | Σc_ix_i`)*: the
  condition `c_4 | c_2e_1 + c_3e_2` is precisely membership in a sublattice
  of `Z⁶` of index `|c_4|³ ~ m³` (the map is surjective since
  `gcd(c_2,c_3,c_4) = 1`) — **this sublattice is exactly `L_c`**. The
  "grid" lever is the covolume of `L_k`; using it *is* the
  `m³`-dilution input.
* *Lever 2 (fixed-`c` quadric dimension bookkeeping)*: `x_4`-eliminated
  `F_c` has rank 6 in 9 vars (radical = translations), zeros `n^{6+ε}` on
  `Z⁹`, fibers `n³` → `Z_eff ≤ n^{4+ε}`, honest sum `n^{7+ε}m²` — bound (A).
  The `+1`-floor / non-equidistribution obstruction is the `skew` term in
  the `L_k` point count (bound (B)); they coincide at the seam.

### 3.2 The four slicings all pay the same factor

| slicing | count | honest bound | missing saving |
|---|---|---|---|
| per-form `Z_eff(c)` sum | `m²` forms × `n^{4+ε}` | `n^{7+ε}m²` | `m²` (dilution) |
| `(h,t,γ)` divisor fibers (memo5) | `n^{4+ε}/r` per ray | `n^{7+ε}m` | `m` (gcd-correlation + resonant slab) |
| `s`-dual filtration | `ν ≤ Cn²/m` sections | `n^{9+o(1)}/m` | `n²/m` |
| `(u_1,u_2)`-pair × circle | `Σν²P²·t_γ` | `n^{6+o(1)}/m` for `M` | same as dual |

Every route lands on: *the `m²` candidate primitive directions `k` each could
a priori saturate the dimension bound*; the truth is that the zeros
concentrate on a `~m^{−3}`-fraction of directions (`Z_L(k) ~ n⁴m^{−3}` average
heuristic). No slicing avoids proving that dilution.

## 4. Lemma M ⟺ Lemma D (equivalence statement)

`M(m) = Σ_k Z_L(k)` is a repackaging of the `(h,t,γ)`-fiber count: with
`k = (c_1,c_2,c_3)` primitive and `(a,b,h,t,κ,η)` from Theorem F, `Z_L(k)` is
`#{(e_1,e_2)}`-conjugate via the `(w ↔ e)` isometry `e_i = w_{i+1}−w_1`, etc.
Thus **Lemma M = memo5 Lemma D at strength `m^{−1}` relative to bookkeeping**
(the deficit sectors are identical: resonant `q = |κt−ηh| ≪ m` needs
`m^{−1/2}`, the `r > √m` sector needs the full `gcd(A,u)·gcd(B,v)`
correlation `m^{−1}` — flat asks for the generic-sector input at full
strength and the resonant-sector input at half strength; there is no
intermediate statement that escapes both).

## 5. New structural facts (proved this pass, verified exactly)

1. **Equal-pair ⟹ symmetric.** If `c` is signable as `(p,q,−p,−q)` — forced
   whenever the multiset is `{p,p,q,q}` — then `p(x_a−x_c) = q(x_d−x_b)`,
   so chords `x_ax_c` and `x_bx_d` are parallel; parallel chords of a circle
   share a perpendicular-bisector diameter, hence the 4-set is
   reflection-symmetric (isosceles trapezoid/rectangle). *Verified:*
   `71304/71304` (`n=6`) and `263664/263664` (`n=7`) `ppqq`-multiset quads
   are symmetric; `0` equal-pair-patterned asymmetric quads exist.
2. **Multiset classification of all concyclic quads** (`n = 6,7`, exact):
   `{p,p,p,p}` → parallelograms/rectangles (all sym); `{p,p,q,q}` → all sym;
   `{p,p,p,q}` → **does not occur** (0 quads — memo3's `{1,1,1,3}` corollary
   generalizes); `{p,p,q,r}` → mixed (`3624/19560` sym at `n=6` — the kite
   subfamily); `{p,q,r,s}` distinct → all asymmetric. So
   `N_asym ⊆ {ppqr} ∪ {pqrs}` and `N_sym ⊇ {pppp} ∪ {ppqq} ∪ {ppqr-kite}`.
3. **The composite-`m` spikes are not (only) equal-pair mass.** At `n=7`:
   `m = 6, 15, 20` carry `38928, 12216, 4968` asymmetric quads — all-sym
   attribution (memo5 §5) is wrong; the spikes are driven by Theorem-F
   factorization multiplicity (`m = uh = κt = |κt±ηh|` has many
   representations at composite `m`), producing *asymmetric* quads too.
4. **Asymmetric shell profile** (`n=7`, `|c|∞: asym`): `3:17208, 4:28824,
   5:24312, 6:38928, 7:21936, 8:9696, 9:11616, 10:10440, 11:3936, 12:8040,
   13:4704, 14:1392, 15:12216, 16:336, …` — max shell
   `asym·√m/(4n⁷) ≈ 0.029` (at `m=6`), flat `n^{7+ε}` empirically safe by
   ~two digits of margin.

## 6. What the full chain would look like (for the writeup if closed)

`N_circ4 = N_sym + N_asym`; `N_sym = O(n⁷ log n)` (memo §3);
`N_asym ≤ (1/48)Σ_cW(c)` split at `|c|∞ = 2.6n^{1+δ}`: top by memo4 §5.1
(`O(n^{8−δ+o(1)})`); each of `O(log n)` shells below by Lemma M
(`O(n^{7+ε})` each) → `O(n^{7+ε}log n) = o(n⁸)`. **The single missing
ingredient is Lemma M**, equivalently memo5 Lemma D (strong form) or a
uniform-`Q` 2D input (Lemma L at `θ > 1/2`).

## 7. The exact statement of the missing input (cleanest version)

> For `k ∈ Z³` primitive write `L_k = {w ∈ Z⁹ : k_1w_1+k_2w_2+k_3w_3 = 0}`
> (covolume `|k|₂³`) and `G_k(w) = Σk_i|w_i|²` (nondegenerate on `L_k`).
> **Needed:** `Σ_{k : |k⁺| ∈ [m,2m)} #{w ∈ L_k ∩ (−2n,2n)⁹ : G_k(w) = 0}
> ≪ n^{4+ε}`, uniformly for `m ≤ 2.6n^{1+δ}`.
> Equivalently: zeros of the quadric `G_k` on the box dilute like the
> covolume `|k|³ ~ m³` predicts (`n⁴/m³` per lattice on average), i.e. a
> **mod-`q` equidistribution bound for quadric zeros on the family `{L_k}`,
> valid for `q ~ m` up to `n^{1+δ}`** — beyond the classical `q ≪ √n` range
> and identical in content to memo5 §7's sphere-product statement.

## 8. Scoreboard

| object | status |
|---|---|
| dep. vector `c = ±(K(w), −ΣK)` kernel/Plücker formula | **proved + verified** (`n=6,7` exact, all quads) |
| `Σ_{|c|~m}W(c) ≍ n³·Σ_{k:|k⁺|~m}Z_L(k)` | **proved** (§2) |
| `G_k|_{L_k}` nondegenerate, covol `|k|₂³~m³` | **proved** (§2) |
| equal-pair `⇒` symmetric; multiset classes | **proved + verified** (`0` exceptions) |
| honest per-shell envelope `min(n^{7+ε}m², n^{9+o(1)}/m)` | **proved** — peaks `n^{25/3}` at `m~n^{2/3}` |
| flat bound `shell(m) = O(n^{7+ε})` | **open** — needs covolume dilution `m^{-1}` vs bookkeeping; = Lemma D at half strength |
| `o(n⁸)` | still open, unchanged overall status |

**Files added:** `quadc.c` (per-quad dependency-vector enumerator with
multiset/symmetry classification; verified `Σ_c`-bookkeeping against
`chist2/3` at `n=6,7`), `quadc_n7.txt`, `dbg2.c` (depvec debug tool —
caught the cofactor-along-column degeneracy bug where constant coordinate
columns gave `c = 0`).

## 9. One-line summary for the next pass

The flat per-shell bound is exactly the statement that the `~m²` candidate
dependency directions `k` cannot each carry `n^{4+ε}` lattice solutions on
`L_k` — i.e. that zeros of `G_k` on a covolume-`m³` lattice dilute by the
covolume on average. That is an averaged strong-approximation statement on
the quadric family `{G_k}`, the same wall as Lemma D/L/Q′ in its most
symmetric form; it does not follow from any proved input, and every
elementary slicing provably delivers only `min(n⁷m², n⁹/m)`.
