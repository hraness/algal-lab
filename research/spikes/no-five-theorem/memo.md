# Round 27 — no-five-on-a-sphere: theorem attempt (lower-bound lane)

Branch `research/no-five-theorem`.
Run directory: `research/spikes/no-five-theorem/` (code in `src/`, raw outputs in `data/`).
Python: a Python 3.12 environment with numpy and sympy; checker compiled with `cc -O2 -o zero5 zero5.c`.
Revised after the referee report `REFEREE-REPORT.md` (major revision); the changes are listed in
Section 7.  Sibling memo (upper bounds): `research/spikes/no-five-upper/memo.md`.

Labels: **Theorem / Lemma / Proposition (proved)** = complete proof here; **Computed** = exact or
floating-point computation with its script; **Numerical** = measurement, not proved;
**Heuristic** = plausibility argument; **Conjecture** = open statement.

## 0. Verdict (read this first)

Target: prove `C(n) >= 2n`, or any `C(n) >= (1+eps) n`, where `C(n)` is the largest subset of
`{0..n-1}^3` with no five points on a common sphere or plane (exact criterion: every 5-subset of the
lifted rows `(x, y, z, x^2+y^2+z^2, 1)` has nonzero determinant).

* **Nothing beyond the known `C(n) >= n - o(n)` is proved unconditionally here.**  No claim below
  is an unconditional proof of `(1+eps) n` for any `eps > 0`.
* **Conditional result (Proposition P, Section 4.4, proved as an implication):** if (H1) the number
  of degenerate, non-coplanar 5-subsets of `[0,n)^3` is `o(n^{11})` and (H2) the number of coplanar
  5-subsets is at most `(K + o(1)) n^{11}`, then `C(n) >= (0.8 (5K)^{-1/4} - o(1)) n`.  The natural
  constant is the series `K_*` of Section 4.4, with `0.0717 <= K_* <= 0.0728` (**Computed**
  partial sum plus a proved tail bound) and `K_* ~ 0.0721` by extrapolation; this is below the
  threshold `(4/5)^4/5 = 0.08192`, so H1 and H2 with `K = K_*` would give `C(n) >= (1.032 - o(1)) n`.
  **Neither H1 nor H2 is proved.**  H1 is supported by the `n <= 128` Monte Carlo data of the
  sibling memo; H2 is a lattice-point counting statement (Open Problem 4.5).
* **Proved (with complete proofs in Section 2):** the four determinant identities (Demonstrandum
  Lemma 1, Lemma 3, the twin-pair factorization, the twisted-cubic identity), the mod-p arc lemma for
  rational quartic curves on the paraboloid (Lemma A: this is Dong–Xu's Section 3 argument written in
  determinant form), an explicit family with `p - 1` points in `[0,p)^3` for every prime
  `p = 1 (mod 4)` (an instance of the Dong–Xu *mechanism*, not literally of their Theorem 4, and not
  a new result — see 2.3), the osculation lemma (the only twin direction with a full second-level
  p-adic certificate is the tangent direction), the Vandermonde-valuation bound for p-adic curve
  certificates (Lemma V, for `2 <= k <= 10`, plus a pigeonhole bound `|T| <= 4 p^{ceil(k/10)}` for
  every `k >= 2`), and the parallelogram lemma for translate constructions.
* **Measured (numerical, not proved):** the 4-translate construction `S1 + p*A` (arc mod p plus a
  tetrahedron of translates, `4p` points in `[0,2p)^3`) is *not* valid: thousands of zero 5-subsets,
  growing like `p^2` (Section 3).  After greedy deletion it survives at only `~1.0 n`.  A uniformly
  random set of `2n` points in `[0,n)^3` followed by greedy deletion survives at `1.41–1.46 n` for
  `n = 26..100` (Section 3.6; starting from `2.5 n` random points it leaves `1.56–1.58 n` at `n = 60, 80`, and the survivor keeps
  growing with the initial density, see the `gamma` sweep in 3.6) — better than the arc construction, but with no proof attached.
* **Obstruction analysis (Section 4):** a single-prime certificate caps at `p+1` points (Ball's
  theorem, `p >= 5`).  What Ball forces beyond that is weak: a set of `|S| >= p+2` points has at
  least `C(|S|,5)/C(p+2,5)` 5-subsets with `det5 = 0 (mod p)`, which for `p ~ n` and `|S| = (1+eps)n`
  is only a constant.  (An earlier version claimed `Theta(eps n^4)` such 5-subsets for every `S`; that
  was false and is withdrawn, see 4.1.)  The only algebraic second-level certificate (tangent twins)
  needs a box of side `~p^{5/3}` (heuristic).  The plain random-deletion route to `(1+eps) n` is
  *open*, not ruled out: it reduces exactly to H1 and H2 above (Section 4.4).

## 1. Setting, exact criterion, checker

For `P = (x,y,z) in Z^3` write `L(P) = (x, y, z, |P|^2, 1)`.  Five points are on a common sphere or
plane iff `det[L(P_1); ...; L(P_5)] = 0` (a common sphere `a|P|^2 + b.P + c = 0`, or plane when
`a = 0`, is a nonzero vector in the left kernel).  Subtracting the first row from the others the
determinant equals the 4x4 determinant of the lifted differences, which is what the checker computes.

`src/zero5.c` reads points `x y z` from stdin, forms all `C(m,5)` subsets, computes the 4x4 determinant
of `(P_i - P_1, |P_i|^2 - |P_1|^2)` in `__int128` (exact for all boxes considered here: entries are
below `2^20`, so the determinant is below `2^90`), prints `zero i j k l m` for the first `maxprint`
zero subsets and a final line `zeros=Z subsets=T`; it aborts if the input has more than 8192
points (buffer guard).  Sanity test: the five cube vertices `000,100,010,001,111` give
`zeros=1 subsets=1` (any five vertices of a cube lie on its circumsphere); adding a sixth point
`2 3 5` gives `subsets=6`.  Every "valid" claim in this memo means `zeros=0` from this program.

Parity: all lifted determinants on the integer grid are even (Demonstrandum parity theorem; a
consequence of `|P|^2 = x + y + z (mod 2)`, so mod 2 the fourth column is the sum of the first three).
Hence the smallest nonzero `|det|` is 2; this is only used as a sanity check on outputs.

## 2. What is proved (complete proofs)

Notation: `L(P) = (P, |P|^2, 1)`, `det5(P_1..P_5) = det[L(P_1); ...; L(P_5)]`, `det3[a,b,w]` the 3x3
determinant with rows `a, b, w`, `V(t) = prod_{i<j} (t_j - t_i)`.

**Translation invariance.** `det5(P_i + c) = det5(P_i)`: `|P+c|^2 = |P|^2 + 2c.P + |c|^2`, so the
fourth column of the translated matrix is the old fourth column plus a linear combination of the
other columns, and the first three columns shift by multiples of the last column.

### 2.1 The four identities (all four also machine-checked in `src/lemmas_sympy.py`; every difference prints `== 0`)

**Lemma 1 (Demonstrandum, (2,2,1) class).** `det5(c+a, c-a, c+b, c-b, c+w) = -4 (|a|^2 - |b|^2) det3[a,b,w]`.

*Proof.* Take `c = 0`.  Replace row 1 by row 1 − row 2 = `(2a, 0, 0)` and row 3 by row 3 − row 4 =
`(2b, 0, 0)`, then swap rows 2 and 3 (sign −1).  The rows are now `(2a,0,0), (2b,0,0), (-a,|a|^2,1),
(-b,|b|^2,1), (w,|w|^2,1)`.  Laplace-expand along the last two columns: the only complementary 3x3
minor in columns 1–3 that can be nonzero uses the rows `2a, 2b, w` (the other choices contain `2a`
together with `-a`, or `2b` with `-b`); it equals `4 det3[a,b,w]`, and its partner is the minor
`det[[|a|^2,1],[|b|^2,1]] = |a|^2 - |b|^2` on rows 3,4 with sign `(-1)^{3+4+4+5} = +1`.  With the row
swap the total is `-4(|a|^2-|b|^2) det3[a,b,w]`.  ∎

**Lemma 3 (Demonstrandum, (2,1,1,1) class).** With `u = (q-p) x (r-p)` and
`w = |p|^2 (q x r) + |q|^2 (r x p) + |r|^2 (p x q)`:
`det5(c+a, c-a, c+p, c+q, c+r) = 2 ( |a|^2 (a.u) - a.w )`.

*Proof.* Take `c = 0` and replace row 1 by `(2a,0,0)`.  Row 2 is `(-a,0,0) + (0,|a|^2,0) + (0,0,1)`;
by multilinearity the first summand gives a determinant with two proportional rows (zero), so
`det5 = D_1 + D_2` with `D_1 = det[(2a,0,0); (0,|a|^2,0); L(p); L(q); L(r)]` and
`D_2 = det[(2a,0,0); (0,0,1); L(p); L(q); L(r)]`.  Expanding `D_1` along row 2 gives
`|a|^2 * det[(2a,0); (p,1); (q,1); (r,1)]` (columns 1,2,3,5); subtracting the `p`-row from the `q`- and
`r`-rows and expanding along the last column gives `2 |a|^2 det3[a, q-p, r-p] = 2|a|^2 (a.u)`.
Expanding `D_2` along row 2 gives `(-1)^{2+5} det[(2a,0); (p,|p|^2); (q,|q|^2); (r,|r|^2)]`
(columns 1–4); expanding along the fourth column,
`= -2 ( |p|^2 det3[a,q,r] - |q|^2 det3[a,p,r] + |r|^2 det3[a,p,q] ) = -2 a.w`.  ∎

