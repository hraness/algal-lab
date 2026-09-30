Take two short lists of numbers. Add every number in one list to every number in the other, keeping each distinct answer only once. Then repeat with subtraction. The two collections can have different sizes, even though the inputs have barely changed.

The laboratory proved an exact limit for a weighted version of this question when one input is restricted to four positions. Reflecting that input can increase the measured total by a factor approaching **seven quarters, or 1.75, but never more**. The matching lower examples and the upper proof establish the same number.[^1]

This is a small-support result inside a larger unsolved problem. Its value is a precise answer with a complete proof: it replaces a range of possible constants with one exact value.

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

## What follows, and what remains open

These estimates imply several cases of a reflected fourfold inequality motivated by Gyarmati, Hennecart and Ruzsa’s sumset question.[^4] They include constant kernels on every five-point support, and a particular five-point support with arbitrary nonnegative kernel weights. The latter has 240 rational certificates covering all 120 weight orders.

The unrestricted fourfold question remains open in this work. For five sites the general support constant still lies between $2$ and $35/16$. Reading the closest retained primary sources also did not establish historical priority for the exact four-site result.

The outcome is an exact four-site constant, obtained by joining an upper proof to matching limiting examples. The [companion construction article](/discoveries/more-differences-from-fewer-sums) moves in the other direction: it builds explicit sets where differences are unusually numerous. The paper, earlier three-point note, source comparison and downloadable checks are linked below.
