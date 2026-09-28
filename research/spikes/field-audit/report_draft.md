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

## Verified papers (29)

- **arxiv_1804.04103** — 1 confirmed claim(s): theorem 3.1
- **arxiv_1904.08730** — 1 confirmed claim(s): theorem 3.10
- **arxiv_1905.00425** — 1 confirmed claim(s): theorem 3.4
- **arxiv_2002.12474** — 1 confirmed claim(s): theorem 9
- **arxiv_2503.21275** — 1 confirmed claim(s): section 4.3.2 result — fr error sign (fgmw parallel system
- **arxiv_2601.07249** — 1 confirmed claim(s): theorem 3.2
- **doi_10.1007_s11587-026-01094-9** — 7 confirmed claim(s): theorem 3.1; theorem 3.2; theorem 3.4; theorem 3.5; theorem 3.6; theorem 3.7; theorem 3.8
- **doi_10.1007_s40745-019-00211-w** — 3 confirmed claim(s): section 3.4 unnumbered theorem (hr part; section 3.4 unnumbered theorem (lr part; section 3.4 unnumbered theorem (st part
- **doi_10.1007_s41060-022-00369-2** — 1 confirmed claim(s): theorem 3.10.1
- **doi_10.1007_s44199-026-00167-w** — 1 confirmed claim(s): theorem (section 3.4, unnumbered
- **doi_10.1017_s026996482400007x** — 1 confirmed claim(s): theorem 3.7
- **doi_10.1038_s41598-026-45633-8** — 1 confirmed claim(s): theorem 2
- **doi_10.1080_02331888.2025.2552185** — 6 confirmed claim(s): theorem 3.10; theorem 3.12; theorem 3.18; theorem 3.7; theorem 3.8; theorem 3.9
- **doi_10.11648_j.ijsda.20261201.11** — 3 confirmed claim(s): theorem 9.1 (case ii, hr part; theorem 9.1 (case ii, lr part; theorem 9.1 (case ii, st part
- **doi_10.1214_18-bjps410** — 1 confirmed claim(s): lemma 8(iii
- **doi_10.19139_soic-2310-5070-1872** — 2 confirmed claim(s): section 3.6 theorem (lr; theorem (unnumbered, section 3.6 stochastic order
- **doi_10.21136_am.2018.0105-17** — 1 confirmed claim(s): theorem 3.5(a
- **doi_10.2298_fil2104315d** — 11 confirmed claim(s): corollary 3.1(i; corollary 3.2(ii; theorem 3.1(i; theorem 3.2(i; theorem 3.3(i; theorem 3.4(ii; theorem 3.5(ii; theorem 3.6(ii…
- **doi_10.29020_nybg.ejpam.v18i4.6653** — 3 confirmed claim(s): theorem 1 (hr part; theorem 1 (lr part; theorem 1 (st part
- **doi_10.29252_jss.12.2.395** — 3 confirmed claim(s): theorem 2 (قضیه ٢; theorem 4 (قضیه ۴; theorem 5 (قضیه ۵
- **doi_10.3390_sym13122248** — 1 confirmed claim(s): theorem 5
- **doi_10.35914_mathstat.v2i1.180** — 1 confirmed claim(s): section 10 unnumbered likelihood-ratio ordering claim
- **doi_10.37119_jpss2023.v21i1.637** — 2 confirmed claim(s): theorem (1)(i; theorem (1)(ii
- **doi_10.37119_jpss2024.v22i1.795** — 1 confirmed claim(s): section 10 unnumbered result (likelihood ratio ordering
- **doi_10.3934_math.2024434** — 2 confirmed claim(s): corollary 2; corollary 3
- **doi_10.5539_ijsp.v10n3p8** — 4 confirmed claim(s): section 3.7 unnumbered theorem (hr part; section 3.7 unnumbered theorem (lr part; section 3.7 unnumbered theorem (rh part; section 3.7 unnumbered theorem (st part
- **doi_10.6339_jds.202001_18_1_.0001** — 4 confirmed claim(s): section 4.7, case i (hr part; section 4.7, case i (lr part; section 4.7, case i (rhr part; section 4.7, case i (st part
- **doi_10.66224_jss.20.1.06** — 6 confirmed claim(s): theorem 1; theorem 2; theorem 3; theorem 6(a; theorem 8; theorem 9
- **doi_10.7153_mia-2020-23-03** — 2 confirmed claim(s): theorem 3.3; theorem 3.4
