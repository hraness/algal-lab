Imagine a population assembled from several types of components, each with its own constant rate of failure. Even when each type is simple, the population’s failure rate changes over time: faster-failing types disappear earlier, leaving a different mix among the survivors.

Two populations with three equally common types make this effect exact. Give one population rates $(1,3,5)$ and the other $(1,4,4)$. Their hazard rates cross exactly once. The population with the lower conditional rate early on has the higher rate later.[^1]

This example answers a proposed extension of a two-component ordering result negatively.[^3] Adding a common third component changes the comparison.

## Why a mixture has a changing rate

A component with exponential rate $v$ survives to time $t$ with probability $e^{-vt}$. A mixture with starting weights $p_i$ has hazard rate

$$
h(t)=\frac{\sum_i p_i v_i e^{-v_i t}}
{\sum_i p_i e^{-v_i t}}.
$$

The denominator is the proportion still surviving. The numerator counts their weighted failure rates. As time passes, the weights among survivors change.

The two example rate vectors have the same total. The first is more spread out: its two larger rates are three and five rather than four and four. This type of comparison, called *majorization*, often supports useful orderings. Here it cannot guarantee a hazard ordering at every time.

## Locating the crossing without rounding

Substitute $y=e^{-t}$. At suitable times the exponential expressions become polynomials or rational functions in $y$. Their signs can then be checked with exact rational arithmetic.

For $(1,3,5)$ and $(1,4,4)$, the proof gives one positive-time crossing, at a time between $\log 2$ and $\log 4$. It is the logarithm of an algebraic number of degree four. Root counting establishes uniqueness, so a plotted crossing is not being mistaken for a proof.

Adjoining any number of common rate-one components preserves a crossing. The failure therefore extends to every number of components greater than two. The paper also checks examples with strictly ordered weights and rates, and examples with two crossings under different hypotheses.

## The algebraic step that breaks

For an additive quantity, unchanged terms on both sides of a comparison cancel. A hazard rate is a ratio of two sums. Adding the same terms to both numerators and both denominators need not preserve their order.

That distinction explains the failed extension. A valid statement about two components cannot be lifted by treating the other components as if they disappeared from the ratio. A companion audit follows this step through precisely identified mixture-ordering statements and supplies exact counterexamples.[^2]

The audit distinguishes statements read in their original inspected manuscript from formulations transmitted by later papers. Where an original was unavailable, it tests the transmitted formulation and does not infer what uninspected hypotheses the original contained. Statement numbers for the 2026 comparison refer to the accepted author manuscript.[^4]

## The surviving conclusions

The original two-component fact remains valid. So does the usual stochastic ordering for the mixtures studied in the main example; the stronger claim about their hazard rates is what fails. Near-origin comparisons also survive in the stated regimes.

The result is a reproducible crossing mechanism, together with a source-specific audit of where it matters. The method combines a small counterexample, exact substitution and root counting. Readers can use the linked scripts to inspect the signs directly, and the papers to check each hypothesis. This analysis concerns mathematical mixture models; it makes no claim about an observed patient population or deployed reliability system.
