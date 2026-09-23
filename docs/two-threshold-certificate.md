# A complete background test for rank-selection inequalities

The earlier [rank-selection identity](rank-selection-and-triples.md) gave a
sufficient condition for two four-point inequalities. This note gives a
necessary-and-sufficient condition for a **fixed quartet** to satisfy those
inequalities in every background population. Arbitrarily many background
clocks reduce to two threshold values. For continuous histogram clocks, an
exact algorithm checks the condition in linear rational-arithmetic work and
returns a counterexample threshold pair when it fails.

These are proved statements in the model below. The conditioning and
quadratic-minimization techniques are standard. Literature priority of the
specific rank-selection characterization is not established; see the
[source comparison](novelty-ledger.md).

The [context-reduction sequel](rank-context-compression.md) proves that the
rank reduction itself permits dependence within the quartet, and that two
backgrounds remain necessary even under strict stochastic ordering and positive
densities on a common support. The CDF formula
and histogram algorithm here retain their independent-quartet assumption.

## Model and the two gaps

Fix four independent, proper, absolutely continuous real random variables
`X_a,X_b,X_c,X_d`, with CDFs `F_i` and densities `f_i`. Their labels need not
be ordered by any stochastic or hazard order. Append any finite background
vector `Z`, **jointly independent of the quartet**. The background variables
may depend on one another and may tie. Retain the `k` largest values of the
combined population. Ties among backgrounds cannot affect quartet membership:
almost surely no quartet value equals a background value.

Let `q_ij` be the chance that both labeled quartet members are retained. Set

\[
 \Delta_1=q_{ab}+q_{cd}-q_{ac}-q_{bd},\qquad
 \Delta_2=q_{ac}+q_{bd}-q_{ad}-q_{bc}.
\]

Define functions of the threshold `t`:

\[
\begin{aligned}
 D_1&=(F_d-F_a)(F_c-F_b),\\
 C_1&=(f_aF_d-f_dF_a)(F_c-F_b)
       +(F_d-F_a)(f_bF_c-f_cF_b),\\
 D_2&=(F_b-F_a)(F_d-F_c),\\
 C_2&=(f_aF_b-f_bF_a)(F_d-F_c)
       +(F_b-F_a)(f_cF_d-f_dF_c),\\
 K_\ell(t)&=\int_{-\infty}^t C_\ell(s)\,ds.
\end{aligned} \tag{1}
\]

The `C` functions are absolutely integrable because their CDF factors are
bounded and the densities integrate to one. Thus `K` is continuous with
finite endpoint limits. Both `D` functions are continuous, absolutely
continuous on finite intervals, and tend to zero at both infinite endpoints.

## Two thresholds determine the conditional gap

For a fixed background realization, order its `s` values as
`z_1≥⋯≥z_s`, and put `z_0=+∞`, `z_(s+1)=−∞`. For an interior horizon
`2≤k≤s+2`, set `m=k−2`, `L=z_(m+1)`, and `U=z_m`.

**Theorem 1 (conditional identity).** For either gap,

\[
 \Delta_\ell\mid Z=z
   = B_\ell(L,U)
   := D_\ell(U)+K_\ell(U)-K_\ell(L). \tag{2}
\]

At `k=0,1,s+3,s+4`, the gaps are zero. If `s=0,k=2`, (2) uses the full
interval `(-∞,+∞)`.

**Proof.** Condition a selected pair on its smaller clock value `t`. Its
density is `f_i(1−F_j)+f_j(1−F_i)`. Let `b(t)` count backgrounds exceeding
`t`. The pair is retained when at most `m−b(t)` of the remaining two
quartet values exceed `t`. Expanding the four signed pair terms gives the
signed density

\[
 C_\ell(t)\,\mathbf1\{b(t)=m\}
 -D_\ell'(t)\,\mathbf1\{b(t)\le m-1\}. \tag{3}
\]

One way to check the expansion is to collect the coefficients of allowing
zero, at most one, and at most two other-quartet exceedances: in the
cumulative-background expansion they are `C`, `−C−D′`, and `0`.
Away from the finitely many background values, `b(t)=m` on `(L,U)` and
`b(t)≤m−1` on `(U,+∞)`. Integrating (3) gives
`∫_L^U C−∫_U^∞ D′=K(U)−K(L)+D(U)`.
If `L=U`, the first interval is empty and the same formula gives `D(U)`.
Background ties therefore require no assumption of distinct order statistics.
The boundary horizons either select fewer than two vertices or omit at most
one; the signed pair sums then cancel. ∎

