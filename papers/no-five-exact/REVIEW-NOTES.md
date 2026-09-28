# Small-grid evidence audit, 28 September 2026

Reviewer: Codex agent `/root/papers`. This is an agent source-and-evidence review, not human peer review. See `../PUBLICATION-REVIEW.md` for current admission and readiness.

The production n6 enumerator was compared byte-for-byte with the retained run's `layer_enum6b.c`; they agree. The n5 source likewise agrees with the corrected run's source. No full upper-bound traversal was repeated in this review. Large run logs and proof files remain outside the paper distribution.

| Evidence | SHA-256 |
| --- | --- |
| n5 source | `f7976a462a91794cbf7946d81da75b292e05efe2d62f3b6dd14cc8bcb8f3169c` |
| n6 source | `7fb9acfc714b7a2559f636fd06c096da9d8328e2db933fb01e173f8148bdc9e5` |
| n5 corrected exclusion log | `cf10d0fa0080c8c2c351b097650ff6fe4301243f51bacc736349451e99e49021` |
| n6 production exclusion log | `611175fa2de60b7c82cfc9d33b17b9af30662f716cbbc6d065d24a35116c77c2` |

The n5 log has 1,905 distinct completed indices, no PARTIAL markers, and 590,980,794 nodes. The n6 log has 8,175 completed lines, 8,133 distinct indices, no PARTIAL markers, and agreeing counts for 42 repeats. The sum after deduplication is 448,735,206,762 nodes. The `admiss` counter is a prune-event count, not a node count.

The full-cache probe, subset-iterator loop and degenerate-locus defects identified in the attempted independent implementation invalidate those runs as independent evidence. They do not change the production source above. A corrected independent reproduction or separately checked proof remains necessary for a claim of independently certified C(5) or C(6).

The new `verify/check_small.py` imports no search-program code. It uses integer Leibniz determinants and an independently written square-symmetry inventory. Its scope is constructions and initial-layer inventories only.
