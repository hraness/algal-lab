Take two short lists of numbers. Add every number in one list to every number in the other, keeping each distinct answer only once. Then repeat with subtraction. The two collections can have different sizes, even though the inputs have barely changed.

The laboratory proved an exact limit for a weighted version of this question when one input is restricted to four positions. Reflecting that input can increase the measured total by a factor approaching **seven quarters, or 1.75, but never more**. The matching lower examples and the upper proof establish the same number.[^1]

This is a small-support result inside a larger unsolved problem. Its value is a precise answer with a complete proof: it replaces a range of possible constants with one exact value. A later boundary argument also keeps the increase below a factor of two for one prescribed choice of five heights, regardless of their positions or the other input.

## From lists to overlapping signals

Think of a finite row of nonnegative heights. To combine two rows, slide one past the other. At each position, multiply the heights of each overlapping pair and keep the largest product. Add those maxima over all positions.

Mathematicians call this operation **max-convolution**. With rows containing only zeros and ones, it counts the distinct sums of the occupied positions. Reflecting one row turns sums into differences. The operation and its connection to sumsets belong to earlier work.[^2]

The theorem allows arbitrary nonnegative heights in the input signals. A separate *kernel* selects the positions to reflect and assigns their weights. Keeping those roles separate matters: a bound involving the kernel’s total weight cannot be used by substituting the total of a different signal.

![The sharp ratios for one, two, three and four sites are 1, 1.25, 1.5 and 1.75. Five sites have a lower bound of 2 and an upper bound of 2.1875.](/discoveries/figures/reflection-constants.svg)

*Solid points are exact suprema. The interval at five sites marks an unresolved gap, rather than an estimated answer.*

## Why the upper and lower answers meet

The upper proof starts from a counting identity. Count pairs of representations that give the same sum, and rearrange the same four entries: the count becomes one involving equal differences. A weighted form of this classical identity puts addition and subtraction into a common calculation.

That shared quantity limits how much the reflected total can grow. For four sites, an inequality involving four events and finite linear-programming duality supplies the final sharp estimate. The published argument is self-contained; this part does not depend on an exhaustive computer search.

A sharp upper bound also needs examples that approach it. The paper constructs such examples using geometric products, then encodes the resulting finite configurations as integers. The orthant-exponential ingredient is credited to Andrea Colesanti’s earlier work.[^3] The construction permits the site locations to vary, which is part of the supremum being measured.

## The precise statement

Let $k$ be a nonnegative kernel on at most four integer sites. Write $K$ for its total weight and $M$ for its largest weight. For nonzero, finitely supported, nonnegative inputs $f$ and $g$,

$$
\frac{\|f\star\widetilde{gk}\|_1}{\|f\star g\|_1}
\leq \frac{K+3M}{4}.
$$

Here $\star$ is max-convolution, the tilde reflects positions, and $gk$ means multiplying the two profiles point by point. The denominator is the full original convolution. The bound is sharp for prescribed kernel values when their locations may vary.

For a kernel equal to one on each of $n$ sites, the exact suprema through four sites are:

| Number of sites | Largest possible ratio, as a supremum |
| --- | --- |
| One | $1$ |
| Two | $5/4$ |
| Three | $3/2$ |
| Four | $7/4$ |

The paper also proves a general bound $(\sqrt K+\sqrt M)^2/4$, with the leading coefficient $1/4$ asymptotically optimal. Averaging the sharp four-site estimate over subsets gives upper bounds $35/16$ and $21/8$ for five and six sites.

## Below two for one five-position profile

Select five heights of $g$ in the proportions $9:5:5:5:5$, and give the kernel weight one at those positions and zero elsewhere. The five positions can be any distinct integers. The other finite, nonnegative signal, $f$, can vary freely, and values of $g$ outside the selected positions stay in the original total.

For this profile, the reflected total from the five selected positions is at most

$$
\frac{27936}{13981}=2-\frac{26}{13981}\approx1.9981
$$

times the full original total. Thus reflection cannot double it. The bound covers arbitrary heights of $f$ and overlaps between translated outputs. It improves the earlier coefficient of about $2.0068$ for this profile.[^1]

