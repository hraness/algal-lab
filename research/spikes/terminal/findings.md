# Terminal-tree experiment v1: exact result and a failed sampling criterion

Date: 2026-09-23. The frozen experiment completed all 24 environments,
192 histograms, and 384 algorithm certificates. No inference or paid provider
calls were used. The mathematical endpoint is expected normalized terminal
service with exactly two survivors, not the earlier trajectory AUC.

**The registered primary criterion failed.** On the pooled 64-vertex
wide-rate/full-frontier panel, the frontier sampler at 2,048 trajectories had:

| Registered metric | Observed | Threshold | Outcome |
| --- | ---: | ---: | --- |
| Mean exact normalized regret | 0.00002581784056 | ≤0.001 | Pass |
| Maximum confidence regret bound | 0.01020463347 | ≤0.01 | **Fail** |
| Median paired speedup over exact construction | 4.551667× | ≥2× | Pass |

The conjunction is false. The small miss is retained as a failure; the
threshold is not rounded or changed. Both quality thresholds are evaluated
with exact rational arithmetic, and displayed values are descriptive decimals.
Timing is a local implementation measurement, not an asymptotic guarantee.

## What is proved and verified

The [frontier theorem](tree-proof.md) and exact optimizer hold for the specified
terminal model. An independent test suite compares 420 pair probabilities
with complete exact weighted-order enumeration and checks 116,344 exhaustive
tree candidates. Larger checks cover 24, 64, and 128 vertices. A second
independent reviewer checked another 17,434 exhaustive trees using a separate
deletion-state DP. The strict four-vertex witness beats every star by `1/160`.

The [sampling certificate](sampling-proof.md) is a probabilistic statement
under independent unbiased sampling. Its tests include exact finite histogram
enumeration, not just high-precision numerical comparisons. Independent review
found examples with nonzero certificate failure probability and verified that
the exact total failure mass remained below the claimed delta. It must not be
described as deterministic proof of optimality.

Every exact construction in this run matched a generic exact maximum spanning
tree. All 384 reported certificates covered the measured exact regret in these
seeded trials. This observation does not independently verify the IID premise
or establish a population coverage rate.

## Work/error comparison

The following rows describe the fixed frontier arm at 2,048 trajectories.
Each row contains four environments and two sampling seeds per environment.
The complete archive also retains the unstructured Kruskal arm and all four
sample budgets; none was selected after observing its results.

| Regime | Mean exact regret | Maximum confidence bound | Median exact/sample speedup |
| --- | ---: | ---: | ---: |
| 24 nodes, rates 1–5 | 0.00006750283 | 0.01772254 | 0.000855× |
| 64 nodes, rates 1–5 | 0.00004262478 | 0.01323468 | 0.002081× |
| 24 nodes, rates 1–99 | 0.00012289722 | 0.01297469 | 0.106561× |
| 64 nodes, rates 1–99 | 0.00003678875 | 0.01020463 | 1.214448× |
| 24 nodes, full frontier | 0.00010973767 | 0.00799224 | 0.350743× |
| 64 nodes, full frontier | 0.00001484694 | 0.00846028 | 9.143304× |

A ratio below one means the exact implementation is faster. Sampling is a poor
choice for the small-rate cases: exact class-cached construction takes about
0.000225 seconds at 24 vertices and 0.000789 seconds at 64 vertices in this
panel. The full-frontier 64-vertex cases require many more exact integrations;
their median exact construction time is 3.062 seconds, versus 0.335 seconds
for the sampled frontier method at 2,048 trajectories.

Increasing to 8,192 trajectories reduced the full-frontier 64-node arm's mean
exact regret to 0.00000681345 and its maximum confidence bound to 0.00225287,
with a 3.686217× median speedup. These were prespecified secondary results,
not a replacement for the failed primary criterion. Other regimes can become
slower than exact construction at this larger sampling budget.

Regret is normalized by original total value. Small absolute regret can become
easier at larger node counts; the archive also records regret divided by the payoff
range `B=second-largest value / total value`. Certificates can be much looser
than measured regret. In particular, a small absolute-regret threshold need
not imply a tight relative bound on the graph-dependent connection benefit.

Quality references remain visible. Every small-rate case had an optimal
reliability-centered star. On the wide-rate 64-node panel, its mean regret was
0.00032802, versus 0.00003679 for the frontier sampler. On the full-frontier
64-node panel, its mean regret was 0.00001628, versus 0.00001485 for the sampler.
An oracle-selected best star had mean regret zero in the wide-rate panel and
0.00001372 in the full-frontier panel. Selecting that best star uses exact
ground truth and is a reference, not a free deployable algorithm.

