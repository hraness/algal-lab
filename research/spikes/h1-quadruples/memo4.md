# memo4.md — the EDM factorization: Lemma Q′ becomes an Egyptian-fraction incidence bound

Continues `memo.md`, `memo2.md`, `memo3.md` (same notation: `B_n = [0,n)^3`,
primitive `c ∈ Z⁴` with `Σc_i = 0`, `c_i ≠ 0`, `|c|∞ ≤ K = ⌊3√3n²/2⌋`;
`W(c)` counts ordered distinct non-collinear 4-tuples with `Σc_ix_i = 0`,
`Σc_i|x_i|² = 0`; `N_circ4 = (1/48)Σ_c W(c) + O(n^{6+ε})`; `Z_eff(c) ≍
W(c)/n³`; Lemma Q′ asks `Σ_c Z_eff(c) = O(n^{5−δ})`, i.e. `Σ_c W(c) =
O(n^{8−δ})`).

**This memo's contributions.**

1. **Theorem E (new, proved + machine-verified).** After eliminating `x_4`
   and writing `c_4 = −(c_1+c_2+c_3)`, the surviving quadratic form factors
   through the *squared-distance matrix*:
   `F_c(x) = −(d_{23}c_2c_3 + d_{13}c_1c_3 + d_{12}c_1c_2)`, i.e. the conic
   condition on `c` is the **Egyptian-fraction equation**
   `d_{23}/c_1 + d_{13}/c_2 + d_{12}/c_3 = 0` on the three squared distances
   alone.
2. **Complete parametrization** of the integer points of that conic by
   coprime `(a,b)` and a level `s` (verified exactly).
3. **Bijection lemma:** primitive admissible `c`'s for a non-collinear
   triple `T` biject with lattice points `x_4` on the circumcircle
   `γ(T) ∩ B_n \ T`; hence `Σ_T N_T = Σ_T(t_γ − 3) = 4·N_circ4` — the
   c-dispersion is an *exact reparametrization* of the master identity.
   Verified: `Σ_T N_T = 4·N_circ4` at `n = 4,5,6,7` (`25440, 155640,
   699312, 2457000 = 4·(6360, 38910, 174828, 614250)`).
4. Honest analysis of the remaining wall + the minimal missing input in
   its cleanest form: a decay bound on the `|c|`-distribution of concyclic
   quads, with a concrete `m^{−1/2−δ}` shell statement.

## 1. The EDM factorization (proved)

Write `d_{ij} = |x_i − x_j|²` (`i,j ≤ 3`). Eliminating `x_4 =
−(c_1x_1+c_2x_2+c_3x_3)/c_4` (valid when `c_4 ≠ 0`; use `c_4 =
argmax|c_i|`) gives

    F_c(x_1,x_2,x_3) = c_4·Σ_{i≤3} c_i|x_i|² + |Σ_{i≤3} c_i x_i|² .

**Theorem E.** With `c_4 = −(c_1+c_2+c_3)`,

    F_c(x) = −( d_{12}·c_1c_2 + d_{13}·c_1c_3 + d_{23}·c_2c_3 ) .

*Proof.* `F_c = |Σc_ix_i|² − σ·Σc_i|x_i|²` with `σ = c_1+c_2+c_3`.
Coefficient of `c_i²`: `|x_i|² − |x_i|² = 0`. Symmetrized coefficient of
`c_ic_j` (`i≠j`): `⟨x_i,x_j⟩ − (|x_i|²+|x_j|²)/2 = −|x_i−x_j|²/2`. ∎

Numeric check: 2000 random `(c, X)` pairs, exact agreement.  ∎✓

**Consequences.**

* `F_c = 0` ⟺ `d_{23}/c_1 + d_{13}/c_2 + d_{12}/c_3 = 0` (divide by
  `c_1c_2c_3`): a 3-term **Egyptian fraction equation** whose numerators are
  the three squared distances of the complementary pairs.
* The conic in `(c_1,c_2,c_3)`-space depends only on `(d_{12}, d_{13},
  d_{23})` — the EDM of the triple. So does the primitive-point set.
* Matrix `B = −½(d_{ij})` has zero diagonal, `det B = −¼ d_{12}d_{13}d_{23}
  ≠ 0` for distinct points: **always nondegenerate**, signature `(2,1)`
  (indefinite, e.g. `c=(1,−1,0)` gives `d_{12} > 0`, `c=(1,1,0)` gives
  `−d_{12} < 0`).
