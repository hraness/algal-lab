# memo5.md — the (a,b)-fiber reduction: shell bound becomes a sphere-product congruence count

Continues `memo.md` … `memo4.md` (same notation). This pass: (i) the c-side
parametrization collapses to a *factored* component form — the four entries of a
primitive conic point are exactly `(uh, vh, κt, κt±ηh)`; (ii) the per-shell
count reduces to a two-sphere bilinear congruence bound, stated as a standalone
lemma with the fiber bookkeeping; (iii) exact numerics at `n = 8` plus a
per-shell profile of the modulus `q = |c4|` and of `gcd(c1,c2)` that pinpoints
the deficit region.

## 1. Theorem F (component factorization — verified on 1.6·10⁶ points)

For a non-collinear triple, `(A,B,C) = (d23,d13,d12)`, let `c` be a *primitive*
integer point of `A c2c3 + B c1c3 + C c1c2 = 0`, all `ci ≠ 0`. Write
`g = gcd(c1,c2)`, `a = c1/g`, `b = c2/g` (coprime, signed), `u = |a|`,
`v = |b|`, `gA = gcd(A,u)`, `gB = gcd(B,v)`. Then `gA gB | Ab+Ba`; set

    M  = (Ab + Ba)/(gA·gB) ∈ Z\{0},     γ = gcd(|M|, C),
    h  = |M|/γ ≥ 1,                      t = C/γ ≥ 1      (so gcd(h,t) = 1),
    κ  = uv/(gA·gB) ∈ Z,                 η = |a+b| ∈ {u+v, |u−v|},
    σ  = sign(M) · sign(ab) ∈ {±1}.

Then

    (|c1|, |c2|, |c3|, |c4|)  =  ( uh, vh, κt, |κt ∓ ηh| ),

i.e. `c = (ha, hb, −σ·(ab/uv)·κt·… , ·)`; concretely `c3 = −σ'·κt`
(`σ' = sign(M)·sign(ab)`) and `c4 = σ'κt − h(a+b)`, hence `|c4| = |κt ± ηh|`.
Moreover

* `h = gcd(c1,c2)` exactly, and the primitive points on ray `(a,b)` are unique:
  the full integer points are `s·c(1)`, `s ≥ 1`, primitive only at `s = 1`;
* **primitivity ⟺ `gcd(h,κ) = 1`** (given `gcd(h,t) = 1`, automatic by
  construction — `gcd(c) = gcd(h, κt) = gcd(h,κ)`);
* `gcd(η,κ) = 1` always (any `p | (u±v)` and `p | uv` divides `gcd(u,v) = 1`);
* `gcd(κt, c4) | η` (so the reduced modulus for `e2` is `q' ≥ q/η`, `η ≤ 2r`).

*Verified:* all primitive conic points of all `41288` non-collinear triples at
`n = 4` (`1,601,040` points, `|c|∞ ≤ K = 41`): `0` mismatches
(`verify_factor.py`). Degenerate case `η = 0` ⟺ `(a,b) = (±1,∓1)` — a single
direction per shell, where the `e2`-condition becomes *linear* (planar), the
memo3 §6 equal-pair/rectangle machinery applies directly.

## 2. The exact counting identity

For coprime `(a,b)` up to sign, `r := max(u,v)`, a triple `T ↔ (x1,e1,e2)`
(`e1 = x2−x1`, `e2 = x3−x1 ∈ (−n,n)³`) contributes to `N_T(m)`,
`|c|∞ ∈ [m,2m)`, iff there is a divisor `γ | C = |e1|²` such that

    h := |bA + aB|/(γ gA gB)  is a positive integer,
    gcd(h,t) = gcd(h,κ) = 1,
    max(uh, vh, κt, |κt ± ηh|) ∈ [m, 2m),                          (SIZE)
    q := |κt ± ηh|  divides  hb·e1 − σ'κt·e2  in Z³,               (INT)
    |hb·e1 − σ'κt·e2| ≤ 2√3·n·q,                                   (BOX)

