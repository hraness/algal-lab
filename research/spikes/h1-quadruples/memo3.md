# memo3.md — third pass: sparse-range measurements, sharper cutoffs, Ptolemy class, and the cleanest residual yet

Continues `memo.md` / `memo2.md` (same notation: `B_n = [0,n)^3`, `v` primitive up
to sign, `s = |v|_∞`, `Λ_v = v^⊥∩Z³` covolume `‖v‖ ∈ [s,s√3]`,
`N = N_{v,k} ≤ 2n²/s + 2`, `S = Π_{v,k}∩B_n`, `Q(S)` concyclic 4-subsets,
`Q_asym` asymmetric part, `K(s) = ⌊3√3n²/(2s)⌋`, dependency vector `c`,
`Z(c,v)` rank-7 zeros bound, covolume `Δ_{c,v} = 2‖v‖²|c|²|v_j|/ind ≍ s³|c|²`).

**What this memo adds.**
1. §1 (new, trivially proved): hard cutoff improves to `s > n²` — better than
   Theorem A's `3√3n²/2 ≈ 2.598n²`. Consequence: the K=1 band is *empty*; on
   `(0.866n², n²]` a single asymmetric shape survives (`{1,2,−1,−2}`); on
   `(0.6495n², 0.866n²]` exactly five `|c|`-multisets.
2. §2 (new, verified n=4): every concyclic 4-set has a **Ptolemy class** — a
   squarefree `d` such that the two opposite-side products and the diagonal
   product (all squared lengths) are each `d·(square)`. Equivalently the product
   of the four squared side lengths is a perfect square. A new arithmetic sieve
   handle on top of the coplanarity/lifted-determinant condition.
3. §3 (new, `seprof.c` exact per-section measurements at n=48,64): the
   empirical per-v asymmetric count decays `~ s^{−3}`, and
   `asym(S)/Σ_k N³ ~ s^{−θ_eff}` with `θ_eff ≈ 1.7–2.2` measured — Lemma L holds
   empirically with 3–4× the needed margin `θ > 1/2`. **Asymmetry does NOT die
   at `s ≈ 2n`**: asymmetric quads are found at `s ≈ 0.9n²` (K=2 band) — the
   small-n "death" was an artifact of `K` reaching 0 quickly at small `n`.
   Many `v` have ~all their concyclic quads asymmetric (symmetry is
   concentrated on special normals).
4. §4: Lemma Z re-posed correctly: the trivial zeros of `Σc_i|x_i|²` on
   `L_{c,v}` are exactly the equality/partition loci (diagonal `n³`; 2+2 loci
   `n⁶`-scale only for parallelogram `c`, which are symmetric anyway). The
   needed input is an **off-locus zeros bound** — the standard output shape of
   the determinant method / strong approximation on quadrics — stated
   precisely with its floor accounting.

## 1. Sharper cutoffs (proved)

**Theorem A′ (hard cutoff, supersedes Theorem A).** `s > n²` ⟹ `N_{v,k} ≤ 3`
for every `k` ⟹ **no** 4-subset, hence no concyclic 4-set.

*Proof.* `N ≤ 2n²/s + 2 < 2 + 2 = 4` since `N` is an integer and `2n²/s < 2`.
∎  (Previously `3√3n²/2 ≈ 2.598n²`; the Pick-type bound `N ≤ 2n²/s+2` already
gives `n²`. The true cutoff is where sections stop having `N ≥ 4`
non-collinear: `s ≤ n²` necessary, sharp up to the collinearity condition.)

**Corollary.** The K-classification bands tighten:
* `s ∈ (3√3n²/6, n²] = (0.8660n², n²]`: `K = 2`; the only primitive
  `|c|`-multisets with a zero-sum signing are `{1,1,1,1}` (parallelogram →
  symmetric) and `{1,1,2,2}` (signed `{1,2,−1,−2}`: `x_a + 2x_b = x_c + 2x_d`,
  "2:1 diagonal"). **Exactly one asymmetric shape** survives in the top band.
  The old `K = 1` band `s > 3√3n²/4 ≈ 1.299n²` is entirely vacuous now.
