# Claim-shape audit: BMKB2023 — Bhakta, Majumder, Kayal, Balakrishnan

**Paper.** Raju Bhakta, Priyanka Majumder, Suchandan Kayal, Narayanaswamy
Balakrishnan, *"Stochastic comparisons of two finite mixtures of general
family of distributions"*, **Metrika 87(6):681–712 (2024)**; published online
**20 November 2023** — hence "Bhakta et al. (2023)" in BKKA2024 and elsewhere.
DOI `10.1007/s00184-023-00930-4`. Received 27 Nov 2022; accepted 25 Sep 2023.
NIT Rourkela (Bhakta, Kayal) + IISER Thiruvananthapuram (Majumder) +
McMaster (Balakrishnan).

- The task's author guess "Misra?" is wrong: the second author is **Priyanka
  Majumder** (the same Majumder who later co-authors VKF2025 — BMKB is the
  edge through which the cluster reaches IISER-TVM).
- The cluster map's "BMKB2024" and BKKA2024's "Bhakta et al. (2023)" are the
  **same paper** (online 2023 vs print 2024).

## Retrieval status: CLOSED — claim-shape audit via citers

- Abstract retrieved verbatim (Springer page; RePEc agrees). Crossref has no
  abstract; OpenAlex `abstract_inverted_index` null, `is_oa: false`,
  `any_repository_has_fulltext: false`; S2 `openAccessPdf.status: CLOSED`,
  `tldr` null.
- arXiv: **no version exists under any title.** `au:"Raju Bhakta"` (HTTPS API)
  lists exactly five papers: 2311.17568 (BKKA2024), 2412.10071 (BTDK),
  2511.00791 (BGSK), 2501.12179, 2506.05773 — none is this paper.
- No NIT-Rourkela/other repository AM found (the IR record 2080/4938 is a
  KBB-lineage conference presentation, st-only, different paper).

### Abstract (verbatim, Springer)

> "We consider here two finite (arithmetic) mixture models (FMMs) with general
> parametric family of distributions. Sufficient conditions for the usual
> stochastic order and hazard rate order are then established under the
> assumption that the model parameter vectors are connected in p-larger order,
> reciprocal majorization order and weak super/sub majorization order.
> Furthermore, we establish hazard rate order and reversed hazard rate order
> between two mixture random variables (MRVs) when a matrix of model
> parameters and mixing proportions changes to another matrix in some
> mathematical sense. We have also considered scale family of distributions to
> establish some sufficient conditions under which the MRVs have hazard rate
> order. Several examples are presented to illustrate and clarify all the
> results established here."

## Reconstructed theorem map (from citers, verbatim contexts)

| BMKB item | Content | Witness |
|---|---|---|
| Lemma 2.4 | Schur-convexity criterion for additive ψ(α)=Σᵢpᵢηᵢ | BKKA2024: "from Lemma 2.4 of Bhakta et al. (2023) it can be shown that ψ(α) is Schur-convex" (l.1518); B&K-Metrika-2025 uses it for χ(1/β) on E⁺ₙ |
| Thms 3.1, 3.4 | st order under vector majorization (p-larger / reciprocal maj.) | SPBB2026 Rem 6: "Theorems 3.1 and 3.4 of Bhakta et al. [10] can also be seen as particular cases of Theorems 2, 3, and 4" — SPBB's st theorems |
| Thm 4.1 | **hr** under matrix change, GP components | SPBB Rem 8: recovered by SPBB **Thm 8 (n=2 hr)** under GP specialization |
| **Thm 4.2** | **st, n≥3, T-transform lift on the SF** | BKKA2024 Thm 3.5 (n≥3 st, (p,α)∈L_n): "proof … similar to that of Theorem 4.2 of Bhakta et al. (2023). Thus, it is omitted" |
| **Thm 4.3** | **st, n≥3, k-chain of T-transforms (different structures)** | BKKA2024 Thm 3.6: "similar to that of the proof of Theorem 4.3 of Bhakta et al. (2023)" |
| Thm 4.4 | **hr** under matrix change, AL components | SPBB Rem 8: recovered by SPBB **Thm 8 (n=2 hr)** under AL specialization |
| (§4/§5, numbers unrecovered) | rh under matrix change (abstract); scale-family hr (abstract) | abstract only |

## Verdict on the audit questions