**Lemma T (twin-pair factorization).** For `m in Z`, `u in Z^3`:
`det5(P, P+mu, R, S, T) = m * det[L(P); sigma; L(R); L(S); L(T)]`, `sigma = (u, 2u.P + m|u|^2, 0)`.

*Proof.* `L(P+mu) - L(P) = (mu, 2m u.P + m^2 |u|^2, 0) = m sigma`; subtract row 1 from row 2 and pull
out `m`.  ∎   (Mod `p`, with `m = p`, `sigma` reduces to `tau_u(P) := (u, 2u.P, 0)`, a point of the
tangent hyperplane of the paraboloid quadric `x^2+y^2+z^2 = wv` at `L(P)`.)

**Lemma C (twisted cubic).** For `P_i = (t_i, t_i^2, t_i^3)`,
`det[1, t, t^2, t^3, |P|^2]_{i=1..5} = V(t) (1 + h_2(t_1..t_5))`, `h_2` the complete homogeneous
symmetric polynomial of degree 2.  In particular no five distinct real points of the twisted cubic
are cospherical or coplanar.

*Proof.* `|P|^2 = t^2 + t^4 + t^6`; subtract column 3 from column 5 to get columns
`1, t, t^2, t^3, t^4 + t^6`, hence `det[1,t,t^2,t^3,t^4] + det[1,t,t^2,t^3,t^6]`.  By the bialternant
formula `det[t_i^{lambda_j + 5 - j}] = V(t) s_lambda(t)`, the exponent sets `(0,1,2,3,4)` and
`(0,1,2,3,6)` give `s_() = 1` and `s_(2) = h_2`.  Over the reals `1 + h_2 > 0`.  ∎
(The real family only gives `n^{1/3}` points in a box of side `n`; recorded because the same
Schur-positivity mechanism works for any curve whose coefficient minors are all nonnegative.)

### 2.2 The mod-p arc lemma

*Attribution.* Lemma A is Dong–Xu's Section 3 argument (arXiv 2506.18113) written in determinant
form: there, a plane or sphere meets the curve in the zeros of a nonzero polynomial of degree
`<= d+1` in the span of the coordinate polynomials.  It is recorded here because the determinant
form is what Sections 2.4–2.5 use.  (Nit: that distinct `t` give distinct points `P~(t)` follows
from the determinant statement only when `|T| >= 5`, since a repeated point would give two equal
rows in some 5-subset; `|T| >= p - 4 >= 5` for `p >= 9`, and for `|T| <= 4` the claim is vacuous.)

**Lemma A.** Let `X, Y, Z, W, U in F_p[t]` have degree at most 4, satisfy `X^2 + Y^2 + Z^2 = W U`, and
be linearly independent (a basis of the polynomials of degree <= 4).  Let `T = { t in F_p : U(t) != 0 }`
and, for `t in T`, let `P(t) = (X/U, Y/U, Z/U)(t) in F_p^3` and `P~(t) in [0,p)^3` its integer
representative.  Then for any five distinct `t_1..t_5 in T`, `det5(P~(t_1), ..., P~(t_5))` is not
divisible by `p`.  Hence `{P~(t) : t in T}` is a valid set in `[0,p)^3` with `|T| >= p - deg U`
points.

*Proof.* `|P(t)|^2 = (X^2+Y^2+Z^2)/U^2 = W/U`, so `L(P(t)) = U(t)^{-1} (X, Y, Z, W, U)(t)`.  Writing
`(X,Y,Z,W,U)(t) = M (t^4, t^3, t^2, t, 1)^T` with `M` the 5x5 coefficient matrix,
`det[L(P(t_i))] = prod_i U(t_i)^{-1} det(M) det[t_i^{4-j}] = ± det(M) V(t) / prod U(t_i)`, which is
nonzero in `F_p` because `det(M) != 0` and the `t_i` are distinct.  Since `P~ = P (mod p)` and
`|P~|^2 = |P|^2 (mod p)`, the integer determinant reduces mod `p` to this nonzero value.  ∎

`src/nrc.py` samples such curves with `U = 1`: `(X,Y,Z)(t) = sum_k v_k t^k`, and `deg(X^2+Y^2+Z^2) <= 4`
is exactly the four conditions `v_4.v_4 = 0`, `v_4.v_3 = 0`, `2 v_4.v_2 + v_3.v_3 = 0`,
`v_4.v_1 + v_3.v_2 = 0` (an isotropic leading vector exists for every `p`); independence is checked
by a 5x5 determinant mod `p`.  These give `p` points.  Checked exactly (`zero5`): e.g. `p = 13`, seed 1:
`zeros=0 subsets=1287`.

### 2.3 An explicit family (an instance of the Dong–Xu mechanism, not a new construction)

Dong–Xu (arXiv 2506.18113) prove `ex([n]^d; d+2) >= n - o(n)` for every `d`.  Their Theorem 4
(Section 2) assumes `p = 1 (mod 4)`, a polynomial identity `f_1^2 + ... + f_d^2 = g h` and linear
independence of `f_1, ..., f_d, g, h`; the curve `(f_1/h, ..., f_d/h)(t)` is then used in their
Section 3 (the argument of Lemma A).  The family below is an instance of this *mechanism* in
`d = 3`, not literally of their Theorem 4: Theorem 4 has degree profile `(3,3,3,2,4)` and assumes
`p > (d+1)! = 24`, whereas `F` has `U = t` of degree 1 and works for every prime `p = 1 (mod 4)`.
Their `n - o(n)` for all `n` also uses a random translation with `p` slightly above `n`; `F` by
itself gives only `C(p) >= p - 1` at primes `p = 1 (mod 4)`.  The family is recorded because it is
used in Section 3 and because its fibre profile (one point per plane `x = const`, at most three per
plane `y = const` or `z = const`) is what the translate constructions need.  Nothing here improves
on their bound.

**Family F(p; q, r).** `p = 1 (mod 4)` prime, `i^2 = -1` in `F_p`, `q(t) = q_2 t^2 + q_1 t + q_0`,
`r(t) = r_2 t^2 + r_1 t + r_0` with `q_2 r_2 r_0 != 0`.  For `t in F_p^*` put
`x = t`, `y = (t q(t) + r(t)) / (2t)`, `z = (t q(t) - r(t)) / (2 i t)`.

*Claim.* `{(x,y,z) mod p : t in F_p^*} subset [0,p)^3` is valid and has `p - 1` points, with all
`x`-coordinates distinct and at most 3 points on any plane `y = c` or `z = c`.

*Proof.* With `U = t`, `X = t^2`, `Y = tU y = (tq + r)/2`, `Z = (tq - r)/(2i)`, `W = t^3 + q r`:
`Y^2 + Z^2 = ((tq+r)^2 - (tq-r)^2)/4 = t q r`, so `X^2 + Y^2 + Z^2 = t^4 + t q r = U W`, all of degree
<= 4.  In the basis `t^4, t^3, t^2, t, 1` the coefficient matrix of `(U, X, Y, Z, W)` has determinant
`q_2^2 r_2 r_0 / (2i)` (expand along the `t^4` column, where only `W` has an entry `q_2 r_2`; then along
the `U` row and the `X` row; the remaining 2x2 block is `[[q_2/2, r_0/2],[q_2/(2i), -r_0/(2i)]]`).
Lemma A applies with `T = F_p^*`.  `x = t` is injective; `y = c` is `t q(t) + r(t) - 2ct = 0`, a cubic in
`t` (leading coefficient `q_2`), so at most 3 solutions; likewise for `z`.  ∎

Exact check (`src/family133.py 73`, default `q = t^2`, `r = t^2 + 1`), file `data/family133_default.txt`:
verified (`zeros=0`, `|S| = p-1`, fibres `[1,3,3]`) for the 8 primes `p = 13, 17, 29, 37, 41, 53, 61,
73` (p = 73: 13,991,544 subsets checked); `p = 5` gives `|S| = 4` and has no 5-subsets, so that
row is vacuous.

### 2.4 The osculation lemma (second-level p-adic certificate for twin pairs)

Let the curve be as in Lemma A and let `P = P(t_0)` be an affine point.  Write
`L'(t) = d/dt L(P(t)) = (P'(t), 2 P(t).P'(t), 0)` (formal derivative), i.e. `L'(t_0) = tau_u(P)` with
`u = P'(t_0)`.

**Lemma O.** For any three distinct affine points `R, S, T` of the curve other than `P`,
`det[L(P); L'(t_0); L(R); L(S); L(T)] != 0` in `F_p`.  Consequently, if `S subset Z^3` contains
`P~` and a twin `P~ + p u~` with `u~ = lambda P'(t_0) (mod p)`, `lambda != 0`, then every determinant
`det5(P~, P~ + p u~, R~, S~, T~)` with `R~, S~, T~` representatives of three other curve points has
p-adic valuation exactly 1 (in particular is nonzero).

*Proof.* Let `f(t) = det[L(P(t_0)); L(P(t)); L(R); L(S); L(T)]`.  By the computation in Lemma A,
`f(t) = c (t - t_0)(t - t_1)(t - t_2)(t - t_3) / U(t)` with `c != 0` and `t_1, t_2, t_3` the parameters of
`R, S, T`.  Since `t_0` is a simple root and `U(t_0) != 0`, the formal derivative satisfies
`f'(t_0) = c (t_0-t_1)(t_0-t_2)(t_0-t_3)/U(t_0) != 0`.  By multilinearity `f'(t_0)` is the determinant
in the statement.  The consequence follows from Lemma T: `det5 = p * det[L(P~); sigma; ...]` with
`sigma = tau_{u~}(P) = lambda L'(t_0) (mod p)`.  ∎

