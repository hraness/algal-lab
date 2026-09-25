# Adversarial review: `Z_plane(n) = (K_* + o(1)) n^11` (h2-proof/memo.md)

**Verdict: accept-with-minor.** The result is correct and in fact stronger than
required (full asymptotic equality, not just `<= (K_*+o(1)) n^11`). Every
load-bearing step was re-derived and independently checked numerically; the
proof strategy — split off collinear 5-subsets, then bound non-collinear
sections by Pick's theorem — is sound and genuinely fixes the divergence the
source memo's sketch glossed over. Two findings are small but real defects in
the *written* derivations (a literally false inequality step in Lemma 5 and a
backwards justification in Lemma 3); neither touches the conclusions.

## Findings

1. **[Minor — genuine gap in a written step, one-line fix]** Lemma 5's chain
   `sum_k C_nc <= sum_k N^5/120 <= (max_k N_{v,k})^4 · n^3/120 <= n^3 (2n^2/s+2)^4/120`
   substitutes the Lemma-3 bound into `max_k N_{v,k}` over **all** k. Lemma 3
   only applies to **non-collinear** sections, and collinear sections can
   exceed the bound: at `n=6`, `v=(1,19,0)` (`s=19 <= 24 = 2n^2/3`), the
   section `k=0` is the vertical line `{(0,0,z)}` with `N=6 > 5.79 = 2n^2/s+2`.
   Verified directly. The fix is trivial — the sum and the max must be
   restricted to *contributing* `k` (those with `C_nc > 0`), where Lemma 3
   applies; the text's preceding sentence ("every contributing k has
   `N <= 2n^2/s+2`") already has the right hypothesis, it just isn't carried
   into the displayed chain. The conclusion `tail <= 27.74 n^11/A` is
   unaffected (in the counterexample `C_nc = 0` for every `k`). Given that
   collinear heavy sections are *the* dangerous case in this whole argument,
   the qualifier should be written in explicitly.

2. **[Minor — backwards justification]** Lemma 3's proof says "Every coset
   point of `H` lies in `P` (convex), so `I + B >= N`". As stated the
   implication runs the wrong way: `H ⊆ P` gives `I+B <= N` (coset points of
   `H` are section points). The needed direction `N <= I+B` holds because the
   `N` section points lie inside their own convex hull. In fact *both*
   inclusions hold, so `I + B = N` exactly — worth saying, since it makes the
   bound's sharpness transparent (a lattice triangle with `I=0` gives
   `N = 2Area(H)/D + 2`, e.g. the corner section `{x+y+z=1}`: `N=3`,
   `Area=D/2`, equality — the `+2` cannot be reduced). Verified numerically:
   `vi·(N-2) <= 2·hull2d` held for **all** ~355k non-collinear sections at
   `n=4,5,6` over the full range `s <= 2n^2/3+2`, worst ratio `0.5`.

3. **[Minor — literally false sentence, harmless]** Line 13 / §4 note: "the
   `s > n` regime feared in the proof sketch does not exist for spanning
   sections". Literally false: non-collinear `N>=5` sections exist for
   `n < s <= 2n^2/3`. At `n=5` there are 1560 of them (e.g. `v=(1,-8,-4)`,
   `s=8 > n`), and at `n=6` the `C_nc` profile is nonzero through `s=10 > n`.
   What is true and intended: Lemma 3 covers all `s` uniformly, so no
   Balogh–White-style `s <= m` hypothesis or case split is needed. Rephrase to
   "the `s > n` regime causes no problem" — the mathematics is already right.

4. **[Nit]** Lemma 0 proof: "`C_nc(N,5) > 0` needs `N >= 5` non-collinear
   points" should read "a non-collinear 5-subset" (i.e. `N >= 5` *and* the
   section not collinear); as written it invites misreading (5 points are
   never individually "non-collinear").

5. **[Nit]** `zplane_planes.py` uses `smax = 2n^2//3 + 2`, slightly past the
   proved cutoff `2n^2/3`. Harmless defensive margin — and self-validating: a
   missed non-collinear `N>=5` section would break the identity check, which
   passes at every tested `n`.

6. **[Nit]** §8's rate remark needs `O_A(n^10)` polynomial in `A`, which is
   true (`diam F = O(||v||)`, `O(A^3)` normals, BV constants `O_v(1)`) but
   only sketched. Fine as a remark; not load-bearing.

## Check-by-check disposition of the items I was asked to hunt

