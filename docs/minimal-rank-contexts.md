# The minimum background needed to preserve a rank reward

The [two-background reduction](rank-context-compression.md) extends beyond
quartets. For any reward on selected focal labels, its changes between
successive cardinalities determine the exact minimum number of deterministic
background clocks needed to preserve it for **every** focal score vector.
This note proves that statement, then applies it to harmonic multilinear
rewards using established algebra.

This is a pathwise preservation result. It does not claim that every focal
probability law needs that many backgrounds to witness a negative expectation.
The elementary rank argument and harmonic preliminaries are not claimed as
new techniques. Priority of the precise combined formulation is unresolved.

## Model and active ranks

Let `h` be any real function on subsets of `d≥1` focal labels. For finite
focal scores `x` and finite background scores `z_1≥⋯≥z_s`, write
`A_k(x,z)` for the focal labels among the largest `k` combined scores.
Here `0≤k≤d+s`. Exclude focal/background ties; ties within either group
are allowed, with a fixed focal-label priority.

For a given focal ordering `i_1,…,i_d`, let `S_j={i_1,…,i_j}`.
Every selected focal set is a prefix of this ordering. Extend the background
values by `z_j=+∞` for `j≤0` and `z_j=−∞` for `j>s`. Then

\[
 i_j\in A_k(x,z)\quad\Longleftrightarrow\quad x_{i_j}>z_{k-j+1}. \tag{1}
\]

Indeed, exactly `j−1` focal labels precede `i_j`; it is selected precisely
when at most `k−j` backgrounds precede it. The padding includes always
selected and always excluded ranks.

Call rank `j` **active** if some `S` with `|S|=j−1` and some `i∉S`
satisfy `h(S)≠h(S∪{i})`. Let `R(h)` be these ranks. In the original
context, the focal cardinality lies between

\[
 a=\max(0,k-s),\qquad b=\min(d,k).
\]

Only the transitions `a+1,…,b` can vary. Put
`T=R(h)∩{a+1,…,b}`.

## An exact minimum theorem

**Theorem 1.** Among all finite deterministic background multisets `W` and
all horizons `r` preserving

\[
 h(A_k(x,z))=h(A_r(x,W)) \tag{2}
\]

for every finite focal vector avoiding cross-ties, the smallest number of
background entries is

\[
 M(h;k,s)=
 \begin{cases}
 0,&T=\varnothing,\\
 \max T-\min T+1,&T\ne\varnothing.
 \end{cases} \tag{3}
\]

Replacement values and horizon may depend on `h,z,k`, but must be fixed
before varying the focal vector. The formula counts entries with their
multiplicities, including when several background values are equal.

**Proof of achievability.** If `T` is empty, use no backgrounds and horizon
`a`. Every edge along the focal prefix chain from `S_a` to the original
selected set is inactive, so the reward agrees.

Otherwise let `L=min T`, `U=max T`. Retain the consecutive background
entries

\[
 W=(z_{k-U+1},\ldots,z_{k-L+1}),\qquad r=U. \tag{4}
\]

All their indices lie in `1,…,s`. For each focal rank `j∈[L,U]`, its
reduced threshold is `W_(U−j+1)=z_(k−j+1)`, exactly (1). If the original
focal cardinality is `c`, the new one is therefore
`min(U,max(L−1,c))`. The selected labels remain the corresponding prefix.
Every traversed edge outside `[L−1,U]` is inactive in the original feasible
range `[a,b]`, so the reward is unchanged.

**Proof of the lower bound.** Suppose a replacement has `n` entries and
horizon `r`. Choose any `j∈T` and an edge `(S,S∪{i})` witnessing its
activity. Put all labels of `S` above every original and replacement
background, and all remaining focal labels except `i` below every background.
Vary `x_i`, keeping its focal rank `j` fixed, across the finite value
`v=z_(k−j+1)`. The original reward has a nonzero jump there. This remains
true with background ties; values on either side of `v` suffice.

The replacement must have the same nonzero jump. A focal label of rank
`j` can change membership there only if

\[
 1\le r-j+1\le n,\qquad W_{r-j+1}=v. \tag{5}
\]

Using the largest and smallest active feasible ranks in these bounds gives
`r≥max T` and `n≥r−min T+1≥max T−min T+1`. This lower bound allows
arbitrary real replacement values; it does not assume they are a subset of
the original values. ∎

The relevant quantity is the **span** of active ranks, not their count.
For example, in eight focal labels let `h(A)=1` exactly when `|A|` is two
or six. Its active ranks are `{2,3,6,7}`. If the context permits them all,
six background entries are necessary. In contrast, `h(A)=1{|A|≥p}` has
only rank `p` active and needs at most one background. A constant needs none.

## Rewards supported on a range of cardinalities

Suppose `h(A)=0` unless `p≤|A|≤q`, with `0<p≤q<d`. Keeping

\[
 W=(z_{k-q},\ldots,z_{k-p+1})
\]

