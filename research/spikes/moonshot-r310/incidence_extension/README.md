# One fixed-remainder exclusion for the R(3,10) search

This package proves a conditional exclusion for sample 19 of a previously
checked set of 128 graphs. No graph **G** satisfies all of these conditions:

- G has 40 vertices, is triangle-free, and is maximal triangle-free.
- Its independence number is at most nine and its minimum degree is at least six.
- A distinguished vertex c has degree six.
- The labelled induced graph **H = G − N[c]** is exactly the 33-vertex graph
  in `data/input.json`.

The canonical adjacency SHA-256 of H is
`159658dd5992a1c1ab00a12917328c9d216cd7ab99e4cc76d5b6d5c6a0ec0fb3`.
Its file checksum differs because the file also contains a trailing newline.
The JSON list gives one integer adjacency mask for each vertex, in order;
bit v in row u records the edge uv, with vertices numbered 0 through 32.

The published count of **113 exclusions among 128 sampled remainders stays
unchanged**. This result concerns the additional minimum-degree and maximality
conditions above. It establishes neither a new Ramsey bound nor a census of
possible remainders. It does not exclude nonmaximal extensions: making such
an extension maximal could change H or the degree of c.

## Verify the result

Use Python 3.10 or later on Linux or macOS. Python's standard library is
sufficient. Download the release archive and its `SHA256SUMS`, then extract
the archive into an empty directory. Check the archive and extracted manifest
against the detached checksums with `sha256sum -c SHA256SUMS` on Linux or
`shasum -a 256 -c SHA256SUMS` on macOS. From the extracted package directory:

```sh
python3 -I -B verify.py .
python3 -I -B test_verify.py --packet . -v
```

The first command must exit zero and print JSON with `"status": "verified"`.
The second runs nine control groups, including rejection of changed inputs,
changed proof bytes, altered scope, incomplete reconstruction and incomplete
proof replay. A nonzero exit, interruption or resource limit means verification
did not finish; it cannot establish the exclusion.

The replay command checks the complete file list, sizes and hashes before
loading any packaged source. It checks the raw graph and all seven recorded
cut witnesses, independently rebuilds the DIMACS formula byte for byte, and
checks every proof addition by reverse unit propagation. It finally checks
the packaged bytes again. Neither command invokes a solver, searches for an
independent set, or enumerates graphs.

The replay allows ten CPU seconds for its checked work and 30 seconds of wall
time. The command also sets an operating-system CPU limit of at most 11
additional seconds, preserving any lower inherited limit. Memory is capped
at 256 MiB of address space on Linux, or a lower inherited limit;
on macOS, the 256 MiB peak-RSS check is cooperative. The package contains less
than 1 MiB of uncompressed file content. No account, network access or
third-party Python package is needed.

An optional second checker is `lrat-trim`:

```sh
lrat-trim --no-trim data/instance.cnf data/proof.lrat
```

Require **both exit status 20 and the line `s VERIFIED`**. This checks the
UNSAT proof; the Python command also verifies the translation from the graph
conditions. The original review accepted this command with an executable
SHA-256 of
`628844d0a1efbbf07b0d00d7e112ed74b945d9afacf27ef58a2a8c76880908e6`.
That platform-specific binary is not distributed here or required for replay.

## Why the formula proves the stated exclusion

Write A for the six neighbours of c. Triangle freedom makes A independent,
and every possible remaining edge joins A to H. The 198 incidence variables
record these choices as six subsets of V(H), called attachment columns.
Each column must be independent in H, must have five through eight vertices,
and must dominate H. The bounds follow from the minimum degree, the edge to
c, and the independent set consisting of c and the column.

Every H vertex must meet at least one attachment, because G is maximal and
c is not adjacent to H. Its incidence count lies between
`max(1, 6 − degree_H(v))` and `9 − degree_H(v)`. The upper bound holds because
a triangle-free graph has an independent neighbourhood. Every nonedge in H
whose endpoints have no common H neighbour must have a common neighbour in
A. These conditions account for all graph degrees, triangles and missing
edges in the fixed layout.

