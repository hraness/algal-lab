# SNI size-aware train-only intake: pre-access freeze (2026-10-13)

**Agent-decided, owner may revisit. NOT approved for blob fetch, corpus admission or delivery.** Question: can one fixed, new selection of at most 32 previously unattempted train tasks produce **16 independently supported, instance-use-permitted source families for development**? The first-64 pilot stopped at 12 extracted sidecars and 52 failures (46 oversized, six invalid JSON), before rights and alias review. It remains separate and consumed. CLINC150's development-only 193/302 TF-IDF result concerns a different task; no cross-corpus score comparison follows. A higher extraction count alone is not correctness, novelty or practical value.

## Immutable inputs and selection

Source: `allenai/natural-instructions` commit `55a365637381ce7f3748fa2eac7aef1a113bbb82`, root tree `cc84a807512603c2a8e5978cd067f5397dff8edd`. The existing split/task/blob-OID index SHA-256 is `2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38` (756 train / 119 test / 738 excluded); the **already attempted** first-64 selection TSV SHA-256 is `97cb7f38b55869de58e4667f28458d2c1d15799211bfdb9e25d795b9444f0728`. Sorted test **names** (not bodies) have SHA-256 `5f65a29afa7b0c4bbb3b6c4c2b885e03d3c72adb182e67d06f9d91cb87d1d1c0`.

Fetch only the immutable recursive Git **tree metadata** (no `tasks/*.json`) to get its `size` fields. Require the tree SHA above, `truncated: false`, unique paths, valid nonnegative integer blob sizes, and matching OIDs for all 1,613 index rows. Git blob modes `100644` **and** `100755` occur in this tree; neither makes a body eligible independently of its size. The GitHub tree API response bytes used here have SHA-256 `3fe322798aa299fb1c515c2f774329e49226f206b4194d9503f34d9f8fff3930`. The canonical `split<TAB>task<TAB>OID<TAB>size<LF>` manifest in index order has 1,613 rows, 153,763 bytes, SHA-256 `951646cf44809e2b27216ead0c91a94f8d0deb42666a99e39ea09c4ef0b37531`. API-provided size is selection metadata, **not authenticated by the Git tree OID**; a later body must pass its own size/OID check. These metadata-only bytes are preserved privately in `runs/sni-size32-20261013-01/all-task-sizes.tsv`.

Exclude all 64 previous names, filter the remaining **train** entries to `size <= 1,000,000` bytes, sort task IDs by unsigned UTF-8 byte order and take the **first 32**, without balancing or replacement. There are 351 size-eligible unattempted names. The selected sizes total 4,016,222 bytes by tree metadata; the 32-row four-column TSV is 2,794 bytes, SHA-256 **`6ea37fc2bff821ed5cbd5f10352c98b451442f29ee5dbf6bc2029c340c069388`**. Its exact rows, including terminal LF, are:

