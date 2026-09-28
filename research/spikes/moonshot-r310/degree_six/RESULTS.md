# Two inconclusive degree-six searches

Neither run found a triangle-free 40-vertex graph with independence number
at most nine, and neither established an exclusion. Both stopped at the
predeclared 100,000-cut limit. The final models still contain independently
checked independent ten-sets. **Neither Ramsey bound changes.**

## Scope and method

The baseline searches a necessary-condition relaxation of maximal
triangle-free graphs with a degree-six vertex, minimum degree six and
maximum degree nine. The [stronger profile](PROFILE.md) adds the published
118-edge bound on the 33-vertex remainder, an ordering of interchangeable
labels, and private-neighbor and attachment bounds. These restrictions
preserve every eligible graph in this degree case. Neither run covers
minimum degrees seven, eight or nine.

An incremental CaDiCaL solver proposes structural models. An exact graph
check supplies independent ten-sets; each becomes a 45-literal clause
requiring an edge within that set. A model of only the accumulated clauses
is not a Ramsey witness. All recorded cuts are necessary conditions, but
the cut limit prevents these trials from exhausting the full formula.

## Fixed settings and observations

Both runs used seed zero, batches of 16 cuts, a 20,000-model ceiling,
100,000 cuts and a 600-CPU-second budget on one core. The cooperative stop
was 590 CPU seconds, the worker's hard CPU limit 595 seconds and the
supervisor's wall limit 660 seconds. The cooperative memory threshold was
1 GiB; file size was limited to 256 MiB. Every exact graph check had a
two-second and one-million-node limit. Runs used Python 3.14.6 and
CaDiCaL 3.0.1 on macOS arm64, with separately frozen source copies.

| Observation | Baseline | Stronger profile |
| --- | ---: | ---: |
| Initial variables | 14,580 | 17,933 |
| Initial clauses | 63,272 | 78,702 |
| Returned models | 6,251 | 6,251 |
| Saved independent-set cuts | 100,000 | 100,000 |
| Final clauses | 163,272 | 178,702 |
| Total CPU seconds, worker and supervisor | 281.690 | 153.808 |
| Total wall seconds | 376.928 | 176.199 |
| Reported peak worker bytes | 90,488,832 | 165,838,848 |
| Exit status | Cut limit | Cut limit |

These are single observations with different formulas, model sequences and
host conditions. The timing difference is not evidence of an improved
ability to decide the problem. The matching model counts arise from the
same batch and cut limits.

## Verification after stopping

Both runs exited cleanly. Their source hashes matched their frozen copies;
their saved formulas reconstructed from those copies and their ordered cut
logs. Every mask contains ten distinct valid vertices, and every saved cut
matches the 45 positive edge variables for its mask. Each final graph
satisfies every recorded cut but fails the full independence requirement:

- Baseline: `{0,7,8,9,10,18,19,23,29,30}` is independent.
- Stronger profile: `{0,7,8,9,10,22,26,27,33,36}` is independent.

An independently written bitset search found the second set in 18 recursive
calls; direct pairwise checks confirmed it. Independent recounting of that
model found 118 edges in the remainder and 43 attachment edges. Its six
private-neighbor classes have sizes `4,3,4,4,4,4`; its sorted signatures,
degrees, symmetry of adjacency and absence of triangles were also checked.

| Retained object | SHA-256 |
| --- | --- |
| Baseline final DIMACS | `6f6e9ab1c189dcf18863fa24741431a8e6f00a3b15b44935dae93dd7a639f2b7` |
| Stronger final DIMACS | `d32bd889fca0966ebfeea9e46894f1e149e7b6fd69bccb7d0c6f46d0d101fa96` |
| Stronger ordered cut log | `a9921de4ef8466ef6bbdc65120452a666fd3c38f1e76fe5fa62a633b4d74e6df` |
| Stronger source manifest | `24b833a51abe3ce02ff232136b0c1b33b603e68f7e82498a254f9a81fe108a44` |
| Linked solver library | `12b16587d9be573286520fff1468f54fa0fb46a657bc5db3fd9486d8248bf064` |

Generated evidence remains under ignored `runs/`. Source identities,
mathematical review and focused control results are recorded in
[the baseline review](REVIEW.md) and [the profile review](PROFILE-REVIEW.md).
Together the implementation and independent reviewers ran 29 passing
focused tests, including real process interruption and isolated-source
reconstruction. These were AI-agent reviews, separate from external peer
review and from any determination of publication priority.

The next research question is which smaller subproblems can be exhausted
with independently checked certificates. Repeating these limited searches
does not establish a Ramsey result.