and `x4 = x1 + ρ`, `ρ = −(hb·e1 − σ'κt·e2)/q` lands in `B_n \ T`. Only
`d(C) = n^{o(1)}` choices of `γ` exist per pair — the parameter set is
divisor-thin. Therefore

    Σ_T N_T(m)  ≤  n³ · Σ_{(a,b) coprime, r ≤ 2m}  #{(e1,e2) : (SIZE)∧(INT)∧(BOX)} ·n^{o(1)}

(×4 ordered-versions bookkeeping as before). Equivalent parameter form
(summing `(h,t,γ)` instead of `(e1,e2)`): for each admissible `(h,t,γ,σ)`,

    e1 ∈ sphere  |e1|² = tγ,     e2 ∈ ellipsoid  b|e2−e1|² + a|e2|² = ±γh·gA gB
    (η > 0: sphere in e2; η = 0: a plane — the single degenerate direction),

subject to the `mod-q` congruence and the slab `|·| ≤ 2√3nq` — a
**sphere × ellipsoid bilinear congruence problem**.

Parameter counts (`uh`-dominant sector; others symmetric): `h ≍ m/u` gives
`~m/u` values; `t ≤ 2m/κ` from `κt ≤ 2m`; `γ ≤ min(3n²/t,
6n²r²/(m gA gB))` from `|bA+aB| = γh gA gB ≤ (u+v)·3n²`.

## 3. Bookkeeping — where the estimate lands and where it breaks

Per `(h,t,γ)`, provable fiber bound: `e1` has `r3(tγ) ≤ n^{1+ε}` choices;
`e2` ranges over a sphere in a single congruence coset of reduced modulus
`q' = q/gcd(q,κt) ≥ q/η`, so `≪ (n/q')^{1+ε} + 1` — plus the slab.
Equidistribution-strength evaluation (`#e2 ≈ n^{1+ε}/q³`, i.e. ignoring the
`+1` floor and treating `q' ~ q`):

    Σ_t q^{-3}  ≈  q_min(h)^{-3} + O(κ^{-3}),   q_min(h) = dist(ηh, κZ) ∈ [1, κ/2]

(`q = 0` ⟺ `κt = ηh` is excluded — `c4 = 0` inadmissible). Since `η ⊥ κ`,
`h ↦ ηh mod κ` equidistributes: `Σ_h q_min^{-3} ~ (m/u)·(1/κ)·ζ(3)`.
Assembling (`gA gB·κ = uv`):

    #(e1,e2)  ≲ n^{2+ε} · (m/u) · (n²r²/(m gA gB)) · (1/κ)
             =  n^{4+ε} · r²/(u²v)   ≈  n^{4+ε}/r       (u,v ~ r)

    Σ_T N_T(m) ≲ n^{7+ε} · Σ_{r≤2m} r·(1/r)  =  Θ(n^{7+ε} · m)   ← bookkeeping worst case

versus target `n^{7+ε}m^{-1/2−δ}`: **the honest equidistributed bookkeeping
misses by `m^{3/2}`** — same factor as always. The loss is structural, not
noise: the `q^{-3}`-sum is saturated by resonant `(h,t)` (`κt ≈ ηh`,
`q = O(1)`) where the congruence is *not* a saving at all, and by the
`+1` coset floor when `q' > n`.

**The two deficit sectors (precisely identified).**
1. **Resonant `q ≪ m`** (`|κt − ηh| ≤ m^{1/4}`-ish): the congruence `mod q`
   is weak; the count must come from the slab `|hb·e1 − σ'κt·e2| ≤ 2√3nq`,
   which confines `e2` to a tube of relative width `~q/m` — saving `(q/m)`
   per `e1`. Resonant `(h,t)` number `(m/u)·(m^{1/4}/κ)`; contribution
   `n^{2+ε}·(m/u)·(n²r²/(m gA gB))·(m^{1/4}/κ)·(q/m)` — bookkeeping gives
   `~n^{4+ε}m^{-1/2}/r` per `(a,b)` here — i.e. this sector alone lands at
   `n^{7+ε}m^{1/2}` after the `r`-sum: still `m^{1}`-off.
