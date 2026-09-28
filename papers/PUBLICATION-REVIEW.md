# Publication review, 28 September 2026

Reviewer: Codex agent `/root/papers`; source and copy review, with computational and PDF checks recorded below. This is an agent review, not human peer review. Author identity was already present in all five source files. Prior referee reports are retained as historical agent-review documents; this note supersedes their stale author-placeholder and unmerged-branch entries.

Owner: Benjamin Guo / Hraness. Evidence check date: 2026-09-28. Reassess: 2026-11-09, or earlier when a cited source or exclusion proof becomes available. No journal submission or acceptance is asserted.

## Softmax thresholds

Reader job: choose a temperature range preserving majorization on a box or fixed-total simplex. The original contribution is the dimension-dependent constants, strict boundary behavior and exact crossover; the generic non-monotonicity observation is credited to earlier Esscher work. The repository owns the proofs and executable rational certificates. Closest papers are Boltzmann purity (optimization of an allocation matrix), hazard mixtures (rates under parameter majorization), and the mixture audit (source-specific counterexamples). This paper owns a distinct domain/temperature classification and should remain separate.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. The partial literature search prevents a priority claim; this is explicit. Agent assistance is visibly disclosed. The ICLR venue claim was removed because the local source records did not consistently establish it; the versioned preprint is cited instead. No invented personal experience appears.

## Boltzmann purity

Reader job: determine when an optimal nested Boltzmann allocation is pure, and how temperature changes the optimal occupancy pattern. The repository owns the structural proofs and independent symbolic/numerical checks. Its closest overlap is the softmax paper's scalar mean; that paper does not classify allocation optima. The hazard paper and cluster audit concern a different probabilistic model. This manuscript has an independent theorem and reader task, so remains separate.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. Claims of first priority remain qualified; some related sources were unavailable. Numerical grid maxima are explicitly checks, not proofs. The AI disclosure now distinguishes script checks from formal proof verification.

## Hazard mixtures

Reader job: determine which hazard-order conclusions survive majorization and construct exact crossing examples. The manuscript owns equal-weight constructions, crossing analysis and small certified witnesses. The cluster audit uses one such mechanism across published statements; it does not replace this self-contained mathematical treatment. The softmax and purity papers share exponential weights but answer different questions. Retain the paper and use one companion reference for the audit.

Admission: utility 2, original evidence 2, factual confidence 2, host fit 2, voice integrity 1, maintenance 2 = 11/12. Proof checking is described as mathematical and computational agent review, not formal certification or human review. Exact script provenance is retained.

## Mixture claim audit

Reader job: identify the precise hypothesis and algebraic step behind a claimed mixture-rate ordering before using it. Its contribution is a source-indexed collection of explicit rational counterexamples, a correct additive-lift argument, and distinguished source-access levels. The companion hazard paper owns the general equal-weight mechanism; the audit owns the cross-paper statement and script map. The softmax and purity papers concern different target models. Retain as an audit with calibrated attributions.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. Unavailable original texts prevent direct attribution of reconstructed claims. This review removes suggestions of fabrication, institutional blame and an inferred original-proof defect. SPBB's parameter-monotonicity hypothesis forces a parameter-independent distortion family; it does not force D(u)=u. The PHR crossing witnesses omit that hypothesis and are explicitly not counterexamples to the literal theorem. The rational, Sturm, interval and numerical evidence classes are separated. Previously gitignored BKF and additive-lemma scripts are now portable manuscript supplements.

## Small-grid enumeration

Reader job: distinguish certified constructions and recorded refutations from candidate exact values in a finite extremal search. The repository owns coordinates, enumerator sources and solver/checker records. The other four manuscripts do not study integer-grid geometry. This paper's independent output is a corrected reproducibility and evidence audit, so it remains useful even without claiming an independently certified C(6).

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. C(3)=8 and C(4)=11 rely on existing recorded independent LRAT checking; their full proof files were not rerun here. Fresh integer checks cover all four lower-bound constructions and both larger orbit inventories. C(5)=14 and C(6)=18 are candidate exact values supported by completed corrected single-implementation searches. Attempted independent runs were invalidated by implementation defects; no independent larger exclusion is claimed. The false fitted formula, priority claim, layer predicate, table-memory estimates, entrywise-selftest claim and node counts were corrected.

## Validation

Completed on 28 September 2026. Python checks used CPython 3.12.14, SymPy 1.14.0 and mpmath 1.3.0; the Boltzmann numerical checks used NumPy 2.5.3. `python` below denotes that interpreter. These checks corroborate the stated calculations; they are not machine-checked proofs of every theorem.

| Manuscript | Fresh validation | Result |
| --- | --- | --- |
| Softmax thresholds | `python verify/identities.py`, `python verify/roots.py`, `python verify/counterexamples.py`, `python verify/violations.py`, from the paper directory | All completed successfully; exact identities, root certificates and the stated boundary counterexamples passed. |
| Boltzmann purity | `python verify/identities.py`, `python verify/occupancy.py`, `python verify/negative_outer.py`, `python verify/additive_boundary.py`, from the paper directory | All completed successfully; the numerical scripts reported `FAILURES: none`. The separate historical brute-force program was not rerun. |
| Hazard mixtures | `python verify/verify_core.py`, `python verify/verify_general_mechanism.py`, `python verify/verify_strict_variant.py`, `python verify/verify_two_crossings.py`, `python verify/verify_reversed_hazard.py`, from the paper directory | 110 passed, 0 failed, across five programs. |
| Mixture claim audit | `python verify/bkf2024/sturm_cert.py` and `python verify/bhb2022/audit_bhb.py`, from the paper directory; review of the cited per-claim memos and retained certificates | The four whole-interval checks passed; additive identities, 731 admissible three-column instances, the nonseparability witness and the exact differential value 25/11 agreed. This does not claim a fresh rerun of every historical cluster search. |
| Small-grid enumeration | `python papers/no-five-exact/verify/check_small.py`, from repository root | All four configurations passed independent integer determinant checks; the two orbit inventories are 1,905 and 8,133. Completed production logs were counted and source hashes compared as recorded in `no-five-exact/REVIEW-NOTES.md`. No full upper-bound search was rerun by this reviewer. |

All five sources were copied with their bibliography and figure dependencies to a temporary build directory, built with `tectonic --only-cached --keep-logs main.tex`, and their PDFs rendered with Poppler. The final PDFs are installed beside their sources. Every page was visually inspected, including full-size checks of the audit's dense tables and the longest paper's final references. A stranded one-entry final page was removed from the Boltzmann paper; the audit's table spacing and bibliography pagination were corrected. No missing citations, undefined references or overfull boxes remain in the final build logs. A minor underfull box in the softmax bibliography has no visible layout defect.

| PDF | Pages | Agent disposition |
| --- | --- | --- |
| `softmax-thresholds/main.pdf` | 18 | Ready for publication as a research manuscript with the bounded novelty search stated. |
| `boltzmann-purity/main.pdf` | 24 | Ready for publication as a research manuscript with numerical and source-access limits stated. |
| `hazard-mixture/main.pdf` | 17 | Ready for publication as a research manuscript with computational checks and agent assistance disclosed. |
| `mixture-cluster-audit/main.pdf` | 12 | Ready for publication as a calibrated audit; unavailable originals remain a limit on attribution, not a hidden pending claim. |
| `no-five-exact/main.pdf` | 5 | Ready for publication as an evidence and reproducibility report; not as independent certification of C(5) or C(6). |

`git diff --check -- papers` passed. The integration owner owns the repository-wide final gate, independent integration review and publication delivery. No external submission, publication or human review was performed by this reviewer.
