# Claim evaluator conventions (frozen harness)

Each sample paper gets `harness/eval_<name>.py` (<name> = key with ':' and '/'
-> '_'). It reads `canonical/<name>.json`, encodes the paper's families and
systems, and tests every checkable claim record. Output:
`harness/eval_<name>.result.json`.

## What counts as a test

- A claim is tested at one or more concrete instances satisfying its printed
  hypotheses (parameter values, vector lengths, copula generators, priors).
  Use the paper's own printed examples where they exist; otherwise pick a few
  simple instances (small integers, halves, the paper's own parameter ranges).
- Orders st/hr/rh/lr are decided by `closedform.check` (interval evaluation on
  the scaled grid) or by `ratdist` exact checks where the model is rational.
- Systems: compose survivals with `syscomp` (series = product, parallel =
  1-prod(1-S), order statistics by binomial sum, mixtures by weighted sum,
  random-size extremes by mixture over P(N=m)).
- A claim in an unsupported order (disp, mrl, lorenz, star, icx, ageing) is
  recorded `{"status": "unsupported order"}` — do not improvise.
- A claim with dependent components or non-checkable quantification (all
  copulas, all baselines) is `{"status": "out of harness scope"}`.

## Result record (per claim)

{"claim": <record's claim label>, "order": <order>, "status":
 "holds" | "refuted" | "unsupported order" | "out of harness scope" |
 "ambiguous hypotheses",
 "instances": <count tested>, "witness": <rational point or null>,
 "undecided_points": <count>}

A refutation REQUIRES a witness point whose enclosure is strictly on the
wrong side AND that satisfies every printed hypothesis of the claim. Never
report refuted from a witness that violates a hypothesis; when unsure, use
status "ambiguous hypotheses" and explain.

## Independence / C3

Every refutation gets a second evaluation written independently (a separate
`c3_<name>_<claim>.py` or an exact closed-form argument), and the witness must
satisfy the claim's hypotheses as adjudicated. Report surviving claims as
"survived bounded testing", never "proved".