* **The conic is always isotropic over Q**: the circumcircle of a
  non-collinear lattice triple has rational centre and infinitely many
  rational points (reflect `x_1` in the perpendicular bisector of `x_2x_3`,
  or stereographically project from `x_1`), and each rational circle point
  yields a rational conic point (§2 bijection). So the conic always has
  integer points — the question is only *how small* (minimal height `h_T`)
  and *how divisible* (`c_4 | Σc_ix_i`).
* Sanities: rectangle triples (`d_{13} = d_{12}+d_{23}`, right angle at
  `x_1`… wait `d_{12}+d_{23}=d_{13}` is right angle at `x_2`) give
  `c = (1,−1,1,−1)` a point — the parallelogram/rectangle shape ✓.
  Isosceles `d_{13} = d_{23}` gives `(A−B)`-degenerate directions.

## 2. Parametrization of the conic's integer points (verified)

With `(A,B,C) = (d_{23}, d_{13}, d_{12})`, solve `Ac_2c_3 + Bc_1c_3 +
Cc_1c_2 = 0` for `c_3 = −Cc_1c_2/(Ac_2+Bc_1)`. Write `c_1 = ga, c_2 = gb`
with `gcd(a,b) = 1` (signed). Since `gcd(Ab+Ba, ab) = gcd(A,a)·gcd(B,b)`, the
integrality condition is

    M(a,b) := (Ab + Ba)/(gcd(A,a)·gcd(B,b))  divides  C·g .

Minimal multiplier `g₀ = |M|/gcd(M,C)`; writing `g = sg₀`, `s ≥ 1`:

    c_1 = s·a·M/γ,   c_2 = s·b·M/γ,   c_3 = −s·C·ab/(γ·gcd(A,a)gcd(B,b)),
    c_4 = −(c_1+c_2+c_3),    γ = gcd(M,C).

Every integer point arises uniquely this way (up to the global gcd
normalization). Verified: all conic points at `n=5`, `K=64`, for 119 random
triples — exact agreement with direct enumeration, 0 mismatches.

**Minimal height.** `h_T := min |c|∞` over nonzero integer conic points.
From the formula, `h_T` is governed by *divisibility structure inside the
EDM*: `|c| ≍ s·max(aM, bM, Cab/(g_A g_B))/γ` where `M ~ (Ab+Ba)/(g_A g_B)`.
For generic `A,B,C ~ n²` pairwise coprime, the `(a,b) = (±1,±1)` choices
give `h ~ (A±B)/gcd(A±B,C) ~ n²/γ` — comparable to `K = 2.6n²`: consistent
with the observed `O(1)`-fraction of triples carrying an in-range conic
point. Cassels' theorem (`h ≲ |F|^{(N−1)/2}`, `N=3` → `h ≲ |F| ≤ 3n²`) is
the matching universal bound — genuinely borderline, explaining why
`N_T > 0` is an `Θ(1)`-density event for triples before integrality.

## 3. The bijection (proved): `N_T = t_{γ(T)} − 3`

For non-collinear `T = {x_1,x_2,x_3}`, every primitive `c` on the EDM conic
with `c_4 ≠ 0`, `c_4 | Σ_{i≤3} c_ix_i`, and `x_4 := −Σc_ix_i/c_4 ∈
B_n\{x_i}` lands on the circumcircle of `T` (the lift criterion); conversely
every lattice `x_4` on the circle yields such a `c` (primitive `c_i =
A_i/g`, `|c_i| ≤ K(s) ≤ K` automatic). Distinct `x_4` give distinct `c`
(the affine dependence of a convex 4-set is 1-dimensional). Hence

    N_T = #{c admissible for T} = t_{γ(T)∩B_n} − 3,
    Σ_T N_T = Σ_T (t_γ − 3) = 4·N_circ4 .

So the c-dispersion is an *exact equivalence* — the same count re-indexed
by `(triple, c)` instead of `(quad)`. Its content is not a shortcut but a
clean parametrization: **`t_γ(T) − 3` is the number of points of a
completely explicit conic** (Egyptian equation on the EDM) satisfying an
explicit divisibility and a box condition.

