# Field audit: stochastic-ordering literature — draft results memo

## Design (frozen protocol, protocol.md + 5 amendments)

- Frame: 858 OpenAlex candidates citing landmark stochastic-ordering sources.
- Screening: 858 decided; 144 eligible (ordering claims on named parametric families with retrievable text).
- Sample: first 100 eligible in frozen order (`sample100.json` + sha256); two same-paper pairs → headline denominator 98.
- Extraction: two independent passes, 100/100 each; 1,045 theorem-level canonical records + 413 printed examples/counterexamples (`canonical/FREEZE.json`).
- Adjudication: ~600 disagreement items resolved against printed text; all queues closed.
- Evaluation: frozen harness (exact rational + interval enclosures, st/hr/rh/lr); per-paper `eval_*.py` + result JSONs.
- C3: every refuted record independently re-derived (fresh code, premise verification against printed definitions).

## Headline (to fill after C3 groups A/C land)

- Papers evaluated: 100 (98 distinct)
- Theorem-level records evaluated: 1,045; testable (st/hr/rh/lr): 788
- Refuted records (pre-verification): 172 across 42 papers
- C3-confirmed so far (group B): 43/49 genuine, 3 invalid-instance excluded, 1 artifact excluded, 2 direction-reversed
- **P1 (papers with ≥1 C3-confirmed refuted theorem-level claim)**: TBD/98 — with pilot: TBD; ex-pilot: TBD
- P2 (printed example/counterexample reproduction): TBD

## Failure taxonomy (verified so far)

1. **Direction-reversed conclusions**: MWU Theorem (1)(i)/(ii) all orders; s11587 convention slip (≼w defined backwards → 7 theorems); s44199 lr direction; EGG family.
2. **Parameter-ordering claims failing at boundary**: MGGD lr claim; several "α₁<α₂ ⇒ ordering" results.
3. **Self-contradiction**: am.2018.0105-17 Thm 3.5(a) vs own Thm 3.1(b); s13660 Cex 4.6 vs Thm 4.4 converse.
4. **Vacuous hypotheses**: x²r-class conditions unsatisfiable for proper distributions (ELS; fil2104315d C3/C6).
5. **Printed premises unsatisfiable/defective**: printed baselines whose "CDF" exceeds 1 (fil2104315d MOQL); example parameters violating stated hypotheses (math.2024434 Ex 3, s13660 Ex 4.5, jmi Ex 2.7).
6. **Arithmetic/print slips**: 1912.00798 printed 1.0019 (exact 1.0009944); jmi Ex 2.6 (7.4 vs 7.3); poisson-paper Cex 3.3 premise fails own majorization.

## Methodological findings

- Extraction agreement pre-adjudication: 61.2% order+direction identical; disagreements were mostly convention ambiguities (rh/hr, cx/icx, paper-defined orders) resolved verbatim.
- C3 necessity demonstrated: one full set of "refutations" (2407.18801) demoted to holds — wrong generator reading; one artifact (bounded scan missed real sign change); three invalid instances (premise violations).
- Pilot non-transfer: mia-2020-23-03 pilot "holds" tested raw-p majorization; printed hypothesis is h(p)-majorization — canonical evaluation supersedes.

## Limitations (to enumerate)

- Frame skews toward open-access low/mid-tier venues; 121 downloads blocked (documented).
- Copula/dependence claims untested (out of harness scope): ~214 records.
- Unsupported orders (disp/mrl/star/ageing/paper-defined): ~368 records.
- "holds" = bounded grid survival, not proof.
- Double-pass agreement ≠ correctness (BJPS-510 Thm 3.9 was agreed-but-wrong until adjudication).
