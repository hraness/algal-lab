# Independent review of the degree-six pilot

Agent review, 2026-09-28. This is an implementation and mathematical review,
not human peer review or a new Ramsey-number result. The long pilot was
not run by this reviewer.

## Mathematical coverage

The initial formula soundly covers maximal triangle-free (3,10,40) graphs
whose minimum degree is six. Relabel a degree-six vertex as 0 and its six
neighbors as 1 through 6. Maximal triangle-freeness gives diameter two, so
every other vertex meets this neighborhood. The minimum-degree argument
credited to Pandey–Ravi and the independent-neighborhood upper bound give
degrees in 6 through 9. Other minimum-degree cases remain separate.

The four clauses for each prefix-counter cell encode exactly
`y <=> a OR (x AND b)`. Induction on the prefix length therefore proves
the stated lower and upper degree bounds. Omitting other diameter-two
conditions enlarges the search and does not remove a Ramsey witness.

Every added cut says that one pair in a particular ten-set is an edge.
This is necessary for every target graph, irrespective of which partial
model suggested that cut. Saving complete cut batches that might not all
have reached an interrupted solver also preserves this property.

The exact independent-set checker uses a proper coloring of the complement
to bound a clique extension. A node or time limit raises an exception; it
does not establish absence. The secondary bounded enumeration supplies
checked positive witnesses only. Graph structure, degrees, and center
coverage are checked independently of SAT auxiliary-variable assignments.
Freezing all edge variables makes their later use in incremental cuts valid.
The C function signatures match the installed CaDiCaL 3.0.1 header.

No soundness blocker was found for the stated family. An UNSAT solver status
still needs a fresh proof-producing solve and independent certificate check.
A candidate graph still needs an independent final graph check. The current
implementation does neither conversion into a final Ramsey claim.

## Repair and new checks

The original supervisor handled wall timeout but could abandon its worker
when the supervising wait was interrupted. The reviewed repair collects
only its owned child, escalating from terminate to kill if necessary.
SIGINT/SIGTERM produce an unresolved result, preserve the complete recorded
formula, and return the corresponding `128 + signal` exit status.

The implementation owner's earlier eleven focused controls were reviewed
as existing evidence and were not repeated. The reviewer ran:

```sh
CADICAL_LIBRARY="$PWD/runs/moonshot-r310/native-cadical/libcadical.dylib" /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s research/spikes/moonshot-r310/degree_six -p 'test_review.py' -v
```

All **six new controls passed in 2.812 seconds**. They exercised native
requested interruption; a failing native termination callback; an interrupted
exact graph check; real SIGINT and SIGTERM delivery with the owned worker
confirmed absent afterward; truncated-log recovery and duplicate rejection;
and the cleanup escalation contract.

A fresh one-second normal-stop control used seed 0, batch 16, the 100,000-cut
and 20,000-model limits, and the 1 GiB cooperative memory threshold. It
stopped at its CPU limit after 32 models and 512 cuts, with status
`solver_interrupted`. The worker returned zero; no witness or UNSAT proof
was asserted. Total CPU was 0.928 seconds and peak worker memory was
47,284,224 bytes. The independently counted final DIMACS file contained
63,784 clauses and had SHA-256
`7edcec9ae95205215b253898aa467d4e94c2e2e872a1a1b92fdfbb80b04c34ba`.
The cut count, DIMACS header, saved receipt, and formula hash agreed.
Control artifacts were isolated temporary files, removed after checking.

`git diff --check -- research/spikes/moonshot-r310/degree_six` passed.

## Inspected source and solver

| File | SHA-256 |
| --- | --- |
| `encoding.py` | `13f0fdda77534ac68192ec8e0ab28dd1c0a9543d95b11eb55a59a01607415160` |
| `native.py` | `6581f3ab805375de34e83236459363d00d98af3ee75401be97ad083fd8958777` |
| `run.py` | `0a61ed19b6dde7bde381ca99c2e1e52afec139f03fcb81390fc2697fd529b840` |
| `search.py` | `c2d6a287784800535183db170caa219124af5c2431f0193f0d351975446f0b50` |
| `test_review.py` | `ac1b47ff05adeda2695ba4c33370a35c9ca021d51dc2bec4168c0e3887a60318` |
| `test_search.py` | `b60a32587ec21a3ab20f2a971a8ccb8de20a0885f12a2204a50c8c9510432660` |

The linked library is `cadical-3.0.1`, SHA-256
`12b16587d9be573286520fff1468f54fa0fb46a657bc5db3fd9486d8248bf064`.
It was linked from the existing Homebrew static library, SHA-256
`8bb5e4c5128864e8e5f4e2542d9c828befb416c4cda01460718c6ed561600315`.
The build receipt is in ignored `runs/moonshot-r310/native-cadical/`.
No package or network service was installed for this review.

## Existing edge bound and later strengthening

The bound **e(3,10,40) ≥ 161** is in Jan Goedgebeur and Stanislaw P.
Radziszowski, *New Computational Upper Bounds for Ramsey Numbers R(3,k)*,
The Electronic Journal of Combinatorics **20(1)** (2013), Paper P30,
**Table 5, printed and PDF page 12**, row n = 40.
The preceding paragraph on page 11 explains its derivation from integer
constraints (3) and (4) and the exact e(3,9,n) values in Table 4.
The [original journal PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i1p30/pdf)
was read directly; [arXiv:1210.5826](https://arxiv.org/abs/1210.5826) is the
corresponding preprint record. Pandey–Ravi (2026), Section 3, repeats the bound.

This necessary edge bound is omitted by the frozen initial pilot. Its
omission affects efficiency, not soundness. Adding it and sorting outside
vertices by their six-bit neighborhood in 1 through 6 are reasonable
subsequent changes, requiring their own source review and focused controls.
No claim is made that the current formulation is computationally sufficient
to resolve even the degree-six case within its resource budget.