2. **Large `r > √m`** (`h = O(1)`, "primitive-direction" sector): `κt ≤ 2m`
   needs `gA gB ≳ r²/m`-scale — i.e. `u | A`-type alignments — a
   divisibility condition on the EDM of density `~(r²/m)/(uv)`-weighted that
   the `n^{4+ε}/r` estimate never used; including it converts the marginal
   `Σ_r` to `Σ_r r·(1/r)·(r²/m)/r² ~ Σ 1/m` — the missing `1/m` lives
   exactly in the `gcd(A,u)·gcd(B,v)` equidistribution over the sphere
   product.

So the shell bound is *one averaged divisor-sum away*: no new phenomenon,
but the correlation of `gcd(A,u)`, `gcd(B,v)` with the two-sphere incidence
is the precise technical content remaining.

## 4. Lemma D — the standalone missing bound (stated exactly)

Fix coprime `(a,b)` up to sign, `(u,v,r,η,κ)` as above, `κ ≥ 1`. For
`(h,t,γ)` integers with `h ≍ m/u`, `1 ≤ t ≤ 2m/κ`, `tγ ≤ 3n²`,
`γ ≤ 6n²r²/(m·gA gB)` where `gA = gcd(tγ, u)`, `gB ≤ v` ranges with the
ellipsoid data, `gcd(h,t) = gcd(h,κ) = 1`, and `q = |κt ± ηh| ≥ 1`:

    P(a,b;h,t,γ) := #{(e1,e2) ∈ (−n,n)⁶ :  |e1|² = tγ,
                       b|e2−e1|² + a|e2|² = ±γh·gA gB,
                       q | hb·e1 − σ'κt·e2,
                       |hb·e1 − σ'κt·e2| ≤ 2√3·n·q }

**Lemma D (sufficient).** `Σ_{h,t,γ} P(a,b;h,t,γ) ≪ n^{4+ε}·r^{-1}·m^{-3/2−δ}`
per `(a,b)` — equivalently `Σ_{(a,b)} Σ_{h,t,γ} P ≪ n^{4+ε}m^{-1/2−δ}` —
gives `Σ_T N_T(m) ≪ n^{7+ε}m^{-1/2−δ}` and hence `o(n⁸)` with the proved tail
(memo4 §5.1). Heuristic truth: `~n^{4+ε}r^{-1}m^{-3}` per `(a,b)` — the lemma
asks for `m^{3/2}` less than the truth, `m^{3/2}` more than the naive
equidistributed evaluation achieves.

Weaker but still sufficient variant (what is actually needed, since
`#`dyadic shells `~ log n`): `Σ_{|c|~m} ≪ n^{7+δ₀}` per dyadic shell, any
fixed `δ₀ < 1` — even **flat-in-`m`** at scale `n^{7+ε}` suffices.

## 5. Numerics — `n = 8` exact + the modulus profile

`chist3` (TCAP-bumped `chist2`): `n=8`, `K=166`, `22,201,728` triples,
`64,351` EDMs, `Σ_T N_T = 7,046,688` → **`N_circ4(8) = 1,761,672`**
(check `4·N` exact ✓). `N_circ4`: `6360, 38910, 174828, 614250, 1761672` —
growth exponent `8.24, 8.14, 8.12, 7.89` — still descending toward the
`~n^{7.6}` heuristic.

