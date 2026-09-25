<!-- Round-26 spike memo, frozen 2026-09-24 with PR #35. Spike run directories are
gitignored, so this copy is published here for the public record. The only change
from the frozen file (SHA-256 0613578314464c576a875551b3d42312cc4ec13fad2647d3e1f40dc3d161c39d) is the
ledger sentence in section 6, updated on 2026-09-25 with the public post. -->

# Round 26 memo: no five points on a sphere or plane, frontier cells

Date: 2026-09-24 (America/Puerto_Rico). Branch `research/no-five-frontier`,
stacked on `research/extremal-discovery` (PR #32). Local only (`runs/` is
gitignored); the PR body carries this file's SHA-256.

## 1. Pickup state and a correction

This round resumes the Claude Code session "lab" (itself the continuation of
the Codex thread "alab"). After PR #32 the session had started exact searches
for AlphaEvolve problem 60 in a scratchpad: CP-SAT models (C(3) = 8 and
C(4) = 11 proven optimal with the complete plane/sphere hypergraph; n = 5 left
at 14 <= C(5) <= 20), and C tabu searches (`ls5`, `ls5b`, `ls5h`) plus an
isosceles searcher (`iso`). Twelve `ls5h` runs were still going when the
session hit its usage limit; its monitor had reported two "FOUND n=12 k=33".

Re-verification before any use: 6 of the 8 record-matching sets printed by
`ls5h`/`ls5b` fail the repo verifier (both n = 10, one n = 12, both n = 8,
the n = 9), and `iso`'s "k=90" set fails `isosceles_free`. Two defects:

1. `exact_repair` removed conflicting points and searched for replacements
   without checking that the remainder was already valid, so any conflict not
   touching the removed points survived into a printed "FOUND".
2. The search model treated only spheres and planes through four points. Four
   concyclic (or collinear) points make every fifth grid point degenerate
   (the lifted 4x5 matrix has rank 3), so those quadruples were missing.

`ls5x` (and `iso2`, `sym5`) fix both: repair requires a valid remainder,
concyclic/collinear quadruples block every grid point, the tabu aspiration uses
consistent units, and every set is brute-force re-verified before printing (a
failed self-check aborts). The buggy runs were stopped. Nothing from them was
committed or reported to Ben.

## 2. Ledger audit (retrieved 2026-09-24)

Sources copied under `sources/`:

- AlphaEvolve repository page for problem 60 (JS template; values only in the
  paper/notebook, n = 7..12: 21, 23, 26, 28, 31, 33). Repo last commit
  2026-07-02, unrelated.
- DeepMind issues: #4 (Demonstrandum, C(13) >= 36, 2026-06-13), #6
  (milesandmistakes, through C(20) >= 50, comments to 2026-08-20, including the
  prior-art correction prompted by Ganador1), #7 (Ganador1, two chiral 36-point
  witnesses at n = 13, 2026-08-18). Nothing later on problem 60; #9 (2026-09-04)
  is unrelated.
- Demonstrandum Research artifacts (Zenodo 10.5281/zenodo.20673865, initial
  commit 94db9ed, 2026-06-13): C(13..17) >= 36, 38, 40, 42, 44, all centrally
  symmetric; n = 11/12 symmetric runs plateaued at 30/33; fitted law
  C(n) = floor((5n+7)/2) exact for n = 7..14 (OEIS A047219 is that sequence);
  "best upper bound remains the trivial 4n".
- milesandmistakes/no-five-sphere-grid-certificates v1.1.1 (pushed
  2026-08-20): C(14..20) >= 38, 40, 41, 44, 45, 49, 50; only n = 18..20 called
  "apparently new".
- Numaro NUMARO-2026-009 (2026-07-03): first-known rows C(14..26) >= 34, 35,
  39, 40, 40, 43, 45, 46, 50, 51, 53, 55, 56; reproduced but did not improve
  C(11) = 31 and C(12) = 33; no coordinates or checker published.
- Zenodo search: only the Lazarus n = 13 deposit (2026-08-19). GitHub
  repository search: only milesandmistakes and Ganador1/lazarus-no-five-sphere.
  HuggingFace dougdotcon/douvras-no-5-on-a-sphere-certificates (per the
  search-result card): re-verifies the six AlphaEvolve sets only. OEIS: no entry.
  arXiv 2609.25133 (September 2026) treats no-three-in-line and
  no-four-coplanar in the cube, not this problem.

Best public value per cell on 2026-09-24, with the monotone closure
C(n) >= C(n-1): 36, 38, 40, 42, 44, 45, 49, 50, 50, 50, 51, 53, 55, 56 for
n = 13..26 (n = 21 is the inclusion bound; Numaro lists 46).

## 3. Runs

All on the shared workstation (18 cores, load average 35-80 from other
sessions; each process got roughly half a core). CPU budgets are `clock()`
seconds.

