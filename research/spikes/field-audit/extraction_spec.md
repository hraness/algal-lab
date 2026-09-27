# Field audit: claim extraction spec

Both extraction passes follow this spec exactly. The second pass sees only the
paper and this spec, never the first pass's output. Frozen before any
extraction; later changes are dated amendments.

## What to extract

Every theorem, proposition, corollary or lemma in the paper whose conclusion
orders two distributions (or two random variables, systems, mixtures or order
statistics) under a named stochastic order: usual stochastic (st), hazard rate
(hr), reversed hazard rate (rh), likelihood ratio (lr), dispersive (disp), star
or convex transform, Lorenz, mean residual life, increasing convex or concave,
right spread, or an ageing order ("ageing faster" and similar). Also extract
every printed numerical example or counterexample that supports or refutes
such a result, as a separate record.

Do not extract results that only characterize one distribution (moments,
shape, estimation), or ordering results stated for a fully general
nonparametric class unless the paper also states them for a specific family.

## One record per claim

Write one JSON object per claim, following this shape:

```json
{
  "paper": "<frame key, e.g. doi:10.1016/...>",
  "claim": "Theorem 3.2(ii)",
  "page": 7,
  "quote": "<the complete statement, verbatim, including 'Let ...' preambles>",
  "kind": "theorem | proposition | corollary | lemma | example | counterexample",
  "model": "single | mixture | order statistic | series system | parallel system | k-out-of-n system | other: <describe>",
  "family": "<baseline family and parametrization, verbatim where possible, e.g. 'Weibull, shape a > 0 common, scales lambda_i'>",
  "compared": "<what differs between the two sides, e.g. 'mixing proportions p vs q and scales lambda vs gamma'>",
  "hypotheses": [
    {"text": "<verbatim condition>", "formal": "<your formalization>", "source": "statement | section preamble | definition N | earlier theorem N"}
  ],
  "conclusion": {"order": "st | hr | rh | lr | disp | star | lorenz | mrl | icx | icv | rs | ageing: <name> | other: <name>", "direction": "<which side is smaller, e.g. 'U(p,lambda) <= U(q,gamma)'>"},
  "quantifiers": "<ranges of n, parameters and t, e.g. 'n >= 2, all t > 0'>",
  "numbers": "<for examples only: every printed parameter value and printed result>",
  "ambiguity": "<anything unclear: notation, missing definitions, conflicting statements; empty if none>"
}
```

## Rules

1. Quote the full statement verbatim, including any assumptions stated just
   before it in the same section that the statement relies on.
2. List every hypothesis, including ones that come from definitions or from a
   standing assumption of the section. Record where each comes from.
3. Do not repair, strengthen or weaken anything. If the statement looks wrong
   or incomplete, record it as written and say why in `ambiguity`.
4. Resolve notation from the paper's own definitions. If a symbol is never
   defined, say so in `ambiguity`.
5. For each theorem with several parts, write one record per part.
6. If the text is unreadable or garbled at a statement, record what you can and
   say so in `ambiguity`.
7. Output a JSON array for the paper and nothing else.
