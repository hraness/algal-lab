# Rank selection: dependence, context reduction, and ordered sharpness

The [two-threshold certificate](two-threshold-certificate.md) reduces a
quartet's inequalities in arbitrarily large populations to six-clock tests.
This note strengthens that result in two directions:

- The reduction is a statement about ranks themselves. It works for dependent
  focal scores and any reward supported on one selected cardinality.
- Two background clocks are necessary even for independent, strictly
  stochastically ordered focal distributions with positive densities on their
  common support. A general concatenation construction hides a
  local violation from every zero- and one-background test.

The rank counting and polynomial algebra used below are elementary. These
proofs and exact examples establish the mathematical claims; priority of the
specific characterization and sharpness result remains under comparison in
the [novelty ledger](novelty-ledger.md).

The [minimum-context theorem](minimal-rank-contexts.md) further extends the
pathwise statement to every set reward and identifies its exact required
background size. It also separates preservation of each outcome from the
minimum size of an expected-sign counterexample.

## A pathwise reduction for cardinality-supported rewards

Let `x_1,…,x_d` be labeled focal scores, and let `h(A)` be a real reward on
subsets of their labels. Suppose `h(A)=0` unless `|A|=p`, where `1≤p<d`.
Append `s` background scores and retain the `k` largest scores overall.
Assume no focal score equals a background score. Ties within either group
are allowed; use one fixed focal-label tie order throughout.

Write the backgrounds as `z_1≥⋯≥z_s`, with `z_0=+∞` and
`z_(s+1)=−∞`. Rank the focal scores as `x_(1)≥⋯≥x_(d)` and let `T_p`
be the labels of the first `p`. Put `m=k−p`.

**Theorem 1 (pathwise reduction).** If `m` is outside `0,…,s`, the reward
is zero. Otherwise put `L=z_(m+1)` and `U=z_m`. The original reward is

\[
 h(T_p)\,\mathbf1\{x_{(p)}>L,\;x_{(p+1)}<U\}. \tag{1}
\]

It is exactly the reward from retaining the largest `p+1` scores among the
same `d` focal scores and just two background scores, `L,U`.

**Proof.** Selecting exactly `p` focal labels requires selecting exactly
`m` background labels. The selected focal labels must be `T_p`. The p-th
focal score lies above the first excluded background precisely when
`x_(p)>z_(m+1)`; the next focal score lies below the last included background
precisely when `x_(p+1)<z_m`. These two inequalities characterize that
selection, with the infinite endpoints covering `m=0,s`. For two
backgrounds `L,U` and horizon `p+1`, the same criterion applies with `m=1`.
On every other focal cardinality both rewards vanish. ∎

No independence or probability argument entered this proof. In particular,
it preserves the actual selected label set whenever a reward can be nonzero.

**Corollary 1 (universal tests).** Give the focal vector any joint law with
atomless marginals, preserving the same focal tie order. For any background
vector jointly independent of that vector, the following are equivalent:

1. The expected reward is nonnegative for every finite background population
   and every fixed horizon.
2. It is nonnegative for every two deterministic background scores `L≤U`
   at the single horizon `p+1`.

Requiring all background clocks to be mutually independent and absolutely
continuous gives the same universal class.

**Proof.** Atomless marginals and independence of the two vectors rule out
focal/background ties. Condition on the background and apply (1). Infinite
endpoint cases follow by bounded convergence: a reward on a finite label
set is bounded. The same argument shows continuity of the expected reduced
reward in the finite thresholds; changing them can affect the event only
when a focal score crosses a threshold. Every strictly negative deterministic
witness therefore persists for two independent sufficiently narrow uniform
backgrounds. When the centers coincide, order the two sampled backgrounds
before applying (1). ∎

Independence **between** the two vectors matters for averaging tests against
the unconditional focal law. Dependence **within** the focal vector or
within the background vector is unrestricted.

## Why quartet differences have this reduction

For four focal labels let

