Choose points from a three-dimensional integer grid, with no five allowed to lie on one sphere or one plane. How many can fit?

The laboratory’s retained constructions contain eight, 11, 14 and 18 points in grids with side lengths three, four, five and six. Every construction passes exact integer checks. The first two sizes are also proved optimal. For the larger grids, completed searches suggest optimality, but independent complete exclusion evidence is still missing.[^1][^2]

The distinction is central to the result: finding a valid arrangement proves that many points fit; proving the maximum requires ruling out every larger arrangement.

## The grid and the condition

A grid of side length $n$ consists of triples $(x,y,z)$ whose coordinates are integers from zero through $n-1$. Write $C(n)$ for the largest valid selection.

To check five chosen points, form a matrix with one row

$$
(x,\ y,\ z,\ x^2+y^2+z^2,\ 1)
$$

for each point. Its determinant detects the forbidden sphere-or-plane condition. Because all entries are integers, the calculation needs no geometric tolerance or floating-point guess.

The verifier checks every five-point subset of each retained construction. This establishes the lower bounds independently of the search program that found the points.

![Grid evidence table: side lengths 3 and 4 have exact optima 8 and 11. Side lengths 5 and 6 have verified constructions of 14 and 18, with matching upper exclusions supported by one enumerator.](/discoveries/figures/grid-evidence.svg)

*The status changes at five sites along each axis: a completed search is retained, but the larger upper bounds do not have the same independent support.*

## Searching by layers

The search builds a configuration one coordinate layer at a time. Symmetries identify equivalent starts, and mathematical capacity bounds remove branches that cannot reach the target size.

Those reductions must preserve every possible solution. An unsafe capacity prune was found and corrected during the implementation audit. The report preserves the correction and distinguishes actual visited nodes from pruning counters, so the search record can be interpreted accurately.

The corrected enumerator reports exhaustion of 1,905 initial-layer orbits when testing size 15 on the five-grid, and 8,133 orbits when testing size 19 on the six-grid. These are completed results from one implementation. They are evidence for candidate exact values, with a stated verification limit.

## What the evidence establishes

| Grid side length | Verified construction | Upper-bound evidence | Conclusion |
| --- | --- | --- | --- |
| Three | Eight points | Recorded SAT refutation with independently checked proof; independent enumeration | $C(3)=8$ |
| Four | 11 points | Recorded SAT refutation with independently checked proof; independent enumeration | $C(4)=11$ |
| Five | 14 points | Corrected single enumerator reports no 15-point solution | $C(5)\geq14$; exactness is a candidate conclusion |
| Six | 18 points | Corrected single enumerator reports no 19-point solution | $C(6)\geq18$; exactness is a candidate conclusion |

The independent five-grid attempt ended without a decision. It supplies no additional upper bound. A fresh independent complete search or a separately checkable refutation would strengthen the two larger conclusions.

Earlier construction-search work, including PatternBoost, provides context for using learned proposals in finite mathematics.[^3] The evidence here does not show that an AI search method outperforms a matched non-AI baseline.

## A result that can be checked in parts

The published report gives two exact small-grid values, four verified constructions, and a corrected account of the larger searches. Integer determinants verify the examples; independently checked exclusions establish the first two optima. Keeping those jobs separate makes it possible to improve the evidence without discarding valid constructions.

The [Ramsey search](/discoveries/narrowing-a-ramsey-search) uses the same distinction in a different setting: a graph search can establish finite exclusions even when the main existence question remains unresolved.
