# Terminal-pair sampling and finite-sample regret certificates

This note supports the [sampler](../../terminal_sampling.py) and its
[independent arithmetic tests](../../test_terminal_sampling.py). It concerns
one terminal endpoint and does not establish literature priority.

Let n>=2, w_i>0, v_i>0, V=sum_i v_i. Delete n-2 vertices sequentially, each
chosen proportional to its remaining weight. Write E for the unordered surviving
pair, q_e=P(E=e), a_ij=min(v_i,v_j)/V, and B=max_e a_e, which is the
second-largest node value divided by V. For a tree T,

  E[LCC-value(T)]/V = E[max(v_i,v_j): E={i,j}]/V + F(T),
  F(T)=sum_{e in T} a_e q_e.

The constant is independent of T. Thus a maximum spanning tree with weights
a_e q_e is a globally optimal tree for this endpoint. This does not optimize
the earlier trajectory AUC. The statement applies to any distribution of the
surviving pair, not just weighted removal.

## Sampling law

Independent exponential times X_i~Exp(w_i), sorted increasingly, produce the
same deletion order: P(i is first)=w_i/sum_j w_j, and memorylessness repeats
this conditional law on the remaining vertices. The surviving pair is the two
largest X_i. Continuous ties have probability zero. Therefore independent race
replications give unbiased pair indicators and counts.

Finite-grid uniforms plus floating logarithms are not literally continuous
exponentials. No unquantified assertion of exact unbiasedness should be made
for that implementation. For admitted positive integer weights, a uniform
integer ticket in [0,sum remaining weights) and cumulative weight selection
implements each deletion exactly under the independent unbiased-bit premise.
A Fenwick tree supports prefix selection and removal in logarithmic work.

The implementation defaults to secrets.randbelow. This is a randomness source,
not a mathematical proof that physical draws are ideal IID bits. Injected
fixed-seed PRNG runs are numerical reproductions and must be labeled as such.
If instead a sampling approximation is known to have pair-law total variation
distance <=eta from q, its regret guarantee transfers with an added 2B*eta.

## Fixed-N uniform ERM guarantee

For N independent pair draws define qhat_e=count_e/N. Each tree's empirical
benefit is the average of f_T(E)=a_E*1{E in T}, in [0,B]. With M=n^(n-2)
labeled trees, Hoeffding plus a two-sided union bound yields simultaneously

  |Fhat(T)-F(T)| <= B sqrt(log(2M/delta)/(2N))

with probability >=1-delta. The empirical maximum spanning tree therefore has
additive normalized regret at most

  min(B, 2B sqrt(log(2M/delta)/(2N))).

Equivalently N>=2B^2 log(2M/delta)/epsilon^2 suffices for regret<=epsilon.
The B cap is deterministic because all benefits lie in [0,B]. This is an
ordinary finite-class estimation result, not a new concentration inequality.

If the independently proved ordered-Pareto-frontier family contains a true
optimum and has k frontier vertices, its size is (k-1)! k^(n-k): vertex j of
the ordered frontier chooses among its j predecessors, and each other vertex
chooses a frontier parent. An empirical maximizer in that family receives the
same bound with that smaller M. k=1 is a deterministic solved subcase and
needs no samples. This claim is conditional on the separate frontier theorem.

## Simultaneous KL intervals and adaptive candidate certificate

Let m=n(n-1)/2, N fixed, p_e=count_e/N, and L=log(2m/delta). Define

  I_e={q in [0,1]: N kl(p_e||q)<=L},
  kl(p||q)=p log(p/q)+(1-p)log((1-p)/(1-q)).

The binomial Chernoff bound follows directly from the moment generating
function. If X is Binomial(N,q), then E[exp(tX)]=(1-q+q*exp(t))^N. For x>q,
Markov's inequality and minimization over t>0 give
P(X/N>=x)<=exp(-N*kl(x||q)); the minimizing t is
log(x*(1-q)/(q*(1-x))). The same argument with t<0 gives the lower tail for
x<q. Boundary cases follow by limits. For fixed q, kl(x||q) is monotone as x
moves away from q in either direction. Thus the same tail bound applies when
the event is expressed as N*kl(X/N||q)>L on either side of q.

For fixed true q_e, each wrong tail therefore has probability <=exp(-L). A union
bound across all 2m tails gives simultaneous inclusion q_e in I_e with
probability >=1-delta. Independence across edges is unnecessary; independence
across trajectory replications is necessary. For an unseen edge p_e=0,
I_e=[0, 1-exp(-L/N)], so zero counts never imply zero true mass.

Round intervals outward to [l_e,u_e]. The identity sum_e q_e=1 permits

  l'_e=max(l_e,1-sum_{f!=e}u_f),
  u'_e=min(u_e,1-sum_{f!=e}l_f).