\[
 h(A)=\sum_{\{i,j\}\subseteq A}c_{ij},\qquad
 \sum_{j\ne i}c_{ij}=0\quad\text{for every }i. \tag{2}
\]

The total coefficient sum is zero. A three-label subset has that total
minus the missing label's row sum, hence also zero. Cardinalities zero and
one contain no pair. Thus `h` vanishes on every cardinality except two, so
Theorem 1 applies with `p=2`. Both signed quartet gaps have these row sums:

\[
 \Delta_1=q_{ab}+q_{cd}-q_{ac}-q_{bd},\qquad
 \Delta_2=q_{ac}+q_{bd}-q_{ad}-q_{bc}.
\]

Consequently the six-clock/top-three completeness result holds even for
dependent focal scores. The independent-quartet assumption in the
[CDF certificate](two-threshold-certificate.md) remains essential for its
formula `B(L,U)=D(U)+K(U)−K(L)` and its histogram algorithm.

For example, with probability one half let `a,b` be independent uniforms on
`[1/2,1]` and `c,d` independent uniforms on `[0,1/2]`; with probability
one half reverse these roles. This joint law has a density and every
marginal is uniform on `[0,1]`. Its no-background top-two gap is `Δ₁=1`.
Substituting only those identical marginals into the independent-clock
formula gives zero. Context reduction survives this dependence, while the
marginal-product calculation does not.

## Concatenation identities for independent clocks

Use `D_ℓ,C_ℓ,K_ℓ` from equation (1) of the certificate note and write
`A_ℓ=D_ℓ+K_ℓ`. Concatenate compactly supported distribution blocks in time.
Every focal marginal assigns the same mass `s` to a particular block, with
the same preceding mass `a`; within it let its normalized CDF be `G_i`.
Then `F_i=a+sG_i` and `f_i=sg_i`, in the block's local time coordinate.
Each focal clock samples its marginal independently; the block choices are
not shared across focal clocks.

**Lemma 2 (block identity).** Suppressing the gap index,

\[
\begin{aligned}
 D_{\rm global}&=s^2D_{\rm local},\\
 C_{\rm global}&=-as^2D'_{\rm local}+s^3C_{\rm local},\\
 K_{\rm global}&=K_{\rm before}-as^2D_{\rm local}+s^3K_{\rm local},\\
 A_{\rm global}&=K_{\rm before}+(1-a)s^2D_{\rm local}+s^3K_{\rm local}.
\end{aligned} \tag{3}
\]

Both local endpoint values of `D` are zero. A complete block therefore
adds exactly `s³K_local(∞)` to the cumulative `K`.

**Proof.** Every CDF difference gains a factor `s`. Each cross product
becomes `f_iF_j−f_jF_i=as(g_i−g_j)+s²(g_iG_j−g_jG_i)`.
Substitution into `C` gives the second identity. Integrating it from the
block's left endpoint gives the third; adding `D` gives the fourth.
A time rescaling within a block additionally multiplies densities and
derivatives by its derivative, leaving the integrated identities intact. ∎

## A general way to hide a local failure

Let the positive block `P` have these masses on two unit bins, with each
row totaling three:

```text
a: 0 3
b: 1 2
c: 2 1
d: 3 0
```

It is CDF ordered, `D≥0`, and both `K` functions increase from zero to
`p=(1/3,1/9)`. On the first bin `K=0`; on the second, in coordinate
`y∈[0,1]`, `K_ℓ=p_ℓ(2y−y²)`. These observations verify the stated bounds
without a grid search.

**Theorem 3 (buffer construction).** Let `N` be any independent quartet of
proper, absolutely continuous compactly supported laws with
`F_a≤F_b≤F_c≤F_d` and a negative no-background gap `n_ℓ=K_N,ℓ(∞)`.
There is a CDF-ordered concatenation `P,N,P` that passes both quartet
comparisons for every zero- or one-background law independent of the focal
quartet, at every horizon, yet fails the chosen gap with two deterministic
backgrounds.

More precisely, put

