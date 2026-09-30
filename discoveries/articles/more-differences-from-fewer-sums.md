Addition and subtraction use the same two inputs, but they can produce very different numbers of distinct answers. The laboratory produced two explicit constructions that make subtraction unusually expansive: a certified improvement over one published exponent bound, and a finite counterexample to a fivefold sumset inequality.[^1][^2]

Both results are small descriptions of very large sets. Their size makes listing every member impractical; their structure makes exact counting possible.

## A small example of the question

For the set $A=\{0,1,3\}$, adding every pair gives six different numbers. Subtracting every pair gives seven. Repeated answers count only once, so the collisions between pairs decide the outcome.

![For A equal to 0, 1, 3, the sums are 0, 1, 2, 3, 4, 6, and the differences are minus 3, minus 2, minus 1, 0, 1, 2, 3.](/discoveries/figures/sums-and-differences.svg)

*This three-point example explains the counting operation. It is not one of the large constructions that proves the two results below.*

The research question asks how far this imbalance can be pushed while addition stays controlled. A useful construction creates many collisions among sums without losing as many distinct differences.

## Turning a short alphabet into large sets

One route assigns weights to a small alphabet of digits. Long strings made from those digits are selected according to a total cost. Encoding the strings in a sufficiently large base turns them into ordinary integers while preventing carries from changing the coordinate-by-coordinate counts.

This connects a manageable weighted calculation to families of increasingly large finite sets. The paper gives a direct counting proof and also explains how the general formula follows from earlier results of Lau and Nair, together with a transfer theorem of Gyarmati, Hennecart and Ruzsa.[^5][^6] The general weighted-digit principle is therefore credited as an implication of prior work.

The contribution recorded here is the particular alphabet, weights and exact numerical certificate. For every fixed $K>1$, the construction gives arbitrarily large integer sets $E,F$ for which the sumset stays within $K$ times the size of $E$, while the difference set grows faster than a specified power of the sumset.

In the paper’s normalization, the resulting exponent satisfies

$$
\theta>\frac{23713}{20000}=1.18565.
$$

This improves the value $1.173077$ in Zheng’s specifically checked 2025 preprint.[^3] It is a comparison with that source and that definition of the exponent. A larger number from a different sum–difference problem would not be a valid comparison, and no current-record claim is made.

## A fivefold inequality that fails

A second paper gives finite integer sets $A,B$ satisfying

$$
|A-B|^5>|A+B|^5\,|5B|.
$$

The notation $5B$ means adding five elements of $B$, with repetition allowed, and keeping the distinct totals. The example contradicts the universal fivefold inequality posed in the historical source.[^6]

The construction starts with vectors of 128 nonnegative integer coordinates. In one set, coordinate sums are at most 160; in the other, at most 32. Base 193 encodes the vectors as integers without carries in the sums being counted. Standard counting formulas give the exact set sizes, and an integer comparison proves the strict inequality.

The underlying unequal-radius count is already in Daniel Glasscock’s 2012 thesis, including the proof used here.[^4] Substituting the chosen parameters into that known formula supplies the decisive example. The paper also includes a separate finite construction using binary words and exact type counting.

## How the results were checked

The large integers are compared exactly, so numerical rounding cannot decide the sign. Independent counting formulations reproduce the first construction’s difference count. The downloadable programs preserve the parameters, comparisons and certificates.

The literature work examined definitions and quantifiers as well as numerical values. It identified prior ingredients and derived the weighted formula from them. It did not establish that no earlier source used these particular parameters or stated the resulting fivefold example.

Together, the two papers show how short structured descriptions can produce rigorous finite examples. One yields a certified exponent improvement over an identified source; the other disproves the historical fivefold inequality. The [reflection result](/discoveries/the-limit-of-reflection) provides the complementary story: universal upper limits when the reflected kernel has only a few sites.