Joint independence from the quartet is essential. It ensures conditioning on
the background does not change the quartet law. No independence *within* the
background was used.

## A necessary-and-sufficient universal criterion

**Theorem 2 (universal characterization).** For a fixed quartet and either
gap, the following are equivalent:

1. The gap is nonnegative for every finite background vector independent of
   the quartet and every fixed survivor count.
2. It is nonnegative for top-three selection from the quartet plus any two
   deterministic background values.
3. For every pair of finite thresholds `L≤U`,

   \[
    D_\ell(U)+K_\ell(U)\ge K_\ell(L). \tag{4}
   \]

4. For every real `U`,

   \[
    D_\ell(U)+K_\ell(U)\ge\sup_{L\le U}K_\ell(L). \tag{5}
   \]

Requiring only independent, absolutely continuous background clocks gives
the same universal class.

**Proof.** (1) implies (2), and (2) is (4) by Theorem 1 with `s=2,k=3`.
Statements (4) and (5) are equivalent by taking a supremum. Continuity and
the endpoint limits extend (4) to infinite endpoints. Conditional
expectation in (2) then proves (1), including internally dependent
backgrounds. Conversely, a strict negative `B(L,U)` persists in a
neighborhood of `(L,U)`. Replacing each fixed background value by an
independent sufficiently narrow uniform clock stays in that neighborhood,
including after ordering the two values when `L=U`. The expected gap remains
negative. Thus restricting backgrounds to independent continuous clocks
does not hide any failure. ∎

Both inequalities hold universally exactly when (4) holds for `ℓ=1,2`.
Every violation therefore has a six-clock, top-three witness. Two backgrounds
are necessary in general, as the exact example below demonstrates. Individual
quartets may reveal a violation with fewer backgrounds.

For comparison, the complete zero/one-background tests are only

\[
 K_\ell(+\infty)\ge0,\quad
 K_\ell(+\infty)-K_\ell(z)\ge0,\quad
 D_\ell(z)+K_\ell(z)\ge0\quad\text{for every }z. \tag{6}
\]

The familiar pointwise sufficient condition `C_ℓ≥0,D_ℓ≥0` implies (4).
Condition (4) necessarily gives `D_ℓ≥0` by setting `L=U`; its requirement
on `C_ℓ` is an integrated one.

## Sharpness and the limits of hazard conditions

**Two backgrounds are necessary in general.** Give the quartet independent
histogram laws with these masses on the four unit bins of `[0,4]`. Each row
totals 16:

```text
a:  7  1  3  5
b:  5  4  0  7
c:  2  9  4  1
d:  1  9  2  4
```

The three quantities in (6), minimized over all single-background thresholds,
are exactly

| Gap | No background | Minimum single-background top-two gap | Minimum single-background top-three gap |
|---|---:|---:|---:|
| 1 | `203/4096` | `0` | `0` |
| 2 | `121/8192` | `0` | `0` |

These are exact quadratic extrema, independently checked from direct rank
probabilities, not grid minima. Hence **every** zero- or one-background law
passes both comparisons at every horizon. Yet two fixed clocks at 2 give

\[
 B_1(2,2)=1/64,\qquad B_2(2,2)=-1/256.
\]