(As a by-product `P'(t_0) != 0` for every affine point: the affine part of the curve is smooth.)

**Lemma O' (every other twin direction has many bad triples).** Let `u in F_p^3` with `|u|^2 != 0`
and `u` not proportional to `P'(t_0)`.  Then the number of 3-subsets `{R,S,T}` of affine curve points
other than `P` with `det[L(P); tau_u(P); L(R); L(S); L(T)] = 0` is at least `p^2/6 - O(p)`.

*Proof.* Let `l` be the line through `L(P)` and `tau_u(P)`.  On the quadric `Q = x^2+y^2+z^2 - wv`
one has `Q(L(P) + s tau_u(P)) = s^2 |u|^2`, so for `|u|^2 != 0` the line `l` meets `Q`, hence the curve
`C`, only at `L(P)`, and (as `u` is not the tangent direction) with multiplicity 1.  Project from `l`:
`pi : C -> C' subset PG(2,p)`, `deg(pi) deg(C') = 4 - 1 = 3`.  If `deg(C') = 1` then `C` lies in
the plane spanned by `l` and a line, contradicting that `C` spans `PG(4,p)`; so `C'` is an
irreducible plane cubic and `pi` is birational.  A hyperplane contains `l` and `R, S, T` iff
`pi(R), pi(S), pi(T)` are collinear.  For any two affine points `R != S` (other than `P`) with
distinct images, the line through `pi(R), pi(S)` meets `C'` in a third `F_p`-rational point; unless
that point is `pi(R)`, `pi(S)`, `pi(P)`, the (at most one) singular point of `C'`, or the image of one
of the at most `deg U <= 4` points at infinity — each of which happens for `O(p)` pairs, since a
line through a fixed point of `C'` contains at most two further points — it is `pi(T)` for a unique
affine `T`, giving a bad triple.  Each bad triple arises from at most 3 pairs.  ∎

Lemma O' says the tangent direction is the *only* twin direction with a full level-2 certificate;
Section 4.1 explains (heuristically) why this does not help inside a box.

### 2.5 The Vandermonde-valuation bound for p-adic curve certificates

Suppose the curve of Lemma A is given by polynomials with integer (p-adic integer) coefficients,
`det(M)` a p-adic unit, and consider parameters `t in Z/p^k` with `U(t)` a unit.  Exactly as in
Lemma A, for the integer representatives `P~(t) in [0,p^k)^3`,
`det5(P~(t_1..t_5)) = ± det(M) V(t) / prod U(t_i)   (mod p^k)`,
so `v_p(V(t)) = sum_{i<j} v_p(t_i - t_j) <= k - 1` certifies `det5 != 0`.  Call a parameter set
`T subset Z/p^k` *V-certified* if this holds for all its 5-subsets.

**Lemma V (for `2 <= k <= 10`).** Let `2 <= k <= 10` and let `j(k)` be the largest `j` with
`C(j,2) <= k-1` (so `j(2) = j(3) = 2`, `j(4..6) = 3`, `j(7..10) = 4`).  A V-certified set satisfies
`|T| <= p + 1` when `k = 2`, and `|T| <= p * j(k) <= 4p` for `2 <= k <= 10`.

*Proof.* Two parameters in the same class mod `p` contribute at least 1 to the valuation sum of every
5-subset containing both.  Suppose some class contains `j(k) + 1` parameters.  Since `k <= 10` we
have `j(k) <= 4`, so these `j(k) + 1 <= 5` parameters fit in one 5-subset (complete it arbitrarily if
`|T| >= 5`; if `|T| <= 4` there is nothing to prove since `p j(k) >= 4`), whose valuation sum is
`>= C(j(k)+1, 2) > k - 1`, contradicting V-certification.  Hence every class has at most `j(k)`
elements and `|T| <= p j(k)`.  For `k = 2`: `j(2) = 2`, and two classes with two elements each would
give a `(2,2,1)` 5-subset of valuation sum `>= 2 > k-1`; so at most one class has two elements.  ∎

The restriction `k <= 10` is necessary for this argument and for the statement: for `k = 11` and
`T = {0, ..., p^2 - 1} subset Z/p^11`, every pair has valuation `<= 1`, so every 5-subset has
valuation sum `<= 10 = k - 1`, yet `|T| = p^2 > 5p = p j(11)` (counterexample from the referee
report).

**Lemma V' (pigeonhole bound, every `k >= 2`).** A V-certified set `T subset Z/p^k` satisfies
`|T| <= 4 p^{ceil(k/10)}`.  In a box of side `N = p^k` this is `4 N^{ceil(k/10)/k} <= 4 N^{1/2}`.

*Proof.* Let `j = ceil(k/10)`.  If `|T| > 4 p^j`, five elements of `T` share a class mod `p^j`; every
pair of them has valuation `>= j`, so their valuation sum is `>= 10 j >= k > k - 1`, and the 5-subset
is not certified.  Finally `ceil(k/10)/k <= 1/2` for every `k >= 2` (equality at `k = 2`; for
`k <= 10` the ratio is `1/k`, and for `k >= 11` it is `<= (k/10 + 1)/k <= 1/10 + 1/11`).  ∎

So the only way to use a *single* curve mod `p` beyond `p` points is to lose at least a square root of
the box side (constant 4); Lemma O is the `k = 2`, one-class case seen from the archimedean side.

### 2.6 The parallelogram lemma for translate constructions

**Lemma R.** Let `S` contain `Q + Ma, Q + Ma + Mu, Q' + Mb, Q' + Mb + Mu` (two twin pairs with the same
translate direction `u`).  These four points form a parallelogram; it is concyclic iff it is a
rectangle iff `(Q' - Q + M(b - a)) . u = 0`; and in that case *every* 5-subset of `S` containing the
four points is degenerate.

*Proof.* Opposite sides are the equal vectors `Mu`.  A parallelogram inscribed in a circle has
opposite angles both equal and supplementary, hence right; a rectangle is concyclic.  The right-angle
condition is `Mu` perpendicular to the other side.  Finally a circle lies on a pencil of spheres and
on its plane; a fifth point `X` is either in that plane (five coplanar points) or on the unique sphere
of the pencil through `X`.  ∎

In `S = S_1 + M A` with `A` a tetrahedron the six edge directions `u` give, for each ordered pair of
base points and each pair of translates, one linear condition `(Q' - Q) . u = -M (b-a) . u`; with
`|S_1| = p` base points there are `Theta(p)` solutions per direction, and each rectangle kills
`|S| - 4 = Theta(p)` 5-subsets — the `Theta(p^2)` "concyclic4" zeros of Section 3.  The condition is
archimedean (exact equality of integers), so it is *independent of M* and of the mod-`p` structure of
`S_1`; the census confirms this (Section 3.4).

## 3. The 4-translate construction and what the computations say (numerical, not proved)

### 3.1 The construction and its exact accounting

Let `S_1 subset [0,p)^3` be the residue set of a Lemma-A curve (`|S_1| = p`), `A subset {0,1}^3` a
tetrahedron (`TETRA = {000, 110, 101, 011}` or `AXES = {000, 100, 010, 001}`; any five vertices of a
cube are cospherical, so `|A| <= 4`, and four vertices must not be a rectangle), and
`S = S_1 + p A subset [0,2p)^3`, `|S| = 4p`, i.e. `|S| = 2n` at `n = 2p`.  Reducing mod `p`, every
5-subset whose five base points are distinct has `det5 != 0 (mod p)` by Lemma A (checked: with base =
curve and `M = p` or `2p` there are 0 zeros with five distinct base points; with a random base there
are 114, `data/shift_rand13.txt`).  The remaining 5-subsets, by multiplicity pattern of base points
`(2,1,1,1), (2,2,1), (3,1,1), (3,2), (4,1)`, have `det5 = 0 (mod p)` by Lemma T and must be nonzero
for archimedean reasons.  There are `~64 p^4` of pattern `(2,1,1,1)` and `~72 p^3` of `(2,2,1)`.

### 3.2 Exact census at p = 13 (`src/translate4.py 13 1 tetra|axes`, file `data/translate4_p13.txt`)

Both patterns fail badly.  Base fibres (max points of `S_1` on a plane `x=c`, `y=c`, `z=c`) are `[2,2,4]`.

| A | zeros / 2,598,960 | (2,1,1,1) | (2,2,1) | (3,1,1) | (3,2) | (4,1) |
|---|---|---|---|---|---|---|
| TETRA | 3522 | 1041 | 2157 | 126 | 196 | 2 |
| AXES  | 3986 | 1291 | 2242 | 214 | 237 | 2 |

Mechanism census (`src/analyze_zeros.py`; each zero 5-subset is classified as: contains a collinear
triple; contains four concyclic points; five coplanar; else a genuine cospherical five) for TETRA,
by number of distinct base points (`data/shift_nrc13.txt`, line `M=13`):

| distinct base points | collinear3 | concyclic4 | coplanar5 | sphere5 |
|---|---|---|---|---|
| 4 = pattern (2,1,1,1) | 69 | 480 | 90 | 402 |
| 3 = (2,2,1)+(3,1,1) | 324 | 1484 | 218 | 257 |
| 2 = (3,2)+(4,1) | 36 | 104 | 52 | 6 |

The `concyclic4` column is Lemma R (rectangles from equal translate directions) plus isosceles
trapezoids from two base points on a common axis fibre; `collinear3`/`coplanar5` come from the fibre
coincidences (`fibers = [2,2,4]`: four base points on one plane `z = c` give, with their translates,
up to 8 points on that plane).