## Exact probability evaluation

The polynomial method and an independently implemented rational subset DP
agreed exactly on all six reference instances. Each method ran twice in
alternating order. The following ranges cover the two registered seeds:

| Vertices | Polynomial seconds | Subset DP seconds | Measured speedup |
| --- | ---: | ---: | ---: |
| 8 | 0.000139–0.000210 | 0.001429–0.001455 | 6.79–10.48× |
| 12 | 0.000139–0.000188 | 0.03425–0.03954 | 210.78–246.42× |
| 16 | 0.000259–0.000278 | 0.8523–0.9117 | 3276.73–3295.99× |

The arithmetic-operation improvement for bounded integer rates follows from
the algorithm: no enumeration of all removed subsets is needed. These timings
only compare the included Python implementations. Integer-polynomial
evaluation has prior art; this table does not establish a new fastest
Wallenius probability algorithm.

## Reproduction, accounting, and identities

The run used Python 3.14.6 on macOS 26.5.1, arm64. CPU and thermal conditions
were not controlled. Exact construction is timed three times per environment.
Sampled timings include integer draws, candidate construction, and numerical
confidence certification. Complete exact ground-truth evaluation is excluded
from both construction timings. Randomness is seeded for reproduction.
The timed source is `random.Random.randrange`, not the public sampler's default
`secrets.randbelow`; the latter's randomness overhead is not benchmarked here.

The initial run used 522,240 trajectories and 21,934,080 integer deletion draws,
produced 384 candidate/certificate pairs, and evaluated 768 seeded Prüfer
reference trees. Both methods share each histogram and each is charged the
full sampling cost. A fresh replay repeats this work; it is a separate cost.
The frozen protocol spends `0.05/384` failure probability per certificate,
conservatively allocating separately to both arms on a shared histogram.

```sh
python3 -m research.spikes.terminal.experiment run --out research/spikes/terminal/runs/new
python3 -m research.spikes.terminal.experiment replay --out research/spikes/terminal/runs/new
```

Retained archive: ignored `research/spikes/terminal/runs/v1/`. The manifest is
written before calculations begin, and source identities are checked again
before results are committed to the archive. Replay compares all seeded
histograms, candidates, exact values, certificates, and deterministic work
counts. It verifies the recorded summary against its original timing rows;
it does not claim to reproduce wall-clock timings.

| Artifact/source | SHA-256 |
| --- | --- |
| `manifest.json` | `e77b64d719b0ebf9b4e264e644abb1360b18e0ce2fd1d74518165cadf1c6f02e` |
| `results.json` | `9c38963161b4f200d8d36d3713b91319d1b65a989b6b044ed153d17cd9bd80dd` |
| `terminal_tree.py` | `eda888799c2da424c15078829618be7b5688a710f351565531c5ed0f83f6cd1d` |
| `terminal_sampling.py` | `94858507b224a17d96a0823d37d1ba00ef1500aee60d0c4b96b7b3e73f9e3724` |
| `experiment.py` | `6f8b2fdaa30419deeb4ef840bee389c21f40ffdf0079dae7b30950d53468b033` |
| `protocol.json` | `a13a0095b3c22e9daafc85b42c159584dc2e66b853ccbe409d9aec8f1faee9d0` |

Hashes bind retained bytes, not an external timestamp, author identity, or
scientific truth. Independent numerical reproduction and proof review are
separate evidence. Literature priority remains unresolved.

## Justified next experiment

The v1 confidence certificate considers every competing spanning tree even
though the structural theorem already identifies a smaller family containing
an optimum. A proposed refinement certifies against that proved family,
prunes dominated leaf choices, and avoids sampling when every choice is forced.
The mathematical proposal was discussed before the v1 outcomes; implementation
and evaluation follow this failed run. It must use new environment/sampling
seeds and a separately frozen protocol. The v1 sources, archive, and failed
criterion remain unchanged.

That refinement is now implemented with a separate proof and
[fresh experiment](hybrid-findings.md). The v1 replay completed successfully:
all 24 cases, six reference instances, seeded histograms, candidate graphs,
certificates, and deterministic work counts matched in a fresh process. Timing
values were intentionally excluded from numerical reproduction.
