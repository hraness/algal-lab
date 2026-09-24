# Partial specialization in nested softmax task allocation

Three agents suffice for a positive heterogeneity gain where an early
conjecture predicted zero. More generally, every pure allocation with full
budgets strictly between complete concentration and complete specialization
beats both endpoints at every matched positive temperature. This note also
proves the exact optimum and all maximizers when the inner temperature is
positive and the outer temperature is nonpositive.

These are proved comparisons for a specified allocation problem. They refute
the exactness conjecture in the first arXiv version of Amir, Bettini and Prorok,
which was omitted from the second version onward. The current lower-bound
theorem survives. Global priority, the reason for the conjecture's removal,
and optimality of the positive-temperature grouped construction remain open.

The [boundary sequel](softmax-specialization-boundaries.md) solves every
two-agent temperature pair and proves that three is minimal even over
continuous allocations. It also classifies the optimal pure grouping in
small- and large-temperature regimes.

## Model and results

Write the Boltzmann, or softmax-weighted, mean as

\[
 B_a(x_1,\ldots,x_d)=\frac{\sum_i x_i e^{a x_i}}{\sum_i e^{a x_i}}.
\]

There are `N` agents and `M` tasks. A feasible allocation is a nonnegative
matrix `A=(r_ij)` with each row sum at most one. Its task scores and reward are

\[
 s_j=B_t(r_{1j},\ldots,r_{Nj}),\qquad R(A)=B_\tau(s_1,\ldots,s_M).
\]

A homogeneous allocation has identical rows. Let `R_hom` and `R_het` be the
maximum rewards over homogeneous and arbitrary feasible allocations, and put
`ΔR=R_het−R_hom`. These maxima exist by continuity and compactness. Define

\[
 \sigma(a,d)=\frac{e^a}{e^a+d-1}.
\]

The results are:

| Parameters | Conclusion |
|---|---|
| `t≤0`, any `N,M` | Homogeneous and arbitrary allocations have exactly the same attainable task-score vectors, the nonnegative subunit simplex. Any outer utility therefore has the same supremum over both classes. |
| `N=M=n≥2`, `t>0`, `τ≤0` | `R_het=σ(t,n)`, `R_hom=1/n`, and `ΔR=σ(t,n)−1/n`. The maximizing allocations are exactly the permutation matrices. |
| `N=M=n≥3`, `t=τ>0` | Every pure allocation with full budgets, except concentration and permutation allocations, strictly beats both of those endpoints. |

Here a pure allocation with full budgets means that every row is a unit
coordinate vector: each agent devotes its whole budget to exactly one task.
Abstaining agents are excluded. The last row supplies a positive gain for
every `n≥3` and every matched positive temperature. It is a lower bound, not
a classification of all optimal allocations for positive outer temperature.

## Exact counterexamples with monotone reward functions

First take `N=M=3`, `t=τ=log 2`, and assign two agents to the first task and
one to the second, leaving the third task empty. The task scores are
`(4/5,1/2,0)`, and the homogeneous optimum is `1/2`. With
`r=2^(4/5)` and `q=√2`, direct subtraction gives

\[
 R-\frac12=\frac{3r-5}{10(r+q+1)}.
\]

The integer comparison `12^5<16·7^5` proves `r>12/7`, while `2<9/4`
proves `q<3/2`. The displayed fraction increases with `r` and, once its
numerator is positive, decreases with `q`. Substitution therefore gives

\[
 \Delta R\ge R-\frac12>
 \frac{3(12/7)-5}{10(12/7+3/2+1)}=\boxed{\frac1{295}}.
\]

This is the smallest possible team size for a strict improvement among pure
allocations with full budgets. A four-agent example gives a larger certified
gap with equal groups:

Take `N=M=4`, `t=τ=log 2`, and

\[
 A=\begin{pmatrix}
 1&0&0&0\\
 1&0&0&0\\
 0&1&0&0\\
 0&1&0&0
 \end{pmatrix}.
\]

Every agent uses its full budget. The task scores are `(2/3,2/3,0,0)`. With
`r=2^(2/3)`, the reward is

\[
 R(A)=\frac{2r}{3(r+1)}.
\]

The homogeneous optimum and the completely specialized reward are both
`σ(log 2,4)=2/5`, as proved below. Since

\[
 r^3=4>\left(\frac{19}{12}\right)^3
 \quad\text{because}\quad 6912>6859,
\]

strict monotonicity of `r/(r+1)` gives the exact certificate