```tsv
train	task109_smsspamcollection_spamsmsdetection	f8d4f2868b08d8d3b8f526695c4561db2f2b1359	277094
train	task1135_xcsr_en_commonsense_mc_classification	b866bba444c27c21113bf833cb52647a3d759189	323466
train	task1146_country_capital	9c6cd1dabc2b4a9627b63664a891d50d74458bc3	43918
train	task1147_country_currency	316ac24a5b1ec99748c54b98dc91d233d7d7d528	45220
train	task1148_maximum_ascii_value	fa32f2aaed342514ea50fe70410b4e3c8c0bac7d	37584
train	task1149_item_check_edible	e4be0af697f49fee172773c07e02395e5f883cdb	21968
train	task1150_delete_max_min	1073ee796a33a52f6e80966e21f06972b47b8162	54472
train	task1151_swap_max_min	1f7bd61c89475a95dff7c39ad073315b318f9d3f	73593
train	task116_com2sense_commonsense_reasoning	99e803c7a4badb9d8a4dddcf9e8a1d1284ddcbf9	524734
train	task1188_count_max_freq_char	fb101503d813f6fe8a9f383622b2d7951233efc7	43158
train	task1189_check_char_in_string	ed81f4ba27a91ad3ba68ea6e943ac7963917d252	39683
train	task118_semeval_2019_task10_open_vocabulary_mathematical_answer_generation	4658df1f262b569331b2c4fb82e3cc063b5c26c9	113386
train	task1190_add_integer_to_list	a4aecda77fc169b6fdd9ba3826e166e064ab356c	72585
train	task1191_food_veg_nonveg	11e2f95cc0ebdf8a407614f4d7d623031e2820c1	20442
train	task1192_food_flavor_profile	6aed27e0b03f5a87c1c29162af02c178684d9978	40653
train	task1193_food_course_classification	b7707e333e25941f46f1e8162de9d523843d5fca	41988
train	task1194_kth_largest_element	1928b7c2628c9a5087831030b1716ac32ff75dd8	55385
train	task119_semeval_2019_task10_geometric_mathematical_answer_generation	dc09edbcae555f0e0df199da0c2c97f0e86a032f	55217
train	task1208_atomic_classification_xreason	ee681a2b43edc1f70e01a5a85898b6ccd6ebdf42	164352
train	task1216_atomic_classification_causes	af061005903e2f32fdf1668a4525df3f5f03d392	154334
train	task1284_hrngo_informativeness_classification	a4a9303d37014d29e60fe22b976df189bcf4d520	556881
train	task1294_wiki_qa_answer_verification	dfa28c59bbffa51e7081db615dc91ef0bd8178c6	796548
train	task1314_country_abbreviation	d288e4f9efb8813d986990c23e6e05133ecbaabf	43812
train	task1315_find_range_array	2a630665ffd50cbec9c5aa537d22c54a32611088	54661
train	task1316_remove_duplicates_string	a6fcf2327bf4a31faf463868b72412f03a7206f5	43880
train	task1317_country_calling_code	366d8f706afb8b0bee07c41c2814934787f4f407	51128
train	task1318_country_national_dish	0d3348fb0ddc8cd1ba51c39bb46f6c723391f52d	33452
train	task1319_country_by_barcode_prefix	7f9e7d7ce42b3532f12295d9c16f80ef5d977d18	21958
train	task1320_country_domain_tld	a62dfc563fbc005451e83af14fc3504668350197	46940
train	task1321_country_continent	0a8ebc2837c316c447a3c4f5ce76158c00f1c67a	45128
train	task1322_country_government_type	d7f13f6b3473bbd1b1bd824974c2bd0627821bad	47324
train	task1331_reverse_array	85ca1ea02d5fc0e9fd33b5e337676f76a47d88e5	71278
```

The exact plan and selection also live in ignored `runs/sni-size32-20261013-01/`. The first metadata preflight incorrectly rejected a real `100755` task blob; it did not fetch that body. A manual transcription of row 30 initially omitted the last hex character of its OID; the independent comparison caught it, and the row above and private TSV were corrected **before any task fetch**. These are failed pre-freeze checks, not new blob attempts; neither was silently treated as a valid selection.

## Pre-access review and attempt rules

A separate auditor must independently reconstruct index, tree metadata, prior 64 attempted outcomes, all 32 OIDs/sizes and the exact selection digest **before permitting a selected blob fetch**. The author's second Python calculation is a cross-check, not independent-person review. Do not read test-task JSON, labels, instances or outcomes to perform it. This record is frozen pending that review; do not edit the sample to improve its group yield.

Only after that gate, attempt each selected train blob at the pinned commit, at most once, using HTTPS with redirect rejection, 30 seconds per fetch, <=1,000,000 bytes per blob and <=32,000,000 response bytes total; **32 attempts total**, no automatic retry or adaptive fill. Write an exclusive `NN.attempt.json` before each request. Verify the Git SHA-1 over `blob <byte-length>\0<bytes>` against its selected OID **before parsing**. Raw JSON is bounded process memory only. Keep only OID-bound `task`, `Source`, `Categories`, `Instance License` in a closed sidecar. Record exactly one exclusive failure or sidecar per attempt, with a safe error code and observed response-byte count, never upstream raw text. Include timeouts, transport errors, size mismatch, invalid UTF-8/JSON/metadata, OID mismatch and write failures. A missing terminal record, interrupted or uncertain write stops the run unresolved; **do not retry, continue, or call a failure a success**. Aggregate counts and actual bytes from the per-attempt records; no attempt can be hidden by a summary. Zero attempts/failures/unresolved and $0 charged so far in this new intake; model allowance **0 calls / $0**. The first-64 outcomes and charges are not reset.

After extraction, independently check each candidate group's original **instance** terms (definition Apache-2.0 is insufficient), Source aliases and related derivatives, conservative train/test-name intersections and excluded-name bridges; quarantine WSC, SQuAD and QASC relatives and every unknown right or unreviewed alias. Count **source families**, not tasks, and accept only if >=16 are supported independently; otherwise retain the negative intake and stop. Even a positive development pool does not qualify a fresh holdout, six-arm study, prior-art novelty, practical value or paid requests. A genuinely untouched, source-disjoint evaluation set and separate numerical protocol with margins, baselines and full costs remain necessary. Preserve the field-audit correction and draft PR #84 author-response hold.
