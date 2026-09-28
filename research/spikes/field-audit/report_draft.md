# Field audit: stochastic-ordering literature — results memo

## Design (frozen protocol + 5 amendments)

- Frame: 858 OpenAlex candidates citing landmark stochastic-ordering sources.
- Screening: all 858 decided; 144 eligible; first 100 in frozen order sampled (`sample100.json` sha256-pinned); two same-paper pairs → denominator 98.
- Extraction: two independent passes, 100/100 each; 1,045 theorem-level canonical records + 413 printed examples/counterexamples (`canonical/FREEZE.json`).
- Adjudication: ~600 disagreement items resolved verbatim against printed texts; all queues closed.
- Evaluation: frozen harness (exact rational + interval enclosures over a scaled grid; st/hr/rh/lr); per-paper `eval_*.py`.
- C3: every refuted record independently re-derived — fresh mpmath code, premise re-verified against the paper's *printed* definitions.

## Verified headline

**P1 = 29/98 papers (29.6%) carry at least one C3-confirmed false-as-printed theorem-level ordering claim** (26/88 = 29.5% excluding the 10 pilot papers).

- 73 distinct confirmed theorem-level refutations; 172 raw "refuted" records → 106 confirmed after C3 (65 excluded: invalid instances, artifacts, inconclusive).
- Evidence level: of 43 papers with checkable printed examples/counterexamples, **12 (28%) have a confirmed failure** — printed examples violating the paper's own hypotheses or wrong-signed conclusions.
- Venue split: arXiv 6/23 (26%), journal 23/75 (31%).

## Failure taxonomy (all C3-confirmed)

1. **Direction-reversed printed conclusions** (the opposite ordering verifiably holds): MWU Theorem (1)(i)/(ii) — all three orders backwards; s44199 lr; s40745 ×3; ejpam6653 ×3; ijsp8 ×4; soic-1872 ×2; jds ×4; jss.13.2.319 Example 1.
2. **Genuine claim failure** (no direction holds / crossing): fil2104315d flagship Thm 3.1(i) + 11 more; 2552185 Thms 3.7–3.10, 3.12 (the 3.9/3.10 opposite-direction pair both fail); math6100197-class crossings; 03610926.2021.1919898 ×6.
3. **Paper-wide convention slip**: s11587's `≼w` defined backwards → 7 theorems refuted at premise-satisfying instances.
4. **Vacuous hypotheses**: `x²r`-type conditions unsatisfiable for any proper distribution — fil2104315d (C3)/(C6); arxiv_2104.08525 `w²r_b` decreasing.
5. **Defective printed objects**: fil2104315d's "MOQL baseline" F reaches 2.12 (not a CDF); mia-2020-23-03 Example 3.1's own printed data satisfies every premise and the claim still fails.
6. **Self-contradiction**: am.2018.0105-17 Thm 3.5(a) contradicts its own Thm 3.1(b); Harris-paper Remark 3.1 corrects a cited claim.

## Methodological findings

- **Independent C3 was load-bearing**: 65 of 172 raw refutations did not survive verification — convention-direction misreads (EGG: 14/15 invalid), premise violations (zip-truncation, inadmissible baselines, comonotonicity flips), bounded-scan artifacts, one wrong-generator encoding.
- **Agreed-but-wrong exists**: BJPS-510 Thm 3.9's premise ratio was inverted in BOTH extraction passes; caught only in adjudication.
- **Pilot non-transfer**: the pilot's mia "holds" tested raw-p majorization; the printed hypothesis is h(p)-majorization — canonical evaluation supersedes.

## Limitations

- Frame skews open-access; ~121 candidates had blocked downloads (documented; Unpaywall recovered few).
- ~214 records are copula/dependence-quantified → out of scope; ~368 use unsupported orders (disp/mrl/star/ageing/paper-defined).
- "holds" = bounded-grid survival only, never a proof.
- P1 is a *lower bound*: unverified-ish records can only have added papers; stratification by venue is coarse.