\[
 R(A)>\frac{38}{93},\qquad
 \Delta R\ge R(A)-\frac25>\boxed{\frac4{465}}.
\]

The v1 conjectured value at matched positive temperatures was zero. These
examples do not depend on a failure of coordinatewise monotonicity on the
allocation domain: if `0<a<1` and `x∈[0,1]^d`, then

\[
 \partial_i B_a(x)=p_i[1+a(x_i-B_a(x))]\ge p_i(1-a)>0,
 \qquad p_i=\frac{e^{a x_i}}{\sum_j e^{a x_j}}.
\]

All feasible efforts and task scores lie in that unit box, and `log 2<1`.
Thus both levels are strictly increasing throughout their feasible boxes.
This is not a claim of monotonicity on unbounded real space. If the general
aggregator definition is read as requiring that larger domain, composing
with coordinatewise clipping to `[0,1]` supplies symmetric, nondecreasing
extensions that agree on every feasible inner and outer input.

There is a larger exact gap at `t=τ=log 4`. The same allocation has scores
`(4/5,4/5,0,0)` and reward `(4/5)r/(r+1)`, now with `r=4^(4/5)`.
Since `r^5=256>3^5=243`, this reward exceeds `3/5`. The homogeneous optimum
is `4/7`, giving `ΔR>1/35`. The `log 2` examples certify
monotonicity throughout the feasible domain.

## Elementary bounds and the homogeneous optimum

For real `x_i` and weights `w_i=e^{a x_i}`,

\[
 d\sum_i x_iw_i-\left(\sum_i x_i\right)\left(\sum_i w_i\right)
 =\sum_{i<j}(x_i-x_j)(w_i-w_j).
\]

Consequently `B_a(x)` is at most the arithmetic mean for `a≤0` and at least
that mean for `a≥0`. This identity is an elementary ordering argument, not a
novelty claim about the Boltzmann mean.

For `a>0` and `x∈[0,1]^d`, each weight satisfies

\[
 p_i=\frac{e^{a x_i}}{e^{a x_i}+\sum_{j\ne i}e^{a x_j}}
 \le\frac{e^a}{e^a+d-1}=\sigma(a,d).
 \tag{1}
\]

If also `∑x_i≤1`, multiplying by the nonnegative coordinates gives
`B_a(x)≤σ(a,d)∑x_i≤σ(a,d)`. A unit coordinate attains the bound.
For `a≤0`, the arithmetic-mean bound instead gives `B_a(x)≤1/d`, attained
by `(1/d,…,1/d)`.

In a homogeneous allocation with common row `c`, the task scores are exactly
`c`, independently of `t`. It follows that, for all inner temperatures,

\[
 R_{\rm hom}=
 \begin{cases}
 1/M,&\tau\le0,\\
 \sigma(\tau,M),&\tau>0.
 \end{cases}
 \tag{2}
\]

The uniform allocation and the concentrated allocation are different
baselines. In particular, at positive outer temperature the uniform allocation
is not the optimal homogeneous allocation when `M≥2`.

## Nonpositive inner temperature: the entire attainable region

Suppose `t≤0`. For any feasible allocation the mean bound gives

\[
 s_j\le\frac1N\sum_i r_{ij},\qquad
 s_j\ge0,\qquad \sum_j s_j\le1.
\]

Conversely, for any nonnegative vector `s` with `∑s_j≤1`, take every row of
`A` equal to `s`. Each column is constant, so its Boltzmann mean equals
`s_j`. Therefore both homogeneous and arbitrary allocations attain exactly

\[
 \{s\in\mathbb R^M:s_j\ge0,\ \sum_j s_j\le1\}.
\]

Equality of feasible score sets proves equality of suprema for **any** outer
utility, without requiring symmetry, monotonicity, or continuity. For the
Boltzmann outer reward the maxima are exactly (2), giving `ΔR=0` for all
`N,M` and all `τ`.

The score-set statement uses row budgets **at most** one. It does not hold
with arbitrary outer utilities when every row must sum to exactly one.
For example, with `N=M=2`, `t=−log 2`, the identity allocation yields
`(1/3,1/3)`, whereas every full-budget homogeneous score vector sums to one.
The utility `U(s)=−∑s_j` separates the two classes. For a Boltzmann outer
reward, the zero-gain conclusion does hold under exact budgets: the same
upper bounds apply, and both homogeneous attainers in (2) use full budgets.

