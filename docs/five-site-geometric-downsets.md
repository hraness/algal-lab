# A bound for geometric weights on downward-closed sets

For the geometric weights defined below on any nonempty finite coordinate downset, the reflected-to-forward max-convolution ratio is at most

$$
\frac QP\le 2-\frac{26}{13981}=\frac{27936}{13981}<2.
$$

A coordinate downset contains every nonnegative lattice point below each of its points, coordinate by coordinate. This includes boxes, simplex cutoffs, and irregular staircases. Future searches for a ratio above two can exclude this family with the weight rule below.

This note concerns the [five-site profile](../papers/four-point-covering/five-site-profile.tex) with weights proportional to $9:5:5:5:5$. It does not determine the general five-site constant, the optimal bound within this family, or historical priority. The proof uses the standard Boolean antichain inequality; its random-chain argument is included.

## The family and its boundary

Let $D$ be a nonempty finite subset of $\mathbb Z_{\ge0}^4$ such that $x\in D$ and $0\le z_i\le x_i$ for every $i$ imply $z\in D$. Put $r=5/9$, $|x|=x_1+x_2+x_3+x_4$, and

$$
f(x)=r^{|x|}1_D(x).
$$

Use sites $0,e_1,e_2,e_3,e_4$, with weights $1,r,r,r,r$. The two sums are

$$
P=\sum_x\max\{f(x),rf(x-e_1),\ldots,rf(x-e_4)\},
\qquad
Q=\sum_x\max\{f(x),rf(x+e_1),\ldots,rf(x+e_4)\}.
$$

Write $m=\sum_{x\in D}r^{|x|}$. For each point $y\notin D$ reached by a forward shift, let $k(y)$ be the number of its immediate predecessors $y-e_i$ in $D$, and define

$$
U_j=\sum_{\substack{y\notin D\\k(y)=j}}r^{|y|},\qquad 1\le j\le4.
$$

All active forward values at a point agree, so

$$
P=m+U_1+U_2+U_3+U_4.
$$

For direction $i$, let $F_i$ be the mass of the face $\{x\in D:x_i=0\}$, and let $E_i$ be the mass of outside points whose predecessor in direction $i$ belongs to $D$. Each nonempty coordinate fiber starts at zero and has no gaps. Telescoping its geometric series gives

$$
F_i=(1-r)m+E_i,\qquad \sum_iE_i=\sum_{j=1}^4jU_j.
$$

In the reflected sum, the root dominates on $D$. Every other output has exactly one coordinate equal to $-1$ and comes from the corresponding face. Therefore

$$
Q=m+r\sum_iF_i
=\frac{161}{81}m+r\sum_{j=1}^4jU_j.
$$

Subtracting yields

$$
2P-Q=\frac m{81}+\frac{13}{9}U_1+\frac89U_2+\frac13U_3-\frac29U_4.
$$

Only the boundary points with all four predecessors can make a negative contribution. The next step bounds their total mass.

## A bound on the four-predecessor boundary

Let $\mathcal C=\{y\notin D:k(y)=4\}$. Every point of $\mathcal C$ is a minimal excluded point: every smaller nonnegative point lies in $D$. Thus no two points of $\mathcal C$ are comparable coordinate by coordinate. Also, for every nonempty $S\subseteq\{1,2,3,4\}$,

$$
y-1_S\in D\quad\text{when }y\in\mathcal C,
$$

where $1_S$ has coordinate one on $S$ and zero elsewhere.

Fix $x\in D$. The subsets $S$ with $x+1_S\in\mathcal C$ form an antichain: none contains another. Choose a uniformly random ordering of the four coordinates and consider its nested initial segments. A given subset of size $j$ is one of these segments with probability $1/\binom4j$. A chain meets an antichain at most once, so

$$
\sum_{\substack{\varnothing\ne S\subseteq\{1,2,3,4\}\\x+1_S\in\mathcal C}}
\frac1{\binom4{|S|}}\le1.
$$

Multiply by $r^{|x|}$ and sum over $x\in D$. Counting the same pairs from $y\in\mathcal C$ gives

$$
m\ge \sum_{y\in\mathcal C}r^{|y|}
\sum_{j=1}^4r^{-j}
=aU_4,\qquad
a=\frac{13356}{625}.
$$

Set $\varepsilon=(a-18)/(81(a+1))=26/13981$. The norm identity now factors as

$$
\begin{aligned}
(2-\varepsilon)P-Q
={}&\left(\frac1{81}-\varepsilon\right)(m-aU_4)\\
&+\left(\frac{13}{9}-\varepsilon\right)U_1
+\left(\frac89-\varepsilon\right)U_2
+\left(\frac13-\varepsilon\right)U_3\ge0.
\end{aligned}
$$

All displayed coefficients are positive. This proves the stated bound. It is strict for each nonempty finite $D$, because each coordinate axis ends in an outside point with exactly one predecessor, so $U_1>0$. For $D=\varnothing$, both sums are zero.

## Integer inputs and use in the discovery loop

Let $L$ be the largest coordinate occurring in $D$, choose $B=2L+5$, and encode $x$ as $\sum_{i=1}^4x_iB^{i-1}$. This map is injective on $\{-1,\ldots,L+1\}^4$. At the highest differing digit $j$, the leading contribution has absolute value at least $B^j$, while the lower contributions have total absolute value at most

$$
(L+2)\sum_{i=0}^{j-1}B^i=\frac{B^j-1}{2}<B^j.
$$

This box contains the support and all one-step outputs. The encoding therefore preserves $P$ and $Q$ on the integer sites $0,1,B,B^2,B^3$.

The bound applies to these injectively encoded supports with the specified geometric weights. It lets the [discovery loop](discovery-loop.md) avoid searching their shapes for $Q>2P$.

The [interior-attenuation note](five-site-geometric-family.md) addresses a different question: whether a family can enter an unresolved region in the published proof. This ratio bound does not exclude that region, which also depends on the slack in the proof's intermediate inequalities.