* `s ∈ (3√3n²/8, 3√3n²/6] = (0.6495n², 0.8660n²]`: `K = 3`; asymmetric
  `|c|`-multisets are exactly
  `{1,1,1,3}`, `{1,1,2,2}`, `{1,1,3,3}`, `{1,2,2,3}`, `{2,2,3,3}` — five types.
  (Enumeration: all 4-submultisets of {1,2,3}⁴ with even total and a subset
  summing to half; `{2,2,2,2}` is non-primitive.)
* `s > n²`: nothing.

Consistency check vs `seprof64`: asymmetric quads found at `s = 3581, 3602`
(`n² = 4096`, `K = 2`) and `s = 3344` (`K = 3`) — exactly the bands above;
`maxN ≤ 16` there, matching `N ≤ 2n²/s + 2`.

## 2. The Ptolemy class of a concyclic lattice 4-set (new)

**Proposition P.** Let `{p,q,r,t}` be concyclic, in cyclic order, with squared
lengths `a = |pq|², b = |qr|², c = |rt|², d = |tp|²` (sides) and
`e = |pr|², f = |qt|²` (diagonals) — all integers in `[1, 3n²)`. Then

    sqf(ab) = sqf(cd) = sqf(ef),

i.e. there is a squarefree `d_P ≥ 1` (the **Ptolemy class**) and integers
`u,v,w` with `ab = d_P u²`, `cd = d_P v²`, `ef = d_P w²`.  Equivalently
`abcd` is a perfect square and `√(ef) = √(ab) + √(cd)` forces the three
squarefree parts equal (rational-linear dependence of square roots:
`√x + √y = √z` with `x,y,z ∈ Z` ⟹ `sqf x = sqf y = sqf z`).

*Proof.* Ptolemy's equality for cyclic quadrilaterals: `√(ef) = √(ab) + √(cd)`
(lengths, not squares). Square: `ef = ab + cd + 2√(abcd)`, so
`2√(abcd) ∈ Z⁺`; since `abcd ∈ Z`, `√(abcd) ∈ Z` and
`sqf(ab)·sqf(cd) = 1` in `Q*/Q*²` ⇒ equal; then `√(ab) = u√d'`, `√(cd) = v√d'`
give `√(ef) = (u+v)√d'`. ∎

*Verified*: all 6360 concyclic 4-sets at `n=4` satisfy the equal-squarefree-part
condition in their convex order (exhaustive check, `Fraction`-free).

**Consequence — a third necessary condition.** A concyclic 4-set requires
(i) coplanarity `det = 0` (rank condition in `Z⁹`), (ii) the lifted-paraboloid
coplanarity `det[Q(x_i), x_i, 1] = 0`, and now (iii) the class condition.
Condition (iii) is *nonlinear in the six distances* but purely multiplicative:
for random integers `≤ X` the probability that two products share a squarefree
part is `~ X^{−1/2+o(1)}` and three `~ X^{−1+o(1)}` — a `~n^{−2}`-scale sieve.
Whether it can be made to bite on *lattice-realized* distance multisets (highly
dependent) is open; note it does **not** separate symmetric from asymmetric
quads (rectangles satisfy it), so it can only feed the total count via a
direct distance-multiset sieve, not via the `s`-filtration.

## 3. Per-section measurements (`seprof.c`, n = 48, 64)

`seprof` samples primitive `v` uniformly per dyadic block, computes the exact
section sizes `N_{v,k}` (counting sort over `n³`), samples ≤ `sec_cap` sections
with `N ≥ 4`, and counts concyclic/asymmetric 4-subsets exactly (`N ≤ 40`,
i.e. always in the sparse range) or by `mc` uniform 4-subset draws otherwise.
Per-v estimates are scaled by `nsec4/sampled`.

Measured at `n = 64` (`nv = 60` per block, `sec_cap = 100`, `mc = 2·10⁴`):

