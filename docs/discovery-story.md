# Why some redundancy designs reduce to sorting

Suppose components fail one at a time. Each has a positive failure rate, and
the next failed component is chosen proportionally to its rate among those
still working. We arrange components into groups before failures begin, then
maximize the expected number of groups that remain useful.

The interesting discovery is how much the answer depends on what “useful”
means. Some versions need only sorting. A closely related version can encode
a strongly NP-complete problem.

| Design | When a group works | Horizon | Proven result |
|---|---|---|---|
| Pairs | Both members survive | Any fixed survivor count | Pair adjacent failure rates |
| Pairs | Either member survives | Any fixed survivor count | Pair opposite ends of the rate order |
| Equal-size groups | Every member survives | Any fixed survivor count | Use consecutive blocks of sorted rates |
| Triples | At least two members survive | Exactly two failures | Exact optimization is strongly NP-hard |

The pair result rests on an inequality among four joint survival probabilities.
It compares adjacent, crossing, and nested pairs in a consistent order. That
makes a sorting rule globally optimal, without estimating any probabilities.
Our latest proof extends the inequality to a wider class of independent
continuous rankings. Memoryless exponential failure clocks are one example;
they are not essential to the argument.

The newest result separates the two pairing objectives. Ordinary stochastic
dominance alone suffices when **both members must survive**: adjacent pairs
are optimal. It also suffices for equal-size groups of any size when **every
member must survive**, at every fixed survivor count. The clocks must be
independent and atomless. A positive four-clock integral survives conditioning
on all other scores; a product factorization then builds every larger
regrouping from those four-clock comparisons. The
[proof and histogram optimizer](stochastic-intact-groups.md) remove the
hazard-order assumption from the [earlier argument](intact-groups-all-horizons.md).
The conclusion covers more than the average: consecutive groups maximize the
chance of having at least any specified number of intact groups. The same
proof also covers discrete scores with uniform random tie-breaking.

An [exact finite proof](block-separated-triples.md) now allows CDF crossings
inside each target group for three groups of three. It checks algebraic
identities for every partition and selection state, then applies the
four-clock inequality. A [robustness result](robust-stochastic-groups.md)
also bounds grouping regret when the distributions depart from an ordered
reference model. Its projection step is established isotonic regression.

For pairs that work when **either member survives**, stochastic dominance
does not suffice. Four strictly ordered continuous distributions with positive
densities make crossing pairs outperform opposite-end pairs by exactly
`1/675` in expected working-pair count. The stronger reversed-hazard condition
in the [rank-selection note](rank-selection-and-triples.md) still gives the
full adjacent–crossing–nested inequality and the opposite-end rule.

Another result removes the need to test indefinitely many surrounding
components. For any fixed quartet of independent clock distributions, every
background reduces to two threshold values. We can check the resulting
necessary-and-sufficient condition exactly in linear work for histogram
distributions. A negative certificate gives six clocks whose top-three
selection violates the inequality. There are quartets for which every
zero- and one-background test passes but two backgrounds expose a failure,
even when all four distributions have positive densities and are strictly
stochastically ordered. The
[certificate note](two-threshold-certificate.md) supplies the formulas and
exact examples.

The ordered counterexample revealed a general construction. Put a bad region
between two positive regions: their contributions make every test with one
background clock pass, while two clocks isolate the hidden failure. Fixed
block masses work for any ordered quartet with a negative no-background gap.
The [construction and proof](rank-context-compression.md) explain why. The
same note separates the rank argument from the probability formula: any
reward supported on one focal cardinality reduces to two backgrounds, even
when the focal scores depend on one another. This gives a precise boundary
for what a small test population can certify. A further
[minimum-context theorem](minimal-rank-contexts.md) identifies exactly how many
background entries preserve an arbitrary set reward for every possible focal
score vector. It distinguishes that preservation problem from finding a
negative expected value for a particular probability law.

A majority triple has the opposite preference: one failure in each of two
triples leaves both useful, while two failures in one triple disable it.
Optimizing this dispersion is harder. We proved a reduction from 3-PARTITION
with an explicit finite error bound, showing strong NP-completeness of deciding
whether a given expected service can be reached. The result still holds when
the failure rates are nearly equal.

That statement needs its companion result. When rates are nearly equal,
the expected service of *any* two groupings is close: we bound the gap by a
quantity that shrinks quadratically with relative rate spread. Exact
optimization can therefore remain hard while a useful approximate design
requires little effort. This distinction matters more than a hardness label
on its own.

The scientific claim is narrower than a priority announcement. The proofs are
checked here, with exact examples and independently implemented calculations.
Literature priority remains under review. Sampling theory already contains
probability representations and neighboring ordering results; reliability
design already contains rearrangement methods and hardness results. Our
[novelty ledger](novelty-ledger.md) records the specific comparisons and which
full papers remain unread.

There is also a lesson for the laboratory. The earlier six-call Qwen3-14B
experiment used 2,804 reported tokens, but a zero-model enumeration control
selected more valid laws, and feedback did not improve the model's score.
This continuation used a lead agent and bounded Sol/Luna workers to derive,
challenge, and check the mathematics. It does not establish that a small model
originated the result cheaply. It demonstrates a concrete research workflow:
preserve failed generalizations, turn exact counterexamples into sharper
hypotheses, prove the surviving claims, and make the checks public.

The source and credential-free reproduction commands are linked from the
[research note](rank-selection-and-triples.md). External expert review is the
next test of the priority claims; the results should be described as proved
within these models until that review resolves their relationship to prior art.
