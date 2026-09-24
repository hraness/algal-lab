# Sharp softmax ordering on a fixed-total simplex

Let `B_τ(x)=Σ_i x_i exp(τx_i)/Σ_i exp(τx_i)`, and restrict its inputs to
`Δ_n(S)={x∈[0,∞)^n: Σ_i x_i=S}`, where `S>0` and `n≥3`.
Unlike a box, this domain gives different sharp thresholds for the two signs
of temperature. The result below is independently proved; its literature
priority remains unresolved in the [novelty ledger](novelty-ledger.md).

## Exact classification

Define the positive roots

\[
 (n-2)(c_n-2)e^{c_n}=4,\qquad
 (d_n-2)e^{d_n}=2(n-1).
\]

Equivalently,
`c_n=2+W_0(4/((n−2)e²))` and
`d_n=2+W_0(2(n−1)/e²)`. With `K=|τ|S`:

- For `τ>0`, `B_τ` is Schur-convex on `Δ_n(S)` if and only if `K≤d_n`.
- For `τ<0`, `B_τ` is Schur-concave on `Δ_n(S)` if and only if `K≤2c_n`.
- Both valid regimes are strict modulo permutations, including equality.
  Above the relevant cutoff, the function has neither Schur property.

For `n=2`, the appropriate strict order holds at every nonzero temperature.
For `τ=0`, the value is constantly `S/n` and both non-strict properties hold.
Here majorization compares decreasing prefix sums with equal totals.

The [box theorem](sharp-softmax-spread.md) uses one cutoff `c_n` for both
signs because reflection maps a box to itself. Reflection does not preserve
this fixed-total nonnegative simplex, so that argument does not equate the
two regimes here.

## The sign comparison changes at dimension 58

The positive cutoff `d_n` strictly increases with `n`, whereas the negative
cutoff `2c_n` strictly decreases. The exact root certificates give these
strict, deliberately wider decimal enclosures:

| `n` | Positive cutoff `d_n` | Negative cutoff `2c_n` |
|---:|---:|---:|
| 3 | `(2.372856, 2.372857)` | `(4.745712, 4.745713)` |
| 4 | `(2.494985, 2.494986)` | `(4.435430, 4.435431)` |
| 8 | `(2.827909, 2.827910)` | `(4.166068, 4.166070)` |
| 32 | `(3.635304, 3.635306)` | `(4.035455, 4.035456)` |
| 57 | `(4.016924, 4.016925)` | `(4.019494, 4.019495)` |
| 58 | `(4.028769, 4.028770)` | `(4.019149, 4.019150)` |
| 128 | `(4.586881, 4.586882)` | `(4.008556, 4.008557)` |

In particular, `d_57<2c_57` and `d_58>2c_58`. Monotonicity then proves
that negative temperature permits the larger `|τ|S` range for every
`3≤n≤57`, and positive temperature permits the larger range for every
`n≥58`. This conclusion uses rational enclosures with certified endpoint
signs, not a floating-point root comparison.

## Positive temperature

Scale to `u=τx`, so `Σu_i=K` and `B_τ(x)=H(u)/τ`, where `H=B_1`.
Put `Z=Σexp(u_i)` and `p_i=exp(u_i)/Z`. Nonnegativity gives

\[
 p_i\le\frac{e^{u_i}}{e^{u_i}+n-1}
      \le\frac{e^K}{e^K+n-1},\qquad
 H(u)\le\frac{K e^K}{e^K+n-1}. \tag{1}
\]

The final bound is attained at a vertex. Its right side increases with `K`
and is at most `2` exactly when `K≤d_n`.

At a fixed vector,
`∂_iH=exp(u_i)(1+u_i−H)/Z`. When `H≤2`, the scalar function
`f(s)=exp(s)(1+s−H)` has derivative `exp(s)(2+s−H)≥0` for `s≥0`.
The integral over any interval `x<y` is strictly positive, even at `H=2`.
Thus `∂_yH>∂_xH` for unequal coordinates. Every genuine pair averaging
strictly decreases `H`. Such operations preserve the simplex, proving
strict Schur-convexity without requiring the domain to have an ambient
full-dimensional interior.

For necessity, suppose `K>d_n`. We give a finite violation strictly inside
the simplex. Set

\[
 \delta_0=\frac{K e^K}{e^K+n-1}-2>0,\qquad
 A=2(n-1)(K+1)+1,
\]
\[
 \varepsilon=\min\{K/(2n),\delta_0/(2A)\},\qquad
 v=(K-(n-1)\varepsilon,\varepsilon,\ldots,\varepsilon),
\]
\[
 z=\min\{\varepsilon/2,\sqrt{3\delta_0/2}\}.
\]

Replace two small coordinates of `v` by `ε−z,ε+z`, obtaining `v'≽v`.
Both vectors have positive entries and total `K`. Throughout the simplex,
`|∂_iH|≤K+1`. The displacement from the vertex to `v` has ℓ₁ norm
`2(n−1)ε`, so

\[
 H(v)-\varepsilon-2\ge\delta_0-A\varepsilon
                         \ge\delta_0/2. \tag{2}
\]

Let `E` be the sum of exponential weights outside the split pair. Direct
subtraction gives

