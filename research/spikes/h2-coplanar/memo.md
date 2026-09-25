# H2: `Z_plane(n) <= (K_* + o(1)) n^11` — proof draft

Attacks Open Problem 4.5 part 2 of `research/spikes/no-five-theorem/memo.md`.
Committed copy: `research/spikes/h2-coplanar/` (`zplane.c` brute-force checker,
`zplane_planes.py` plane-decomposition counter).

**Verdict.** The claim holds, and in fact the full asymptotic holds:
`Z_plane(n) = (K_* + o(1)) n^11`. Every step below is elementary and self-contained.
The naive sum `sum_v sum_k C(N_{v,k},5)` over *all* primitive `v` **diverges** for
`n >= 5` (a collinear 5-set lies in infinitely many lattice planes), so the
bookkeeping must split off collinear 5-subsets; after that split a single uniform
section bound (Pick's theorem) handles *all* normal sizes, including `s > n` —
the `s > n` regime feared in the proof sketch causes no problem — non-collinear
`N >= 5` sections do exist for `n < s <= 2n^2/3`, but Lemma 3 covers them
uniformly, so no `s <= m` hypothesis or case split is ever needed.

## 0. Setup and notation

* `B_n = [0,n)^3 cap Z^3`, `|B_n| = n^3`.
* `v in Z^3` *primitive*: `gcd(|v_1|,|v_2|,|v_3|) = 1`; we take one representative per
  `+-` pair (canonical sign: first nonzero coordinate positive). `s = s(v) := max_i |v_i|`.
* `N_{v,k} = #{x in B_n : v.x = k}`; `Pi_{v,k} = {x in R^3 : v.x = k}`;
  `P_{v,k} = Pi_{v,k} cap [0,n)^3` (the section polygon).
* `phi_v` = density of `v.U`, `U` uniform on `[0,1)^3`; equivalently
  `phi_v(t) = Area({v.x = t} cap [0,1)^3) / ||v||_2` a.e., and with the half-open box this
  holds for every `t` (see Lemma 2's convention note). `phi_v` is a probability density,
  `sup phi_v <= 1/s` (condition on the coordinate with `|v_i| = s`: `v.U = v_i U_i + X`,
  `U_i` uniform independent of `X`, so `phi_v <= sup phi_{v_i U_i} = 1/s`), and
  `int phi_v = 1`.
* `K_* = (1/120) sum_{v prim, +-} int phi_v^5`, convergent (`int phi_v^5 <= s^{-4}` and
  there are `<= 12 s^2 + 1` primitive vectors of size `s` up to sign); `0.07172 <= K_* <=
  0.07273` by Lemma K of the source memo.
* `Z_plane` = number of coplanar 5-subsets of `B_n` (collinear 5-subsets included).
* `Z_coll` = number of 5-subsets lying on a single line (`L_ell` = #box points on line
  `ell`; `Z_coll = sum_ell C(L_ell,5)`, exact since a collinear 5-set has a unique line).
* For a plane section, `C_nc(N_{v,k},5)` = number of 5-subsets of the section that are
  **not** all on one line `= C(N_{v,k},5) - sum_{ell subset Pi_{v,k}} C(L_ell,5)`.

## 1. Bookkeeping lemma (exact)

**Lemma 0.** `Z_plane = Z_coll + sum_{v prim, +-} sum_{k in Z} C_nc(N_{v,k},5)`,
and the double sum is finite (it is supported on `s <= 2 n^2/3`).

*Proof.* A coplanar 5-subset `T` is either collinear — counted once in `Z_coll` — or
contains three non-collinear points, which determine a unique plane `Pi`. Since `Pi`
contains lattice points, `Pi = Pi_{v,k}` for a primitive `v` unique up to sign and a
unique `k`, and `T` is a non-collinear 5-subset of that section: counted exactly once.
Finiteness: `C_nc(N,5) > 0` needs the section to be non-collinear with `N >= 5`
points, hence `s <= 2n^2/3` by
Lemma 3 below.  ∎

**Warning (the divergence the sketch's bookkeeping hides).** The unrestricted sum
`sum_{v,k} C(N_{v,k},5)` is `+infinity` already at `n = 5`: the vertical line
`x = x_0, y = y_0` contains 5 box points and lies in every plane `a x + b y =
a x_0 + b y_0`, `(a,b)` primitive — infinitely many `v = (a,b,0)`, each with
`N >= 5`. Numerically at `n = 5`: `sum` truncated at `s <= 18, 30, 50` gives
`1874190, 1950222, 2164494`, growing without bound, while `Z_plane = 1830235`.
So `Z_plane <= sum_{v,k} C(N,5)` is true but vacuous; the `C_nc` decomposition is the
correct object. (For the *upper* bound we will use `C_nc <= C(N,5)` only inside the
fixed-normal range `s <= A`, where the overcount is absorbed by the `O_A(n^10)`
error term; for `s > A` only `C_nc` is summed, and collinear sections contribute `0`.)

## 2. Section geometry

**Lemma 1 (covolume).** For primitive `v`, `Lambda_v := v^perp cap Z^3` is a rank-2
lattice of the plane `v^perp`, of covolume `||v||_2`. The integer points of
`Pi_{v,k}` form a coset `Lambda_v + x_0` (v primitive gives `v.Z^3 = Z`).

*Proof.* `x -> v.x : Z^3 -> Z` is surjective with kernel `Lambda_v`; consecutive
lattice planes `v.x = k` are spaced `1/||v||`, so `covol(Lambda_v) = ||v||`.  ∎

**Lemma 2 (equidistribution, fixed `v`).** `N_{v,k} = n^2 phi_v(k/n) + O_v(n)`,
uniformly in `k`. Here `phi_v(t) = Area({v.x = t} cap [0,1)^3)/||v||` — the half-open
convention makes `phi_{e_i}` the indicator of `[0,1)` and gives exact agreement at the
face levels; for `v` with `>= 2` nonzero coordinates `phi_v` is continuous
(convolution of `>= 2` bounded densities) and all conventions agree a.e.

*Proof.* Scale: `P_{v,k}` is `n` times the unit-box section, so
`Area(P_{v,k}) = n^2 ||v|| phi_v(k/n)` (coarea: `vol{v.U in [t,t+dt]} = phi_v dt =
Area·dt/||v||`). Let `F` be a fundamental parallelogram of a Minkowski-reduced basis
of `Lambda_v`, `diam F <= lambda_1 + lambda_2 <= 1 + (2/sqrt 3)||v||`
(`lambda_1 >= 1` since `Lambda_v subset Z^3`; Hermite `lambda_1 lambda_2 <= (2/sqrt3)
covol`). The `Lambda_v`-translates of `F` tile the plane and each contains exactly one
point of the coset `Lambda_v + x_0`; tiles wholly inside `P` vs tiles meeting `P` give
`|N - Area/D| <= (perim(P)·diam F + pi diam^2 F)/D`. A plane section of `[0,n]^3` has at
most 6 sides, each `<= n sqrt 2`, so `perim <= 6 sqrt2 n`, and the difference between
`[0,n)^3` and `[0,n]^3` counts is confined to the three boundary faces — `O(n)` points —
absorbed by the same error. For fixed `v`: `O_v(n)`.  ∎

**Lemma 3 (flatness — the uniform section bound).** If the section `Pi_{v,k} cap B_n`
is **not** collinear (equivalently `C_nc(N_{v,k},5)` can be nonzero), then

    N_{v,k} <= 2 Area(P_{v,k}) / ||v|| + 2 = 2 n^2 phi_v(k/n) + 2 <= 2 n^2/s + 2.

Consequently `N_{v,k} >= 5` in a non-collinear section forces `s <= 2 n^2/3`.

*Proof.* `H` = convex hull of the `N` section points is a lattice polygon of the coset
lattice `Lambda_v + x_0` (all vertices are section points). The `N` section points lie
inside `H`, hence `N <= I + B` where `I`, `B` are the coset-lattice points interior to
and on `H` (in fact equality holds: every coset point of `H` is a section point of the
same coset, `H subset P`). The bound is sharp — a lattice triangle with `I = 0` gives
`N = 2 Area(H)/D + 2` (e.g. the corner section `{x+y+z=1}`: `N = 3`). By Pick's
theorem in the 2-dimensional lattice `Lambda_v` (fundamental area `D = ||v||`):
`Area(H)/||v|| = I + B/2 - 1 >= (I+B)/2 - 1 >= N/2 - 1`, giving
`N <= 2 Area(P)/||v|| + 2`. Then `phi_v <= 1/s`.  ∎

This is the substitute for the intended Balogh–White input; it is *stronger*:

* **Balogh–White Lemma 3** (arXiv:2404.02369, verified against the arXiv HTML): for
  primitive `a`, `L = {a.x = 0}`, `s = max|a_i|`, `m >= s`, if `L cap [m]^d` spans a
  `(d-1)`-space then `|L cap [m]^d| <= 3^d m^{d-1}/s` — for `d = 3`, `27 n^2/s`.
  Two limitations for us: (i) hypothesis `s <= m`, which excludes `n < s <= 2n^2/3`
  where spanning sections with `N >= 5` still exist; (ii) it is stated for `a.x = 0`
  (though the proof — count projected lattice points via parallelepiped translates —
  extends verbatim to cosets `a.x = k`). Lemma 3 covers all `s`, has the better
  constant `2` vs `27`, and its `+2` survives only because `N >= 5` then forces
  `s <= 2n^2/3`, cutting off the tail for free.

## 3. Main term: fixed normals `s <= A`

**Lemma 4.** For each fixed primitive `v`,
`sum_k C(N_{v,k},5) = (n^11/120) int phi_v^5 + O_v(n^10)`.

*Proof.* Write `N = n^2 phi_v(k/n) + E`, `|E| <= C_v n` (Lemma 2); `N <= n^2` always
(some `v_i != 0`, so each choice of the other two coordinates determines `x_i`).
`C(N,5) = (N^5 - 10 N^4 + 35 N^3 - 50 N^2 + 24 N)/120`.  The lower-order terms sum to
`sum_k N^4 <= max N^3 · sum_k N <= n^6 · n^3 = n^9` (using `sum_k N_{v,k} = n^3`).
For the fifth power, `(a+E)^5 - a^5 = 5a^4E + 10a^3E^2 + ... + E^5` with
`a = n^2 phi <= n^2`, `|E| <= C_v n`: each term `<= C'_v n^{10-j}` for the `j`-th term;
summing over the `O_v(n)` values of `k` with `N >= 1`
(`|v.x| <= ||v||_1 (n-1)` on the box) gives `O_v(n^10)`. Finally `phi_v` is piecewise
polynomial of degree `<= 2` with `O_v(1)` breakpoints, hence bounded variation, and
`sum_k phi_v(k/n)^5 = n int phi_v^5 + O_v(1)` by the standard Riemann sum for BV
functions.  ∎

Summing over `<= (2A+1)^3/2 = 4A^3 + O(A^2)` normals of size `s <= A`:

**Corollary.** `sum_{v: s<=A} sum_k C(N_{v,k},5) = K_A n^11 + O_A(n^10)`,
`K_A = (1/120) sum_{s<=A} int phi_v^5 -> K_*`. The same holds with `C_nc`:
`sum_{s<=A} sum_k C_nc = K_A n^11 + O_A(n^10) - theta_A`, where
`0 <= theta_A = #{(T,v): T collinear, v perp dir(T), s(v) <= A} <= (4A^3+O(A^2))
Z_coll = O_A(n^7)` by Lemma 6 — `o(n^11)` for fixed `A`.

## 4. Tail: normals `s > A`, uniform in `n`

**Lemma 5.** `sum_{v: s>A, +-} sum_k C_nc(N_{v,k},5) <= (3328/120) n^11 / A`
for every `1 <= A` and every `n`.

*Proof.* Only non-collinear sections contribute. For each `v` of size `s`, by Lemma 3
every contributing `k` (one with `C_nc(N_{v,k},5) > 0`) has `N_{v,k} <= 2n^2/s + 2`,
and the support is empty unless `s <= 2n^2/3`. (Collinear sections can exceed the
Lemma-3 bound — e.g. `v = (1,19,0)` at `n = 6` has `N = 6` — but they contribute
`C_nc = 0`, so they drop out of both sides.) Using `sum_k N_{v,k} = n^3` (every box
point lies on exactly one `v`-level):

    sum_k C_nc(N_{v,k},5) <= sum_{k: C_nc>0} N_{v,k}^5/120
                          <= (max_{k: contributing} N_{v,k})^4 · n^3/120
                          <= n^3 (2n^2/s + 2)^4 /120 <= n^3 (4n^2/s)^4/120
                          = (256/120) n^11 s^{-4}        (s <= n^2, and s <= 2n^2/3 < n^2
                                                         makes 2n^2/s+2 <= 4n^2/s).

Number of primitive `v` up to sign with `s(v) = s`: `<= ((2s+1)^3-(2s-1)^3)/2 =
12 s^2 + 1 <= 13 s^2`. Hence

    tail <= sum_{s>A} 13 s^2 · (256/120) n^11 s^{-4} = (3328/120) n^11 sum_{s>A} s^{-2}
          <= 27.74 · n^11 / A,

since `sum_{s >= A+1} s^{-2} <= int_A^inf x^{-2} dx = 1/A`.  ∎

Note this covers `s > n` — indeed all `s` up to `2n^2/3` — with no case split: the
`n^15/s^4`-type blowup feared in the sketch came from bounding *all* sections
(including collinear ones, which can have `N ~ n` at arbitrarily large `s`, e.g.
`v = (a,b,0)` producing vertical lines); in `C_nc` those contribute `0`.

## 5. Collinear 5-subsets

**Lemma 6.** `Z_coll <= C n^7` (in fact `Z_coll = Theta(n^7)`, dominated by the
`3 n^2` axis-parallel lines).

*Proof.* A line of primitive direction `w` (`s_w = max|w_i|`) meets `B_n` in
`L <= (n-1)/s_w + 1 <= 2n/s_w` points; `L >= 5` needs `s_w <= n`. The number of
`w`-lines meeting the box is `<= 3 s_w n^2` (a line has a unique first point `p` with
`p - w notin B_n`; orienting `w`, `p` must have `p_i < |w_i|` or `p_i >= n - |w_i|` for
some `i` — at most `|w|_1 n^2 <= 3 s_w n^2` such points). Then

    Z_coll = sum_w sum_{ell||w} C(L_ell,5)
           <= sum_{s_w <= n} (12 s_w^2 + 1) · 3 s_w n^2 · (2n/s_w)^5/120
           <= sum_{s_w >= 1} 13 s_w^2 · 3 s_w n^2 · 32 n^5/(120 s_w^5)
           = (13·96/120) n^7 sum_{s_w >= 1} s_w^{-2}
           <= 10.4 · (pi^2/6) n^7 <= 18 n^7.  ∎

Exact check (`zplane.c`, brute force over `C(n^3,5)`): `Z_coll = 0, 0, 109, 984, 4833`
at `n = 3..7`; by hand for `n = 5`: `3·25` axis lines (`L = 5`) + `30` face-diagonal
lines + `4` body diagonals `= 109`. ✓  And `n = 7`: axis `3·49·C(7,5) = 3087`, face
diagonals `6·245 = 1470`, body diagonals `4·69 = 276`, total `4833`. ✓

## 6. Assembly

**Theorem (H2, and more).** `Z_plane(n)/n^11 -> K_*` as `n -> inf`; in particular
`Z_plane(n) <= (K_* + o(1)) n^11`, which is hypothesis H2(K_*) of Proposition P.

*Proof.* Lemma 0 decomposes `Z_plane = Z_nc + Z_coll`. For any fixed `A`:

    Z_nc = sum_{s<=A} sum_k C_nc + sum_{s>A} sum_k C_nc
         <= sum_{s<=A} sum_k C(N_{v,k},5) + (3328/120) n^11/A      (C_nc <= C; Lemma 5)
         = K_A n^11 + O_A(n^10) + 27.74 n^11/A.                    (Corollary, §3)

With `Z_coll <= 18 n^7` (Lemma 6):
`limsup_n Z_plane/n^11 <= K_A + 27.74/A` for every fixed `A`; `A -> inf` gives
`limsup <= K_*`.
Lower bound: `Z_nc >= sum_{s<=A} sum_k C_nc = K_A n^11 + O_A(n^10) - O_A(n^7)`
(§3), so `liminf >= K_A` for every `A`, hence `>= K_*`.  ∎

## 7. Numerical verification

`zplane.c` enumerates all `C(n^3,5)` subsets and tests coplanarity (four 3x3
triple-product determinants vanish) and collinearity (all differences parallel);
`zplane_planes.py` computes the decomposition `sum C_nc + Z_coll` directly.

| n | Z_plane (brute) | Z_coll | Z_nc + Z_coll (identity) | Z_plane/n^11 |
|---|---|---|---|---|
| 3 | 2274 | 0 | 2274 ✓ | 0.01284 |
| 4 | 109680 | 0 | 109680 ✓ | 0.02615 |
| 5 | 1830235 | 109 | 1830126 + 109 = 1830235 ✓ | 0.03748 |
| 6 | 15699720 | 984 | 15699720 ✓ | 0.04328 |
| 7 | 98876337 | 4833 | — (brute only) | 0.05000 |

`n = 3, 4` reproduce the memo's known values; the ratio rises toward
`K_* ~ 0.0721` consistent with convergence at a `~1/n`-type rate.

Per-`s` profile (`n = 6`): `sum_k C_nc` is `12636192, 1782288, 663408, 333216,
236832, 22224, 10800, 8112, 1392, 4272` for `s = 1..10` and **zero for `s >= 11`**
(spanning `N >= 5` sections die far below the `2n^2/3 = 24` bound), while
`sum_k C(N,5)` stays `~10^4–10^5` for every `s <= 26` — pure collinear multiplicity,
confirming the failure mode of the naive sum.

Equidistribution (`N_{v,k} = n^2 phi_v(k/n) + O(n)`), measured
`max_k |N - n^2 phi|/n`: `v=(1,2,3)`: `0.49, 0.46` at `n = 40, 80`;
`v=(2,3,5)`: `0.33, 0.32`; `v=(1,1,1)`: `1.37, 1.26` (max at the kink `t = 1`);
`v=(0,1,7)`: `0.99, 0.98` (at the support edge). ✓

## 8. Remaining gaps / honest status

* **None for the stated claim.** `Z_plane <= (K_* + o(1)) n^11` is proved above; we in
  fact get the asymptotic equality. What is *not* established here:
  - **Explicit `o(1)` rate.** The bound `K_A + O_A(n^{-1}) + 27.74/A` lets one take
    `A = A(n) -> inf` slowly (say `A = log log n`, since the `O_A` hides at most a
    polynomial in `A` — the Lemma-2 constant is `O(diam F) = O(||v||) = O(A)`), giving
    `Z_plane = (K_* + O((log log n)^{-1})) n^11`-type error. A power saving would
    need a uniform-in-`v` equidistribution bound (`O(perim/lambda_1)` does not hold
    uniformly for skewed lattices; Lemma 3's `2n^2/s + 2` is too weak for the main
    term). Not needed for H2.
  - **Sharpness of constants.** `27.74/A` is loose (the `2n^2/s + 2 <= 4n^2/s` step
    and the `s^2` count are wasteful); it can be tightened, e.g. using the exact
    `2n^2 phi_v(k/n)` bound per `k` and `int phi_v^5 <= s^{-4}` — cosmetic.
  - **Dependence on `K_*`'s value** from the source memo's Lemma K
    (`0.07172 <= K_* <= 0.07273`, computed with a proved tail bound); nothing here
    re-derives it.
  - **Caveat on `phi_v` at jump points** (only `v = +-e_i`): the proof uses the
    half-open-box density convention so that `N = n^2 phi + O(n)` holds verbatim;
    `int phi^5` is convention-independent.
  - H1 (`Z_sphere = o(n^11)`) is untouched; H2 alone does not deliver
    `C(n) >= 1.03 n` — that still needs Open Problem 4.5 part 1.
