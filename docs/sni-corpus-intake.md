# Super-NaturalInstructions English: metadata-only intake receipt

**2026-10-08 — stopped before corpus admission.** This is an index and exclusion
receipt, not a frozen experimental protocol, model evaluation, or a fresh
holdout. No paid run was requested; this step's allowance is **$0**.

## Version, rights, and access

- Upstream: [`allenai/natural-instructions`](https://github.com/allenai/natural-instructions),
  commit `55a365637381ce7f3748fa2eac7aef1a113bbb82` (committer date
  2023-03-22), root tree `cc84a807512603c2a8e5978cd067f5397dff8edd`.
  Index collected 2026-10-08; the script uses the immutable tree endpoint,
  not the moving branch. `LICENSE` SHA-256
  `1eb85fc97224598dad1852b5d6483bbcf0aa8608790dcc657a5a2a761ae9c8c6`
  (Apache-2.0); `README.md` SHA-256
  `bd5c0768d317f0184c00afd3233d166672aa63a6fee52fa368f3aa117111ccd7`;
  `splits/README.md` SHA-256
  `db3737ce9310717e3ef6ec6a787b816e8e9249fbbd7c200db365cbbb14ea018c`.
- The README's **License** section applies Apache-2.0 to task definitions **except
  instances** and delegates instance rights to each task's `Instance License`.
  The English split README says train tasks can be used for modeling and test
  tasks are for reporting; its excluded list attempts to remove shared sources.
  This is not a per-task instance-rights grant. Three development-only files
  inspected for a risk probe report `CC BY 4.0` (enhanced WSC, eQASC) and
  `CC BY-SA 4.0` (SQuAD 1.1); no inference about test-task licenses follows.
- The official pinned English lists contain **756 train / 119 test / 738
  excluded** distinct names, covering all 1,613 task JSON blobs in that Git
  tree. The owner's earlier 757 train-task estimate did not apply to this
  revision; the [frozen 64-task pilot](sni-train64-freeze.md) confirmed 756 on
  2026-10-11. This does not resolve rights or source-family separation. List
  SHA-256 digests (train/test/excluded):
  `7ba69b22c1d6096f9747290782e5e0f358728407b065c4bd561fdf4f6239db1c`,
  `8b2068c1e0c5e545abd1172fcf83b17935a791dae19912b5cf68e29355af3cba`,
  `5d1e0c00933ae63ee73a527e9d0e5440527898ed8dbbe49f66e803495319faa8`.
- Every task file has a Git blob **SHA-1 OID** in the pinned tree. Reproduce the
  ordered `split<TAB>task<TAB>blob-OID<LF>` table with
  `bun scripts/sni-intake.ts --out runs/NEW-NAME`; its SHA-256 is
  `2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38`.
  The local private copy is `runs/sni-index-20261008-01/task-blob-oids.tsv`.
  These are Git content OIDs anchored to the commit, **not** raw-file SHA-256
  digests or permission to open evaluation blobs. The script fetches only the
  tree metadata and the three split lists; it never requests `tasks/*.json`.
- Access history for **this step**: no test-task body, `Instances`, example,
  output, label, or score was read. One test-file HEAD and a range GET whose
  response **headers only** were inspected to assess metadata transport; its
  body was closed unread. The three development-task JSON files named above
  were inspected. The owner reports that this repository had not read test
  instances before this step; this receipt cannot audit model-pretraining
  exposure. The public test partition is **not** a fresh holdout.

## Separation risks and non-admission

Official filename membership already contradicts a naive task-ID separation:

| Family to merge before splitting | Train examples | Test examples | Status |
| --- | --- | --- | --- |
| WSC and derivatives | `task276_enhanced_wsc_classification`, `task275_enhanced_wsc_paraphrase_generation`, `task489_mwsc_question_generation` | `task249_enhanced_wsc_pronoun_disambiguation`, `task1390_wscfixed_coreference` | Shared enhanced-WSC name; quarantine the entire source component pending metadata review. |
| SQuAD 1.1 / 2.0 | `task074_squad1.1_question_generation`, `task075_squad1.1_answer_generation` | `task349_squad2.0_answerable_unanswerable_question_classification` | Related dataset versions; quarantine pending provenance review. |
| QASC / eQASC | `task1580_eqasc-perturbed_question_generation`, `task1581_eqasc-perturbed_answer_generation` | `task036_qasc_topic_word_to_generate_related_fact`, `task039_qasc_find_overlapping_words` | Derived/perturbed source risk; quarantine pending provenance review. |

These names identify **risks**, not proof that individual texts duplicate; no
cross-split instance comparison has been run. `src/foundation/sni-intake.ts`
accepts only closed metadata-only sidecars (`task`, `Source`, `Categories`,
`Instance License`), rejects instance/example/output fields, merges semicolon
`Source` aliases plus the explicit WSC/SQuAD/QASC derivative families, and
quarantines a *whole connected source group* when train/test meet, including
links through official excluded tasks. Unknown or unsupported licenses are
excluded. Its diagnostic always says `review-required`: an arbitrary sidecar
cannot authenticate its own extraction, prove rights, cover all paraphrases,
or establish task-family independence. Adversarial tests cover that boundary.

**Stop condition met.** No authenticated metadata-only export of all task
`Source`, `Categories` and `Instance License` fields is available here without
opening public evaluation task JSON (where definition examples and `Instances`
share the file). Therefore rights, group counts, and a nonoverlapping evaluation
pool have **not** been established. Do not fetch those task bodies, admit the
119 test tasks, use their outcomes to select arms, or run cheap headroom yet.
An authorized custodian could supply a commit/blob-bound export of just those
fields, with an auditable extraction procedure that does not release examples
or outputs to the experimenter. The pinned-version 756/757 discrepancy was
reconciled for the [train-only pilot](sni-train64-freeze.md); independently review
all aliases and derived datasets, and retain exclusions and a split/access
ledger before freezing numerical margins, uncertainty, stopping, allowance and
the six-arm protocol. A source-disjoint public split still does not become a
fresh model-pretraining holdout.
