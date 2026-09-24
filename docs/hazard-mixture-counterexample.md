# A single-crossing counterexample for hazard ordering of finite mixtures

An equal-weight mixture of exponential rates `(1,3,5)` and one of rates
`(1,4,4)` have crossing hazard rates, although the first rate vector majorizes
the second. The first survival function is larger at every positive time.
Padding both vectors with any number of common rate-one components preserves
the crossing. Thus the unchanged higher-dimensional extension asked about in
Shojaee, Asadi and Finkelstein (2022), Remark 6.3, is false.

The same example contradicts Theorem 3.8 **as stated in the accepted author
manuscript** of Sahoo, Kayal and Finkelstein (2026). The exact correspondence
is given below. The publisher's final theorem text has not been retrieved;
this note identifies the inspected version precisely. Independent calculation
and source review support the mathematical counterexample. Literature-first
priority remains unresolved; see the [coverage record](#source-coverage-and-priority).

## The three-component calculation

For a positive rate vector `v`, write

\[
 S_v(t)=\frac1n\sum_i e^{-v_i t},\qquad
 h_v(t)=\frac{\sum_i v_i e^{-v_i t}}{\sum_i e^{-v_i t}}.
\]

Set `λ=(1,3,5)` and `γ=(1,4,4)`. In the increasing-prefix convention,
`λ` majorizes `γ`: the partial sums are `(1,4,9)` and `(1,5,9)`.
The exact hazard values are:

| Time | `h_λ` | `h_γ` | `h_λ−h_γ` |
|---|---:|---:|---:|
| `log 2` | `11/7` | `8/5` | `−1/35` |
| `log 4` | `103/91` | `12/11` | `41/1001` |

These are rational evaluations with `q=exp(−t)` equal to `1/2` and `1/4`.
They use neither a floating-point sign nor a plotted crossing. In particular,
neither hazard-rate order holds. Usual stochastic dominance does hold, since

\[
 S_\lambda(t)-S_\gamma(t)
 =\tfrac13(q^3+q^5-2q^4)=\tfrac13q^3(1-q)^2>0
 \quad(t>0).
\]

## Every dimension above two, with exactly one crossing

Let `m=n−2≥1`, and use uniform individual weights with

\[
 \lambda=(\underbrace{1,\ldots,1}_{m},3,5),\qquad
 \gamma=(\underbrace{1,\ldots,1}_{m},4,4).
\]

Their increasing prefixes agree through index `m`. The next prefixes are
`m+3<m+4`, and both totals are `m+8`, so the same majorization holds.
Cancellation of the common rate-one term gives

\[
 h_\lambda-1=\frac{2q^2+4q^4}{m+q^2+q^4},\qquad
 h_\gamma-1=\frac{6q^3}{m+2q^3}.
\]

Consequently

\[
 h_\lambda-h_\gamma=
 \frac{2q^2(1-q)\{m(1-2q)-q^3(1+q)\}}
 {(m+q^2+q^4)(m+2q^3)}. \tag{1}
\]

All factors outside the braces are positive for `0<q<1`. The bracket
`B_m(q)=m(1−2q)−q³−q⁴` has derivative
`−2m−3q²−4q³<0`. Also

\[
 B_m(1/4)=m/2-5/256>0,\qquad B_m(1/2)=-3/16<0.
\]

There is exactly one root `q_*` in `(1/4,1/2)`, hence exactly one positive
crossing time in `(log 2,log 4)`. The hazard difference is negative before
that time and positive afterwards. Meanwhile
`S_λ−S_γ=q³(1−q)²/n>0` for all positive times. The unbounded statement follows
from this algebra and monotonicity, rather than a finite enumeration of `n`.

For comparison, `m=0` is the original two-component pair `(3,5)` versus
`(4,4)`. Its bracket is strictly negative, so it has no hazard crossing.

## The common slow component explains the failure

This phenomenon is not special to the integer rates. Choose
`a>0`, `d>0`, `b−d>a`, and `0<w<1`. Compare survival functions

\[
 S_X(t)=w e^{-at}+(1-w)e^{-bt}\cosh(dt),\qquad
 S_Y(t)=w e^{-at}+(1-w)e^{-bt}.
\]

They represent a common slow component and, respectively, a symmetric
two-rate mixture or a single rate `b`. Put `c=b−a>d`. The survival ratio is

\[
 R(t)=\frac{S_X(t)}{S_Y(t)}
 =1+\frac{(1-w)(\cosh(dt)-1)}{we^{ct}+1-w}>1.
\]

For positive times,

\[
 \frac{d}{dt}\log(R(t)-1)
 =d\coth(dt/2)-\frac{cw e^{ct}}{we^{ct}+1-w}.
\]

The first term strictly decreases from infinity to `d`; the subtracted term
strictly increases to `c>d`. Their difference has exactly one zero. Therefore
`R` has exactly one maximum, and `h_X−h_Y=−(log R)'` changes from negative to
positive exactly once. Usual stochastic dominance survives throughout.
With `w=0`, the hazards instead satisfy `h_X=b−d tanh(dt)≤b=h_Y`.
Every positive common slow weight destroys this hazard ordering.

This general mechanism is a mathematical explanation, with no separate
priority claim. To satisfy the source's antiordering of the three component
weights and rates, take `w≥1/3`; the all-dimension construction uses effective
slow weight `w=m/(m+2)` while keeping each labeled component weight uniform.

## Exact connection to the published statements

### The 2022 open extension

Shojaee, Asadi and Finkelstein's [publisher text](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D81AA9C7EA4636774C4F553F1C9D4827/S0269964821000243a.pdf/stochastic-properties-of-generalized-finite-mixtures.pdf),
Theorem 6.3, printed page 1073, proves a two-component hazard comparison.
Remark 6.3 on page 1075 leaves its higher-dimensional extension open.
Here is the specialization of its non-strict hypotheses:

| Hypothesis | Counterexample specialization |
|---|---|
| Baseline hazard increasing and concave in its parameter | `h(t;v)=v`, a linear function; the paper also uses this baseline in Example 6.4 |
| Baseline survival decreasing in the parameter | `exp(−vt)` |
| Ordered nonnegative powers and nonincreasing products with weights | All `α_i=1`, all `p_i=1/n` |
| Antiordered weights and rate parameters | `(p_i−p_j)(v_i−v_j)=0` for either rate vector |
| Rate majorization | Prefix calculation above |

The generalized mixture then reduces to `S_v`. Formula (1) rules out the
proposed conclusion `h_λ≤h_γ` in every dimension `n≥3`. This answers the
unchanged extension negatively; it does not contradict the stated
two-component theorem or exclude extensions with extra hypotheses.

### The 2026 accepted-manuscript theorem

Sahoo, Kayal and Finkelstein's [accepted manuscript](https://strathprints.strath.ac.uk/96227/1/Sahoo-etal-ASMBI-2026-Stochastic-ordering-results-between-two-finite-alpha_mixture-models.pdf)
defines its model in (1.3), the antiordered matrix class `V_n` on printed
page 6, and Theorem 3.8 on page 20. Set its baseline survival to `exp(−t)`,
`α=θ=1`, `p=q=(1/3,1/3,1/3)`, its shape vectors to our `λ,γ`, and

\[
 T=\begin{pmatrix}1&0&0\\0&1/2&1/2\\0&1/2&1/2\end{pmatrix}
   =\tfrac12(I+P_{23}).
\]

Then `[p;λ]T=[p;γ]`, the baseline hazard is positive, and the input matrix
belongs to `V_3`. The stated conclusion is `U_3≥_hr V_3`, equivalently
`h_λ≤h_γ`, contradicted by `41/1001>0` at `log 4`.

The proof invokes Lemma 2.5, which concerns a sum of functions of individual
columns. Its displayed mixture hazard is a ratio of two sums, with a shared
denominator. That lemma does not supply the claimed extension. The
counterexample establishes the failure independently of this proof diagnosis.

### Strict weights and distinct rates also fail

Equality of weights and repeated rates are unnecessary. Take

\[
 p=(2/5,1/3,4/15),\quad \lambda=(2,6,10),\quad \gamma=(2,7,9).
\]

The weights strictly decrease, both rate vectors strictly increase, and
`λ` majorizes `γ`. With the same `p` on both sides, the hazard difference at
`log 2` is `248/4455>0`, again refuting the 2022 extension.

For the 2026 statement instead set `T=(3/4)I+(1/4)P_23`. Then
`pT=(2/5,19/60,17/60)=p'` and `λT=γ`; both matrices are strictly antiordered
between distinct columns. Direct evaluation gives

\[
 h_{p,\lambda}(\log 2)=898/405,\qquad
 h_{p',\gamma}(\log 2)=6829/3165,
 \qquad h_{p,\lambda}-h_{p',\gamma}=1019/17091>0.
\]

Thus restricting the matrix ordering to strict inequalities would not repair
this extension. Both strict examples also have a negative hazard difference
at `log(4/3)`, as retained in the exact verifier.

## Reproduction and provenance

Run the standard-library [exact verifier](../research/spikes/stochastic/hazard_mixtures.py):

```sh
python3 -m research.spikes.stochastic.hazard_mixtures
```

It evaluates hazards directly from mixture definitions, checks majorization
and the explicit matrix transformations, and compares the raw and factored
hazard numerators as formal polynomials. Rational grids for `3≤n≤32` provide
additional implementation checks; they are not the proof of the unrestricted
result. The repository's combined stochastic verifier also executes it.

The counterexample arose while comparing the lab's
[rank-grouping theorem](mixture-rank-grouping.md) with mixture-order literature.
The investigating assistant supplied the construction and proof; a separate
reviewer checked the source hypotheses and arithmetic, and a bounded worker
implemented the supplied exact checks. No autonomous small-model origination,
token-efficiency advantage, or external peer review is claimed.

## Source coverage and priority

Audit date: 23 September 2026. The 2022 publisher theorem, definitions,
exponential example and open remark were read and visually checked. The 2026
accepted manuscript's model, definitions, lemma, theorem and proof were read;
the lemma and theorem pages were visually checked. The [institutional record](https://strathprints.strath.ac.uk/96227/)
identifies that version, and the [publisher record](https://onlinelibrary.wiley.com/doi/10.1002/asmb.70089)
dates publication to 8 April 2026. The final full theorem text was unavailable.
The inspected accepted PDF has SHA-256
`67efbc3770e16abdb2c4c2c6158323bf8e4966e9d8dd4dae6d0ac8efd6d1fe7c`.
Bounded title/DOI/correction searches did not locate a correction; that does
not establish its absence.

The [novelty ledger](novelty-ledger.md) records other inspected results and
unread leads. The defensible present claim is an exact negative answer to the
2022 extension and a counterexample to the identified 2026 manuscript theorem.
Whether this observation, its general mechanism, or an equivalent correction
has already appeared elsewhere remains a separate priority question.