### 3.3 The zeros are not a mod-p artefact: the shift test (`src/shift_test.py`, `data/shift_*.txt`)

Replacing the translate step `M = p = 13` by `M = 14, 16, 26, 97` (same `S_1`, same `A`):
zeros = 3522, 3309, 3014, 2820, 2526 (curve base) and 3729, 3651, 3328, 3456, 2927 (random base of 13
points).  The `concyclic4`/`collinear3`/`coplanar5` counts are essentially constant in `M` (they are
exact integer coincidences, Lemma R), while the `sphere5` count with four distinct base points drops
from 402 (`M = p`) to 42 (`M = 97`) for the curve base and from 330 to 33 for the random base.  So
`M = p` enhances genuine cospherical fives by roughly a factor `p` (consistent with Lemma T: these
determinants are forced to be `0 mod p`, which raises the chance of an exact zero by about `p` in a
random-integer model), and the enhancement is the same for a random base — the arc property is
irrelevant for repeated-base 5-subsets, as it must be.

### 3.4 p-adic profile (`src/padic_profile.py`, 200,000 random (2,1,1,1) configurations)

Valuation `v_p(det5)` histogram: `p = 13`: `v=1: 185149, v=2: 13610, v=3: 1027, v=4: 37, exact zero: 177`;
`p = 29`: `v=1: 193115, v=2: 6636, v=3: 231, v=4: 6, exact zero: 12`.  Valuations `>= 2` follow the
random model `p^{-(v-1)}` (13610/200000 = 0.068 ~ 1/13 = 0.077; 6636/200000 = 0.033 ~ 1/29 = 0.034);
Lemma O' predicts exactly this: for a non-tangent twin direction a fraction `~1/p` of triples is bad.
The exact zeros are what remains after the archimedean coincidence.

### 3.5 What the genuine cospherical fives look like (`src/sphere_load.py 13 1 tetra nrc|random 13`)

At `p = 13`, TETRA: 420 distinct spheres carry a `sphere5` zero; they carry 5, 6, 7 points of `S` in
346, 69, 5 cases; 257 of the 420 centres have denominator 1 or 2 (half-integer centres such as
`(19/2, 23/2, 10)`, `(10, 12, 8)`).  A random 13-point base gives the same picture (417 spheres,
362/48/7).  Uniformly random 5-subsets of `S` have a centre with denominator < 100 in 39% of cases.
*Interpretation (not a finding):* we see no sign of a hidden identity behind these zeros beyond the
`mod p` boost of 3.3; they look like ordinary lattice coincidences of a set that is `2n` points
dense in a box of side `n`.

### 3.6 Greedy deletion: the arc construction is worse than random (`src/greedy_delete.py`, `data/greedy_delete.txt`, `data/greedy_delete_random_large.txt`, `data/greedy_delete_gamma.txt`)

List all zero 5-subsets (exact), repeatedly delete the point contained in the most surviving zero
subsets, re-verify the survivor with `zero5` (all survivors below re-check `zeros=0`).  Seed 1 in
all rows; "random" is `4p = 2n` uniformly random distinct points of `[0,2p)^3` unless the row says
`2.5 n` (then `5p` points).

| n = 2p | construction | zeros before | deleted | survivor | survivor / n |
|---|---|---|---|---|---|
| 26 | `S_1 + 13 TETRA` | 3522 | 24 | 28 | 1.077 |
| 26 | random 52 pts | 210 | 15 | 37 | 1.423 |
| 34 | `S_1 + 17 TETRA` | 3931 | 33 | 35 | 1.029 |
| 34 | random 68 pts | 180 | 20 | 48 | 1.412 |
| 38 | `S_1 + 19 TETRA` | 6144 | 41 | 35 | 0.921 |
| 38 | random 76 pts | 204 | 22 | 54 | 1.421 |
| 46 | `S_1 + 23 TETRA` | 5710 | 45 | 47 | 1.022 |
| 46 | random 92 pts | 316 | 25 | 67 | 1.457 |
| 58 | `S_1 + 29 TETRA` | 11838 | 61 | 55 | 0.948 |
| 58 | random 116 pts | 474 | 33 | 83 | 1.431 |
| 62 | `S_1 + 31 TETRA` | 13790 | 62 | 62 | 1.000 |
| 62 | random 124 pts | 665 | 34 | 90 | 1.452 |
| 80 | random 160 pts | 542 | 44 | 116 | 1.450 |
| 100 | random 200 pts | 617 | 56 | 144 | 1.440 |
| 60 | random 150 pts (`2.5 n`) | 1287 | 55 | 95 | 1.583 |
| 80 | random 200 pts (`2.5 n`) | 1499 | 75 | 125 | 1.562 |

The arc-plus-translates set has `Theta(p^2)` structural zeros (Lemma R and fibre coincidences) and
ends near `1.0 n`; a uniformly random `2n`-point set has `O(n)` zeros and ends near `1.41–1.46 n`
(`1.44 n` at `n = 100`).  Starting denser helps: `2.5 n` random points leave `1.58 n` at `n = 60` and `1.56 n` at `n = 80`
(`data/greedy_delete_gamma.txt`, `n = 40`, seed 1, `m = gamma n` initial points):

| m | gamma | zeros before | deleted | survivor | survivor / n |
|---|---|---|---|---|---|
| 100 | 2.5 | 1097 | 41 | 59 | 1.475 |
| 120 | 3 | 2262 | 53 | 67 | 1.675 |
| 140 | 3.5 | 4961 | 71 | 69 | 1.725 |
| 160 | 4 | 10201 | 89 | 71 | 1.775 |

The zero counts follow the random model `~ kappa gamma^5 n` (**numerical**: `kappa = 0.23–0.28`
here, where `kappa ~ Z(n)/n^{11}` with the crude sampling factor; 3.7 gives `0.19` at larger `n`;
this `kappa` is a finite-size measurement, not the asymptotic constant of 4.4), the deleted fraction of `m` rises from 0.41 to 0.56, and the survivor still
grows with `gamma`.  Whether it saturates below `2n` is unknown; the limit `gamma = n^2` is greedy
independent-set selection on the whole box, which is the starting point the round-26 searches improve
on (they reach `~2.6 n`).
For comparison the verified records are `2.5 n`–`2.6 n` (`C(26) >= 67`, `C(46)` unknown).  None of
this is a proof of anything; it is the measured size of two deterministic procedures.

### 3.7 Zero census of random sets versus box size (`src/random_census.py`, `data/random_census_g2.txt`, `_g15.txt`)

`m = 2N` uniformly random points of `[0,N)^3`, three seeds each; counts of zero 5-subsets by mechanism
(mean over seeds):

| N | subsets | zeros (mean) | coplanar5 | sphere5 | concyclic4 + collinear3 |
|---|---|---|---|---|---|
| 20 | 658,008 | 138 | 22 | 92 | 24 |
| 30 | 5,461,512 | 230 | 37 | 171 | 22 |
| 40 | 24,040,016 | 289 | 57 | 196 | 36 |
| 60 | 190,578,024 | 352 | 87 | 259 | 7 |

and for `m = 1.5 N`: `N = 30`: 51, 52, 109 zeros; `N = 60`: 65, 62, 87 zeros (sphere5 45–68).

Two readings matter for Section 4.4 (both **numerical**).  (i) Scaling in the density: from
`m = 1.5N` to `m = 2N` at `N = 60` the sphere5 count grows by `~4.4`, compared with `(2/1.5)^5 = 4.2`
— the fifth-moment behaviour of independent 5-subsets.  (ii) Scaling in `N`: at fixed `m/N = 2`, the
coplanar5 count grows roughly linearly in `N` (as it must: the `3N` axis planes each carry
`Poisson(2)` points).  The ratio sphere5/N is 4.6, 5.7, 4.9, 4.3 for `N = 20, 30, 40, 60`: it
*falls* after `N = 30`.  (An earlier version read this as linear growth; that reading is withdrawn.)
With three seeds and a heavy-tailed distribution these numbers cannot decide between `n^{10+o(1)}`
and `n^{11}` cospherical 5-subsets of the grid.  The sibling memo's exact Monte Carlo of `E(n)`
(expected number of further grid points on the circumsphere of four random grid points,
`research/spikes/no-five-upper/`, `n <= 128`) is more informative: it gives
`Z_sphere(n)/n^{11} ~ n E(n)/120 = 0.27, 0.23, 0.19, 0.175, 0.135, 0.084` for
`n = 16, 32, 48, 64, 96, 128`, clearly decreasing.  This supports hypothesis H1 of Section 4.4
(`Z_sphere = o(n^{11})`) and the standard heuristic `n^{10+o(1)}` (spheres whose centres have bounded
denominator number `~n^5` and carry `~n` grid points each), but proves nothing.

Caveats on the coplanar column: `random_census` uses three seeds, the distribution is heavy-tailed,
and the classifier files coplanar 5-subsets that contain a collinear triple or a concyclic
quadruple under those columns.  The resulting "coplanar5 ~ 1.45 N" (i.e. `Z_plane ~ 0.045 n^{11}`)
is about 35% below the asymptotic constant `K_* ~ 0.072` of Section 4.4; the referee's 20 seeds at
`N = 20`, `m = 40` gave a coplanar mean of 36.0 (standard deviation 29.1), i.e. about `0.073` after
dividing by the exact sampling factor `C(m,5)/C(N^3,5)` (the cruder factor `(m/N^3)^5` used for the
`0.045` figure also biases it low at these sizes).