\[
 H(v')-H(v)=\frac{2e^\varepsilon(\cosh z-1)}{E+2e^\varepsilon\cosh z}
 \left[\varepsilon-H(v)+z\coth(z/2)\right]. \tag{3}
\]

For `z>0`, `z coth(z/2)≤2+z²/6`. To see this, put `r=z/2` and
differentiate `(1+r²/3)sinh r−r cosh r`: its derivative is
`r(r cosh r−sinh r)/3>0`, with zero initial value. By (2), the bracket
in (3) is at most `−δ_0/2+z²/6≤−δ_0/4<0`.
Thus the more spread vector has a smaller value, proving necessity.
There are two small coordinates available precisely when `n≥3`.

## Negative temperature

Scale to `F=B_{−1}` on `Σu_i=K`, and write `m=n−2`.
The [box proof](sharp-softmax-spread.md#proof-of-the-sufficient-bound)
shows that for coordinates `x<y`, center `c=(x+y)/2` and half-spread
`z=(y−x)/2`, the numerator controlling `∂_xF−∂_yF` satisfies

\[
 \frac{N}{2e^{-c}\sinh z}
 =m(1-c+z\coth z)+2e^{-c}\left(\cosh z+\frac z{\sinh z}\right)
 >m(2-c)+4e^{-c}. \tag{4}
\]

The preliminary bound in that proof needs only nonnegative remaining
coordinates. Here `2c≤K`. If `K≤2c_n`, the last expression in (4) is
nonnegative; the strict inequality remains valid when `c=c_n`.
Hence every nontrivial pair averaging strictly increases `F`, proving
strict Schur-concavity, including at the threshold.

If `K>2c_n`, choose the following explicit interior vectors. Put

\[
 C=(K+2c_n)/4,\quad s=(K-2C)/n>0,\quad q=e^{-C},
\]
\[
 \eta=1-\frac{2(m+2q)}{mC}>0,\quad
 z=\min\{C/2,\sqrt{3\eta}\}.
\]

Compare `v=(s,…,s,s+C,s+C)` and
`v'=(s,…,s,s+C−z,s+C+z)`. They have positive coordinates, total `K`,
and `v'≽v`. Shift invariance and direct subtraction give

\[
 F(v')-F(v)=
 \frac{2q\{mC(\cosh z-1)-z\sinh z(m+2q)\}}
 {(m+2q\cosh z)(m+2q)}.
\]

Its numerator has the sign of

\[
 mC\frac{\tanh(z/2)}z-(m+2q)
 \ge\frac{mC\eta}{2}-\frac{mCz^2}{24}
 \ge\frac{3mC\eta}{8}>0.
\]

The inequality uses `tanh r≥r−r³/3`. This finite comparison proves necessity.

## Opposite orientations and exact examples

At the equal vector with coordinate `c=K/n`, a split `(c−z,c+z)` gives

\[
 B_{\pm1}(\text{split})
 =c\;\pm\;\frac{2z\sinh z}{n-2+2\cosh z}.
\]

For `0<z<c`, this excludes the opposite Schur property for each nonzero
sign. For two coordinates the formula is `c±z tanh z`; it gives the
unrestricted corresponding strict ordering.

Two violations can be checked with rational arithmetic on the unit simplex.
For `τ=8 log2`,

\[
 (3/4,1/4,0)\succeq(3/4,1/8,1/8),\qquad
 B_\tau(3/4,1/4,0)-B_\tau(3/4,1/8,1/8)
 =49/69-97/136=-29/9384.
\]

For `τ=−8 log2`,

\[
 (0,3/8,5/8)\succeq(0,1/2,1/2),\qquad
 B_\tau(0,3/8,5/8)-B_\tau(0,1/2,1/2)
 =17/296-1/18=5/2664.
\]

These are illustrative finite checks. Equations (2)–(4) establish the sharp
statements and interior failures at every temperature above the cutoffs.

## Reproduction and priority

```sh
python3 -m research.spikes.stochastic.simplex_spread
```

The [fixed verifier](../research/spikes/stochastic/simplex_spread.py) supplies
exact rational root enclosures and the two rational examples. It reuses
the box verifier's rational degree-48 Taylor bounds for `exp(x/2)` and
squares both endpoints to bound `exp(x)` for `2≤x≤6`. The positive-root
brackets have width `2^−24`; the `c_n` brackets also have width `2^−24`,
so the actual negative cutoffs `2c_n` have enclosure width `2^−23`.
The bisection checks both endpoint signs and the two separated intervals
that establish the crossover dimension. These finite enclosures support
the displayed constants; the analytic argument proves the full classification.

The investigating assistant proposed the formulas; an independent
reviewer checked both classifications and supplied the explicit finite
interior constructions. The implementation worker was given these formulas.
No small-model origination or token-efficiency claim follows from this work.

The source audit in the box note credits the earlier two-variable and
Lehmer-mean results. The expectation ratio is also an Esscher premium;
its ordering failures are established prior territory. The candidate
contribution here is the exact classification on a fixed-total simplex,
including the distinct sign-dependent constants and their strict boundaries.
The [novelty ledger](novelty-ledger.md) records the remaining comparisons.