## Positive inner and nonpositive outer temperature: exact optimum

Let `N=M=n≥2`, `t>0` and `τ≤0`. Applying (1) to each column,

\[
 s_j\le\sigma(t,n)\sum_i r_{ij},\qquad
 R(A)\le\frac1n\sum_j s_j
 \le\frac{\sigma(t,n)}n\sum_{i,j}r_{ij}
 \le\sigma(t,n).
\]

Every permutation matrix attains equality: each task has one unit-effort
agent and `n−1` zero-effort agents, hence every score equals `σ(t,n)`.
Equation (2) then gives the claimed exact gain.

To classify all maximizers, equality at the last bound requires total effort
`n`, so every row uses its full budget. Equality in the sum of the column
bounds requires, for every positive `r_ij`, equality in its weight bound (1).
Since `t>0`, that requires `r_ij=1` and every other entry in that column to
be zero. Full row budgets force one such entry in every row; distinct occupied
columns then force a permutation matrix. This argument also covers `τ=0`.

For `t>0` and `τ>0`, concentration gives `σ(τ,n)` and a permutation gives
`σ(t,n)`. Taking the better of these two feasible allocations and using (2)
recovers the later paper's remaining lower bound directly:

\[
 \Delta R\ge\max\{\sigma(t,n)-\sigma(\tau,n),0\}.
\]

## Every intermediate pure allocation improves the reward

Let `N=M=n`, `t=τ>0`, and `E=e^t>1`. A pure allocation with full budgets is
specified, up to permutations, by the positive task occupancies
`m_1,…,m_k`, where `∑m_j=n`; the other `n−k` tasks are unoccupied. Define

\[
 D_m=\frac{mE+n-m}{n},\qquad
 s_m=\frac{mE}{mE+n-m},\qquad
 h=\frac{E}{E+n-1}.
\]

The nested reward and a useful exact identity are

\[
 R=\frac{\sum_{j=1}^k s_{m_j} E^{s_{m_j}}}
         {\sum_{j=1}^k E^{s_{m_j}}+n-k},\qquad
 s_m-h=\frac{h(m-1)}{D_m}.
\]

Since `∑(m_j−1)=n−k`, subtracting `h` gives

\[
 R-h=
 \frac{h}{\sum_{j=1}^k E^{s_{m_j}}+n-k}
 \sum_{j=1}^k(m_j-1)
       \left(\frac{E^{s_{m_j}}}{D_{m_j}}-1\right).
 \tag{3}
\]

Every summand is nonnegative, and one is positive unless the allocation is
an endpoint. To prove this, fix `0<m<n`, put `p=m/n`, and write
`D=1−p+pE`, so `s_m=pE/D`. Define

\[
 f(E)=pE\log E-D\log D.
\]

Then `f(1)=0` and

\[
 f'(E)=p\log\frac ED>0\qquad(E>1,\ 0<p<1),
\]

because `E−D=(1−p)(E−1)>0`. Therefore `E^{s_m}>D_m`.
Equivalently, `f(E)>0` is the strict Jensen inequality for `x log x` at
`E` and `1` with weights `p` and `1−p`; the underlying convexity is standard.
For `m=1`, the prefactor `m−1` in (3) vanishes. For `m=n`, there is only
one occupied task, and `E^{s_m}=D_m=E`, also giving equality. Every other
occupancy pattern has some `2≤m≤n−1`, giving a strictly positive term in
(3). This proves the claim for every finite matched positive temperature.

