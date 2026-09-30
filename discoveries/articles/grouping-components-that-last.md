Suppose a group works only while every one of its members survives. Some members tend to last longer than others. Should the longest-lasting members be spread across groups, or placed together?

In the model studied here, grouping similar members together is optimal. Sort the members by their lifetime distributions, then divide the list into consecutive groups of the same size. At every fixed number of survivors, this arrangement maximizes the probability of having at least one intact group, at least two intact groups, and so on.[^1]

It therefore improves the whole distribution of the intact-group count, as well as its average.

## What “tends to last longer” means

Each member has a random lifetime, independent of the others. The distributions are ordered so that an earlier member in the list is at least as likely to survive past any chosen time as a later member. This is called *stochastic dominance*.

The theorem does not require exponential lifetimes. Its main statement uses atomless distributions, so ties have probability zero. A companion corollary permits atoms under specified tie-breaking.

Choose a fixed number of survivors by keeping the members with the largest lifetimes. A group is intact exactly when all of its members are among those survivors. Assigning groups does not change the lifetimes or how survivors are selected.

![Eight members ranked from longer-lasting to shorter-lasting are placed into four adjacent pairs: 1 with 2, 3 with 4, 5 with 6, and 7 with 8.](/discoveries/figures/grouping.svg)

*Consecutive grouping after sorting. The theorem concerns equal-size groups that need every member.*

## A four-member comparison becomes a general proof

The key step compares the ways to pair four ordered lifetimes. After conditioning on the other members, the difference between the grouping probabilities can be written as an integral. Every term in the crucial expression has a nonnegative sign under the distribution ordering.

That local comparison remains valid when multiplied by the relevant nonnegative factors from other selected members. A product factorization then turns larger regrouping comparisons into these four-member steps.

The result applies to every upper-tail probability of the intact-group count at every fixed survivor count. One arrangement therefore works simultaneously for all those objectives; a new search is not needed for each horizon.

## When the objective changes

The equal group sizes and all-members-survive rule are essential. A redundant group that works when *any* member survives has a different objective. So does a network whose score is the size of its largest connected surviving component.

The repository keeps those problems separate. Companion work studies pairing, majority triples and a terminal-tree objective when two vertices survive.[^2][^3] A grouping theorem for one of these tasks cannot be substituted for another merely because both mention failures.

The same care applies to research provenance. Conditioning on the background variables, rearrangement arguments and several algebraic ingredients have established precedents. The retained source comparisons do not establish historical priority for this precise random-rank application.[^4]

## From a search question to a sorting rule

For the stated lifetime model, a potentially large grouping search reduces to sorting and taking consecutive blocks. The proof explains why the rule works at every survivor count and why its objective matters.

The linked proof gives the integral identities and assumptions. The companion notes cover other objectives, and the network laboratory provides the separate experiment machinery. For another example of a continuous search collapsing to a finite rule, [the task-allocation result](/discoveries/when-specialization-wins) proves when every optimal agent specializes.
