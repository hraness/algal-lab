# Review of the degree-six publication changes

AI-agent review, 2026-09-28, against the proposed changes on
`codex/ramsey-degree-six-pilot-20260928`, based on commit
`5a47c4e7558b5a99f041f4fc9e4f7e0adbd2b8a8`.

The reviewed changes add the degree-six search, its focused controls and
reports, links from the repository guides, and native Linux controls in CI.
No remaining code or scientific-claim defect was found in this bounded
review. The final repository checks and the new Linux native build remain
required before integration. This review does not establish a new Ramsey
bound or publication priority, and it is separate from external peer review.

## Scope and consequences

The new command-line driver consumes an explicitly selected local CaDiCaL
library and writes resource-limited search records to a new output directory.
The stronger profile is optional; `baseline` remains the default. Its
incremental cuts and reconstruction logic have the mathematical coverage
described in the [baseline review](REVIEW.md) and
[profile review](PROFILE-REVIEW.md). Other minimum-degree cases remain open.

The direct consumers are the research command-line driver and its tests.
Repository readers reach the reports through README and CONTRIBUTING links.
Operationally, the existing research CI job now checks out CaDiCaL release
3.0.1 at a pinned commit, builds position-independent code, links a local
shared library, and runs the native controls with `CADICAL_LIBRARY` set.
The checkout does not persist credentials, and the workflow retains its
read-only permissions, time limits and required aggregate job. This adds
a compiler and public-source dependency to that job; Linux linking and the
resulting workflow duration need evidence from the actual CI run.

The changed paths do not modify the application runtime, existing research
formulas outside this experiment, deployment configuration or persistent
user data. This change adds no field-audit manuscript, recipient manifest,
courtesy notice or delivery package. Older field-audit material already
exists in the repository; this is a statement about the reviewed changes.

## Evidence checked

- All eight proposed Python files in this directory and the sibling graph
  checker match the exact source hashes recorded for the reviewed stronger
  run. Their identities are listed in [PROFILE-REVIEW.md](PROFILE-REVIEW.md).
- Regenerating both initial formulas from the proposed source reproduces
  the documented baseline and stronger-profile SHA-256 values. The formulas
  have respectively 14,580 variables and 63,272 clauses, and 17,933 variables
  and 78,702 clauses.
- Direct hashing of both retained final formulas and ordered cut logs agrees
  with the run receipts. Each run recorded 6,251 models and 100,000 cuts and
  stopped at the cut limit. The public numerical observations match those
  receipts.
- Direct pairwise adjacency checks confirm the two independent ten-sets
  printed in [RESULTS.md](RESULTS.md). Thus neither final model is a witness.
  Neither run supplies a checked exclusion. The report also correctly
  distinguishes these single-run timings from evidence of search capability.
- The existing focused controls cover signed counters, graph structure,
  label ordering, small positive examples, incomplete formulas, interruptions,
  child collection, truncated logs and isolated source copies. Their earlier
  results were inspected as source-review evidence. The new CI job must run
  the complete native suite on Linux; a run that skips it is insufficient.
- All 105 relative Markdown destinations across the nine publication files
  inspected resolve. The new source and
  reports have no trailing whitespace; `git diff --check` passed.

## Corrections and remaining checks

Two documentation corrections were made: the plan's opening now records
both completed searches, and the README describes the resource budget as
used by the completed runs. No runtime or test source changed during this
review.

The integration owner must run the final aggregate check on the converged
tree and obtain the native Linux CI result. The repository also requires
the pull request to record previous and new workflow timing. Neither a long
search nor an external message was started by this reviewer.