The equality cases within this class are precisely complete concentration
and permutation allocations. For `n=2` these exhaust all pure allocations
with full budgets, so `n=3` is the smallest dimension admitting a strict
improvement **within this class**. The separate
[two-agent proof](softmax-specialization-boundaries.md#exact-two-agent-solution)
extends this minimum-dimension conclusion to continuous allocations.

### Equal groups as a closed-form corollary

When `1<k<n` divides `n`, assign `n/k` agents to each of `k` tasks. Each
active score is `s=E/(E+k−1)`. With `r=E^s`, the reward is

\[
 R_k=\frac{k s r}{k r+n-k}>\frac{E}{E+n-1}.
 \tag{4}
\]

Equivalently, `r>(E+k−1)/k`, the preceding strict inequality with `p=1/k`.
The two four-agent certificates use this special case. Equal groups simplify
the formula; they are not necessary for a gain.

The mechanism in (3) is additive across occupied tasks: each task receiving
between two and `n−1` agents contributes a strictly positive amount to the
reward's cross-multiplied improvement. Concentration and permutation
allocations make every term vanish. This identifies a whole family of better
allocations without an optimization search. It does not prove that pure
allocations or equal group sizes are globally optimal.

## Source comparison and priority

The dated primary reference is Amir, Bettini and Prorok, *When Is Diversity
Rewarded in Cooperative Multi-Agent Learning?*, arXiv:2506.09434 / ICLR 2026.

| Version | Inspected statement |
|---|---|
| [v1, 11 June 2025](https://arxiv.org/pdf/2506.09434v1), printed/PDF page 5 | The paragraph before Theorem 3.4 conjectures exactness of its lower bound. At `t=τ>0` that would give zero gain. The page was visually checked. |
| [v2, 28 September 2025](https://arxiv.org/html/2506.09434v2) | The exactness conjecture and “Exact” theorem-title qualifier are absent. The positive-inner statements remain lower bounds. |
| [v3, 4 November 2025](https://arxiv.org/html/2506.09434v3), and [v4, 1 March 2026](https://arxiv.org/html/2506.09434v4) | The conjecture remains absent. Theorem 3.4 retains the lower bounds. |

The inspected v1 PDF has SHA-256
`14c3a02ab1427008beb897cf544fe703fd642622c79b67784a5291b7e7b7fa82`.
The version dates are listed on the [arXiv record](https://arxiv.org/abs/2506.09434).
Targeted reading of v2/v3 theorem, proof, metadata and limitations passages
found no explanation of the omission or a replacement counterexample. That
bounded reading does not establish why the authors changed the text.
The [public OpenReview discussion](https://openreview.net/forum?id=uJCGMBO6Qx)
required browser verification and remained unread.

The new construction contradicts the v1 conjecture, while strengthening the
positive-outer lower bound in later versions. Our exact nonpositive-outer
solution confirms the other positive-inner branch of that old conjecture.
The score-set proof independently recovers and extends the nonpositive-inner
conclusion. None of these conclusions requires the unrestricted Schur claim
addressed in the [box-threshold note](sharp-softmax-spread.md).

The paper's other general theorems do not already certify this comparison:
Theorem 3.1 exempts trivial optimal homogeneous allocations; (2) places the
positive-outer case in that exception. Theorem 3.3 requires constant total
task score, but concentration has total score `1` and a permutation has total
`nσ(t,n)>1`. Its equal-size groups in the foraging appendix use a different
threshold reward, not the nested Boltzmann means here.

Balanced specialization is an established broad subject. The bounded search
did not locate an equivalent construction or formula for this exact model;
it also did not close the wider task-allocation literature. An institutional
PDF lead for Dahl, Matarić and Sukhatme's 2009 vacancy-chain scheduling paper
could not be retrieved with certificate verification and remains unread.
The source-relative improvement and early-conjecture refutation are proved;
first-discovery priority remains unresolved. See the [novelty ledger](novelty-ledger.md).

## Reproduction and limits of the evidence

Run the credential-free, standard-library exact checker:

```sh
python3 -m research.spikes.stochastic.softmax_allocation
```

The combined `python3 -m research.spikes.stochastic.verify` includes it in CI.
The checker enumerates all 1,000 three-by-three allocations on row entries
`{0,1/2,1}` with row sum at most one. At inner temperatures `±8 log 2` and
outer temperature **zero**, it checks column bounds, both optimum values,
and that the positive-inner maximizers are precisely the six permutation
matrices. This finite enumeration is not evidence for arbitrary outer
parameters by itself.

It also enumerates all integer occupancy partitions for `3≤n≤12`, constructs
their pure allocation matrices, and checks the component identity and
strict-term classification for integer `2≤E≤8`. The certificate for
`E^{s_m}>D_m`, with `P=mE+n−m`, is the integer comparison
`n^P E^(mE)>P^P` for `0<m<n`; it is equality at `m=n`.

A separate check covers equal groups for every proper divisor at `4≤n≤32`
and integer `2≤E≤8`, together with the exact rational certificates for the
three-agent example and both four-agent examples. For the equal groups,
(4) is certified by

\[
 k^{E+k-1} E^E>(E+k-1)^{E+k-1}.
\]

The universal results rest on the proofs above and independent mathematical
review, not on the bounded enumeration. Formula supply, mechanical checker
implementation and independent proof checking were separate activities.
No small-model theorem-origination, token-efficiency, learned-policy, or
runtime-performance advantage is claimed.