\[
 m_\ell=\min_t K_{N,\ell}(t),\quad
 M_\ell=\max_t K_{N,\ell}(t),\quad
 R=\max_{\ell=1,2}\left\{\frac{-m_\ell}{p_\ell},
                       \frac{M_\ell-n_\ell}{p_\ell}\right\}.
\]

Choose any `0<β≤1/(1+2∛R)` and put `α=γ=(1−β)/2`. Give the three
blocks masses `α,β,γ`. Here `R>0` because one `n_ℓ<0`. A rational
sufficient choice is `β=1/(2J+1)` for any integer `J≥max(1,R)`.

**Proof.** Concatenation preserves the CDF order, so every local `D≥0`.
The specified masses give, for each gap,

\[
 \alpha^3p_\ell\ge-\beta^3m_\ell,\qquad
 \gamma^3p_\ell\ge\beta^3(M_\ell-n_\ell). \tag{4}
\]

The final `K` is `T=(α³+γ³)p+β³n`. By (3), on the middle block
`A≥α³p+β³m≥0` and `K≤α³p+β³M≤T`. The cumulative `K` just before
the final block is `α³p+β³n≥0`, since `n≥m`. On the first block
`A≥0` and `K≤α³p≤T`; the last inequality follows from (4) and `M≥0`.
On the last block `A≥0` and `K≤T`, because `0≤K_P≤p` and `D_P≥0`.
Thus `A≥0`, `K≤T`, and `T≥0` everywhere, exactly the complete
zero/one-background conditions.

Put `L,U` at the start and end of the middle block. Its endpoint `D`
values vanish, and (3) gives `B_ℓ(L,U)=β³n_ℓ<0`. Narrow independent
continuous backgrounds also preserve this strict failure. ∎

The conclusion is stronger than an isolated counterexample. Any such
CDF-ordered no-background violation can be made invisible to every test
with at most one background clock. Checking those tests cannot replace
the two-threshold condition, even with stochastic ordering.

The later [positive-integral theorem](stochastic-intact-groups.md) proves
that a CDF-ordered independent quartet never has a negative first gap.
Consequently every eligible ordered failure used here is a second-gap
failure; the construction and its two-gap checks remain valid.

There is also a fixed choice that works for **every** qualifying `N`:
`β=1/6` and `α=γ=5/12`. To see this, let `Y` be the second-largest
focal value and `h_ℓ(T₂)` its signed pair reward. The no-background signed
density is `C_ℓ`, so

\[
 K_{N,\ell}(t)=\mathbb E[h_\ell(T_2)\mathbf1\{Y\le t\}],\qquad
 n_\ell-K_{N,\ell}(t)=\mathbb E[h_\ell(T_2)\mathbf1\{Y>t\}].
\]

Since `|h_ℓ|≤1`, both `−m_ℓ` and `M_ℓ−n_ℓ` are at most one.
Thus `R≤9`. The fixed masses have `(α/β)³=(5/2)³>9`, which implies
(4). This bound avoids estimating any extrema of the input quartet.

## A seven-bin exact witness

Use the earlier negative block
`N=[[0,1,2],[1,0,2],[2,0,1],[2,1,0]]`, each row totaling three.
Its `K(∞)=(8/27,−1/54)`, with
`0≤K₁≤8/27` and `−2/81≤K₂≤0`. Taking all three block masses equal
to `1/3` satisfies (4), producing these masses on `[0,7]`:

```text
a: 0 3 0 1 2 0 3
b: 1 2 1 0 2 1 2
c: 2 1 2 0 1 2 1
d: 3 0 2 1 0 3 0
```

Every row totals nine. Their endpoint CDF numerators, including zero, are

```text
a: 0 0 3 3 4 6 6 9
b: 0 1 3 4 4 6 7 9
c: 0 2 3 5 5 6 8 9
d: 0 3 3 5 6 6 9 9
```

Hence `F_a≤F_b≤F_c≤F_d` throughout, by linear interpolation inside
each bin. This is weak stochastic order, with equalities at some thresholds.
The complete zero/one-background minima are

