# Hybrid terminal-tree experiment: fresh registered test passed

Date: 2026-09-23. The [frozen follow-up protocol](hybrid-protocol.json)
completed all 24 new environments and 48 paired trials. The earlier
[failed experiment](findings.md), its numerical sources, and its archive remain
unchanged. This endpoint concerns terminal service with two survivors, not AUC.

**The fresh primary criterion passed.** On the specified 64-vertex wide-rate
and full-frontier panel, the hybrid at a fixed budget of 2,048 trajectories had:

| Registered metric | Observed | Threshold | Outcome |
| --- | ---: | ---: | --- |
| Mean exact normalized regret | 0.00003987950 | ≤0.001 | Pass |
| Maximum confidence regret bound | 0.008348098 | ≤0.01 | Pass |
| Median paired speedup over exact construction | 5.725864× | ≥2× | Pass |

The panel contains eight environments, each with two sampling seeds. The
quality thresholds are evaluated with exact Fractions, not rounded displayed
numbers. Timings are descriptive local measurements. This is a successful
bounded experiment, not a claim of speedup on every input or over every
deterministic algorithm.

## What changed after the failed experiment

The [hybrid theorem and algorithm](hybrid-proof.md) exploit facts already
proved about the optimum. Nonfrontier leaves need only a prefix of possible
frontier parents. Parent-choice groups form a product family containing a
global optimum. The selected edge cancels when bounding regret within each
group, and forced choices need no probability interval at all.

If every choice is forced, the algorithm returns an exact optimum without
requesting randomness. Otherwise it samples integer weighted deletions and
bounds regret over the remaining groups. The queried pairs are determined
from the environment before observing counts. Their probabilities can sum
to less than one, so the algorithm does not impose the old full-pair simplex
constraint on this subset.

The proposal was reviewed and its sources frozen before evaluating these new
seeds. The follow-up preserves the first test's sample budget, per-certificate
failure allowance, primary regimes, and three thresholds. It compares the
original frontier sampler with the hybrid on paired seeded ticket streams;
nonforced cases must produce identical histograms. The fixed sample size is
not selected by looking at the resulting bound.

## Matched results and limitations

Each row below has four environments and two sampling seeds. A speed ratio
below one means the exact implementation is faster. The low-rate regimes
remain important counterexamples to a general sampling-speed claim.

| Regime | Hybrid mean exact regret | Maximum confidence bound | Median exact/hybrid speedup | Zero-draw exact trials |
| --- | ---: | ---: | ---: | ---: |
| 24 nodes, rates 1–5 | 0.00003777735 | 0.007532131 | 0.013579× | 2/8 |
| 64 nodes, rates 1–5 | 0 | 0.000470191 | 0.778116× | 4/8 |
| 24 nodes, rates 1–99 | 0.00010491139 | 0.008322244 | 0.208415× | 0/8 |
| 64 nodes, rates 1–99 | 0.00006434438 | 0.008154125 | 1.565656× | 0/8 |
| 24 nodes, full frontier | 0.00007237682 | 0.008367889 | 0.398974× | 0/8 |
| 64 nodes, full frontier | 0.00001541462 | 0.008348098 | 9.526596× | 0/8 |

Six hybrid trials were structurally exact and used zero draws. Fifteen of
48 hybrid outputs matched the exact optimum when evaluated; the additional
nine are measured optima, not deterministic claims made by the algorithm.
None of the 16 primary outputs was exactly optimal; their positive regret is
the measured cost of approximation.
All 16 primary runs used the full sampling budget. The six zero-draw controls
are outside that primary panel. Their shortcut is deterministic and could also
be added to an exact implementation; their speed is not evidence of an advantage
from randomness itself.

In the 64-node wide-rate regime, median exact construction took 0.5443 seconds
and the hybrid took 0.2764 seconds. In the full-frontier regime, these medians
were 3.9900 and 0.3966 seconds. The pooled 5.73× figure is the median of
per-trial ratios, not a ratio of pooled median times, and should not conceal
the substantial difference between these regimes.

On these same fresh cases, the original frontier sampler's worst primary
confidence bound was 0.01494106, exceeding the retained 0.01 threshold. Its
mean primary regret was approximately 0.00004549187. The hybrid's mean is
0.00003987950 and its worst bound is 0.008348098. These are paired descriptive
results; no statistical significance or population superiority is asserted.

The hybrid's median speedup over that existing sampling baseline was only
1.0840× on the primary panel (1.7199× over all 48 paired trials). The headline
5.73× uses the exact solver as its comparator. Across the 48 pairs, hybrid
regret was lower in 17 and equal in 31; it was never higher on this panel.
Every hybrid bound was no larger than its paired original bound here. These
observations do not establish such domination on arbitrary future inputs.