*Verified exactly* (`chist2.c`, two-pass over EDMs):
`n=4`: `41288` non-collinear triples, `Σ_T N_T = 25440 = 4·6360` ✓
`n=5`: `315892` triples, `Σ_T N_T = 155640 = 4·38910` ✓
`n=6`: `1650664` triples, `Σ_T N_T = 699312 = 4·174828` ✓
`n=7`: `6650464` triples, `Σ_T N_T = 2457000 = 4·614250` ✓

Every integral conic completion was checked concyclic (`0` exceptions at
`n=4` over `176448` hits).

## 4. New numerics

**`N_T` distribution** (buckets by size): overwhelming majority `0`;
`#(N_T>0)/#triples` = `0.431, 0.352, 0.294, 0.256` at `n = 4,5,6,7` —
an `O(1)`-fraction slowly decaying (this is the "circumcircle carries a
4th lattice point in the box" rate; on the conic side it is `h_T ≤ K` ∧
integrality ∧ box). Max `N_T` per triple stays `O(1)`–`15` in range.

**`|c|∞`-shell mass** (`Σ_T #c` with `|c|∞ = m`, `= 4·(#quads with
|c|∞=m)`):

    n=6: 1:183408 2:111456 3:137472 4:67968 5:72576 6:47904 7:23424
         8:9408 9:9888 10:6816 11:4032 12:5472 13:4992 15:7872 17:2496
         18:384 19:192 20:3360 21:192
    n=7: 1:546744 2:359232 3:496464 4:215328 5:291648 6:166464 7:87744
         8:41136 9:47952 10:41760 11:15744 12:32160 13:18816 14:5568
         15:48864 16:1344 17:9216 18:4512 19:2400 20:19872 21:1536
         22:384 24:1728 27:192 31:192

Envelope decays roughly `m^{−1.1}`–`m^{−1.3}` at these tiny `n` (memo3
measured `m^{−1.3}` at `n=6`; `n=7` is similar) — far slower than the
`m^{-3}` asymptotic heuristic, but the range `K ≤ 2.6n² ≈ 127` at `n=7` is
pre-asymptotic; the spikes at highly-partitioned `m` (`15, 20, 24, 27, 31`
at `n=7`) are exactly where the equal-pair family `(p,q,−p,−q)` with
`max(p̂,q̂) = m` has many coprime representatives (`φ(m)`-driven) — direct
evidence that the shell mass at large `m` is dominated by the §6
parametrizable family.

**`h_T` histogram** (`n=4`, min `|c|∞` over conic points ignoring
divisibility): supported on sparse values (`1,2,3,4,5,6,7,8,9,11,13,17,19`
present; `10,12,14,15,16,18` absent) — minimal heights are arithmetic, not
generic.

## 5. Where the wall now sits (exact bookkeeping)

`Σ_c W(c) = Σ_T N_T`, and `N_T` counts conic points `≤ K` satisfying
`c_4 | Σc_ix_i` and `x_4 ∈ B_n`. Three naive decompositions and their
sizes:

* *Ignore everything but the conic*: `Σ_T #conic-pts ≤ K` —
  `~n⁹·K^{1+ε}/h_T`-ish ≈ `n^{11+ε}` upper bound, vacuous. The `Θ(1)`
  fraction of triples with `h_T ≤ K` already makes the "existence" part
  `Θ(n⁹)`-dense at `K = 2.6n²`: **the conic existence is not the rarity**.
* *Divisibility only*: for fixed `c`, `c_4 | c_1x_1+c_2x_2+c_3x_3` is a
  sublattice condition of index `|c_4|³` on `Z⁹` (proved: `ĥ = |c_4|` for
  primitive `c`). Pointwise bound per coordinate:
  `# ≤ n²(n·g_min/|c_4| + 1)` per coordinate with
  `g_min = min_{i≤3} gcd(c_i,c_4)` — giving `φ(c) ≤ n⁶(ng_min/|c_4|+1)³`
  triples. For `|c_4| > n` the `+1` dominates (`≤ O(1)` residue hits per
  `(v,w)`): the bound `n⁶` is `n³` worse than the equidistributed truth —
  the same non-equidistribution wall as `s > n` sections (skew lattices).