The fixed proportions matter. The interval in the earlier chart allows every five-position profile, so its lower bound of two and upper bound of $35/16$ remain unchanged. The best possible constant even for $9:5:5:5:5$ is not yet determined.

## How counting overlaps gives the stronger bound

Start on a four-dimensional grid, with the largest of the five heights at the origin and each smaller height one step along a different axis. Divide the other input by a geometric weight, then split the resulting heights into finitely many nested levels. At each position in the original combination, one overlapping pair wins in every layer. The original total therefore adds exactly across the layers; the reflected total is at most the sum of their reflected totals.

It is enough to count what happens to one weighted set of grid points. Outside points reached from all four directions are the only ones that could push the ratio above two. The proof separates them according to whether all the corners immediately below them are occupied. Complete lower cubes require enough weight inside the set, bounded by a random ordering of the four directions. A missing corner instead forces several reflected translates to overlap. Since max-convolution keeps only the largest contribution, those overlaps reduce the reflected total. Together, the two counts give the bound for every finite set, including sets with holes.[^1]

![Two squares: forward shifts reach y. In the second, reflected shifts meet at the missing corner z, where the maximum keeps one contribution.](/discoveries/figures/boundary-overlap.svg)

*A two-dimensional analogy: the first square has all three lower corners occupied. In the second, dashed reflected shifts meet at missing z, where the maximum keeps one contribution. Solid arrows show forward shifts to y. The proof uses four directions.[^1]*

Finally, the proof lifts an arbitrary integer input to repeated copies across a large box in the extra grid directions. Away from the box's boundary, the grid totals reproduce the integer totals exactly. The boundary's relative contribution tends to zero as the box grows. This transfers the bound to arbitrary integer positions, including positions whose translated outputs overlap. The argument is a proof for all finite inputs; it does not require a new numerical search.

The earlier coefficient of about $2.0068$ came from combining estimates about how well shifted copies cover the input. Reweighting that specified family of comparisons cannot improve its uniform coefficient. The boundary proof uses additional relations between the translates, so the earlier limitation on that proof family remains valid.[^1]

## A separate constraint on the next proof attempt

An actual ratio below two does not ensure that every proposed proof can establish it. One approach replaces the reflected total with an intermediate upper estimate. That estimate can be too large even when the true total is small enough, leaving the proof inconclusive.

A companion argument controls the estimate itself for a restricted family. On the nonnegative coordinate grid, keep the same five profile heights and require each positive coordinate step to multiply the other input's height by a factor at most $5/9$. Encode the finite configuration as integers without merging distinct outputs. For every such nonzero input, the intermediate estimate is also below $27936/13981$ times the original total.[^5]

This result combines boundary counting with projections onto coordinate faces and a nested-layer decomposition. It excludes these inputs from the stated unresolved proof condition, including different decay rates in different directions. The broader ratio theorem above does not extend this separate conclusion about the intermediate estimate to arbitrary inputs.[^5]

## What follows, and what remains open

These estimates imply several cases of a reflected fourfold inequality motivated by Gyarmati, Hennecart and Ruzsa’s sumset question.[^4] They include constant kernels on every five-point support, and a particular five-point support with arbitrary nonnegative kernel weights. The latter has 240 rational certificates covering all 120 weight orders.

The unrestricted fourfold question remains open in this work. For five sites the general support constant still lies between $2$ and $35/16$. Reading the closest retained primary sources also did not establish historical priority for the exact four-site result.

The outcome is an exact four-site constant, obtained by joining an upper proof to matching limiting examples. For the five-site profile $9:5:5:5:5$, layers, boundary counts and a finite-box transfer now keep the ratio below two for arbitrary input heights and integer positions. Coordinate projections also exclude a restricted family from obstructing the separate proof condition. The [companion construction article](/discoveries/more-differences-from-fewer-sums) moves in the other direction: it builds explicit sets where differences are unusually numerous. The paper, fixed-profile guide, geometric-family proof, earlier three-point note, source comparison and downloadable checks are linked below.