This spends no additional probability budget. For any candidate C, including a
candidate selected using the same counts, define b_e=a_e*l'_e if e in C and
b_e=a_e*u'_e otherwise. Then

  regret(C)<=MSTweight(b)-sum_{e in C}a_e*l'_e.

Proof: for each competitor T, shared edges cancel, and
F(T)-F(C)<=sum_{T\C} a_e*u'_e-sum_{C\T}a_e*l'_e
=sum_{T}b_e-sum_C a_e*l'_e. Maximize over all trees. The result is nonnegative
because C is itself a feasible tree for the optimistic maximum. Cap by B.
This is the exact worst-case bound over the rectangular interval box before
the deterministic B cap; the true simplex-constrained bound may be smaller.

The same simultaneous event certifies every candidate from the histogram,
including both unrestricted Kruskal and the fixed frontier family. There is
no extra multiplicity cost for comparing these candidates on that histogram.
Zero bound proves optimality on this probability-coverage event; it must not
be presented as a deterministic exact-optimality certificate.

## Numerical enclosures used in code

The dyadic denominator is D=2^40. To decide that a grid point k/D lies outside
the KL set, bound below

  c log c+(N-c)log(N-c)-N log N+N log D
  -c log k-(N-c)log(D-k)-log(2m)-log(delta_den)+log(delta_num).

Zero coefficient terms vanish. All logarithm arguments are positive integers.
Python documents Decimal.ln as correctly rounded. Its immediate predecessor
and successor at 70-digit precision enclose the exact logarithm. Directed
rounding for products and sums gives a lower bound on the displayed expression.
A point is rejected only when that lower bound is strictly positive.
Inconclusive comparisons retain the point and can only widen the interval.
Binary searches return the proven outside endpoint to the left/right of the
exact KL interval. Simplex tightening, edge weights, and MST arithmetic use
integers; division by V*D produces an exact Fraction. The display float rounds
upward after an exact comparison with its Fraction representation.

Tests independently compare dyadic endpoints using integer likelihood products
rather than logarithms. They also enumerate exact binomial coverage and all
462 six-draw multinomial histograms for a four-vertex profile, including both
data-dependent candidates. These are bounded implementation checks, not a
replacement for the general theorem.

## Experiment interpretation and stopping constraints

Freeze profiles, epsilon, sample budgets, methods, seed panel and summaries
before evaluation. Use at least the known non-star four-vertex case
w=(1,1,2,5),v=(1,1,4,4), whose terminal best-star deficit is 13/2520, and a
control with aligned values/reliability. Unique optimum identity is not an
appropriate reliability target because many profiles have ties. Use exact
regret<=epsilon, and report regret/B alongside normalized endpoint regret
when comparing different n or value totals.

Use the same histogram for Kruskal and frontier; include the minimum-rate star,
uniform Prüfer random trees, the exact best-star reference, and the exact
terminal optimum. Explain that the latter references consume exact-oracle
work and are not free deployment competitors. Charge pair sampling, candidate
optimization and certificate generation separately. Report operation counts
and measured runtime; do not promise a speedup. Exact integer-weight polynomial
integration may beat sampling for small reduced total weight and repeated rates.

For multiple sample checkpoints, either label confidence per run only, or
spend delta/K over K predeclared checkpoints for joint coverage. A confidence
bound used to stop sampling requires an anytime-valid construction or explicit
alpha spending, e.g. delta_t=delta/[t(t+1)]. A fixed-N interval cannot silently
be reused until a desirable certificate appears. Zero observed failures on a
small seed panel is not proof of a tiny failure probability.

The [frozen comparison protocol](protocol.json) allocates its family failure
budget across all 384 reported algorithm certificates. The two methods share
each pair histogram, so counting both separately is conservative: the same
simultaneous edge event certifies both. This accounting does not make the
archived seeded trials a source of ideal IID randomness.

## Primary references

- Hoeffding (1963), Probability Inequalities for Sums of Bounded Random Variables:
  https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf
- Chernoff, A Measure of Asymptotic Efficiency for Tests of an Hypothesis Based
  on the Sum of Observations, Stanford's original 1951 technical-report record
  preceding the 1952 journal article:
  https://statistics.stanford.edu/technical-reports/measure-asymptotic-efficiency-tests-hypothesis-based-sum-observations
- Maurer and Pontil (2009), Empirical Bernstein Bounds and Sample Variance
  Penalization, theorem 4 (alternative valid edge intervals):
  https://www.cs.mcgill.ca/~colt2009/papers/012.pdf
- Braverman, Ostrovsky and Vorsanger (2015), Weighted Sampling Without Replacement
  from Data Streams, discusses finite-precision limitations of key-based methods:
  https://arxiv.org/abs/1506.01747
- Python Decimal arithmetic and correctly rounded ln:
  https://docs.python.org/3/library/decimal.html#decimal.Decimal.ln

These ingredients and reductions do not themselves establish literature novelty.
