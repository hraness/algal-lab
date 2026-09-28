# Independent review of the stronger degree-six profile

Agent review, 2026-09-28. No soundness or reconstruction blocker was found
for the proposed bounded comparison. This review added tests and documentation
only; it did not change the four runtime modules or start a long solver run.
The result is an implementation review, not human peer review, a graph
exclusion, or a new bound on R(3,10).

## Scope and preservation

The reviewed profile covers maximal triangle-free (3,10,40) graphs with
minimum degree six. Choose such a vertex as 0 and label its neighbors
1 through 6. Maximality gives diameter two, hence the required coverage of
all 33 remaining vertices by that neighborhood. The proof does not require
a graph automorphism. Cases with minimum degree seven, eight or nine remain
outside this profile. In particular, excluding this family would not exclude
a nonmaximal degree-six graph whose maximal extension has higher minimum
degree. A directly checked positive graph needs no maximality assumption.

Let A be the six neighbors of 0 and H its 33-vertex anti-neighborhood.
An independent nine-set in H would extend with 0 to a forbidden ten-set.
Thus H is a (3,9,33) graph. The original journal PDF was checked directly:
Goedgebeur–Radziszowski, EJC 20(1) (2013), P30, **Table 4, printed and PDF
page 11**, gives **e(3,9,33) = 118**. Its SHA-256 matches the profile:
`d2abf9b7c2c184869d6d1caa080e47e27cd75d918d8bd541698b2c311572b2cb`.
This is a published premise, not a fresh enumeration by this pilot.

Each degree is six plus the sum of its exact degree-at-least-7, 8 and 9
threshold bits. With their sums T_A and T_H and crossing-edge count c,

```text
c = 30 + T_A,
2 e(H) = 168 + T_H - T_A.
```

Therefore e(H) ≥ 118 is equivalent to T_H − T_A ≥ 68. The 99 negated
H bits and 18 positive A bits have sum 99 − T_H + T_A, so their upper
bound 31 is exact. The counter has 3,248 variables and 12,844 clauses.
The existing full-equivalence counters support signed inputs and expose
the required exact threshold bits; no approximate degree estimate is used.

Sorting H by its six adjacency bits to A preserves a representative of
every qualifying graph. Relabelling H preserves every other graph property;
the auxiliary counter assignments can be recomputed after the relabelling.
The signature comparison forbids precisely a descending first differing
bit, using all shared prefixes. Its 63 clauses per adjacent pair give
2,016 clauses for 33 signatures.

Vertices with the singleton signature for a particular a in A form an
independent set. Any five of them, together with A minus {a}, would be an
independent ten-set. Hence each singleton signature occurs at most four
times. Sorting makes identical signatures consecutive, so the 174
five-row-window clauses impose that cap exactly, including the two endpoint
windows. Every remaining H vertex has at least two neighbors in A by
coverage. Thus c ≥ 66 − 24 = 42, equivalently T_A ≥ 12. The counter on
the 18 negated A bits with upper bound six adds 105 variables and 396
clauses. Consequently e(G) = 6 + c + e(H) ≥ 166 in this case.

These additions account for all **17,933 variables and 78,702 clauses**.
The independent graph recount uses adjacency masks, not auxiliary SAT
values, to check the H edges, crossing edges, signature order, singleton
multiplicities, and implied global edge bound.

## Reconstruction, imports and controls

The supervisor passes the selected profile explicitly to its worker and
uses the same selection when rebuilding the final formula. The worker
records the profile and premises in `instance.json`. Complete logged cuts
remain necessary Ramsey constraints, including a final batch whose complete
submission might be uncertain after interruption. A solver UNSAT answer
still requires a separate proof-producing solve and independent replay.

The runtime checker loads from the exact sibling `vertex_transitive/checker.py`
path with a separate module specification. It does not modify `sys.path`
or rely on an unrelated module named `checker`. The copied runtime needs
the four `degree_six` runtime modules, that sibling checker, and the
explicitly selected solver library. The implementation owner's isolated-copy
control already verifies worker profile selection and the complete rebuilt
base formula; its evidence was reused without repeating the test.

The implementation owner's **26 tests passed in 16.788 seconds**. The reviewer
added three controls and ran only those:

```sh
CADICAL_LIBRARY="$PWD/runs/moonshot-r310/native-cadical/libcadical.dylib" /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s research/spikes/moonshot-r310/degree_six -p 'test_profile_review.py' -v
```

All **three passed in 0.498 seconds**:

- Twenty full-size signed-counter assignments straddle both T_A = 12 and
  T_H − T_A = 68, using valid monotone degree-threshold patterns.
- Seven complete 33-signature sequences check every singleton's four/five
  boundary, including the first and last forbidden windows.
- An isolated source copy loads and exercises the exact checker even when
  both potential module names are prepopulated with an incorrect checker.
  The module search path remains unchanged. An initial assertion compared
  a macOS temporary-directory alias with its canonical path; the test was
  corrected to normalize that path before the passing run.

A separate direct comparison with the previously frozen baseline encoding
confirmed identical baseline clauses, variable counts, edge map and
structural metadata. The profile retains that exact clause prefix and edge
map. With the DIMACS header and one `clause 0` line per clause, the hashes are:

| Initial formula | SHA-256 |
| --- | --- |
| Baseline | `0f55cb008e8373c608361e857d72e8dd3279ddb691affc49abe796808913e744` |
| Stronger profile | `17bedcc200d888417768cf8a0e45549ad6418a5f0007b1b591939ad5544489b5` |

`git diff --check -- research/spikes/moonshot-r310/degree_six` passed.
The long comparison, final integration checks and delivery remain with
the integration owner. No new package or external service was used.

## Reviewed source identities

| File | SHA-256 |
| --- | --- |
| `encoding.py` | `525808c8cb36924c35b5c35cc47055a11976dc20465a22b4be04c921edc6545b` |
| `native.py` | `6581f3ab805375de34e83236459363d00d98af3ee75401be97ad083fd8958777` |
| `run.py` | `bd850996d4d437a7fd644760f22cbdbc2d268c68d950a94de00880218a5c433c` |
| `search.py` | `a1a3c530d975180aa7edefd65141923c44afd72d84511444a59f89a4cbe739d4` |
| `test_profile.py` | `74225d6dcef7d91f5d2d93ac557ea5d5482f76af5ae30c0c528171117bd2e710` |
| `test_profile_review.py` | `2a445a3910510b6b2b21f17143b6c3a5e3a9be67eff615bf1f0a30fd29b338a6` |
| `test_review.py` | `ac1b47ff05adeda2695ba4c33370a35c9ca021d51dc2bec4168c0e3887a60318` |
| `test_search.py` | `b60a32587ec21a3ab20f2a971a8ccb8de20a0885f12a2204a50c8c9510432660` |
| Sibling `checker.py` | `aecfd40ba0e6cda88b72a66c8c03431e1d07301fc4f1665739b7f8e2c0ac5bf1` |

The CaDiCaL 3.0.1 library remains
`12b16587d9be573286520fff1468f54fa0fb46a657bc5db3fd9486d8248bf064`.

## Later observation, absent from this profile

For v in H, d_H(v) must be at least five. Otherwise H minus its closed
neighborhood has at least 28 vertices and, by R(3,8) = 28, an independent
eight-set; adding v contradicts the definition of H. If r is v's number
of neighbors in A and T_v its three higher-degree bits, this is exactly
`r + (3 - T_v) <= 4`, since d_H(v) = 6 + T_v − r. It also excludes
signatures of weight five or six. This sound additional condition was
not added to the reviewed source; a later profile needs its own checks.
