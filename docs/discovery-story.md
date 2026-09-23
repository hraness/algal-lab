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

The extension has a precise limit. Merely knowing that one lifetime
distribution stochastically dominates another's is insufficient. Four simple
continuous distributions give an exact counterexample. A stronger condition
involving reversed hazards makes the proof work. The full
[research note](rank-selection-and-triples.md) states that condition and gives
the counterexample in rational arithmetic.

For larger groups, the same sorted grouping now has a proof at **every**
survivor count. The useful step is to condition on a failure outside the group.
That exposes a sum of positive terms to which a classical rearrangement
argument applies. The [proof](intact-groups-all-horizons.md) also works for a
class of ordered hazards beyond exponential clocks.

Another result removes the need to test indefinitely many surrounding
components. For any fixed quartet of independent clock distributions, every
background reduces to two threshold values. We can check the resulting
necessary-and-sufficient condition exactly in linear work for histogram
distributions. A negative certificate gives six clocks whose top-three
selection violates the inequality. There are quartets for which every
zero- and one-background test passes but two backgrounds expose a failure,
so the two-threshold reduction is sharp in general. The
[certificate note](two-threshold-certificate.md) supplies the formulas and
exact examples.

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