1. **Bookkeeping identity — correct and exact.** Non-collinear coplanar
   5-set `T`: unique plane through any 3 non-collinear points of `T`; that
   plane has equation `v.x = k` with primitive `v` unique up to sign (integer
   cross product, reduced); counted once in `C_nc(N_{v,k},5)`. Collinear
   `T`: unique supporting line, counted once in `Z_coll`, zero contribution
   to every `C_nc`. A 5-set with exactly 4 collinear points is non-collinear
   (line + off-line point determine a unique plane) — counted once. A 5-set
   in two distinct planes lies on their intersection line — collinear —
   handled by `Z_coll` only. `C_nc = C(N,5) - sum_{ell⊂Π} C(L_ell,5)` is
   exact because a collinear subset has a unique supporting line. The
   identity `Z_plane = Z_coll + Σ_{v,k} C_nc` was verified **independently of
   the memo's code** at `n=3,4,5,6`: brute force (`zplane.c` recompiled)
   gives `Z_plane = 2274, 109680, 1830235, 15699720` and `Z_coll = 0, 0, 109,
   984`; the plane decomposition gives `Z_nc + Z_coll = ` the same totals.
   `n=7` brute force: `Z_plane = 98876337`, `Z_coll = 4833` — matches memo.
   The divergence warning is also correct and necessary: `ΣC(N,5)` diverges
   (any `v=(a,b,0)` section carries a vertical line, `N≥5` at arbitrary `s`);
   at `n=5`, `S1` truncated at `smax=18` gives `1874190 > Z_nc = 1830126`.

2. **Pick bound — correct, including edge cases.** Derivation re-done:
   `H = conv(section pts) ⊆ P` (convex); Pick on the coset lattice
   (`covol = ||v||`) gives `Area(H)/||v|| = I + B/2 - 1 >= (I+B)/2 - 1 >=
   N/2 - 1`, hence `N <= 2Area(P)/||v|| + 2 <= 2n^2/s + 2`. Edge cases:
   `v=e_i` gives `2n^2+2 >= n^2` ✓; corner triangles attain equality (the
   `+2` is needed and `2` is the sharp constant). Exhaustive check
   (`n=4,5,6`, all primitive `v` with `s <= 2n^2/3+2`, all `k`): **zero
   violations** of the exact Pick inequality `vi*(N-2) <= 2*hull2d`, and
   zero violations of the coarse `N <= 2n^2/s+2`. `sup phi_v <= 1/s`
   re-derived correctly (convolution with `v_i U_i` where `|v_i|=s`).

3. **Main-term argument — sound.** `N = n^2 phi_v(k/n) + O_v(n)` via the
   fundamental-parallelogram tiling bound `|N - Area/D| <= (perim·diamF +
   πdiam²F)/D`, with `diam F <= λ_1+λ_2 <= 1+(2/√3)||v||` (Hermite constant
   `2/√3` is sharp — hexagonal lattice attains it) and `perim <= 6√2 n`.
   Uniformity in `v` is *not* needed: `A` is fixed when the main term is
   used, so `O_v` constants sum to `O_A(n^10)` over `<= 4A^3+O(A^2)`
   normals; the `s > A` regime is handled by the uniform-in-`n` tail, not by
   equidistribution. The `C(N,5)` expansion coefficients and the
   lower-order bound `Σ_k N^4 <= n^9` (via `N <= n^2`, `Σ_k N = n^3`)
   check out. `phi_v` piecewise-quadratic BV gives `Σ_k phi(k/n)^5 =
   n∫phi^5 + O_v(1)` — I verified the convention subtlety directly:
   `v=(1,1,0)` gives `N = n(2n-1-k)` vs `n^2phi = n(2n-k)` on the upper
   half, i.e. `E = -n`, consistent with `O(n)` and the half-open
   convention. `v=e_i` is exact (`E=0`).

4. **Tail bound and quantifier swap — valid.** `Σ_k C_nc <= (max over
   contributing k N)^4·n^3/120 <= (2n^2/s+2)^4 n^3/120 <= (4n^2/s)^4 n^3/120`
   (using `s <= 2n^2/3 < n^2` so `2 <= 2n^2/s`) `= 256n^11/(120s^4)`; times
   `<= 12s^2+1 <= 13s^2` normals per `s`; `Σ_{s>A} s^{-2} <= 1/A`; total
   `(3328/120)n^11/A = 27.73…n^11/A <= 27.74 n^11/A`. All arithmetic
   confirmed. The limit argument is exactly as the prompt anticipated and is
   **valid**: for each *fixed* `A`, `limsup_n Z/n^11 <= K_A + 27.74/A`;
   taking `inf_A` gives `limsup <= K_*` (no interchange of limits — each `A`
   yields a theorem). Similarly `liminf >= K_A ∀A` gives `>= K_*`. So the
   full asymptotic `Z_plane/n^11 -> K_*` is established, and `o(1)` in
   `Z <= (K_*+o(1))n^11` is justified: given `eps`, fix `A` with
   `K_* - K_A + 27.74/A < eps/2`, then `n` large kills `O_A(n^{-1})`.