## 4. Obstruction analysis

### 4.1 Single-prime certificates, boxes, and twins

*Ball's theorem* (arcs in `PG(4,p)` have at most `p+1` points; this needs `p >= 5`, the MDS
condition `k = 5 <= q` — in `PG(4,2)` and `PG(4,3)` the maximum arc has 6 points) means that any set
whose 5-subsets are all certified by "`det5 != 0 (mod p)`" has at most `p+1` points.  *Heuristic:*
Weil equidistribution for the affine points of a curve mod `p` suggests that a near-complete arc
has about `p (n/p)^3` points in a sub-box of side `n < p`; if every large arc lay on a normal rational
curve (known only for arcs close to the maximum size), a single prime `p` would certify at most
`~ min(p, n^3/p^2) <= n` points inside `[0,n)^3`.  Ball's theorem is used as a black box (not
re-proved here); the `min(p, n^3/p^2)` bound is a heuristic for general arcs.

*What Ball forces (proved, weak).*  Let `p >= 5` be prime and `S subset Z^3` with `|S| >= p + 2`.
(i) Every `(p+2)`-subset of `S` contains a 5-subset with `det5 = 0 (mod p)`: if two of its points
coincide mod `p`, any 5-subset containing both has two equal rows mod `p`; otherwise the `p+2`
points `L(P) mod p` are distinct points of `PG(4,p)`, not an arc by Ball, so five of them lie on a
hyperplane.  (ii) Averaging over the `(p+2)`-subsets (each 5-subset lies in `C(|S|-5, p-3)` of them),
at least `C(|S|,p+2)/C(|S|-5,p-3) = C(|S|,5)/C(p+2,5)` 5-subsets of `S` have `det5 = 0 (mod p)`.
(iii) Equivalently, at least `|S| - p - 1` points must be deleted before the mod-`p` test certifies
every remaining 5-subset.  For `p ~ n` and `|S| = (1+eps) n` the count in (ii) is only
`~ (1+eps)^5`, a constant.

*Withdrawn claim.*  An earlier version stated that every `S subset [0,n)^3` with `|S| >= (1+eps) n`
has, for every prime `p <= n`, at least `eps n - 1` points sharing their residue class mod `p` with
another point, hence `Theta(eps n^4)` 5-subsets with `det5 = 0 (mod p)`.  This is false: residue
classes of points mod `p` live in `F_p^3`, and there are `p^3` of them, not `p` (for example, any 11
points of `[0,7)^3 subset [0,10)^3` are pairwise distinct mod 7).  Pigeonhole forces repeated classes
only when `|S| > p^3`.  The count `Theta(eps n^4)` does hold for curve-based constructions: when `S`
contains a near-complete arc on a normal rational curve, a point off the curve lies on `~p^3/24`
hyperplanes spanned by four curve points (**heuristic** count, from the referee report).  But this
is special to such constructions, and nothing in Sections 4.2–4.4 depends on the withdrawn claim.

