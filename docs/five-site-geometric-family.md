# A rejected geometric family for the five-site problem

Reducing the interior weights of a geometric box does not reach the unresolved region in the current five-site proof. The argument below covers every finite box size and every uniform interior multiplier between zero and one. Future runs can exclude this whole family before allocating a parameter search.

This is a scoped follow-up to the [five-site profile proof](../papers/four-point-covering/five-site-profile.tex), published in [V11](https://github.com/hraness/algal-lab/releases/tag/sum-difference-results-20260930-v11). It leaves the general five-site constant and historical novelty unresolved. It does not establish a measured improvement in the discovery strategy.

## The remaining proof condition

Use the paper's five distinct sites, with root weight one and four leaf weights $r=5/9$. Its forward and reflected max-convolution sums are $P$ and $Q$. Write $R$ for the sum of the four nonnegative resolvent surpluses and $Z$ for the sum of the envelope losses when each leaf is deleted.

Let $S$ be the sum over $x$ of the integrated, coefficient-weighted slack in the paper's indicator table after retaining the $\sigma Z$ term. Let $L$ be the sum over $x$ of the nonnegative gap between the indicator-layer integral of $q_+$ and $q_+$ itself. Retaining these terms in the published proof gives

$$
Q\le CP-\lambda R-\sigma Z-S-L,
\qquad Q\le\alpha P+\tau R+r^2Z,
$$

where

$$
C=\frac{68768}{34263},\quad \lambda=\frac{19}{188},\quad
\sigma=\frac{125}{94}-\frac{304}{34263}>1,\quad
\alpha=\frac{161}{81},\quad \tau=\frac{405}{64}.
$$

Define $D=\lambda R+\sigma Z+S+L$. By the definitions of the two retained slacks,

$$
D=CP-\sum_x q_+\bigl(g_i f(x-h_i)\bigr).
$$

A sufficient route to $Q\le2P$ would exclude every realizable finite input satisfying both

$$
\tau R+r^2Z>(2-\alpha)P,
\qquad D<(C-2)P.
$$

This exclusion is unproved in general. An input inside the region would defeat this proposed proof condition; it would not by itself imply $Q>2P$.

## The family

Work first on $\mathbb Z^4$, with sites $0,e_1,e_2,e_3,e_4$. For an integer $N\ge1$, let

$$
f_N^{\mathrm{full}}(x)=r^{x_1+x_2+x_3+x_4}\,1_{\{0,\ldots,N\}^4}(x).
$$

Let $f_N^{\mathrm{boundary}}$ agree with this function where at least one coordinate is zero and vanish elsewhere. For $0\le\theta\le1$, define

$$
f_{N,\theta}=(1-\theta)f_N^{\mathrm{boundary}}+\theta f_N^{\mathrm{full}}.
$$

Thus boundary values stay fixed while every interior value is multiplied by $\theta$. **Every member satisfies $D\ge(19/1269)P>(C-2)P$**, so none lies in the displayed region.

## Endpoint estimates

Put $s=\sum_{j=0}^N r^j$, $w=r^{N+1}$, and $u=s-1-r$. All nonzero entries of an endpoint's forward vector are equal. In particular, $L=0$ at both endpoints.

For the boundary endpoint, counting the positions reached by exactly one leaf gives

$$
P_{\mathrm b}=s^4-u^4+4w\bigl[s^3-(s-1)^3\bigr],\qquad
Z_{\mathrm b}=4ru^3+4w\bigl[s^3-(s-1)^3\bigr].
$$

The first term of $Z_{\mathrm b}$ counts one coordinate equal to one and the other three between two and $N$. The second counts the four outer faces. The infinite boundary function dominates every finite one and has forward sum $(1-r^8)/(1-r)^4$, so $P_{\mathrm b}$ is at most this value. Direct expansion gives

$$
\frac{(1-r)^3Z_{\mathrm b}}4
=r^7+(1-r^3-3r^5)w+3(r^3+r^2-1)w^2+(3-4r)w^3.
$$

Since $0<w\le r^2$, the nonconstant part is at least
$(1-3r^2-r^3+3r^4)w=(412/2187)w>0$. It follows that

$$
\frac{D_{\mathrm b}}{P_{\mathrm b}}
\ge\sigma\frac{Z_{\mathrm b}}{P_{\mathrm b}}
>\frac{4r^7(1-r)}{1-r^8}>\frac1{36}.
$$

The last comparison uses $r^7>1/64$ and $1-r=4/9$.

For the full endpoint, put $t=s-1\ge r>1/2$ and $\beta=19/141$, as in the paper. The only positive-slack forward indicator rows have the root with one leaf or with four leaves. Their respective coefficients are $\beta/4$ and $\beta$, giving

$$
S_{\mathrm f}=\beta(t+t^4),\qquad
Z_{\mathrm f}=4ws^3,\qquad P_{\mathrm f}=s^4+Z_{\mathrm f}.
$$

The identity

$$
9(t+t^4)-(1+t)^4=(2t-1)^3(t+1)\ge0
$$

implies $S_{\mathrm f}\ge(\beta/9)s^4$. Since $R\ge0$ and $\sigma>1>\beta/9$,

$$
D_{\mathrm f}\ge S_{\mathrm f}+\sigma Z_{\mathrm f}
\ge\frac{\beta}{9}P_{\mathrm f}=\frac{19}{1269}P_{\mathrm f}.
$$

## Interpolation and integer realization

At each position, the boundary forward vector contains either none or a subset of the full vector's equal positive entries. Its maximum is therefore either zero or the full maximum. This proves the exact identity

$$
P(f_{N,\theta})=(1-\theta)P_{\mathrm b}+\theta P_{\mathrm f}.
$$

The paper's $q_+$ is convex. The identity defining $D$ then gives

$$
D(f_{N,\theta})\ge(1-\theta)D_{\mathrm b}+\theta D_{\mathrm f}
\ge\frac{19}{1269}P(f_{N,\theta}).
$$

Here $1/36>19/1269>242/34263=C-2$. The optional case $N=0$ is a singleton at both endpoints, with $P=1+4r$ and $Z=4r$, and satisfies the same conclusion directly.

For a finite $N$, encode $x$ as $\sum_{i=1}^4x_i B^{i-1}$ with $B=2N+3$. This map is injective on $\{-1,\ldots,N+1\}^4$: the largest differing digit dominates the sum of all smaller digits. It preserves both max-convolution arrays, the deleted-leaf envelopes, and the pointwise slacks. Thus the exclusion also applies to finite integer inputs, with sites $0,1,B,B^2,B^3$ that vary with $N$.

## Use in the discovery loop

Retain this family as a rejected approach and a control for any future evaluator. A new attempt at the unresolved region must change the family, such as its support or the relative weights within the interior, and state why that change could evade the estimate above. The related [downset bound](five-site-geometric-downsets.md) also excludes all finite downward-closed supports with unaltered geometric weights from achieving $Q>2P$. Reserve any evaluation under the campaign's existing allowance and independently review the mathematics before execution. See the [discovery loop guide](discovery-loop.md) for recovery, budgets, and publication.