5. **`N >= 5` forces `s <= 2n^2/3` — correct** (for non-collinear sections,
   which is exactly where `C_nc > 0`): `5 <= 2n^2/s + 2 iff s <= 2n^2/3`.
   Empirically sharp and conservative: at `n=6` the `C_nc` support actually
   ends at `s=10` (bound allows `24`); no `N>=5` non-collinear section exists
   beyond `2n^2/3` in any case checked. (Collinear `N>=5` sections do exist
   far beyond — that's the divergence the split exists to avoid.)

6. **`Z_coll = Theta(n^7)` — correct.** Re-derived: `L <= (n-1)/s_w + 1 <=
   2n/s_w` on the `L>=5` support; `#w-lines = #first points <= |w|_1 n^2 <=
   3 s_w n^2` (unique first point per oriented primitive direction); total
   `<= (13·96/120)(π^2/6) n^7 ≈ 17.1 n^7 <= 18 n^7`, and `>= 3n^2 C(n,5) ~
   n^7/40`. Hand/line enumeration independently reproduced `Z_coll = 109`
   at `n=5` (75 axis + 30 face-diag + 4 body) and `4833` at `n=7` (`3·49·21 +
   6·245 + 4·69`), both matching memo and brute force.

7. **Result strength — fully established.** Both directions are proved:
   `liminf >= K_*` (via `C_nc` sums on `s <= A` minus the `O_A(n^7)`
   collinear overlap `theta_A <= #v·Z_coll`) and `limsup <= K_*`. No term
   was dropped: `Z_nc >= Σ_{s<=A}Σ_k C_nc`, `theta_A` correctly accounts for
   the `C` vs `C_nc` gap inside `s <= A`, and the `s > A` part is
   nonnegative. The claim `Z_plane = (K_* + o(1)) n^11` is the theorem;
   `<= ` alone would suffice for H2 but the equality holds.

## Independent checks run

- Recompiled `zplane.c` (`gcc -O3`) and ran `n=3..7` — all values match the
  memo (`Z_plane = 2274, 109680, 1830235, 15699720, 98876337`; `Z_coll = 0,
  0, 109, 984, 4833`). Determinant/cross-product tests in the C code are
  correct (rank ≤ 2 iff all four 3×3 minors vanish; collinear iff all pairs
  of differences have zero cross product).
- Ran their `zplane_planes.py` at `n=3..6` — identity `Z_nc + Z_coll =
  Z_plane` holds exactly at every `n`.
- Wrote my own `check_lemma3.py` (fresh collinearity + planar-hull code):
  all ~355k non-collinear sections at `n=4,5,6` satisfy the *exact* Pick
  inequality `vi(N-2) <= 2·hull2d` and the coarse `N <= 2n^2/s+2`; the
  largest `s` carrying any non-collinear section is `9, 16, 25` (with `N>=5`:
  within `2n^2/3` as required).
- Wrote my own `zcoll_check.py` line enumerator — `Z_coll` and its
  direction-type breakdown match the memo's hand count at `n=5,7`.
- Reproduced the per-`s` support cutoff at `n=6` (nothing beyond `s=10`;
  memo's per-`s` values sum exactly to `Z_nc = 15698736`; my own
  non-subtracting count differs by exactly the 23928 collinear 5-subsets
  inside non-collinear sections — consistent).
- Recomputed `K_1` exactly by hand (axis + face-diagonal trapezoids +
  Irwin–Hall order-3 for body diagonals): `0.0467623` — matches Lemma K's
  `0.04676`.
- Constructed the Lemma-5 counterexample (`v=(1,19,0)`, `n=6`,
  `max_k N = 6 > 5.79`) and the `s>n` counterexamples for finding 3.

## Bottom line

Mathematics: correct, complete, and stronger than stated goal. Required
revisions are expository: fix the `max_k` qualifier in Lemma 5 (finding 1),
fix the backwards implication in Lemma 3 (finding 2), and repair the
"`s > n` regime does not exist" phrasing (finding 3). After those, this is
publishable-quality for its purpose: it discharges Open Problem 4.5 part 2
(H2) in full. H1 (`Z_sphere = o(n^11)`) remains open — the memo's §8 says so
honestly.