| block | avg Σ_k N³ | avg estCirc | avg estAsym | θ_eff = log(N³/asym)/log s_mid | v with asym |
|---|---|---|---|---|---|
| [16,32)   | 4.44e9 | 1.3e7  | 6.09e6 | 2.11 | 60/60 |
| [32,64)   | 1.25e9 | 3.03e6 | 7.02e5 | 1.96 | 56/60 |
| [64,128)  | 3.09e8 | 4.12e5 | 7.39e4 | 1.85 | 38/60 |
| [128,256) | 7.68e7 | 2.82e4 | 2.44e3 | 1.99 | 13/60 |
| [256,512) | 2.50e7 | 2.8e3  | 876    | 1.74† | 7/60 |
| [512,1024)| 1.22e7 | 6.94e3 | 6.32e3†| 1.15† | 6/60 |
| [1024,2048)|2.09e7 | 2.01   | 0      | —    | 0/60 (41/60 have N≥4 secs) |
| [2048,4096)|1.92e6 | 553    | 472†   | 1.04† | 3/60 (10/60 have N≥4 secs) |

(† = few-event MC/scaling noise: e.g. one exact quad in a sampled section
scales by `nsec4/msec ~ 300`; treat those entries as "exists, magnitude
uncertain".) `n = 48` (`nv = 40`) gives the same picture:
θ_eff = 2.20, 2.02, 1.78, 2.5†, 1.1†, 1.0† on [16,32)…[512,1024); asym found
to s ≈ 1024 ≈ 0.44n², none ≥ 1024 (n² = 2304).

**Readings.**
* `θ_eff ≈ 1.7–2.2` in the reliable range — Lemma L's `s^{−θ}` holds
  empirically at `θ ≈ 2`, three-to-four times the needed `θ > 1/2`.
* Per-v absolute asym count decays `~ s^{−3}` over s ∈ [16,512] (fit over
  block midpoints). Summing `12s²·s^{−3}` gives a logarithmically divergent
  block sum — i.e. `N_asym` receives `Θ(1)`-weight per dyadic octave, total
  `~ n^{7+o(1)}`-scale, consistent with the global `asym ~ n^{7.3–7.4}` MC.
* **No cutoff**: asym quads exist at `s ≈ 0.88n²` (n=64) — in the K=2 band —
  and at `s ≈ 0.44n²` (n=48). The earlier "asymmetric dies at `s ≲ 2n`"
  impression (memo §5, from `n ≤ 24` data) is a small-n artifact: at `n = 24`,
  `n² = 576` and the K-band structure compresses the tail.
* Per-`v` asym fraction varies wildly: many `v` have `estAsym ≈ estCirc`
  (essentially all concyclic quads asymmetric) — the `~64%` global symmetric
  share comes from *symmetry-friendly* normals; for most `v`, nearly all
  concyclic quads are asymmetric. So the symmetric bound of memo §3
  concentrates on special `v` and the asymmetric counting cannot leverage
  trapezoid structure.
* `nsec4` (sections with `N ≥ 4`) stays `~2–4·10⁴` per `v` for `s` up to
  `~n²/4` — the Poisson-ish tail `Pr[N ≥ 4]` decays slowly. At `s ~ n²/2`
  (`maxN ~ 4–13`) most `v` still have `≥4`-point sections.

## 4. Lemma Z restated correctly: off-locus zeros

`Z(c,v) = #{(x_1..x_4) ∈ B_n⁴, all distinct: Σc_ix_i = 0, v·x_i equal,
Σc_i|x_i|² = 0}` counts zeros of a quadratic form on the rank-7 lattice
`L_{c,v}` (covolume `Δ ≍ s³|c|²/ind`, memo2 §2.4).

**The trivial zeros.** Any tuple with `Σc_i = 0` has the 3-dimensional
*diagonal locus* `x_1 = x_2 = x_3 = x_4` — `n³` trivial zeros of the quadric.
More generally a partition `π` of `{1,2,3,4}` gives the equality locus
`{x_i = x_j on each block}`; its tuples satisfy the linear constraints
identically iff each block-sum `Σ_{i∈block} c_i = 0` up to the residual
system, and then the quadric contributes one more equation per block-generally.
The relevant facts:

* the 1-block partition (full diagonal) always works: `n³` zeros;
* a 2+2 partition `{i,j}|{k,l}` gives the locus `x_i = x_j, x_k = x_l` —
  `n⁶`-scale — iff `c_i + c_j = c_k + c_l = 0`, i.e. a zero-sum 2+2 partition;
  for primitive `c` that means `|c|-multiset {a,a,b,b}`-type signed
  `(a,−a,b,−b)` — the **parallelogram types** (`{1,1,1,1}` and its multiples;
  `{2,2,1,1}`-signed `(1,1,−1,−1)` is the same class). These quads are
  rectangles/parallelograms → *symmetric* — exactly the `c`'s excluded from
  the asymmetric sum;
* 2+1+1 partitions (one pair equal) reduce to a 3-vector system with no forced
  cancellation unless a pair-sum vanishes; they contribute `≤ n⁴`-scale zeros
  on strata that are anyway excluded by the distinctness requirement;
* for `c` with **no** vanishing 2+2 sub-partition (all asymmetric-`c` shapes),
  the maximal isotropic subspace of the restricted form is the diagonal, so
  `#{zeros} = n³ + Z(c,v)` with `Z` the distinct-coordinate count.

**Lemma Z′ (sufficient input, sharpened form).** For primitive `c` with all
`c_i ≠ 0` and no zero-sum 2+2 partition, `1 ≤ |c|∞ ≤ K(s)`:

    Z(c,v) ≤ C_ε·( n^{5+ε}·Δ_{c,v}^{−α} + n^{2+ε} ),   α > 3/5,

and additionally the exceptional/floor term sums acceptably — concretely it
suffices that the floor applies with full weight only on `o(n^{6})` `(v,c)`
pairs (since `#pairs = Θ(n⁶ log n)`, a uniform `n^{2+ε}` floor gives `n^{8+ε}` —
*logarithmically over*; a uniform `n^{2−δ}` floor suffices). Natural candidate
for the exceptional set: `(v,c)` where `ind_{c,v}` is large, i.e. where
`L_{c,v}` loses genericity (resultant locus) — a sparse algebraic set in the
`(v,c)` space, plausibly `o(n^6)`.

**Why this form is believable — and what to cite.** The determinant method
(Heath–Brown; Browning–Gorodnik "Rational points on the intersection of
a quadric..."; Sardari's optimal strong approximation on quadrics) produces
bounds for zeros of a fixed-height nondegenerate quadratic form in `m ≥ 5`
variables lying in a box: `~ B^{m−2}` total, with sub-lattice/sublocus
dilution. Our `m = 7` sits deep in the convergent range; the only subtlety is
that the zeros count *off* the equality loci — i.e. the statement is "zeros of
`T` on `L_{c,v}∩n-box`, none on a bounded list of isotropic subspaces, number
`≪ n⁵Δ^{−α} + n^{2−δ}`". Isotropic-subspace classification for `T = Σc_iQ(u_i)`
on `V = {Σc_iu_i = 0, v·u_i equal}` is a *finite* problem per `c`-shape (the
`K ≤ 3` bands have 1, 5 shapes respectively; general `c` has `Θ(K³)` shapes
but the isotropic-locus analysis depends only on the sub-sum structure of the
multiset, not on `n`).

**Summation with Z′.** (memo2 §2.4, redone with the floor)
`N_asym ≤ Σ_{v,c asym} Z(c,v)`:

    main:  n^{5+ε} Σ_s 13s²·s^{−3α} Σ_{m≤K} m^{2−2α}
         = n^{5+ε}·Θ(Σ_s s^{2−3α}·K^{3−2α})
         = Θ(n^{11−4α+ε}·Σ_s s^{−1−α})
         = O(n^{11−5α+ε})           (dominated by the bottom s ≈ n^{1−δ})
         = o(n⁸)                    ⇔ α > 3/5    (as before)
    floor: Θ(n^{2+ε}) per pair × Θ(n⁶ log n) pairs = n^{8+ε}  — over budget;
           needs floor `n^{2−δ}` uniformly, or `n^{2+ε}` off an `o(n⁶)` set.

So the honest residual is a *uniform* off-locus zeros bound with a floor just
below `n²` — or a second bookkeeping improvement: split the `(v,c)` sum at
`|c| = M(n,s)`; for `|c|` below the split the pair count `Σ s² M³` is
`O(n^{6−η})` when `M³ ≪ s^{-2}n^{−η}·...` — check: restricting `|c| ≤ C_0`
constant leaves `Σ_s 13s²·C_0³` pairs `= Θ(n⁶)` — still `Θ(n⁶)·n^{2+ε}` — the
floor must genuinely shrink below `n²` per pair or live on a sparse
exceptional set. This is the precise remaining wrinkle.

## 5. The alternative: per-section circle counting via the Ptolemy class

Section §2 suggests a different sufficient bound: for each section, condition
on the Ptolemy class `d_P` of the quad. Two points `x,y` in the section have
`|x−y|² = D ∈ [1,3n²]`; pairs whose squared-distance product lies in a fixed
squarefree class `d_P` ... a bound of shape

    #{(x,y) ∈ S² : sqf(|x−y|²·|z−w|²) = d} ≪ (N²/√D)·n^{o(1)}-ish

summed over `d` and combined with the 4-set structure could supply a saving.
This is genuinely different input (a multiplicative-energy estimate on
squared distances of a lattice-coset point set) and equally unproved.

## 6. Scoreboard after this pass

| range of s | status |
|---|---|
| `s ≤ n^{1−δ}` | PROVED `O(n^{8−δ+o(1)})` (trivial bound) |
| `(n^{1−o(1)}, 0.65n²]` | OPEN — needs `θ>1/2` per-section (measured `≈2`) or Lemma Z′ (`α>3/5` + floor `n^{2−δ}`/sparse exceptions) |
| `(0.65n², 0.866n²]` | open but **5 asym shapes only** (`K=3`) |
| `(0.866n², n²]` | open but **1 asym shape only**: `{1,1,2,2}` "2:1 diagonal" (`K=2`) |
| `s > n²` | **PROVED empty** (Theorem A′) |

## 7. Next steps (in rough order of leverage)

1. Prove Lemma Z′ for the *single shape* `{1,1,2,2}` on `s ∈ (0.866n², n²]` —
   a 1-shape, `K = 2` problem: `x_a + 2x_b = x_c + 2x_d`, `Σ |x|²` weighted,
   on rank-7 `L_{c,v}` with `Δ ≍ 6s³·s²·...` — actually `Δ ≍ s³|c|² = 10s³` —
   so `main ~ n⁵s^{−3α}` is tiny and the whole band needs only an `n^{2−δ}`
   floor per pair `× Θ(n⁶)` pairs. Even simpler: **the top band might be
   directly countable** — `K=2` means each quad has a vertex dividing a
   diagonal `2:1`; count `(x_a,x_b)` pairs `→ x_c+2x_d` lattice-determined —
   worth a separate look; it would isolate the residual to `s ≤ 0.87n²`.
2. Sardari/HB-type citation hunt for the off-locus rank-7 zeros bound at
   `α > 3/5`; the `m = 7`, `height ≤ K` regime is mild.
3. Uniform-`Q` transplant of GGK: `C_ε(Q) = O(|disc|^{κ})`, `κ < 1/2` handles
   `s ≤ n^{...}` from the 2D side.
4. Ptolemy-class multiplicative sieve (§5) as an independent arithmetic
   input; also worth checking empirically whether the Ptolemy class `d_P`
   correlates with `s` (large `d_P` needs rich factorizations).
5. Extend `seprof` to `n = 96` to verify `θ_eff ≈ 2` and measure the
   `K`-band shape distribution (`vmaxc` already tracks max `|c_i|`).
