# A sharp spread threshold for Schur ordering of the softmax mean

For the softmax-weighted mean

\[
 B_\tau(x)=\frac{\sum_{i=1}^n x_i e^{\tau x_i}}
                  {\sum_{i=1}^n e^{\tau x_i}},
\]

the sign of `τ` alone does not determine a global Schur ordering when
`n≥3`. The exact condition on a box `[a,b]^n` depends on temperature times
spread. This note sharpens an earlier dimension-free sufficient bound to
an exact finite-dimensional condition, proves its necessity, and gives
a rational counterexample to an unrestricted claim in an ICLR 2026 author
PDF. The mathematical result has independent review; literature-first
priority is unresolved in the [source audit](#source-comparison-and-priority).

The [task-allocation sequel](softmax-task-allocation.md) proves the downstream
lower bounds directly, sharpens one to an exact optimum, and gives a grouped
allocation that contradicts an exactness conjecture in the paper's first
arXiv version. That conjecture was omitted from later revisions.

Here `x≽y` means equal totals and larger decreasing partial sums for `x`.
A Schur-convex function assigns `f(x)≥f(y)` to such a pair; a Schur-concave
function reverses the inequality. Strictness excludes permutations.

## Exact classification

**Theorem.** Let `a<b` be finite real numbers and `n≥3`. Define `c_n>2` by

\[
 (n-2)(c_n-2)e^{c_n}=4,
 \qquad
 c_n=2+W_0\!\left(\frac{4}{(n-2)e^2}\right), \tag{1}
\]

where `W_0` is the nonnegative real branch of Lambert's inverse
`W(z)e^{W(z)}=z`. Then:

- For `τ>0`, `B_τ` is Schur-convex on `[a,b]^n` **if and only if**
  `τ(b−a)≤c_n`.
- For `τ<0`, `B_τ` is Schur-concave on that box **if and only if**
  `|τ|(b−a)≤c_n`.
- Both valid regimes are strict modulo permutations, including equality in
  the bound. Outside the corresponding regime, `B_τ` is neither Schur-convex
  nor Schur-concave on the box.

For `n=2` the corresponding strict ordering holds for every nonzero `τ`
and every finite spread. At `τ=0` the function is the arithmetic mean,
so it has both non-strict Schur properties.

The constants decrease with dimension and tend to `2`. Certified rational
enclosures from the [verifier](../research/spikes/stochastic/softmax_spread.py)
imply these deliberately wider decimal intervals:

| `n` | Strict enclosure for `c_n` |
|---:|---:|
| 3 | `(2.372856, 2.372857)` |
| 4 | `(2.217715, 2.217716)` |
| 8 | `(2.083034, 2.083035)` |
| 32 | `(2.017727, 2.017728)` |
| 128 | `(2.004278, 2.004279)` |

This concerns the weighted mean `B_τ`. Log-sum-exp is a different operator;
the distinction is established in [Asadi and Littman (2017)](https://proceedings.mlr.press/v70/asadi17a/asadi17a.pdf).

## Proof of the sufficient bound

It suffices first to consider the negative-temperature normalized function

\[
 F(u)=\frac{\sum_i u_i e^{-u_i}}{\sum_i e^{-u_i}}
 \quad\hbox{on }[0,L]^n.
\]

Indeed, for `t>0`, setting `u_i=t(x_i−a)` gives
`B_{−t}(x)=a+F(u)/t`, with `L=t(b−a)`. Positive affine changes preserve
majorization. Positive temperature then follows by reflection:
`B_t(x)=a+b−B_{−t}(a+b−x)`; reflection preserves majorization at equal sums.

Put `S=Σ_i exp(−u_i)`. Differentiation gives

\[
 \partial_i F=\frac{e^{-u_i}}S(1-u_i+F). \tag{2}
\]

By the standard derivative criterion for Schur-concavity, it is enough to
show `∂_xF>∂_yF` whenever two coordinates satisfy `x<y`. Set
`m=n−2`, `A=exp(−x)`, `B=exp(−y)` and `P=xA+yB`.
Each other coordinate `r≥0` contributes a nonnegative numerator and at
most one to the denominator. Therefore

\[
 F\ge \frac{P}{m+A+B}.
\]

Since `A−B>0`, substituting this lower bound into (2) gives

\[
 \partial_xF-\partial_yF\ge\frac{N}{S(m+A+B)},
\]

where direct expansion yields

\[
 N=m[(1-x)e^{-x}-(1-y)e^{-y}]
   +e^{-2x}-e^{-2y}+2(y-x)e^{-(x+y)}.
\]

Writing `c=(x+y)/2` and `z=(y−x)/2>0`, we obtain

\[
 \frac{N}{2e^{-c}\sinh z}
 =m(1-c+z\coth z)
   +2e^{-c}\left(\cosh z+\frac z{\sinh z}\right). \tag{3}
\]

For `z>0`, `z coth z>1`: the difference after multiplication by `sinh z`
has derivative `z sinh z>0` and vanishes at zero. Also
`cosh z+z/sinh z>2`: after the same multiplication, the difference is
`sinh(2z)/2+z−2 sinh z`, with derivative
`2 cosh z(cosh z−1)>0` and zero initial value.
Thus the right side of (3) is strictly greater than

\[
 g(c)=m(2-c)+4e^{-c}.
\]

The function `g` strictly decreases, and its unique zero is `c_n`.
Since `c<L≤c_n`, we have `g(c)>g(L)≥0`. This proves the required strict
derivative inequality. Finite pair-averaging steps remain in the box and
give strict Schur-concavity for every nonpermutation majorization pair.
The same argument applies on closed faces; equal coordinates cause no
additional equality cases. This proves sufficiency, including `L=c_n`.

## Sharpness above the bound

Consider `m` zero coordinates and a high pair `(c−z,c+z)`, compared with
the same zeros and `(c,c)`. The split vector majorizes the equal-pair vector.
Writing `q=exp(−c)`, their exact difference is

\[
 \Delta(c,z)=
 \frac{2q\{mc(\cosh z-1)-z\sinh z(m+2q)\}}
 {(m+2q\cosh z)(m+2q)}. \tag{4}
\]

Its expansion at `z=0` is

\[
 \Delta(c,z)=
 \frac{q\{m(c-2)-4q\}}{(m+2q)^2}z^2+O(z^4).
\]

Whenever `L>c_n`, choose `c_n<c<L`. The coefficient is positive, so
a sufficiently small split with `0<z<min(c,L−c)` has `Δ(c,z)>0`.
Both vectors lie in the box, contradicting Schur-concavity. This proves
necessity. At the threshold itself the strict ordering proved above still
holds; a limiting zero quadratic coefficient is not an equality case.

The failure can also be placed strictly inside the box, with an explicit
split. Set

\[
 C=(L+c_n)/2,\quad s=(L-c_n)/4,\quad q=e^{-C},
 \quad \eta=1-\frac{2(m+2q)}{mC}>0,
\]
\[
 z=\min\{s/2,\sqrt{3\eta}\}.
\]

Compare `(s,…,s,s+C−z,s+C+z)` with `(s,…,s,s+C,s+C)`.
Every coordinate lies in `(0,L)`, and shift invariance reduces their
difference to (4). Its numerator has the sign of

\[
 mC\frac{\tanh(z/2)}z-(m+2q)
 \ge \frac{mC\eta}{2}-\frac{mCz^2}{24}
 \ge \frac{3mC\eta}{8}>0.
\]

Here `tanh r≥r−r³/3` follows by differentiating the difference and using
`0≤tanh r≤r`. This supplies a finite interior violation for every `L>c_n`.

For `n=2`, `F(c−z,c+z)=c−z tanh z`, which strictly decreases with `z>0`;
there is no upper spread restriction. Finally, near an interior all-equal
vector, a split of two coordinates gives
`B_τ(x+εe_i−εe_j)=x_1+(2τ/n)ε²+O(ε⁴)`.
This excludes the opposite Schur property for every nonzero temperature,
and establishes the “neither” claim above the bound.

## Consequence for exponential mixtures

The hazard of a uniform exponential mixture is `H_t(v)=B_{−t}(v)`.
Consequently, for rates in `[a,b]` with `0<a<b`, rate majorization gives
the reversed numerical hazard comparison throughout

\[
 0\le t\le\frac{c_n}{b-a}.
\]

This is the sharp time interval valid for **all** rate vectors in the box.
It does not assert an all-time hazard-rate order for each individual pair.
It explains why the [higher-dimensional counterexamples](hazard-mixture-counterexample.md)
can coexist with a valid short-time comparison. The dimension-free sufficient
constant `2` is also sharp when all dimensions are allowed. Its sufficiency
already follows from earlier Lehmer-mean theory, as detailed below.

The [fixed-total simplex sequel](simplex-softmax-order.md) gives another exact
classification. On nonnegative vectors of total `S`, the negative-temperature
bound is `|τ|S≤2c_n`; the positive bound is `|τ|S≤d_n`, where
`(d_n−2) exp(d_n)=2(n−1)`. Their ordering reverses at dimension 58.

## Exact counterexample to the unrestricted softmax claim

Amir, Bettini and Prorok's [ICLR 2026 author PDF](https://matteobettini.com/publication/hetenvdesign/HetEnvDesign.pdf),
*When Is Diversity Rewarded in Cooperative Multi-Agent Learning?*, Table 3
on page 21, asserts the corresponding strict Schur properties for all
positive/negative temperatures on nonnegative inputs. Its task columns may
take arbitrary values in `[0,1]^n` under the row allocation constraints.

Take

\[
 x=(1,1/2,0),\quad y=(1,1/4,1/4),\quad \tau=8\log2.
\]

Then `x≽y`. The exponential weights are exactly `(256,16,1)` and
`(256,4,4)`, respectively, and

\[
 B_\tau(x)=88/91,\qquad B_\tau(y)=43/44,
 \qquad B_\tau(x)-B_\tau(y)=-41/4004<0.
\]

Reflection gives the opposite-sign violation at negative temperature.
Appending coordinatewise complementary task columns gives three-agent
allocations with every row summing to one; a zero third column also makes
the numbers of agents and tasks equal. This establishes the domain match.
It disproves the unrestricted aggregator property. It does not by itself
disprove downstream heterogeneity-gain conclusions or experimental results.

## Reproduction and provenance

```sh
python3 -m research.spikes.stochastic.softmax_spread
```

The [fixed standard-library checker](../research/spikes/stochastic/softmax_spread.py)
uses rational arithmetic for the softmax counterexample and certified
exponential bounds to enclose five threshold roots. For a positive `x≤3`,
it bounds the tail after Taylor degree `48` by the first omitted term divided
by `1−x/50`; each subsequent term ratio is at most `x/50<1`.
Rational bisection then gives root intervals of width `2^−24` with opposite
certified signs at their endpoints. Numerical enclosures are separate from
the analytic proof for every dimension.

The investigating assistant derived the threshold while analyzing the hazard
counterexample. An independent reviewer verified the proof and supplied the
explicit interior construction. A separate literature lane located the
ICLR claim; a bounded implementation worker received the formulas and fixed
checks. This is not evidence of small-model theorem origination or of a
token-efficiency advantage. The combined stochastic CI verifier runs these
checks without model inference.

## Source comparison and priority

Audited 23 September 2026. The ICLR author PDF's definitions, relevant proof
passages and Table 3 were read; the table was visually checked. Its SHA-256 is
`4473fb913f6cb4a64f6db5fa92ae35320598cc89d029f930c88e747c84ec0d2f`.
The [author page](https://matteobettini.com/publication/hetenvdesign/) identifies
the venue. The official OpenReview route required browser verification;
identity with its final PDF is unconfirmed. The claim here is bound to the
inspected author version.

Asadi and Littman's [ICML 2017 paper](https://proceedings.mlr.press/v70/asadi17a/asadi17a.pdf)
already documents Boltzmann-operator failures of non-expansion and develops
mellowmax. The inspected operator definitions and mathematical sections concern
sup-norm bounds and monotonicity, rather than this equal-sum Schur comparison.
The weighted mean and its possible defects are established subjects.

The same ratio is also the Esscher premium of the uniform law on the input
coordinates. [Gerber (1981)](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CA6B67F264FD91712EE4AA7CD9821E8E/S0515036100007078a.pdf/esscher_premium_principle_a_criticism_comment.pdf)
already supplies a three-point failure of coordinatewise stochastic
monotonicity. That comparison changes the mean and does not give this
equal-sum Schur classification. The ledger records this original and the
unread 1989 source addressing variability ordering.

Fu, Wang and Shi's [2016 paper](https://www.isr-publications.com/jnsa/2618/download-schur-convexity-for-lehmer-mean-of-n-variables),
Theorem 1.4(II), gives a dimension-free sufficient bound for the Lehmer mean
`L_p(u)=Σu_i^p/Σu_i^(p−1)`. It is Schur-geometrically convex on
`[((p−1)/p)^2 A,A]^n` for `p>1/2`. The theorem on printed page 5512 was
visually checked, and its positive-parameter proof in Section 3.2 was read.
The following limit explicitly credits the resulting softmax bound.

For `τ>0`, choose `0<ε<τ`, set `p=τ/ε`, `u_i=exp(εx_i)` and
`A=exp(εb)`. The box premise holds whenever

\[
 \varepsilon(b-a)\le -2\log(1-\varepsilon/\tau).
\]

In particular, `τ(b−a)≤2` implies this premise because
`−log(1−r)≥r` for `0<r<1`. Writing `Z_x(t)=Σ_i exp(tx_i)`,

\[
 \frac{\log L_{\tau/\varepsilon}(e^{\varepsilon x})}{\varepsilon}
 =\frac{\log Z_x(\tau)-\log Z_x(\tau-\varepsilon)}{\varepsilon}
 \longrightarrow B_\tau(x).
\]

Geometric Schur convexity transfers the majorization comparison through
this limit. Therefore the non-strict sufficient bound `|τ|(b−a)≤2`
is already a consequence of that theorem; reflection handles `τ<0`.
Strictness is proved separately above, not inferred from the limit.
The new candidate sharp bound is `c_n>2` for each finite `n≥3`.

Perla, Padmanabhan and Lokesha's [2017 paper](https://journalijcar.org/sites/default/files/issue-files/4103---A--2017.pdf)
uses the name Gini mean for the adjacent-parameter specialization
`G_q=Σu_i^(q+1)/Σu_i^q=L_(q+1)` in equation (1.3). Its inspected
Theorem 3.2(II) gives the same sufficient box after relabeling parameters;
it does not provide the diagonal-general Gini case or a dimension-dependent
threshold. This is a comparison of those statements, not a validity audit
of all results in either paper.

Witkowski's [2011 paper](https://files.ele-math.com/articles/mia-14-74.pdf),
pages 897–899, gives the two-variable Gini mean and recalls its geometric
Schur convexity. The substitution
`log G(τ,τ;exp x,exp y)=B_τ(x,y)` makes the two-variable positive-temperature
case existing mean-inequality theory. No novelty is claimed for that case,
the derivative criterion, or the Lambert-W representation.

The [novelty ledger](novelty-ledger.md) retains unread general-mean, Esscher
premium and recent Boltzmann-operator leads. The candidate contribution is the exact
dimension-dependent box threshold, its boundary and necessity proof, and
its connection to the specific unrestricted assertions above. The inspected
papers do not supply that threshold; this bounded comparison does not prove
its absence from the wider literature.