and selecting the top `q+1` from the focal scores and these `q−p+2`
backgrounds preserves the reward. The same threshold argument clips the
focal cardinality to `[p−1,q+1]`, leaving every potentially nonzero reward
unchanged. Delete each padded `+∞` and lower the horizon by one; delete
each padded `−∞` without changing the horizon. This gives an ordinary
finite context with at most that many backgrounds.

If `p,q` are the actual smallest and largest nonzero support cardinalities,
ranks `p` and `q+1` are active. A context with `s=q−p+2,k=q+1` makes
them both feasible, so Theorem 1 proves this uniform bound is sharp for
every such reward. Equal background values do not lower it. Endpoint support
at zero or `d` and special constant regions are handled by (3), which can
give smaller bounds than a declared support range.

## Harmonic rewards and the degree that matters

A multilinear polynomial is harmonic here when `Σ_i∂_iP=0`. This is the
standard slice-analysis definition; its representation theory is prior art.
See [Filmus and Mossel, §3.1](https://yuvalfilmus.cs.technion.ac.il/Papers/2slice.pdf),
which also credits earlier work of Dunkl.

Let `P` be a nonzero homogeneous harmonic multilinear polynomial of degree
`r≥1`, and put
`h(A)=P(1_A)`. Multilinearity and homogeneity make it zero when `|A|<r`.
Harmonicity gives `P(x+t1)=P(x)` by differentiating in `t`, hence

\[
 P(1-x)=P(-x)=(-1)^rP(x).
\]

Complementation therefore makes it zero also when `|A|>d−r`. Some degree
`r` monomial coefficient is nonzero; evaluating on that monomial's label set
shows that the lower support boundary is actually attained. Complementation
gives the upper boundary too. Thus `r≤d/2`, and the sharp uniform pathwise
count and one fixed reduced horizon are

\[
 \boxed{d-2r+2\ \text{backgrounds},\qquad d-r+1\ \text{survivors}.} \tag{6}
\]

The quartet's quadratic rewards have `d=4,r=2`, giving two backgrounds.
A homogeneous quadratic harmonic on five focal labels needs three in the worst context;
on six labels it needs four. Pure degree `d/2` in even dimension always
has a two-background reduction.

Homogeneity matters. In four variables,

\[
 P(x)=(x_1-x_2)(1+x_3-x_4)
\]

is harmonic with maximum degree two, but its actual support includes sizes
one and three. All four transition ranks are active, so four backgrounds
are needed in a context making them feasible. For a mixed harmonic
polynomial, subtract its constant and use the **lowest nonzero homogeneous
degree** `r₀` in (6). Each homogeneous component is harmonic. Higher-degree
terms vanish on both boundary layers of the lowest component, so they
cannot cancel its support extremes. Subtracting a constant changes no
active edge.

## Expected signs and what sharpness does not say

For a random focal vector with atomless marginals, jointly independent of
its background, the pathwise equalities may be conditioned and averaged.
For support in `[p,q]` as above, universal nonnegativity is equivalent to
testing every deterministic `q−p+2`-background multiset at horizon `q+1`.
Infinite endpoints follow by bounded convergence. Strict negative witnesses
persist under sufficiently narrow independent continuous backgrounds.

For a pure harmonic reward, (6) therefore supplies a sufficient test size.
The corresponding result for a mixed harmonic follows by subtracting its
constant, preserving pathwise values, and adding the constant back.

The lower bound proves optimal **pathwise preservation**, not optimal
negative-witness size for a particular probability law. For example, under
an exchangeable focal law without ties, conditional on focal cardinality the
selected labels are uniform. A positive-degree homogeneous harmonic has
zero mean on every such layer: every degree-`r` monomial has the same
average and the coefficient sum is `P(1)=0`. Hence its expected reward is
zero in every independent background. That law has no negative witness at
all. The [ordered quartet construction](rank-context-compression.md)
supplies a separate sharpness argument for expected signs; no such argument
is asserted here for every higher degree or dimension.

## Independent finite checks

```sh
python3 -m research.spikes.context.support_width
```

The standalone verifier imports no probability or threshold-formula module.
It compares directly sorted selections across 3,915,366 support/endpoint
cases, with one to six focal labels and up to six backgrounds on three
levels. It includes all horizons, support endpoints, and repeated backgrounds.

A second check enumerates all 256 Boolean rewards on three labels, 364
contexts and 336 focal order cells. Function signatures from direct sorting
give 93,184 comparisons of the true minimum within that finite family to
(3), including arbitrary replacement contexts from the five-level family.
The real-valued unrestricted lower bound comes from the proof, not the finite
enumeration. Twenty harmonic products and the mixed-degree counterexample
check the stated support calculations.

This generalization was developed by an independent bounded worker and
reviewed separately from its implementation. It extends the research beyond
pair rewards, without asserting a new harmonic representation theorem or
an advantage in model inference cost.