Cheap deterministic baselines remain competitive. The reliability-centered
star's mean regret was 0.00002429128 on the wide-rate 64-node panel, lower
than the hybrid's 0.00006434438. On the full-frontier panel that star's mean
regret was 0.00006543682, higher than the hybrid's 0.00001541462. An
oracle-selected best star had mean regret 0.00002429128 and 0.00000232871,
respectively; selecting it here uses exact ground truth. The result is a
work/error tradeoff against the exact optimizer, not universal superiority
over simple deterministic designs.

Regret is a fraction of original total value. Small absolute regret can become
easier at larger node counts; the archive also records regret relative to
`second-largest value / total value`. Confidence bounds are conservative
and much larger than the observed regret. Passing an absolute-regret threshold
does not guarantee a similarly small relative error in the graph-dependent
connection benefit.

## Probability, proof, and numerical evidence

For the stochastic branch, each certificate has failure allowance
`delta=0.05/384` (interpreted as the recorded round-trip decimal). At most
96 certificates are reported, so a union bound spends at most 0.0125 under the
independent unbiased-draw premise. This conservative allocation intentionally
keeps the per-certificate allowance unchanged from v1. Forced cases require
no probability assumption.

Every reported bound covered the exact measured regret in this run. Observing
zero violations in seeded trials is not an independent proof of the IID
premise. The confidence theorem, outward numerical enclosure, and finite-law
validation are separate evidence. Sampling confidence is not deterministic
optimality; the implementation labels these statuses separately.

Focused hybrid validation checked all 6,561 four-vertex integer profiles
against 104,976 tree candidates, 72 independent confidence-box comparisons,
nonstar and nondominator regressions, zero-draw cases with randomness and KL
calculation forbidden, and malformed inputs. A separate reviewer checked
15,741 global trees and all 325 histograms of a finite law with unequal true
parent rewards. Its exact certificate-failure probability was about 0.008516,
below its test allowance 0.25; nonzero failures exercise the probabilistic
claim rather than assuming it is infallible.

The mathematical proofs are ordinary reviewed proofs with executable checks,
not theorem-prover formalizations. The sampling law, polynomial integration,
spanning-tree rules, and concentration inequalities have prior art. The
model-specific frontier/pruning result and integrated hybrid are a candidate
contribution; publication-level novelty is not established. No LLM-inference
or token-efficiency advantage was tested.

## Reproduction and cost accounting

```sh
python3 -m research.spikes.terminal.hybrid_experiment run --out research/spikes/terminal/runs/new-hybrid
python3 -m research.spikes.terminal.hybrid_experiment replay --out research/spikes/terminal/runs/new-hybrid
```

The first run performed 72 exact construction timings and 96 candidate/bound
calculations. The original arm used 98,304 trajectories; the hybrid used
86,016 after skipping six forced trials. Total execution was 184,320
trajectories and 7,659,520 integer draws. Unlike v1's shared execution of draws,
this experiment executes both arms separately from the same seed and charges
each its complete call cost. A fresh replay incurs the same numerical work
again; it does not reuse the saved samples as input.

Runtime was Python 3.14.6 on macOS 26.5.1, arm64. Exact construction is timed
three times per environment, arm order alternates by sampling seed, and exact
ground-truth evaluation is excluded from all construction timings. CPU/thermal
conditions were not controlled. Timings compare these Python implementations,
not all available exact or deterministic approximation methods.
The timed sampling source is seeded `random.Random.randrange`. The public
library default uses `secrets.randbelow`; its cryptographic randomness overhead
is not measured by this speedup comparison.

Ignored archive: `research/spikes/terminal/runs/hybrid-v2/`. Its manifest is
written before evaluation, source hashes are checked afterward, and completed
archives are never overwritten. Numerical replay compares all paired samples,
graphs, exact values, bounds, statuses, and operation counts, while checking
the original summary against the original timing rows. Timings themselves are
not claimed to reproduce.

Fresh numerical replay completed successfully for all 24 environments and
96 outputs. All seeded samples, graphs, values, bounds, statuses, and operation
counts matched. The independent archive audit also recomputed every summary,
primary acceptance condition, paired-stream check, and zero-draw claim without
rerunning the experiment.

| Artifact/source | SHA-256 |
| --- | --- |
| `manifest.json` | `83142e040ce34464afd5d4adaa1279d0dd2700a8da7a36b2b7daa6ac939d4de8` |
| `results.json` | `7eb9b187c28727240bef6608e5d0e708878e16051cfee1604658f27c62d92f41` |
| `terminal_hybrid.py` | `ab1d9db4b6fb1bd2b719d2b3557ef331e26a1eb2539457e946c1aa66d078ac7c` |
| `hybrid_experiment.py` | `5b974835eedf5bb9e3f8dbcd4bbfadb92bedcaec7c87177eb793c2c48e4266f5` |
| `hybrid-protocol.json` | `621640d1b57ce4b50d2a72d08eef640996d8e0f47e8e4669088b7cf34a782977` |

The remaining four source identities are identical to the retained v1 study.
Hashes establish byte identity, not external timestamp, authorship, or truth.