*Tangent twins.*  Lemma O gives the only second-level certificate available from the curve
itself: the twin of `P(t_0)` must be `P~ + p u` with `u = lambda P'(t_0) (mod p)`.  Inside `[0,N)^3`,
`N = hp`, the admissible `u` lie in `[-h,h]^3`; for the `U = 1` quartic curves `P'` has degree 3, so
each projective direction is the tangent direction of at most 3 parameters, and the number of
twin pairs is at most `3 (2h+1)^3`.  Heuristically (the residue classes `lambda P'(t_0)` behave like
random points of `F_p^3`) a class has `~ 8h^3/p^2` admissible twins, so two points per class need
`h ~ p^{2/3}`, i.e. `N ~ p^{5/3}` and `|S| ~ 2p ~ 2 N^{3/5}`: sublinear.  (**Heuristic**; the rigorous
statements of the same phenomenon on the p-adic side are Lemmas V and V'.)

### 4.2 p-adic curves (Lemmas V and V')

Putting all points on one p-adic curve and certifying by the valuation of the Vandermonde loses a
square root of the box side: at most `4 N^{1/2}` points for every `k >= 2` (Lemma V'; Lemma V gives
`<= 4p = 4 N^{1/k}` for `2 <= k <= 10`).  *Heuristic:* two curves mod the same `p` do not help either:
a hyperplane through three points of one quartic and one point of the other meets the second
quartic in three further points, one of which is rational on average, so one expects `Theta(p^4)`
mixed 5-subsets that are `0 mod p`.  (An earlier version also claimed that two different primes on
the same point set force `|S| <= min(p,q) + 1`; that claim was unproved — certifying a 5-subset mod
`pq` needs only one of the two primes, so Ball for each prime separately gives nothing — and it is
withdrawn.)

### 4.3 Translate constructions

`S = S_1 + M A` with `A` a tetrahedron always contains `Theta(p)` rectangles (Lemma R: the six edge
directions `u` of the tetrahedron give linear conditions `(Q'-Q).u = -M(b-a).u` on pairs of base
points, each with `Theta(p)` solutions among `p` base points), hence `Theta(p^2)` zero 5-subsets,
independently of `M` and of the arc property (3.3).  Killing them requires a base set on which the
six functionals `x ± y, y ± z, x ± z` avoid the values `0, ±M, ±2M` on all differences — a strong
archimedean condition that a curve reduced mod `p` has no reason to satisfy — *and* per-point
translate patterns `A(P) subset {0,1}^3` chosen so that the axis-plane budget holds
(a plane `x = c` may contain at most 4 points, i.e. `sum_{P : P_x = c} #{a in A(P) : a_x = 0} <= 4`);
with fibres `[1,3,3]` (Section 2.3) this is a constraint-satisfaction problem that I did not solve.
Even then the `~ 64 p^4` pattern-`(2,1,1,1)` subsets remain, each forced to `0 mod p`; among them
the measured exact zeros number in the hundreds at every `p` tested (Section 3.3: `sphere5` count 402
at `M = p = 13`, **numerical**), so *some* deletion appears unavoidable and we see no route to a proof
of exact validity from this construction.

**Fibre lemma (proved).**  Work with binary forms of degree 4 in `(t : s)`, so that `t = infinity`
is a root like any other.  For a Lemma-A curve let `m_x` be the number of common roots of `X` and `U`
(with multiplicity, over the algebraic closure, including `t = infinity`), and similarly `m_y, m_z`.

(a) A plane `x = c` contains at most `4 - m_x` points of `S_1`, and likewise for `y, z`.  *Proof:* the
points with `x = c` come from roots `t in T` of the form `X - cU`, which has degree 4 and vanishes at
the `m_x` common roots of `X, U` for every `c`; those common roots are zeros of `U`, hence not in `T`,
and `X - cU` is not identically zero because `X, U` are independent.  So at most `4 - m_x` roots lie
in `T`.  ∎  We call `(4 - m_x, 4 - m_y, 4 - m_z)` the *guaranteed fibre profile*.  (Actual fibres can be
smaller for a particular `p`.)

(b) The family of 2.3 has guaranteed profile `(1,3,3)`: with `U = t s^3`, the form `X = t^2 s^2`
shares the roots `t = 0` (once) and `s = 0` (twice) with `U`, so `m_x = 3`; `Y` and `Z` have degree
exactly 3 in `t` (leading coefficients `q_2/2`, `q_2/(2i)`), so they vanish once at `s = 0`, and they do
not vanish at `t = 0` (`Y(0) = r_0/2`, `Z(0) = -r_0/(2i)`, `r_0 != 0`), so `m_y = m_z = 1`.  The class of
Lemma-A curves with guaranteed profile `(1,3,3)` therefore *includes* the family of 2.3; we have not
proved the converse (that every such curve is of that form).

(c) *No coordinate of a Lemma-A curve with `U = 1` has degree `<= 1`* (equivalently, for `U = 1`
curves every guaranteed fibre bound is `>= 2`; the cubic family has profile `(2,3,3)`).  *Proof*
(complete version from the referee report).  Suppose, by symmetry, `deg X <= 1`.  `X` is not
constant (else `1, X` are dependent), so `span{1, X} = span{1, t}`, and `1, X, Y, Z` must be
linearly independent.  If `p = 1 (mod 4)`, let `A = Y + iZ`, `B = Y - iZ`, so `span{1,X,Y,Z} =
span{1,t,A,B}` and `X^2 + AB = W` has degree `<= 4`; as `deg X^2 <= 2`, `deg(AB) <= 4`, and `A, B != 0`
(if `A = 0` then `Y, Z` are dependent), so `deg A + deg B <= 4`.  If `min(deg A, deg B) <= 1`, that
polynomial lies in `span{1, t}`: dependent.  Otherwise `deg A = deg B = 2`, and `1, t, A, B` are four
vectors in the 3-dimensional space of polynomials of degree `<= 2`: dependent.  If `p = 3 (mod 4)`,
`x^2 + y^2` is anisotropic over `F_p`, so the leading coefficients cannot cancel and
`deg(Y^2 + Z^2) = 2 max(deg Y, deg Z)`; since `Y^2 + Z^2 = W - X^2` has degree `<= 4`, `deg Y, deg Z
<= 2`, and `1, t, Y, Z` are again four vectors in a 3-dimensional space: dependent.  In both cases
Lemma A's independence hypothesis fails.  ∎

(d) *No Lemma-A curve has guaranteed profile `(1,1,1)`* (so an "axes" translate pattern whose
unit-fibre budget is guaranteed by (a) in all three directions is impossible).  *Proof* (from the
referee report).  `m_x >= 3` means `X = G_x l_x` and `U = G_x mu_x` with `G_x` a cubic form and
`l_x, mu_x` linear forms; similarly for `y` and `z`.  If two of the `mu` are proportional, say
`mu_x ~ mu_y`, then unique factorisation of `U` gives `G_x ~ G_y =: G`, so `X`, `Y` and `U` all lie in
the 2-dimensional space `G * {linear forms}`: dependent.  Otherwise the roots `r_x, r_y, r_z` of
`mu_x, mu_y, mu_z` are distinct points of `P^1`.  `x = X/U = l_x/mu_x` has a simple pole at `r_x`
(`l_x` is not proportional to `mu_x`, else `X ~ U`), while `y = l_y/mu_y` and `z = l_z/mu_z` are
regular there.  So `W/U = x^2 + y^2 + z^2` has a double pole at each of `r_x, r_y, r_z`, i.e. poles of
total order `>= 6`; but the poles of `W/U` are among the roots of `U`, of total order `<= deg U = 4`.
Contradiction.  ∎

### 4.4 The deletion route: a conditional lower bound `C(n) >= (1.03 - o(1)) n`

*Revision note.*  The first version of this section concluded that plain random deletion "cannot
yield `(1+eps) n` ... which the data contradict".  That conclusion rested on two input constants
that were wrong (a coplanar constant measured about 35% low and a cospherical constant read as
growing when the data show it falling) and is withdrawn.  The correct statement is conditional.

**Definitions.**  `Z(n)` is the number of degenerate 5-subsets of `[0,n)^3` (`det5 = 0`).
`Z_plane(n)` is the number of *coplanar* 5-subsets (all five points in one plane; this includes
collinear ones).  `Z_sphere(n)` is the number of 5-subsets that are *degenerate and not coplanar*
(these lie on a unique sphere; this includes non-coplanar 5-subsets containing four concyclic
points).  So `Z(n) = Z_plane(n) + Z_sphere(n)`, a disjoint decomposition.

**Proposition D (proved, elementary).** Let `B subset [0,n)^3`, `|B| = b`, and let `Z(B)` be the number
of degenerate 5-subsets of `B`.  For `m <= b` let `S` be a uniformly random `m`-subset of `B`.  Then
`E[#degenerate 5-subsets of S] = Z(B) C(m,5)/C(b,5) <= Z(B) (m/b)^5`, and deleting one point from each
degenerate 5-subset of `S` leaves a valid set (as in Lemma DEL below); hence
`C(n) >= m - Z(B) (m/b)^5` for every `m <= b`.

*Proof.* Each 5-subset of `B` lies in `S` with probability `C(b-5, m-5)/C(b,m) = C(m,5)/C(b,5)
<= (m/b)^5`; sum over degenerate 5-subsets; some outcome is at least as good as the expectation.  ∎

**Lemma DEL (Bernoulli deletion, proved).**  For every `n >= 1` and `0 < q <= 1`,
`C(n) >= q n^3 - q^5 Z(n)`.

*Proof.*  Let `S subset [0,n)^3` contain each grid point independently with probability `q`.  Let
`D` be the set of degenerate 5-subsets `T subset [0,n)^3` with `T subset S`.  For each `T in D` choose
one point `x_T in T` (say the lexicographically least), let `R = {x_T : T in D}` and `S' = S \ R`.
*Validity:* let `T subset S'` be any 5-subset.  Then `T subset S`; if `T` were degenerate we would have
`T in D`, hence `x_T in R`, but `x_T in T subset S' = S \ R`, a contradiction.  So no 5-subset of `S'`
is degenerate, i.e. `S'` is valid (trivially so if `|S'| < 5`).  *Size:* `|S'| >= |S| - |R| >= |S| - |D|`.
By linearity and independence, `E|S| = q n^3` and `E|D| = sum_{T degenerate} Pr[T subset S] =
q^5 Z(n)`.  Hence `E|S'| >= q n^3 - q^5 Z(n)`, and some outcome has `|S'| >= E|S'|`.  ∎

**Proposition P (conditional lower bound; the implication is proved, the hypotheses are not).**
Fix a constant `K > 0` and assume

* **(H1)** `Z_sphere(n) = o(n^{11})`, and
* **(H2(K))** `Z_plane(n) <= (K + o(1)) n^{11}`.

Then `C(n) >= (0.8 (5K)^{-1/4} - o(1)) n`.  In particular, if `K < (4/5)^4/5 = 0.08192`, then
`C(n) >= (1 + eps_K - o(1)) n` with `eps_K = 0.8 (5K)^{-1/4} - 1 > 0`.

*Proof.*  By (H1) and (H2(K)), `Z(n) <= (K + delta(n)) n^{11}` with `delta(n) -> 0`.  Put
`c = (5K)^{-1/4}` and `q = c/n^2`, which is `<= 1` once `n^2 >= c`.  Lemma DEL gives
`C(n) >= c n - c^5 (K + delta(n)) n = c (1 - K c^4) n - c^5 delta(n) n = (4/5) c n - c^5 delta(n) n`,
since `K c^4 = 1/5`.  (This `c` maximises `c - K c^5`: the derivative `1 - 5 K c^4` vanishes there.)
Finally `(4/5)(5K)^{-1/4} > 1` iff `5K < (4/5)^4` iff `K < 0.08192`.  ∎

Only the combined bound `Z(n) <= (K + o(1)) n^{11}` is used, so (H1) can be weakened to
`Z_sphere(n) <= (K' + o(1)) n^{11}` with `K + K' < 0.08192`.

**Lemma K (the coplanar series; computed, with a proved tail bound).**  For primitive `v in Z^3`
let `phi_v` be the density of `v.U`, `U` uniform on `[0,1]^3`, and put
`K_* = (1/120) sum_{v primitive, one of each pair +-v} int phi_v(s)^5 ds`.  Then
`0.07172 <= K_* <= 0.07273`.

*Computation and proof of the tail.*  `src/kplane.py 100` (output `data/kplane.txt`) sums the terms
with `max|v_i| <= 100`: one nonzero coordinate gives `int phi^5 = 1`; two nonzero coordinates
`a <= b` give a trapezoid and `int phi^5 = (b - 2a/3)/b^5`; three give a piecewise quadratic `phi`,
integrated exactly per piece by 6-point Gauss–Legendre (floating point).  The partial sums are
`0.04676, 0.06485, 0.06821, 0.07013, 0.07112, 0.07172` for `max|v_i| <= 1, 5, 10, 20, 40, 100`.
Tail: if `max|v_i| = A`, then `v.U = X + A U_j` with `X` independent of `U_j`, so `phi_v <= 1/A` and
`int phi_v^5 <= (sup phi_v)^4 int phi_v <= A^{-4}`; there are at most `((2A+1)^3 - (2A-1)^3)/2 = 12A^2 + 1`
such `v` up to sign; so the terms with `A > 100` contribute at most
`(1/120) int_{100}^{inf} (12 x^{-2} + x^{-4}) dx < 0.00101`.  ∎  A fit `K - beta/A - gamma/A^2` to
the partial sums for `33 <= A <= 100` gives `K_* ~ 0.0721` (**numerical** extrapolation), in agreement
with the referee's independent computation (partial sums `0.0468, 0.0648, 0.0701, 0.0711` at
`A = 1, 5, 20, 40`, fit `0.0721`).

**Corollary P'.**  If (H1) and (H2(K_*)) hold, then `C(n) >= (1.030 - o(1)) n` (using
`K_* <= 0.07273`; the value at `K_* ~ 0.0721` is `~1.032`).  This would improve the known
`n - o(n)`.  **It is conditional and is not claimed as a theorem.**

*Why `K_*` is the natural constant in H2 (heuristic).*  A lattice plane `v.x = k` (`v` primitive)
meets `[0,n)^3` in about `n^2 phi_v(k/n)` grid points, so it carries about `(n^2 phi_v(k/n))^5/120`
5-subsets; summing over `k` gives `~ n^{11} int phi_v^5 / 120` per direction, and summing over
directions gives `K_* n^{11}`.

*Status of H2.*  Proved: `Z_plane(n) >= 3n C(n^2,5) - 3n^2 C(n,5) ~ n^{11}/40` from the axis planes
alone (a 5-subset in two axis planes lies on an axis-parallel line, and each of the `3n^2`
axis-parallel lines lies in exactly two axis planes, so the subtraction removes the double count).
Exact finite sums over lattice planes with normals `max|v_i| <= n-1` (referee's computation; lower
bounds up to a negligible overcount of collinear 5-subsets) give `Z_plane(n)/n^{11} >= 0.0580,
0.0668, 0.0691` at `n = 10, 20, 30`, increasing towards `K_*`; the same code reproduces the census
coplanar totals exactly at `n = 3, 4` (2274, 109680).  **H2(K_*) itself is not proved.**