**Q3 — is Thm 4.2 the frozen-column lift on a ratio?** **No — it is the
legitimate additive-domain claim.** BMKB Thm 4.2 is transmitted verbatim into
BKKA2024 Thm 3.5, an *st-order* theorem: the functional is the mixture
survival function F̄ = ΣᵢpᵢF̄ᵢ, a sum over columns, so a T-transform on the
2×n parameter matrix acts inside the sum and the n=2 criterion lifts
correctly. Same for Thm 4.3 (different-structure chains → BKKA Thm 3.6) and
Lemma 2.4 (additive Schur-convexity → BKKA Thm 3.3, B&K-Metrika χ). Every
BMKB citation found in the literature invokes **only** its additive
machinery; no citer transmits an hr/rh theorem from it.

**Is BMKB itself a carrier?** The abstract does advertise hr **and** rh "when
a matrix of model parameters and mixing proportions changes" — the
chain-majorization signature. But the only hr items citers recover (Thms 4.1,
4.4) are obtained via SPBB2026's **n=2** theorem (Remark 8), while SPBB's
n≥3 lift theorem (Remark 11) conspicuously does **not** list BMKB next to
BKB2022-Thm 2 / HF2018-3.6/3.10 / GY-2/4. Best reconstruction: §4 pairs
**n=2 rate bases** (4.1, 4.4, presumably rh companions) with **n≥3 st lifts**
(4.2, 4.3) — the same discipline BKF2024 shows (T-lift used only for st,
Thms 11–13) and BKKA2024 shows (§3 chains all st; ratios attacked with
max-gap/min-gap quadruple sums instead). **Verdict: probable clean node for
the lift defect — not a demonstrated carrier.** Residual risk honestly
flagged: BMKB's rh matrix-change theorems are unnumbered in the citer record
and the text is paywalled; if any of them is stated at general n via the
lift, CERT B/C apply.

**Q4 — provenance: is BMKB the entry point?** **No — it postdates the whole
Layer-2 cluster and cites all of it.** Its 20-item bibliography is
essentially the complete lift lineage:

- lift sources: **HF2018** [9], **HKFN2017** [10], **BKB2022** [4],
  **BKZ2021** [5], **NT2022** [15], **PKP2022** [17], **SBB2022** [18];
- sibling/background: KBB2023 [11] (st-only sibling), ASZ2017 [1],
  Navarro–Hernández 2008 [16], Shojaee–Babanezhad Metrika 2023 [20];
- machinery/books: MOA2011 [14], Shaked–Shanthikumar 2007 [19]; plus
  Badia 2002, Bagai–Kochar 1986, Blackstone 1986, Block–Joe 1997,
  Finkelstein–Esaulova 2006, Khaledi–Kochar 2002, Lynch 1999.

BMKB (received Nov 2022) cannot predate BKZ2021 (online Mar 2021) — it
*inherits* from the SPL bridge, not the reverse. In the avalanche it is a
**consolidation node and a citation handle**: BKKA2024, B&K-Metrika-2025,
VKF2025, BKB-SPL24, SPBB2026, BGSK, and the MOTL-G 2026 paper all cite it,
but always for the additive lift (Lemma 2.4, Thms 4.2/4.3) or in review
prose — i.e. it serves the cluster as the "similar to that of Theorem 4.2"
deferred-proof target for **st-order** chain-majorization claims, the role
BKB2022 Lemmas 2.4/2.5 play for the rate claims. If the n=2-rate
reconstruction holds, BMKB is arguably where the Bhakta–Kayal school
*localized* the lift to its legal domain — while importing the defective
ratio machinery separately (as BKKA2024's certified-false Thm 3.10 shows,
the school broke ratios by direct-bound errors rather than by the lift).

## Artifacts

- `crossref.json`, `openalex.json`, `s2.json`, `s2_ctx.json` — records +
  citing contexts (S2 `/citations?fields=contexts`)
- `arxiv_bhakta.xml` — author listing, 5 papers, no BMKB preprint
- `unpaywall.json` — 422 (needs real email); S2 already attests CLOSED
- `mardi.html`, `find.html`, `bhakta_a.html`, `arxiv_test.xml` — retrieval
  probes (MaRDI stub page only)

Verbatim status summary: abstract verbatim; all theorem-level attributions
are via citer quotes (SPBB2026 OA text `shekari2026.txt` l.702–712, 935–945,
BKKA2024 arXiv text l.755, 792, 1518); the paper's own text unretrieved.