Attachment labels are interchangeable, so the formula sorts the six columns
lexicographically. Equal columns are allowed. Every admissible graph has a
representation satisfying this ordering.

Each of the seven saved cuts supplies an independent eight-set T in H, six
attachment columns, and a reconstructed 40-vertex graph containing a stated
independent ten-set. For each of the 15 pairs B of attachment vertices, the
formula requires at least one edge between B and T. Otherwise B ∪ T would
be an independent ten-set. Adding all 15 clauses preserves the attachment
symmetry. The saved rejected graphs explain the cuts; the independently
checked independence of T makes every one of these clauses necessary.

The final formula has **2,452 variables and 9,838 clauses**: 9,733 structural
clauses and 105 cut clauses. The 188,141-byte text LRAT proof contains 2,326
additions, 4,144 deletions and 3,231 lines. Each addition is checked by reverse
unit propagation until an empty clause is derived. Thus the necessary
conditions are inconsistent, proving the exclusion for this exact H and the
stated class of G.

The portable proof does not need a fresh computation of the independence
number of H: the target assumption already bounds independent subsets of H,
and every cut used here comes with an explicit independent set. It does not
use a census of maximal independent sets or remove the minimum-degree
condition.

## Contents and provenance

`manifest.json` gives the exact scope and a size and SHA-256 for every other
file in the package. `SHA256SUMS`, supplied beside the archive, binds both the
archive and the manifest. The archive contains only these named payloads;
it carries no local execution paths, solver binaries or unrelated runs.

| Files | Purpose |
| --- | --- |
| `data/input.json` | Exact labelled graph H |
| `data/cuts.json` | Seven subsets, columns, rejected graphs and ten-set witnesses |
| `data/instance.cnf`, `data/instance.json` | Final formula and its recorded counts |
| `data/proof.lrat` | Complete RUP-only LRAT proof |
| `source/incidence_extension/` | Original seven source and profile files |
| Other files under `source/` | Four exact dependencies of that source |
| `verify.py`, `test_verify.py` | Portable replay and its focused controls |
| `README.md`, `LICENSE` | Result, instructions and repository license |

The original source bytes are unchanged. `PROFILE.md` documents the historical
pilot, including its search procedure, resource limits and requirement for
independent review. It is not the public replay procedure. The packaged
`run.py` preserves that protocol's implementation; replay uses only the
reconstruction and proof-checking paths.

The original focused controls passed seven groups covering 4,204 complete
incidence assignments on 20 small configurations. An independent result
review accepted the exclusion, checked all seven saved SAT models and ten-set
witnesses, rebuilt all eight formula prefixes, replayed the final proof, and
reconciled the saved process records. The manifest records the SHA-256 of
that historical review and its source/input approvals. Those hashes identify
the retained records; the public proof stands on the included mathematical
inputs and the replay above. The historical review is not redistributed
because it contains local execution details.

The original pilot and its independent review used 1.737013 CPU seconds of
the 60-second pilot allowance. Memory observations were cooperative; 18 short
stages were unsampled. An unsampled process is not evidence of zero memory
use. No solver or graph search was repeated to prepare this publication.

## Repository commands

From the repository root, run wrapper controls that do not need the release
artifact:

```sh
python3 -I -B research/spikes/moonshot-r310/incidence_extension/portable/test_verify.py -v
```

The four exact-packet control groups require `--packet PATH` and are reported
as skipped when that argument is omitted. Replay an extracted package with:

```sh
python3 -I -B research/spikes/moonshot-r310/incidence_extension/portable/verify.py PATH
python3 -I -B research/spikes/moonshot-r310/incidence_extension/portable/test_verify.py --packet PATH -v
```

The publication builder copies only the explicit allowlist, refuses changed
source or data, strips archive owner and timestamp metadata, and creates a
new output directory. It never changes the retained pilot:

```sh
python3 -I -B research/spikes/moonshot-r310/incidence_extension/portable/build_packet.py \
  --run-output runs/moonshot-r310/incidence-extension-20260928/output \
  --output runs/ramsey-incidence-publication
```

The builder assembles the archive; the replay and control commands above
perform verification. These commands do not start the historical pilot.