- AlphaEvolve cells, asymmetric `ls5x`, n = 7..12: from scratch at the record
  (growth enabled) and from the AlphaEvolve set at the record plus one. Only
  n = 8 reached its record (23) from scratch; no record plus one.
- Central-symmetric `sym5`, n = 8..12: best 22, 24, 27, 29, 32, all below the
  records (Demonstrandum saw the same). Sanity: `sym5` reaches 34 at n = 13 in
  a minute.
- Embedding test: each public certificate placed in the next grids and grown
  greedily. The n = 20 set extends in 2 of 8 placements in the 21-grid and 18
  of 27 in the 22-grid; Demonstrandum's n = 17 set extends to 45 in the
  18-grid; milesandmistakes' n = 19 set extends to 50 in the 20-grid; its
  n = 17 and n = 18 sets do not extend.
- Frontier `ls5x` chains (commands and iteration counts in the claims file):
  see the results table below.
- Unseeded controls: `ls5x` from a cold start at n = 18, 20, 21 reached 47,
  52 and 55 — matching the seeded bests at n = 20 and 21 — in seconds to
  minutes. The public certificates are a convenience warm start, not a
  requirement; these cells were simply under-searched.
- Isosceles-free 64 (`iso2`): from the 112-point set, best 113 points with 2
  violations; mirror-symmetric 114 with 4 violations.

## 4. Frontier results (freeze 2026-09-24)

| n | registry best | claim | seed set | run |
| --- | --- | --- | --- | --- |
| 17 | 44 | 45 | milesandmistakes 44 (also Demonstrandum 44) | mm44-n17-k45-s790491471 |
| 18 | 45 | 48 | Demonstrandum 44 in the 18-grid | dem44-n18-k46-s908851045 |
| 19 | 49 | 50 | milesandmistakes 49 | mm49-n19-k50-s60067597 |
| 20 | 50 | 53 | milesandmistakes 50 | mm50-n20-k51-s417239277 |
| 21 | 50 | 55 | chain via the 53-point n=22 set | g52-n21-k53-s720026319 |
| 22 | 50 | 58 | same chain | g53-n22-k54-s730191814 |
| 23 | 51 | 59 | same chain | e53-n23-k54-s237969326 |
| 24 | 53 | 62 | same chain | e53-n24-k54-s819521430 |
| 25 | 55 | 65 | same chain via 63-point n=25 set | g63-n25-k64-s512163841 |
| 26 | 56 | 67 | same chain via 63-point n=26 set | g63-n26-k64-s869449535 |

Cells that did not move: n = 13–16 (record-plus-one runs ended with 1–5
degenerate 5-subsets) and n = 7–12.

## 5. Independent verification

Every claimed set passes three checks:

1. `ls5x`'s in-binary brute-force check before printing (`selfcheck=ok` in the
   run logs);
2. the repo verifier `no_five_on_sphere` (4x4 cofactor determinants;
   MAX_POINTS raised to 96 in this PR, covering every claim), and
3. an independent route in `scratch-src/verify5np.py`: the full 5x5 Leibniz
   determinant of lifted rows `[x, y, z, x^2+y^2+z^2, 1]` in int64 over every
   5-subset.

Results at freeze: all ten sets have 0 zero determinants; minimum |det| = 2.
Five-subset counts: n=17: 1,221,759; n=18: 1,712,304; n=19: 2,118,760;
n=20: 2,869,685; n=21: 3,478,761; n=22: 4,582,116; n=23: 5,006,386;
n=24: 6,471,002; n=25: 8,259,888; n=26: 9,657,648. CI re-verifies every claim
through `claims.check` against the registry snapshot; the test suite also
rebuilds `ls5x` and regenerates the n = 20 certificate (k = 52 at it = 59).

## 6. Scope and limits

- Lower bounds only; no optimality claim at any n.
- "Beats the registry" means beats the dated public snapshot audited on
  2026-09-24 (section 2), not a guarantee of worldwide priority; unpublished
  or newer work cannot be excluded. The ten bounds were posted publicly on 2026-09-25 as a comment on DeepMind issue #6
  (https://github.com/google-deepmind/alphaevolve_repository_of_problems/issues/6#issuecomment-5826575488),
  lower bounds only, no priority claim, after a fresh independent re-check
  (0 zero determinants, minimum |det| 2 in all ten sets).
- The n >= 21 gains mostly reflect how weak the public cells were (Numaro
  published no coordinates; unseeded controls reproduce or nearly match the
  seeded results at n = 18, 20, 21). The seed authors are credited in
  `known/record-constructions.json` and each claim derivation.
- The evolution loop contributed nothing this round; the gain came from
  target choice plus exact local search.
- Run logs, point lists and this memo stay local under `runs/` (gitignored);
  `manifest.json` records SHA-256 of every artifact the PR body cites.