| Gap | No background | Minimum single-background top-two gap | Minimum single-background top-three gap |
|---|---:|---:|---:|
| 1 | `26/729` | `0` | `0` |
| 2 | `11/1458` | `0` | `0` |

The proof above gives these minima analytically: the totals are
`(2K_P(∞)+K_N(∞))/27`, `A(0)=0`, and `K(7)=T`. But at the two
background values `L=2,U=5`, top-three selection gives

\[
 B_1(2,5)=8/729,\qquad B_2(2,5)=-1/1458. \tag{5}
\]

The second value is also the global minimum, first attained by the exact
scan at `(2,4)`. The first gap's global minimum is zero. The example remains
negative with fully continuous independent backgrounds:

\[
 L\sim\operatorname{Uniform}[7/4,9/4],\quad
 U\sim\operatorname{Uniform}[19/4,21/4],\qquad
 (\Delta_1,\Delta_2)=(133/11664,-7/11664). \tag{6}
\]

The supports are disjoint and ordered. For exact integration, split them at
2 and 5; on each resulting rectangle the conditional gaps are quadratic
in each threshold. Product Simpson integration is therefore exact, not
a numerical approximation. An additional independent categorical calculation
integrates all six clocks over 14,400 positive-mass assignments to eleven
refined intervals. It checks total probability one and obtains the same gaps
without using `C,D,K`, deterministic-threshold formulas, or quadrature.

## Strict stochastic order and positive densities

The necessity result does not rely on equal CDF values or zero densities.
To the seven-bin rows `H` above, apply `12H_i+V_i`, where
`V_i=[1+i,1,1,1,1,1,4−i]` for `i=0,1,2,3`. The resulting rows,
each totaling 118, are

```text
a:  1 37  1 13 25  1 40
b: 14 25 13  1 25 13 27
c: 27 13 25  1 13 25 14
d: 40  1 25 13  1 37  1
```

Every density is at least `1/118` on every bin. Adjacent unnormalized CDF
differences for `V` are `t` on `(0,1)`, one on `[1,6]`, and `7−t` on
`(6,7)`. Adding twelve times the nonnegative differences for `H`, then
dividing by 118, proves `F_a<F_b<F_c<F_d` at every `t∈(0,7)`.

Exact quadratic minimization gives the complete zero/one-background minima

| Gap | No background | Minimum single-background top-two gap | Minimum single-background top-three gap |
|---|---:|---:|---:|
| 1 | `7671/205379` | `0` | `0` |
| 2 | `1723/205379` | `0` | `0` |

Nevertheless, `B₂(2,5)=−5/410758`, which is the global second-gap minimum.
The first-gap minimum is zero, and `B₁(2,5)=4989/410758`. Independent
categorical rank calculations and slower critical-point searches reproduce
all these values. Continuity again provides independent, absolutely
continuous background witnesses. Thus two-background minimality holds for
strict stochastic order and positive densities on a common compact support.
No optimality of the bin count, masses, or violation magnitude is asserted.

## Evidence and scope

```sh
python3 -m unittest research.test_context_certificate
python3 -m research.spikes.context.verify
python3 -m research.spikes.context.pathwise
python3 -m research.spikes.context.continuous
```

The last two commands are standalone subsets of the verifier and unit tests,
respectively. The pathwise check exhaustively covers up to five focal scores,
up to three backgrounds and seven total distinct scores: 141,626 comparisons.
There are also 2,592 comparisons with background ties, 17,442 permitting
focal ties, and 20 quartet reward-support checks. The main verifier
independently recomputes global and single-background
minima from categorical ranks. These finite checks support the implementation;
the arbitrary-population claims rely on the proofs.

The lead investigator found the ordered example by composing the positive
and negative blocks after a bounded random search had produced no ordered
example. An independent reviewer checked the rank reduction, the block
algebra, the full zero/one-background extrema and the continuous witness.
This continuation used no new external model API experiment. It supplies
no evidence of a low-token or small-model advantage in theorem origination.
