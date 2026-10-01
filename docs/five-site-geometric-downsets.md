# A bound for geometric weights on downward-closed sets

For the geometric weights defined below on any nonempty finite coordinate downset, the reflected-to-forward max-convolution ratio is at most

$$
\frac QP\le 2-\frac{26}{13981}=\frac{27936}{13981}<2.
$$

A coordinate downset contains every nonnegative lattice point below each of its points, coordinate by coordinate. This includes boxes, simplex cutoffs, and irregular staircases. Future searches for a ratio above two can exclude this family with the weight rule below.

The same bound holds for the proof's intermediate upper estimate of $Q$. This stronger statement also excludes the family from the [unresolved proof condition](five-site-geometric-family.md#the-remaining-proof-condition), which concerns the unused margin in that estimate.

The [coordinate decay extension](#weights-that-decrease-at-every-coordinate-step) allows more general heights: each positive coordinate step may multiply the input height by any factor at most $5/9$. Decomposing these inputs into nested geometric layers gives the same bound and proof-condition exclusion.

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

## The intermediate proof estimate also stays below two

Let $q_+$ be the fixed convex, positively homogeneous function in the five-site profile proof, with coefficients

$$
A=\frac{77}{47},\qquad B=\frac{67}{94},\qquad
\beta=\frac{19}{141},\qquad C=\frac{68768}{34263}.
$$

For $v(x)=(f(x),rf(x-e_1),\ldots,rf(x-e_4))$, write

$$
T=\sum_xq_+(v(x)),\qquad \Delta=CP-T.
$$

The paper's tree inequality and translation identity give $Q\le T$. The [retained-slack identity](five-site-geometric-family.md#the-remaining-proof-condition) identifies $\Delta$ with $\lambda R+\sigma Z+S+L$; the geometric-family note calls this quantity $D$. Here $D$ continues to denote the support. We will prove

$$
T<(2-\varepsilon)P,\qquad
\Delta>(C-2+\varepsilon)P,\qquad
\varepsilon=\frac{26}{13981}.
$$

Let $W_j$ be the mass of points of $D$ with exactly $j$ positive coordinates. Then $W_0=1$ and $m=\sum_{j=0}^4W_j$. On $D$, a forward vector has the root and exactly those $j$ leaves present. Outside $D$, it has no root and $k(x)$ leaves. All its positive entries agree.

For an indicator vector, the paper gives $q_+=A+2\beta j-\beta\binom j2$ when the root is present and $q_+=Bj-\beta\binom j2$ otherwise. Thus the complete nonempty row calculation is

| Number of leaves $j$ | $0$ | $1$ | $2$ | $3$ | $4$ |
| --- | --- | --- | --- | --- | --- |
| $282(2-q_+)$, root present | $102$ | $26$ | $-12$ | $-12$ | $26$ |
| $282(2-q_+)$, root absent | Empty vector | $363$ | $200$ | $75$ | $-12$ |

The empty vector contributes zero. Set

$$
I=102W_0+26(W_1+W_4)-12(W_2+W_3).
$$

Summing the rows gives the exact identity

$$
282(2P-T)=I+363U_1+200U_2+75U_3-12U_4.
$$

### Control the interior by coordinate projection

Put $t=r/(1-r)=5/4$. For a coordinate subset $J$, let $M_J$ be the mass of points whose positive coordinates are exactly $J$. If $i\in J$, setting coordinate $i$ to zero maps into the section with support $J\setminus\{i\}$. The positive fiber above each projected point has total weight at most $(r+r^2+\cdots)=t$ times its projected weight. Hence $M_J\le tM_{J\setminus\{i\}}$.

Sum over all size-$j$ subsets $J$ and all $i\in J$. Each size-$j$ section occurs $j$ times, and each size-$(j-1)$ section has $5-j$ possible added coordinates. Therefore

$$
jW_j\le(5-j)tW_{j-1},\qquad 1\le j\le4.
$$

The normalized masses $b_j=W_j/(\binom4j t^j)$ satisfy $1=b_0\ge b_1\ge\cdots\ge b_4\ge0$. Set $b_5=0$. The coefficients $b_s-b_{s+1}$ are nonnegative and sum to one, so $(m,I)$ is a convex combination of the pairs obtained by setting $b_j=1$ for $j\le s$ and zero otherwise:

| Last included index $s$ | $m_s$ | $I_s$ | $I_s/m_s$ |
| --- | --- | --- | --- |
| $0$ | $1$ | $102$ | $102$ |
| $1$ | $6$ | $232$ | $116/3$ |
| $2$ | $123/8$ | $239/2$ | $956/123$ |
| $3$ | $371/16$ | $103/4$ | $412/371$ |
| $4$ | $6561/256$ | $11421/128$ | $94/27$ |

The smallest ratio is $412/371$. Consequently

$$
I\ge\frac{412}{371}m,\qquad
\frac I{282}\ge dm,\qquad d=\frac{206}{52311}.
$$

This argument uses a relaxation of the possible section masses; it does not require a finite downset realizing each row.

### Combine the interior and boundary bounds

The antichain count already proved $m\ge aU_4$, where $a=13356/625$. These constants satisfy

$$
ad-\frac2{47}=\frac{26}{625}=(a+1)\varepsilon.
$$

Substituting this identity into the exact certificate gap gives

$$
\begin{aligned}
(2-\varepsilon)P-T
={}&\left(\frac I{282}-dm\right)
+(d-\varepsilon)(m-aU_4)\\
&+\left(\frac{121}{94}-\varepsilon\right)U_1
+\left(\frac{100}{141}-\varepsilon\right)U_2
+\left(\frac{25}{94}-\varepsilon\right)U_3.
\end{aligned}
$$

Every term is nonnegative: the first two use the interior and antichain bounds, and $a(d-\varepsilon)=2/47+\varepsilon>0$. The three remaining coefficients are positive. Since $U_1>0$ for a nonempty finite downset, the inequality is strict. This proves the stronger estimate and, by $\Delta=CP-T$, the stated lower bound on the unused margin.

In particular, $\Delta>(C-2)P$. The family cannot satisfy the second inequality defining the unresolved proof condition, regardless of the first. This conclusion uses the bound on $T$ directly; the earlier bound on $Q$ alone would not establish it.

## Weights that decrease at every coordinate step

Keep the five sites and their weights $1,r,r,r,r$ fixed, with $r=5/9$. Let $f$ be a nonzero, nonnegative, finitely supported function on $\mathbb Z_{\ge0}^4$ satisfying

$$
f(x+e_i)\le r f(x)\qquad
(x\in\mathbb Z_{\ge0}^4,\ 1\le i\le4).
$$

Extend $f$ by zero outside this orthant. The decay condition is imposed only inside the orthant. Then, with $c=2-26/13981$,

$$
Q(f)\le T(f)<cP(f),\qquad
\Delta(f)>\left(C-2+\frac{26}{13981}\right)P(f).
$$

Thus these inputs also lie outside the unresolved proof condition.

To prove this, put $h(x)=r^{-|x|}f(x)$ on the nonnegative orthant. The decay condition makes $h$ nonincreasing in each coordinate. List its distinct positive values as $0<t_1<\cdots<t_s$, put $t_0=0$ and $a_j=t_j-t_{j-1}>0$, and define

$$
D_j=\{x:h(x)\ge t_j\},\qquad
f_j(x)=r^{|x|}1_{D_j}(x).
$$

Each $D_j$ is a finite nonempty coordinate downset, and the sets are nested. The finite layer decomposition is

$$
f=\sum_{j=1}^s a_jf_j.
$$

For these layers the forward sum is exactly additive. To see why, write

$$
v^+(u,x)=\bigl(u(x),ru(x-e_1),\ldots,ru(x-e_4)\bigr).
$$

For $x$ in the nonnegative orthant, this vector for $f$ equals $r^{|x|}$ times $(h(x),h(x-e_1),\ldots,h(x-e_4))$, taking $h=0$ at arguments outside the orthant. A coordinate maximizing these five values also maximizes their five membership indicators at every level $t_j$. Consequently

$$
\max_i v_i^+(f,x)
=\sum_{j=1}^s a_j\max_i v_i^+(f_j,x).
$$

If $x$ has a negative coordinate, all forward entries vanish and the equality still holds. Summing proves $P(f)=\sum_j a_jP(f_j)$.

The intermediate estimate is subadditive. In the [profile proof](../papers/four-point-covering/five-site-profile.tex), $W$ is a nonnegative weighted sum of minima of linear forms, so it is concave and positively homogeneous. The linear form minus $W$ defining $q_+$ is therefore convex and positively homogeneous. It follows that

$$
q_+\left(\sum_j a_jv_j\right)\le\sum_j a_jq_+(v_j),
\qquad
T(f)\le\sum_j a_jT(f_j).
$$

Apply the strict downset estimate to every layer:

$$
T(f)\le\sum_j a_jT(f_j)
<c\sum_j a_jP(f_j)=cP(f).
$$

The inequality is strict because there are finitely many nonempty layers, each with positive coefficient. The established inequality $Q\le T$ and the identity $\Delta=CP-T$ give the two conclusions.

The condition includes two useful subfamilies:

- The [box with reduced interior weights](five-site-geometric-family.md) has $h=1$ on its coordinate boundary, $h=\theta$ inside, and $h=0$ outside, where $0\le\theta\le1$. Its separate argument gives the stronger estimate $\Delta\ge(19/1269)P$, or $T\le(2-271/34263)P$.
- On any finite nonempty coordinate downset $D$, the weights $f(x)=a_0\prod_{i=1}^4s_i^{x_i}1_D(x)$ qualify whenever $a_0>0$ and $0<s_i\le5/9$. The signal may decay at different rates in the four directions; the five profile weights remain $1,5/9,5/9,5/9,5/9$.

## Integer inputs and use in the discovery loop

Let $L$ be the largest coordinate occurring in the support of $f$, choose $B=2L+5$, and encode $x$ as $\sum_{i=1}^4x_iB^{i-1}$. This map is injective on $\{-1,\ldots,L+1\}^4$. At the highest differing digit $j$, the leading contribution has absolute value at least $B^j$, while the lower contributions have total absolute value at most

$$
(L+2)\sum_{i=0}^{j-1}B^i=\frac{B^j-1}{2}<B^j.
$$

This box contains the support and all one-step outputs. The encoding therefore preserves every forward and reflected vector, $P$, $Q$, $T$, and $\Delta$ on the integer sites $0,1,B,B^2,B^3$. For the coordinate decay extension, choose this single base from the largest layer $D_1$ and use it for every layer. The sites may vary with the support.

The bounds apply to these injectively encoded inputs under the coordinate decay condition, including common positive scalings. They let the [discovery loop](discovery-loop.md) exclude the class both from searches for $Q>2P$ and from the unresolved proof condition. Within this representation, a new candidate must have at least one step with $f(x+e_i)>(5/9)f(x)$. Inputs with other geometries or encodings that merge outputs require separate arguments.