* *Per-form zeros bound*: `Z_eff(c) ≤ n^{4+ε}` uniform (determinant
  method: dimension-growth bound for the quadric `G_c = 0` in `P⁵` is
  `B^{4+ε}` coefficient-free — it cannot see the `|c|^{−5}` decay at all);
  summing over `Θ(n⁶)` forms gives `n^{10+ε}`, vacuous. Decay must come
  from the `σ∞ ~ |c|^{−2} × index |c_4|³` mechanism = uniformity in
  coefficients — the part no off-the-shelf theorem supplies.

**The `(1,1)`-sector computation** (why `Θ(n⁸)` is the standing
threshold). For the conic points generated by `(a,b) = (1,1)`, `s` small:
`M = A + B` (generic gcds), size condition `s·M/γ ≤ K` forces
`γ = gcd(A+B, C) ≥ M/K·s` — i.e. `A+B | (small multiple of)·C·s`, a strong
divisibility among the EDM entries. Counting EDMs with `A+B | tC`,
`t ≲ O(1)`: `~n⁴·polylog` of `n⁶` EDMs; times multiplicity `≤ n^{4+ε}`
(Lemma 1: `x_2` on a sphere `r_3 ≤ n^{1+ε}`, `x_3` on a circle
`n^{o(1)}`) lands at `n^{8+ε}` — **exactly the barrier, again**. The
surviving suppression is the `c_4`-divisibility, which is not a uniform
density inside an EDM class.

### 5.1 The large-`|c|` tail is FREE (new sharpening, proved)

The `s`-filtration bound `|c_i| ≤ K(s) = ⌊3√3n²/(2s)⌋` (memo2 (2.1)) reads
in the c-language: **a quad with `|c|∞ ≥ M` lives on a section with
`s ≤ 2.6n²/M`**. Therefore

    Σ_{|c|∞ ≥ 2.6n^{1+δ}} W(c) ≤ Block(s ≤ n^{1−δ})
        = O(n^{8−δ+o(1)})            (proved, memo2 §1.3a).

So Lemma Q′ needs only the shells `m ≤ O(n^{1+δ})`: **the forms sum
shrinks from `Θ(n⁶)` to `Θ(n^{3+3δ})`**, and the per-shell requirement
`Σ_{|c|~m}Z_eff ≪ n^{4+ε}m^{−1/2−δ}` is needed only for
`m ≤ n^{1+δ}` (where it sums to `n^{4.5+ε}`). Numeric sanity at `n=7`:
`|c|∞ > 27` (`δ = 0.2`) carries `96/614250 = 0.016%` of quads.

Equally on the other end: `|c|∞ = 1` ⇔ rectangles (symmetric, proved
`O(n⁷ log n)`-covered); and the equal-pair shapes `(p,q,−p,−q)` with
`|c|∞ = max(p̂,q̂)` in the surviving range `m ≤ n^{1+δ}` still need work —
the `Σ_{family} ≲ n^{7+ε}K̂` bound (memo3 §6) is fine only for
`K̂ ≤ n^{1−δ}` without using the `d^{−3}` decay in earnest.

## 6. The minimal missing input — cleanest standalone forms

All of the following are equivalent-sufficient for `N_circ4 = O(n^{8−δ})`
(and `o(n⁸)` follows from slightly weaker versions):

**(Q′) shell form.** `Σ_{|c|∞∈[m,2m)} W(c) ≪ n^{7+ε}m^{−1/2−δ}` — and by
§5.1 it suffices to prove this **only for `m ≤ 2.6n^{1+δ}`** (the tail is
now proved). In plain language: **the number of concyclic 4-subsets of
`B_n` whose primitive dependency vector has `|c|∞ ~ m` is
`O(n^{7+ε}m^{−1/2−δ})`** for `m ≤ n^{1+o(1)}` — a decay statement about
the height of the unique affine dependence. (Trivial shell scale is
`m²`-many forms; the heuristic truth is `~n⁷m^{−3}` per shell.)

**(Q″) Egyptian-incidence form.** With `Ñ(A,B,C) = #{c ≤ K prim on
the conic}`, `mult(A,B,C) ≤ n^{4+ε}` the EDM multiplicity:
`Σ_{(A,B,C) ≤ 3n²} mult(A,B,C)·Ñ(A,B,C)·ρ(A,B,C) = O(n^{8−δ})` where `ρ`
is the `c_4`-divisibility-and-box fraction — needs `ρ ≍ |c_4|^{−3}`-strength
averaging inside EDM classes.

