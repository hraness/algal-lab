# A bound below two for the five-site profile 9:5:5:5:5

For the prescribed five heights `9:5:5:5:5`, reflection increases the selected max-convolution total by a factor at most

$$
c_* = \frac{27936}{13981}=2-\frac{26}{13981}<2.
$$

The five positions can be any distinct integers. The other input can have arbitrary nonnegative finite heights, and translated outputs may overlap. A search for a reflected ratio above two must therefore change the prescribed profile.

## Exact statement

Let $H=\{h_0,h_1,h_2,h_3,h_4\}\subset\mathbb Z$ have five distinct elements, and let $f,g$ be nonzero, nonnegative and finitely supported. Suppose $g(h_0)=t>0$ and $g(h_i)=5t/9$ for $1\le i\le4$. Max-product convolution means $(f\star g)(s)=\max_x f(x)g(s-x)$, and reflection means $\widetilde u(s)=u(-s)$. Write $P=\|f\star g\|_1$ for the original total and $Q=\|f\star\widetilde{g1_H}\|_1$ for the selected reflected total. Then

$$
\frac QP\le c_*.
$$

The numerator uses only the five selected values. Values of $g$ outside $H$ are unrestricted and can only increase the full original denominator. The restriction is on these values of $g$, with kernel $1_H$; it is not a theorem for arbitrary kernel weights.

The [paper](../papers/four-point-covering/main.pdf) contains the complete proof under “A bound below two for a prescribed five-site profile”; its [TeX source](../papers/four-point-covering/five-site-boundary.tex) is also available.

## How the proof works

First place the five heights at $0,e_1,e_2,e_3,e_4$ in $\mathbb Z^4$, and write $P_0,Q_0$ for the corresponding original and reflected totals. Divide an arbitrary finite input by the geometric weight $(5/9)^{x_1+x_2+x_3+x_4}$, using the signed coordinate sum. Its finitely many height levels produce nested weighted sets. The original total adds exactly across the layers, while the reflected total is at most the sum of their reflected totals. No downward-closure or coordinate-decay assumption is needed.

For each set, count the forward and reflected outside boundaries, retaining their multiplicities. The potentially adverse forward points have all four immediate predecessors in the set. If such a point has every lower Boolean corner in the set, a random ordering of coordinate directions bounds its weight by the available interior weight. Otherwise, a missing corner forces several reflected translates to overlap. The reflected maximum counts that corner once; the excess multiplicity bounds the weight of incomplete corners. Combining these two counts proves the strict bound $Q_0<c_*P_0$ for every nonzero finite input on the free lattice.

To cover arbitrary integer sites, lift each residue class of the integer input to a large finite box in the kernel of the site map. The free-lattice forward and reflected totals, divided by the box size, converge separately to the corresponding integer totals for the selected profile $g1_H$. This transfers the uniform bound even when integer outputs overlap. The full denominator $P$ is at least the selected original total, so the limiting argument yields $Q\le c_*P$. It does not establish strictness against $c_*$ on the integers.

## What this changes in the search

The earlier certificate gives the larger uniform coefficient `3143504/1566459`, together with input-dependent corrections and a barrier for its specified family of comparisons. The new boundary proof improves the uniform coefficient by using relations outside that family. The certificate and its correction terms remain valid.

The [coordinate-decay note](five-site-geometric-downsets.md) controls a different object as well: an intermediate upper estimate used by a proposed proof. Under that note's decay and injective-encoding conditions, the estimate itself stays below $c_*P$. The arbitrary-input theorem here bounds the actual reflected total only. It does not show that the intermediate estimate, or its remaining proof condition, behaves the same way for arbitrary inputs.

Use the distinction when selecting another experiment:

- To seek an actual ratio above two, change the five prescribed heights or the number of sites. Changing the input shape, its heights, the five integer positions, or their additive relations while retaining `9:5:5:5:5` cannot succeed.
- To investigate the intermediate proof condition, retain its separate hypotheses. Within the coordinate representation of the decay note, a candidate must violate $f(x+e_i)\le(5/9)f(x)$ somewhere. Its actual reflected ratio can still be below two.

The exact optimum for this profile, the general five-site constant, and historical priority remain unresolved. The argument was developed and independently checked by Codex agents using retained sources and hand reasoning; this is AI review, not human peer review.
