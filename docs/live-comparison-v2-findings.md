# First live comparison under network.v2 — findings

2026-09-23, `openai/gpt-6-luna` via Vercel AI Gateway (`providerOptions.only:
["openai"]`), 240 admitted calls (the exact plan slot count), 288 recorded
attempts including priming. Archive verified offline:
`comparison digest sha256:f85eb7b83362b4733303d1ad3b825e1a646052b8a995d82d8fd488c878cf53bd`
at `runs/live-comparison-v2/` (local, not committed). Spend: $0.145 observed
(310k input / 216k output tokens). All eight controls passed; two call
failures (one `model_mismatch`, one `provider_error`) are retained
failure-inclusively.

## Mean champion exact weighted AUC

| Scope | Arm | Isolated | Shared artifacts | +Messages | Reference | Ceiling |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| primary | adaptive | 0.7214 | 0.7279 | 0.7279 | 0.7287 | 0.8127 |
| primary | random | 0.7423 | 0.7423 | 0.7423 | 0.7287 | 0.8127 |
| primary | live | 0.7353 | 0.7381 | 0.7380 | 0.7287 | 0.8127 |
| transfer-0 | adaptive | 0.7104 | 0.7104 | 0.7104 | 0.7216 | 0.7949 |
| transfer-0 | random | 0.7104 | 0.7104 | 0.7104 | 0.7216 | 0.7949 |
| transfer-0 | live | 0.7102 | 0.6963 | 0.6849 | 0.7216 | 0.7949 |

## What the instrument measured

- The live arm is a competent but not dominant designer: above the
  label-blind adaptive baseline in isolation (+0.0139, 7/0/1 wins,
  inconclusive), near the reference, below the random-search control.
- Sharing helped slightly at the primary budget: `shared − isolated`
  +0.0028 [0.0005, 0.0054], within the 0.01 margin — a small positive
  trend, not a claim.
- **Sharing hurt on transfer**: `messages − isolated` −0.0253
  [−0.0370, −0.0131], sign-flip p = 0.0156, verdict below-margin — peer
  designs and messages actively degraded the live arm's held-out
  generalization. This is the first measured sharing effect in the lab
  and it is negative.
- The model did not reliably improve over host priming: mean
  improvement ≈ −0.004, 2/8 replicates positive. Host-primed designs
  remain competitive under heterogeneous environments.

## Honest limits

- One model, one run, 8 replicate seeds: every arm contrast is
  inconclusive or within-margin except the negative transfer effect.
- The scripted arms are controls, not intelligence evidence; the live
  arm's mid-pack placement shows the instrument discriminates designers
  without saturation (ceiling 0.81 remains far off).
- The transfer degradation suggests shared context biases proposal
  diversity — plausible mechanism, not established. Replications under
  the frozen plan (same seeds and budgets) would strengthen it; a new
  plan is required to test other regimes.