The failure persists with fully continuous independent backgrounds: use two
independent `Uniform[7/4,9/4]` clocks. Direct exact integration gives
`Δ₂=−4531/1572864` for top-three selection. For credential-free reproduction
using common unit bins, apply one increasing piecewise-linear time change
that sends `0,1,7/4,2,9/4,3,4` to `0,1,2,3,4,5,6`. A quartet row
`[a,b,c,d]` then becomes `[4a,3b,b,c,3c,4d]`, and each background row is
`[0,0,1,1,0,0]`. Ranks are invariant under this common transformation.
This example has crossing CDFs. The
[seven-bin ordered construction](rank-context-compression.md#a-seven-bin-exact-witness)
strengthens the result to the CDF-ordered subclass, with all zero/single
tests passing but `B₂(2,5)=−1/1458`.

**Neither hazard order is necessary.** A separate quartet has these masses
on the five unit bins of `[0,5]`, each row totaling 40:

```text
a:   8   8  8  8  8
b:  10   9  6  8  7
c:  11  10  5  8  6
d:  13  11  4  8  4
```

Its CDFs are strictly ordered in the support interior. Checking both endpoints
of every bin gives `C₁,C₂≥0`, while `D₁,D₂>0` there. Thus the quartet
satisfies both universal inequalities. At `t=3/2`, its reversed hazards
for `b,c` are `18/29<5/8`, violating the sufficient descending order.
At `t=5/2`, its ordinary hazards for `a,b` are `2/5>1/3`, violating the
ascending ordinary-hazard order. These strict inequalities persist on
neighborhoods, so neither is merely a choice of density at a breakpoint.
This example separates universal validity from both sufficient hazard
conditions while retaining ordinary stochastic order.

## An exact linear scan for histogram clocks

Suppose each clock has a constant density on each of `b` common unit bins
and is zero outside `[0,b]`. Integer masses are normalized separately for
each row. Within a bin, every CDF is affine. The cross-product
`f_i F_j−f_j F_i` is constant, so `C` is affine and `K,D` are quadratic.
Thresholds outside the support are equivalent to its endpoints.

Write `A=K+D`. Minimize `A(U)−K(L)` over `0≤L≤U≤b` by scanning bins
from left to right. At each bin `[j,j+1]`, retain the maximum of `K` over
all preceding bins, together with a maximizing threshold. There are only
four kinds of candidates:

1. `L≤j`: minimize the quadratic `A(U)` in this bin and subtract the
   retained prefix maximum.
2. `L=U` in this bin: minimize the quadratic `D`.
3. `U=j+1`, with `L` in this bin: subtract the bin maximum of `K` from
   `A(j+1)`.
4. Both thresholds in the bin interior: solve the linear equations
   `K′(L)=0` and `A′(U)=0`, and evaluate if `L≤U`.

This list is exhaustive. For thresholds in the same bin, it covers the
three edges and interior stationary points of the compact triangular
domain. If a polynomial is constant, a boundary realizes the same minimum.
Every quadratic extremum is at an endpoint or its rational derivative root.
After updating the prefix maximum, continue to the next bin.

The algorithm uses `O(b)` exact rational-arithmetic operations and `O(b)`
space in the supplied implementation. This is an arithmetic-operation bound,
not a constant-cost assertion for arbitrarily large integers. It returns the
global minimum and a rational witness `(L,U)` for each gap, including
negative minima occurring strictly between bin endpoints. A time grid or
Monte Carlo estimate is unnecessary.

The [implementation](../research/context_certificate.py) admits exactly four
rows, `1..4096` common bins, and integer counts in `0..1,000,000`, with a
positive total in each row. Its scope is a fixed quartet; certifying every
quartet in an `n`-clock population would require an additional enumeration
or a separately proved shortcut.

## Reproduction

```sh
python3 -m research.context_certificate
python3 -m unittest research.test_context_certificate
python3 -m research.spikes.context.verify
```

The checks use an independent reference based on interval assignments and
exact combinatorial cutoff probabilities, and a slower global critical-point
enumeration to check the linear scan. They exercise rational thresholds,
background ties, boundary horizons, zero densities, and misordered labels.
The verifier covers 319 conditional cases and eleven quartet profiles against
both slower universal and one-background minimizers. Unit tests additionally
compare the fully continuous six-clock witness against an independent
categorical integration and integrate the ordered continuous witness exactly
from direct rank probabilities. The verifier also checks the pathwise
reduction independently of probability formulas. Two named fixtures have negative minima at rational
thresholds strictly inside a bin, including an off-diagonal stationary pair.
The existing CDF-order counterexample has a universal second-gap minimum
`−1/54`, witnessed by `L=0,U=2`. Negative witnesses can be evaluated directly
with `threshold_gaps`.

The same verifier runs the [general minimum-context check](minimal-rank-contexts.md),
including the exact finite-family minimum search and harmonic counterexample.

The public checks require no credentials or model inference. They validate
finite implementations of the formulas. The universal conclusion follows
from the proofs, and literature priority remains a separate question.

The lead investigator proposed the conditional reduction and linear scan;
a Sol worker implemented independent rank calculations, and a Luna worker
found the small sharpness and hazard-order examples. Another Luna worker
checked the conditional reduction, ties, endpoint limits and minimizer cases.
An initial floating-grid candidate was discarded after exact integration;
an auxiliary direct-integral checker was corrected to count exceedances by
the complementary quartet labels. The public independent reference instead
uses categorical ranks. This provenance does not establish a low-token model
discovery advantage; the earlier small-model pilot remains negative.