**(Q′′′) lattice-points-on-circumcircles (the classical form).**
`Σ_T (t_{γ(T)}−3) = O(n^{8−δ})`: average over `n⁹` triples of the
circumcircle's excess lattice-point count. This is the original master
identity — the conic parametrization shows `t_γ−3` is enumerable through
an explicit divisor problem on `(d_{12},d_{13},d_{23})`.

## 7. Literature assessment (what exists vs what's needed)

* **Determinant method** (Heath-Brown; dimension-growth, Salberger et
  al.): bounds `N(Q,B) ≪ B^{dim+1/2+ε}` *uniform in coefficients* — but
  coefficient-independence means no `|c|`-decay; summing over `Θ(n⁶)`
  forms is hopeless. Wrong axis of uniformity.
* **Sardari optimal strong approximation / circle method on quadrics:**
  asymptotic `Z(Q,B) ~ σ_∞ σ_p B^{m−2}` *uniform* once `B ≥ ‖Q‖^{δ₀}` —
  for `‖G_c‖ ~ |c|²` this covers only `|c| ≲ n^{δ₀/2}` (`‖Q‖ ≪ n^{δ₀}`);
  inside that range it *would* give the heuristic `n⁴|c|^{−5}` — a real
  partial input worth extracting precisely (the `K`-uniform version is the
  open technical step; Sardari's bounds are stated for fixed `Q` or
  slowly-growing `‖Q‖`, the seam is at `|c| ~ n^{o(1)}–n^{1/2}`).
* **Cassels/Holzer-type least-isotropic-vector bounds** (`h ≲ |F|^{(N−1)/2}`):
  consistent with `h_T ~ n²` borderline vs `K = 2.6n²`; explains the `Θ(1)`
  completion fraction; not a counting tool by itself.
* **Egyptian fraction equation literature** (`a/x + b/y = c/z` counts —
  Elsholtz et al.): parametrizations like §2 are standard; the novelty is
  the *coupling* to the `c_4 | Σc_ix_i` divisibility and the box, and the
  summation over EDMs — no off-the-shelf bound covers it.

## 8. Scoreboard after this pass

| object | status |
|---|---|
| `N_circ4 = (1/48)Σ_c W(c) + O(n^{6+ε})` | proved (memo3) |
| `F_c = −(d_{12}c_1c_2 + d_{13}c_1c_3 + d_{23}c_2c_3)` | **proved + verified** |
| conic integer-point parametrization | **proved + verified (n=5)** |
| `Σ_T N_T = 4·N_circ4` | **proved + verified n=4..7 exact** |
| equal-pair shapes `W = O(n^{7+ε})` per shape | proved (memo3 §6) |
| `Σ_{|c|∞ ≥ 2.6n^{1+δ}} W(c)` tail | **PROVED `O(n^{8−δ+o(1)})`** (new, §5.1 — the `s`-filtration eats the `c`-tail) |
| `Σ_c Z_eff(c) = O(n^{5−δ})` | **open** — needed only for `|c| ≤ O(n^{1+δ})`; equivalent forms in §6; the wall is `c_4`-divisibility uniformity inside EDM classes (equiv.: `|c|`-height decay of dependencies) |

**Files added this pass:** `chist.c` (single-pass per-triple conic stats),
`chist2.c` (two-pass EDM-grouped, used for the n=4..7 exact totals),
`verify_edm.py` (identity + conic↔concyclic correspondence),
`hdist.py` (parametrization verification, sampled).

## 9. The sharpest statement of what is missing

`o(n⁸)` follows from: *for each dyadic `m ≤ 2.6n^{1+δ}`, the number of
concyclic 4-subsets with dependency height `|c|∞ ~ m` is
`O(n^{7+ε}m^{−1/2−δ})`.* Everything else is proved (the `m > n^{1+δ}`
tail by §5.1, `m = 1` rectangles by the symmetric bound). The parametrization
reduces this to a divisor-counting problem on EDMs: `c`'s are generated by
coprime `(a,b)` and `s`, and admissibility for a triple is a divisibility
`M(a,b) | d_{12}·g` among its three squared distances — the missing step
is a uniform bound on **how many box triples satisfy such an EDM-internal
divisibility while also putting `x_4` on a lattice point**. The `s`-filtration
bound `|c| ≤ 2.6n²/s` converts this back to the old sparse-section problem
— the two formulations are now verified to be literally the same count.