*Status of H1.*  Let `E(n)` be the expected number of further grid points of `[0,n)^3` on the
circumsphere of a uniformly random 4-subset of `[0,n)^3` (0 if the four points are coplanar).  Every
degenerate non-coplanar 5-subset lies on a unique sphere and contains between 1 and 5 non-coplanar
4-subsets, so `Z_sphere(n) <= C(n^3,4) E(n) <= 5 Z_sphere(n)` (proved); hence **H1 is equivalent to
`E(n) = o(1/n)`**.  The sibling memo's exact Monte Carlo gives `n E(n) = 32.2, 27.4, 23.1, 21.0, 16.2,
10.1` at `n = 16, 32, 48, 64, 96, 128` (**numerical**; the `n = 128` value has standard error of order
10%), i.e. `Z_sphere/n^{11} ~ n E(n)/120` falling from 0.27 to 0.084; Section 3.7 discusses our own
(noisier) data.  The standard heuristic predicts `n^{10+o(1)}` (spheres with bounded-denominator
centres number `~n^5` and carry `~n` grid points each).  No rigorous bound `o(n^{11})`, or even
`O(n^{11})`, is known to us.  Trivial bounds have the form `C(n^3,4)` times the maximum number of grid
points of the box on one sphere; with the elementary `O(n^{5/3})` of the sibling memo's Lemma 4.1.1(iii)
this is `O(n^{12 + 5/3})`.

*Consistency check with Suk–White (arithmetic checked).*  If one only knows `Z(n) <= n^{e+o(1)}` for
some `e > 11`, Lemma DEL with `q = n^{-(e-3)/4 - eta}` gives `q n^3 = n^{(15-e)/4 - eta}` and
`q^5 Z(n) <= n^{(15-e)/4 - 5 eta + o(1)}`, so `C(n) >= n^{(15-e)/4 - o(1)}`.  For a crude
`Z(n) <= n^{12+o(1)}` this is `n^{3/4 - o(1)}`, exactly Suk–White's exponent `3/(d+1)` at `d = 3`
(arXiv 2412.02866); we do not claim this is how they argue.  (`e = 13` would give `n^{1/2}`, and
`e = 12 + 5/3` only `n^{1/3}`.)  Since `Z_plane = Theta(n^{11})` is harmless at these scales, the
sphere count is the only bottleneck between exponent `3/4` and a linear bound with constant `> 1`.

**Open Problem 4.5 (what would make Proposition P unconditional).**

1. *(H1)* Prove `Z_sphere(n) = o(n^{11})`, equivalently `E(n) = o(1/n)`; or at least
   `Z_sphere(n) <= 0.0091 n^{11}` for large `n` (the margin `0.08192 - 0.07273`).  This is a
   lattice-point statement: on average over spheres through four grid points of the box, the number
   of further grid points must be `o(1/n)`.
2. *(H2)* Prove `Z_plane(n) <= (K + o(1)) n^{11}` for an explicit `K` below the threshold (with
   `K = K_*` the bound of Lemma K suffices).  This needs (a) for each fixed normal `v`, the Riemann-sum
   limit `sum_k C(N_{v,k}, 5) = (int phi_v^5 + o(1)) n^{11}/120`, where `N_{v,k}` is the number of grid
   points on `v.x = k`, which is routine; and (b) a tail bound *uniform in `n`*: the planes with normals
   `max|v_i| > A` contribute at most `epsilon(A) n^{11}` with `epsilon(A) -> 0`.  Part (b) requires
   counting lattice points in planar sections of the cube uniformly in the normal, including
   normals of size up to `~n^2`.
3. *(Alternative)* Replace uniform sampling by a weighted or structured base set `B` in Proposition D
   that lowers the effective constant; compare the weighted random sampling plus careful deletion
   of Ghosal–Goenka (arXiv 2609.20447) in two dimensions.

*What the greedy numerics exploit.*  Greedy deletion (Section 3.6) does much better than the
one-point-per-zero count of Lemma DEL because the zero 5-subsets of a random set overlap heavily in
points.  At `N = 60`, `m = 120` (`data/random_spheres.txt`) the 322 zero subsets touch every point and
the ten most loaded points carry 24–33 zeros each; in the separate run at `n = 62`, `m = 124`
(`data/greedy_delete.txt`) the 665 zero subsets are killed by 34 deletions.  Almost all zero spheres
carry exactly five points of `S` (`data/random_spheres.txt`: 250 of 252 at `N = 60`).  Going beyond
the constant of Proposition P along these lines needs:

* **Statement S (open).** For `S` a uniform random `gamma n`-subset of `[0,n)^3`, the 5-uniform
  hypergraph of degenerate 5-subsets has a vertex cover of expected size `<= (gamma - 1 - eps) n` for
  some `gamma > 1 + eps`.  (The measured greedy cover is `~0.55 n` at `gamma = 2` and `~0.92 n` at
  `gamma = 2.5`, `n = 60`.)  This requires joint statistics of lattice points on spheres through four
  lattice points of the box — an arithmetic, not purely combinatorial, question.
* or a *structured* base set `B` (Proposition D allows any `B`) with `|B| >= (1+eps) n` and provably
  small `Z(B)`.  The algebraic candidates tried here fail for specific reasons: a single prime
  certifies at most `p+1` points (Ball, 4.1); p-adic curves lose a square root (Lemmas V, V'); and
  translate constructions carry `Theta(p^2)` structural zeros (Lemma R, 4.3).  Ball's theorem alone
  does *not* rule out a structured `B` of size `(1+eps) n`: it forces only `C(|B|,5)/C(p+2,5) = O(1)`
  mod-`p` zeros for `p ~ n` (4.1).

## 5. Conjectures (labelled) and candidate families with measured sizes

**Conjecture 1 (`C(n) >= 2n`, not new).** `C(n) >= 2n` for all `n >= 11`.  Evidence: the verified
frontier `research/extremal/claims/no-five-on-sphere-frontier.json` (`n = 17..26`: 45, 48, 50, 53, 55,
58, 59, 62, 65, 67, i.e. `2.58 n`–`2.65 n`), the Demonstrandum `CC(n)` sets at `2.0n–2.4n` for
`n = 7..21`, and the fitted law `floor((5n+7)/2)`.  Nothing in this memo moves it.

**Conjecture 2 (random-greedy law).** A uniformly random `2n`-subset of `[0,n)^3` followed by greedy
vertex-cover deletion of the degenerate 5-subsets leaves `>= 1.4 n` points, and starting from
`gamma n` points the survivor is increasing in `gamma` (`1.78 n` at `gamma = 4`, `n = 40`).  Evidence: Section 3.6
(`1.41–1.46 n` for `n = 26..100`, one seed each; `1.56–1.58 n` at `n = 60, 80` from `2.5 n` initial points).  No proof; Statement S (4.4) would be the statement to prove.

**Conjecture 3 (lattice-point count; revised).** `Z_sphere(n) = o(n^{11})`, and heuristically
`Z_sphere(n) = n^{10+o(1)}`, where `Z_sphere(n)` is the number of degenerate, non-coplanar 5-subsets of
`[0,n)^3`.  This is hypothesis H1 of Proposition P.  Evidence (**numerical**): the sibling memo's
`n E(n)`, proportional to `Z_sphere(n)/n^{11}`, falls from 32 at `n = 16` to 10 at `n = 128`;
our own sphere5/N ratios (Section 3.7) fall after `N = 30`.  *This reverses the first version*, which
conjectured `Z_sphere = Theta(n^{11})` with constant `~0.14` on a misreading of the `N <= 60` data.

**Candidate structured families (all sizes exact, verified with `zero5`):**

| family | box | size | verified for | status |
|---|---|---|---|---|
| `F(p; t^2, t^2+1)` (2.3; Dong–Xu mechanism) | `[0,p)^3`, `p = 1 mod 4` | `p - 1 = n - 1` | 8 primes `13 <= p <= 73` (`p = 5` has no 5-subsets) | proved for all such `p` (Lemma A); not new |
| random Lemma-A curve, `U = 1` (`src/nrc.py`) | `[0,p)^3` | `p = n` | `p = 13` (seed 1) | proved (Lemma A); guaranteed fibre bounds `>= 2` (4.3(c)) |
| `S_1 + p TETRA` (3.1) | `[0,2p)^3` | `4p = 2n` claimed | `p = 13..31`: invalid (3522–13790 zeros) | dead as stated |
| `S_1 + p TETRA` + greedy deletion | `[0,2p)^3` | `0.92 n`–`1.08 n` | `n = 26..62` | numerical only |
| uniform random `2n` points + greedy deletion | `[0,n)^3` | `1.41 n`–`1.46 n` | `n = 26..100` | numerical only |
| uniform random `2.5 n` points + greedy deletion | `[0,n)^3` | `1.56 n`–`1.58 n` | `n = 60, 80` | numerical only |
| uniform random `4 n` points + greedy deletion | `[0,n)^3` | `1.78 n` | `n = 40` | numerical only |
| verified records (round 26 frontier) | `[0,n)^3` | `~2.6 n` | `n = 17..26` | search, not a family |

Nothing in the table is a proof of `C(n) >= (1+eps) n`.  The only `(1+eps) n` statement in this
memo is the conditional Proposition P (Section 4.4).

## 6. Reproduction: commands, files, hashes

All commands run from `research/spikes/no-five-theorem/src/` with
`PY` set to the interpreter of a Python 3.12 environment with numpy and sympy, under `nice -n 15`; each run took
well under 20 CPU-minutes (the largest single `zero5` call, 200 points, checks 2.5e9 subsets).

```
cc -O2 -o zero5 zero5.c
printf '0 0 0\n1 0 0\n0 1 0\n0 0 1\n1 1 1\n' | ./zero5            # zeros=1 subsets=1
printf '0 0 0\n1 0 0\n0 1 0\n0 0 1\n1 1 1\n2 3 5\n' | ./zero5    # zeros=1 subsets=6
$PY lemmas_sympy.py                                                # all identities print == 0
$PY nrc.py 13 1 | ./zero5 5                                        # zeros=0 subsets=1287
$PY family133.py 73                          > ../data/family133_default.txt
$PY translate4.py 13 1 tetra; $PY translate4.py 13 1 axes > ../data/translate4_p13.txt
$PY shift_test.py 13 1 nrc > ../data/shift_nrc13.txt; $PY shift_test.py 13 1 random > ../data/shift_rand13.txt
$PY padic_profile.py 13 1 tetra 200000; $PY padic_profile.py 29 1 tetra 200000   # Section 3.4 (stdout)
$PY sphere_load.py 13 1 tetra nrc 13; $PY sphere_load.py 13 1 tetra random 13    # Section 3.5 (stdout)
for p in 13 17 19 23 29 31; do for mode in nrc random; do $PY greedy_delete.py $p 1 $mode; done; done > ../data/greedy_delete.txt
$PY greedy_delete.py 40 1 random 2; $PY greedy_delete.py 50 1 random 2; $PY greedy_delete.py 30 1 random 2.5; $PY greedy_delete.py 40 1 random 2.5 > ../data/greedy_delete_random_large.txt
for g in 2.5 3 3.5 4; do $PY greedy_delete.py 20 1 random $g; done > ../data/greedy_delete_gamma.txt
for N in 20 30 40 60; do for s in 1 2 3; do $PY random_census.py $N 2 $s; done; done > ../data/random_census_g2.txt
for N in 30 60; do for s in 1 2 3; do $PY random_census.py $N 1.5 $s; done; done > ../data/random_census_g15.txt
$PY random_spheres.py 40 2 1; $PY random_spheres.py 60 2 1 > ../data/random_spheres.txt
$PY kplane.py 100 > ../data/kplane.txt                             # Lemma K (about 15 s)
```

Source files (`src/`): `zero5.c` (exact checker), `nrc.py` (random Lemma-A curves), `family133.py`
(explicit family), `translate4.py` (translate construction + census), `analyze_zeros.py` (mechanism
classifier), `inspect_zeros.py`, `lemmas_sympy.py`, `padic_profile.py`, `shift_test.py`,
`sphere_load.py`, `greedy_delete.py`, `random_census.py`, `random_spheres.py`, `kplane.py` (the
series `K_*` of Lemma K).

### 6.1 SHA-256 of the committed sources and data (`shasum -a 256`, recomputed in the revision)

```
d28670fc6b22a8c5f3c29c55c830f10e6980ca4310176eb8cf227724f29ec3d5  src/zero5.c
8a071b434b85e0ed7f0de0f03e0e0e3e6f5e329d073b0c338d6d0b09012a3482  src/analyze_zeros.py
e1846eb9b0f681ecbdbc39c558859b505cffa2371188979cf29faa5f24b6004b  src/family133.py
87c2961161db284233a5dc6343118ce385643855bf1610764a30d86a8c58e5ef  src/greedy_delete.py
ecd47d75cf3ee4c0ba9d94365529e0a214ba442ab034e2b85bcaeac507cdaa41  src/inspect_zeros.py
2ee1980e42b90182ca5df39e9eea125e6cf82832210ffee26490d67d7105354c  src/kplane.py
cd6627b92d5e124e7d361f4390d2a7dd2d5513d3018afe8eceeff4dce0ad29d3  src/lemmas_sympy.py
6b7e105f848d4346ff6b6fece51384e38fdd67298c6c736fc7899f900f38e190  src/nrc.py
139c20807a0908e31eb4a57f12d5eb68efd9c5f98f374b45398df8b3a63d6a6b  src/padic_profile.py
ff9d1b3b45d753375544a06ba86abfbb1bd2c2d0464636196def4da16ea24991  src/random_census.py
96a8881eebdb49ec2f3835a32b3cf69e44a35578ba8cdced9ca25e2c624c95ba  src/random_spheres.py
b48969dd38d30fb94e7a122380f5275f467fb4c1cdf1f55b554d8bf86ae01b2c  src/shift_test.py
75b5e9beac7c4b8e5937ca1b2b1430a849beaf8f7945accdb973d5d6da9ccac3  src/sphere_load.py
05eb23a454b5e1214a7637a6b472f68051aaed7aaa0be7c06e0bc4aacdb40b43  src/translate4.py
94e65195288f261c7164053016d11f6cfde1e184308c648abd639bd046d9513c  data/family133_default.txt
1efd5c6e2faeb86b13ed29a6103c0bdb99ec28ecb937e871079a3e83ca92a7b5  data/greedy_delete.txt
4d4bb48c8dac40656f690e1ef8084f6ed1d783ba296c02e58fbae2978daa922d  data/greedy_delete_gamma.txt
0544d233e63f20fcfc4ab23952ab199735bd36db9a12fe8e101213f246033d7a  data/greedy_delete_random_large.txt
77b9faf97291e2c97db1effc437de9e7a7c413d60b42b767bafe5a0c67c98f3a  data/kplane.txt
d50ef20b1457123d378aaf71ab9d6a1325d5a06df8c73acf2ad48fa78ee63401  data/random_census_g15.txt
96fb4dd14211b891cf8a7c83e1ad25ec6e57dcd5fcc1f790975a214e3646672b  data/random_census_g2.txt
de5b59556a6e5e8528eddd2d0b3f2027c8d700ad2f9c4d7485c829b8778b8223  data/random_spheres.txt
cc89ca88599728c14fcd3076c0d4f432c59329436f0b6ca81400712b411b0e43  data/shift_nrc13.txt
4cc10d3a11df7f33153128b451a57c6163077ea92822d5b8d50af1e98b541ca5  data/shift_rand13.txt
b6913390774daad8b6dab2aee346719e7b655dd49ec3f9fac9094112396c7c1a  data/translate4_p13.txt
```

The compiled binary `src/zero5` is not committed; rebuild it with `cc -O2 -o zero5 zero5.c`.

## 7. Revision response (referee report `REFEREE-REPORT.md`, verdict: major revision)

| # | Referee item | Change in this revision |
|---|---|---|
| 1 | §4.1 "elementary consequence" (`Theta(eps n^4)` repeated residues) is false; repeated in §0 and §4.4 | Withdrawn in all three places.  §4.1 now states the true Ball-based facts for `p >= 5`: every `(p+2)`-subset has a mod-`p` zero, hence `>= C(|S|,5)/C(p+2,5)` such 5-subsets (only `O(1)` for `p ~ n`), and `>= |S| - p - 1` deletions; the counterexample and the curve-specific `~p^3/24` remark (heuristic) are recorded. |
| 2 | §4.4 negative conclusion unsupported; Conjecture 3 disfavoured | §4.4 rewritten: Lemma DEL (Bernoulli deletion, proved, including validity of the deleted set), Proposition P (conditional on H1 and H2(K), implication proved), Lemma K (`0.07172 <= K_* <= 0.07273`, new script `src/kplane.py`, proved tail bound; fit `~0.0721`), Corollary P' (`>= 1.030 n` under H1, H2(K_*)), the equivalence H1 iff `E(n) = o(1/n)`, and Open Problem 4.5.  Conjecture 3 reversed to `Z_sphere = o(n^{11})`.  §3.7 reading of the sphere data corrected.  Ghosal–Goenka arXiv 2609.20447 cited for weighted sampling. |
| 2 | Suk–White remark | Arithmetic checked: `Z <= n^{e+o(1)}` gives `n^{(15-e)/4 - o(1)}`, so `e = 12` gives exponent `3/4` (§4.4); stated as a consistency check, not as their method. |
| 3 | Lemma V false for `k >= 11` | Lemma V restricted to `2 <= k <= 10` with the corrected proof and the referee's counterexample; new Lemma V' (`|T| <= 4 p^{ceil(k/10)} <= 4 N^{1/2}` for all `k >= 2`); §2.5 and §4.2 constants changed from 3 to 4. |
| 4 | Ball needs `p >= 5` | Stated in §4.1 and §0. |
| 5 | Two-prime claim unproved | Withdrawn (§4.2), with the reason. |
| 6 | "Two curves mod the same `p`" is heuristic | Labelled heuristic (§4.2). |
| 7 | Fibre lemma proofs incomplete | §4.3 fibre lemma rewritten with parts (a)–(d): "includes" instead of "is exactly"; the referee's complete proof for linear coordinates (both `p = 1` and `p = 3 mod 4`); the referee's proof that guaranteed profile `(1,1,1)` is impossible. |
| 8 | `Z_sphere` definition; axis-plane double count | `Z_sphere` = degenerate and not coplanar (§4.4); axis bound now `3n C(n^2,5) - 3n^2 C(n,5)`. |
| 9 | Attribution | Lemma A credited to Dong–Xu §3 at the lemma itself; family F called an instance of their mechanism, with the differences from their Theorem 4 listed (§0, §2.2, §2.3). |
| 10 | Vacuous `p = 5` check | §2.3 and §5 table: "8 primes `13 <= p <= 73`; `p = 5` has no 5-subsets". |
| 11 | zero5 sanity output; buffer | Sanity output corrected to `zeros=1 subsets=1` (six points give `subsets=6`), re-run; `zero5.c` now aborts on more than 8192 points (hash updated). |
| 12 | Mixed data citation; missing `n = 58` row | §4.4 cites the two runs separately (322 zeros at `N = 60`, `m = 120`; 665 zeros and 34 deletions at `n = 62`, `m = 124`); `n = 58` random row added to the §3.6 table. |
| 13 | Heuristic labels | `min(p, n^3/p^2)` labelled heuristic (§4.1); the §3.5 "no hidden identity" sentence labelled an interpretation. |
| — | Local path in §6 | Replaced by a generic environment description. |

The Section 2 results, which the referee checked and accepted, are unchanged apart from the
attribution and the Lemma V restriction.  No unconditional bound beyond `n - o(n)` is claimed.