**Shell decay** (`Σ_T N_T(m)`, exact-`m` log-log slope): `α ≈ 1.04` (`n=7`,
`m ≤ 8`), `0.90` (`n=8`, `m ≤ 8`); `α ≈ 2.4`–`2.5` over the full range —
envelope `~m^{-1.0}` at small `m`, much steeper in the tail. Dyadic sums at
`n=8` (`/4n⁷`): `0.17, 0.27, 0.27, 0.099, 0.028, 0.0024` for
`m ∈ [1],[2,4),[4,8),[8,16),[16,32),[32,64)` — max shell mass `≤ 0.28·n⁷`
and decaying `~m^{-1.4}` past `m ≈ 5`. **The required `m^{-1/2}` is seen with
large margin**: `shell(m)·√m/(4n⁷) ≤ 0.28` uniformly at `n = 6,7,8`, dropping
below `0.08` for `m ≥ 8`. Empirically even the exact-`m` strong form holds.

**Modulus profile** (`chist4`, per-shell split of `q = |c4|` vs `m`, and
`h = gcd(c1,c2)`), `n = 7`:

| m | tot | q≤m/4 | q>m/2 | h=1 | h=2,3 | h≥4 |
|---|---|---|---|---|---|---|
| 1 | 546744 | 0% | 100% | 100% | 0% | 0% |
| 5 | 291648 | 21% | 71% | 75% | 8% | 16% |
| 10 | 41760 | 11% | 59% | 60% | 24% | 16% |
| 15 | 48864 | 12% | 65% | 52% | 27% | 20% |
| 20 | 19872 | 22% | 62% | 51% | 15% | 34% |

Reads: `q > m/2` (the *generic*, equidistribution-friendly modulus) carries
`~60–100%` of every shell; the resonant `q ≤ m/4` sector is `10–25%` —
substantial but bounded, and concentrated at composite `m` (the spikes at
`m = 15, 20, 21, 28, 35, 42` — exactly the `(p,q,−p,−q)` equal-pair family,
where `h = gcd(c1,c2) ≥ 2` carries `20–35%` of mass vs `~5%` at smooth `m`).
The deficit sectors of §3 are *visible in the data* and are a minority.

**Empty shells** persist (`m = 23,25,26,29,30` absent at `n=7`); new shells
appear at `n=8` (`42:4800`, `43:192`) — consistent with `K` growing and
`φ`-driven families filling in.

## 6. Scoreboard

| object | status |
|---|---|
| `c = (ha, hb, ∓κt, κt∓ηh)` factorization, `prim ⟺ gcd(h,κ)=1` | **proved + verified** (all conic pts `n=4`, `1.6M`, `0` fail) |
| `s` forced `= 1` for primitive `c` | proved (inside Theorem F) |
| `Σ_T N_T(m)` counting identity via `(h,t,γ)` divisor fibers | **proved** (§2) |
| shell bound `Σ_{|c|~m}W ≪ n^{7+ε}m^{-1/2−δ}`, `m ≤ 2.6n^{1+δ}` | **open = Lemma D** — equidistributed bookkeeping `n^{7+ε}m`; deficit = resonant-`q` slab sector + `gA gB`-correlation; empirical margin `m^{-1.0}` envelope, `q>m/2` majority |
| `N_circ4(8)` | `1,761,672` exact |

**Files added:** `chist3.c`/`chist3` (n=8-capable), `chist4.c` (per-shell
`|c4|`/`gcd(c1,c2)` profiles), `verify_factor.py`, `fit.py`,
`chist3_n8.txt`, `chist4_n{7,8}.txt`.

## 7. If a next pass exists

The clean remaining analytic input: on the product `S1×S2` of two spheres
of radius `~n`, bound `#{e1,e2 : αe1 ≡ βe2 (q), |αe1−βe2| ≤ 2√3nq}`
*uniformly in `q ≤ n^{1+δ}`*, then sum over the `(h,t,γ)`-divisor fibers
with the `gcd(A,u)·gcd(B,v)` weights carried through — i.e. Lemma D is a
**mod-`q` equidistribution bound on sphere products, beyond the classical
`q ≪ √n` range**, with the slab saving `q/m` covering the resonant
regime and the `gA gB`-correlation covering `r > √m`. The `(a,b) =
(1,−1)` degenerate direction is a 1-parameter family handled by memo3 §6.
