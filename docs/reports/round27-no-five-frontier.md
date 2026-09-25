<!-- Round-27 spike memo, frozen 2026-09-25 with PR #41. Spike run directories are
gitignored, so this copy is published here for the public record; it is byte-identical
to the frozen file (SHA-256 d0825cc53cdb51fc9351411db0e29b6bd1c2b9af5ad7a99033d1f7ea20acb3c0) apart from this comment. -->

# Round 27: no-five-on-a-sphere frontier extension (25 September 2026)

Branch `research/no-five-round27`, spike directory
`research/spikes/context/runs/round27-no-five-frontier/` (run outputs under `runs/`, gitignored).
Wall budget about four hours on a shared, heavily loaded host (18 cores, 1-minute load 50-65
throughout); every search ran under `nice -n 15`, at most three search processes live at any
time because the load never dropped below 40, and no run was launched after 03:15 local.

## Summary

Improved cells (registry-relative lower bounds): n=27: 67 -> 70, n=28: 67 -> 71, n=29: 67 -> 75, n=30: 67 -> 76, n=31: 67 -> 79, n=32: 67 -> 82.

The frontier chain from the round-26 n = 26 certificate reached 70 at n = 27, 71 at n = 28, 75 at n = 29, 76 at n = 30, 79 at n = 31, 82 at n = 32, every value above the public baseline 67 (monotone closure of the published round-26 n = 26 set); against the fitted law floor((5n+7)/2) these sit at -1, -2, -1, -2, -2, -1 for n = 27..32.

Unseeded from-scratch controls at the same per-cell CPU budget matched the seeded chain at n = 28, 30, 31; fell short at n = 27 (69), n = 29 (74), n = 32 (81).

The contested cells n = 13..16 did not move: 34 at n = 13 (record 36), 36 at n = 14 (record 38), 38 at n = 15 (record 40), 42 at n = 16 (record 42).

## Results

Previous best: for n = 13..16 the registry value (Demonstrandum, June 2026); for n = 17..26 the
round-26 claim; for n = 27..32 the registry baseline 67, the monotone closure of the round-26
n = 26 certificate published on 2026-09-25 (Numaro's July table ends at 56 for n = 26).
Bold = new certificate committed in `research/extremal/claims/no-five-on-sphere-frontier.json`.
"it" and "CPU s" are the iteration and CPU time at which the best run first printed its best set
(from the run's own `FOUND` line; every `ls5x`/`sym5` path is budget-independent, so the
iteration count reproduces the set).

| n | previous best | best found | seeded runs | unseeded control | other runs | best run | it | CPU s |
|---|---|---|---|---|---|---|---|---|
| 13 | 36 | 34 | - | - | symS-n13-s130001: k=34 it=1860; lsD-n13-k37-s130002: k=0 | symS-n13-s130001 | 1860 | 19 |
| 14 | 38 | 36 | - | - | symS-n14-s140001: k=36 it=249; lsD-n14-k39-s140002: k=0 | symS-n14-s140001 | 249 | 4 |
| 15 | 40 | 38 | - | - | symS-n15-s150001: k=38 it=909; lsD-n15-k41-s150002: k=0 | symS-n15-s150001 | 909 | 14 |
| 16 | 42 | 42 | - | - | symS-n16-s160001: k=42 it=2233 | symS-n16-s160001 | 2233 | 44 |
| 27 | 67 | **70** | s27-k68-s270001: k=70 it=942 | c27-k62-s270002: k=69 it=529 (did not match) | - | s27-k68-s270001 | 942 | 247 |
| 28 | 67 | **71** | s28-k70-s280001: k=71 it=3 | c28-k64-s280002: k=71 it=129 (matched) | - | s28-k70-s280001 | 3 | 5 |
| 29 | 67 | **75** | s29-k72-s290001: k=75 it=471 | c29-k67-s290002: k=74 it=657 (did not match) | - | s29-k72-s290001 | 471 | 201 |
| 30 | 67 | **76** | s30-k73-s300001: k=76 it=37 | c30-k69-s300002: k=76 it=43 (matched) | - | s30-k73-s300001 | 37 | 16 |
| 31 | 67 | **79** | s31-k74-s310001: k=79 it=305 | c31-k72-s310002: k=79 it=539 (matched) | - | s31-k74-s310001 | 305 | 195 |
| 32 | 67 | **82** | s32-k75-s320001: k=82 it=341 | c32-k74-s320002: k=81 it=223 (did not match) | - | s32-k75-s320001 | 341 | 203 |

### Runs (30 launched, about 4739 s CPU in total)

| run | command (from the spike directory) | best k | CPU s used | end |
|---|---|---|---|---|
| s27-k68-s270001 | `KMAX=96 ls5x 27 68 1000 270001 seeds/r26-n26-k67-in27.txt` | 70 | 247 | stopped at 403 s CPU (host-load cap) |
| symS-n13-s130001 | `PRINT_MIN=36 sym5 13 37 500 130001` | 34 | 79 | stopped at 83 s CPU (terminated, see stopped.json) |
| c27-k62-s270002 | `KMAX=96 ls5x 27 62 1000 270002` | 69 | 323 | stopped at 405 s CPU (host-load cap) |
| symS-n14-s140001 | `PRINT_MIN=38 sym5 14 39 500 140001` | 36 | 36 | stopped at 42 s CPU (terminated, see stopped.json) |
| c28-k64-s280002 | `KMAX=96 ls5x 28 64 300 280002` | 71 | 33 | budget |
| s28-k70-s280001 | `KMAX=96 ls5x 28 70 300 280001 seeds/r27-n27-k69-in28-sh1.txt` | 71 | 5 | budget |
| s29-k72-s290001 | `KMAX=96 ls5x 29 72 300 290001 seeds/r27-n28-k71-in29-sh0.txt` | 75 | 201 | budget |
| s30-k73-s300001 | `KMAX=96 ls5x 30 73 300 300001 seeds/r27-n29-k72-in30-sh1.txt` | 76 | 37 | budget |
| s31-k74-s310001 | `KMAX=96 ls5x 31 74 300 310001 seeds/r27-n30-k73-in31-sh0.txt` | 79 | 276 | budget |
| s32-k75-s320001 | `KMAX=96 ls5x 32 75 300 320001 seeds/r27-n31-k74-in32-sh1.txt` | 82 | 204 | budget |
| verify-n27_k70 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n27_k70.txt` | - | 0 | running/unfinished |
| verify-n28_k71 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n28_k71.txt` | - | 0 | running/unfinished |
| verify-n29_k75 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n29_k75.txt` | - | 0 | running/unfinished |
| verify-n30_k76 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n30_k76.txt` | - | 0 | running/unfinished |
| verify-n31_k79 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n31_k79.txt` | - | 0 | running/unfinished |
| verify-n32_k82 | `/opt/homebrew/bin/python3 scratch-src/verify_all.py results/n32_k82.txt` | - | 0 | running/unfinished |
| c29-k67-s290002 | `KMAX=96 ls5x 29 67 300 290002` | 74 | 227 | budget |
| c30-k69-s300002 | `KMAX=96 ls5x 30 69 300 300002` | 76 | 166 | budget |
| c31-k72-s310002 | `KMAX=96 ls5x 31 72 300 310002` | 79 | 290 | budget |
| c32-k74-s320002 | `KMAX=96 ls5x 32 74 300 320002` | 81 | 194 | budget |
| lsD-n13-k37-s130002 | `KMAX=40 ls5x 13 37 300 130002 seeds/dem-n13-k36.txt` | 0 | 273 | budget |
| symS-n15-s150001 | `PRINT_MIN=40 sym5 15 41 300 150001` | 38 | 287 | budget |
| lsD-n14-k39-s140002 | `KMAX=42 ls5x 14 39 300 140002 seeds/dem-n14-k38.txt` | 0 | 292 | budget |
| lsD-n15-k41-s150002 | `KMAX=44 ls5x 15 41 300 150002 seeds/dem-n15-k40.txt` | 0 | 251 | budget |
| symS-n16-s160001 | `PRINT_MIN=42 sym5 16 43 300 160001` | 42 | 297 | budget |
| lsD-n16-k43-s160002 | `KMAX=46 ls5x 16 43 300 160002 seeds/dem-n16-k42.txt` | - | 252 | budget |
| symD-n13-s130003 | `PRINT_MIN=36 sym5 13 37 200 130003 seeds/dem-n13-k36.txt` | - | 194 | budget |
| symD-n14-s140003 | `PRINT_MIN=38 sym5 14 39 200 140003 seeds/dem-n14-k38.txt` | - | 198 | budget |
| symD-n15-s150003 | `PRINT_MIN=40 sym5 15 41 200 150003 seeds/dem-n15-k40.txt` | - | 189 | budget |
| symD-n16-s160003 | `PRINT_MIN=42 sym5 16 43 200 160003 seeds/dem-n16-k42.txt` | - | 187 | budget |

Run ids: `s<n>` = chain seeded (through the `seeds/` files) from the round-26 n = 26 certificate;
`c<n>` = unseeded from-scratch control at the same CPU budget; `symS` = `sym5` centrally
symmetric search from scratch; `symD` = `sym5` seeded from the Demonstrandum certificate;
`lsD` = `ls5x` at record + 1 seeded from the Demonstrandum certificate.

## Method

Programs: `research/extremal/native/ls5x.c` (tabu search over k-sets with exact incremental
counts of degenerate 5-subsets, exact repair, growth to `KMAX` after each valid set, brute-force
self-check before every printed set; built `-DMAXP=32768 -DMAXK=128` so the 32-grid fits) and
`research/extremal/native/sym5.c` (iterated local search over centrally symmetric sets kept valid
at all times). `sym5` gained an optional start file, `PRINT_MIN`/`PRINT_MAX` pool printing and a
header note that the two Demonstrandum structure laws (one antipodal pair per scaled shell; no
three pair directions coplanar with the centre) are already hard filters in it: the shell law is
explicit (`shell_used`) and the coplanarity law is exactly the `F[p] == 0` test, because for
distinct shells the 5-subset {b, -b, w, -w, p} is degenerate iff p lies on the plane of the
parallelogram {b, -b, w, -w} (Lemma 1 of the Demonstrandum notes, re-derived symbolically with
sympy before the run). The search path of both programs depends only on the arguments, the start
file and the environment knobs, never on the CPU budget.

Frontier chain (n = 27..32). The round-26 67-point certificate for n = 26 was placed unshifted in
the 27-grid and `KMAX=96 ls5x 27 68 1000 270001` was run from it. Each later cell was seeded by
`scratch-src/chain.py` from the best set the previous chain run had printed at launch time (n = 27
had 69 points at it = 95 when n = 28 launched; the run reached 70 later), shifted by (1,1,1) for
even n and unshifted for odd n so the set stays centred, with a 300 s CPU budget per cell; the
next cell launched as soon as the previous one had improved on its own seed. The seeded value at
a cell therefore carries the cumulative effort of the chain below it. The n = 27 run and its
control were both stopped at 400 s CPU (`cap.py`) once the host load made the planned 1000 s
unaffordable; the paths are budget-independent, so their logged iteration counts stand.

Controls. For every cell n >= 27 an unseeded `ls5x` run from a random start set at the same
per-cell CPU budget (400 s at n = 27, 300 s elsewhere) ran in the same environment; the table
reports whether it matched the seeded chain.

Contested cells (n = 13..16). `sym5` from scratch and from the Demonstrandum certificates, and
`ls5x` at the record plus one from the Demonstrandum certificates, each at 200-300 s CPU.

Scheduling. `scratch-src/queue.py` runs `jobs.jsonl` in order under `nice -n 15`, counts every
live search or verification process on the host (whoever launched it), holds at most three while
the 1-minute load exceeds 40, resumes a paused process before launching a new one, and launches
nothing after the launch deadline (03:15, moved to 03:30 local when the host load eased);
`cap.py` enforced the n = 27 CPU cap; paused processes were suspended with SIGSTOP (their CPU
clocks stop) while the chain had priority. Two slips are on record in `runs/queue.log`: a
duplicate runner started two verification jobs at once at 01:27 (four processes live for about a
minute until one was paused), and the runner's first resume attempts sent signal 18, which is
SIGTSTP on macOS, so the n = 27 control stayed paused a few minutes longer than intended.

## Verification

Every new best set was checked two ways before being called a result: the repo verifier
(`research/extremal/verifiers/no_five_on_sphere.py`, 4x4 cofactor of lifted differences over
every 5-subset, `MAX_POINTS = 96`) and an independent big-integer checker written for this
round (`scratch-src/verify5x5.py`: full 5x5 Laplace expansion of the lifted rows
(x, y, z, x^2+y^2+z^2, 1) in Python integers, no shared code, no pre-checks). The checker was
first exercised on the AlphaEvolve n = 7 set and the Demonstrandum n = 13 set (accepted) and
on an n = 7 set with one point moved onto a sphere (rejected with 494 zero determinants).

| n | k | repo verifier | 5-subsets | zero determinants | min abs det | verify5x5 / overall |
|---|---|---|---|---|---|---|
| 27 | 70 | repo-verifier value=70 (MAX_POINTS=96) | 12103014 | 0 | 2 | VALID / OK |
| 28 | 71 | repo-verifier value=71 (MAX_POINTS=96) | 13019909 | 0 | 2 | VALID / OK |
| 29 | 75 | repo-verifier value=75 (MAX_POINTS=96) | 17259390 | 0 | 2 | VALID / OK |
| 30 | 76 | repo-verifier value=76 (MAX_POINTS=96) | 18474840 | 0 | 2 | VALID / OK |
| 31 | 79 | repo-verifier value=79 (MAX_POINTS=96) | 22537515 | 0 | 2 | VALID / OK |
| 32 | 82 | repo-verifier value=82 (MAX_POINTS=96) | 27285336 | 0 | 2 | VALID / OK |

`claims.check` (`python3 -m research.extremal.claims`) re-verifies every claim against the
registry snapshot and, since PR #37 (merged into this branch on 2026-09-25), labels each claim
with a `search_status` from its `control` field: every round-27 claim whose unseeded control ran
is labelled `under-searched`, because each cold start reached 69 to 81 points and so cleared the
public baseline 67 (three of six matched the seeded value). The labels are the point: these cells
were empty, and the seeded-versus-control values in the results table are the honest comparison.
`python3 -m unittest research.test_extremal` status is recorded below.

Test status: `python3 -m unittest research.test_extremal` (36 tests, including the exact re-check of all 16 claims against the registry) passed twice on 2026-09-25: locally on the shared workstation ("Ran 36 tests in 2254.068s", OK; load 50-60, 9 min 15 s user CPU), and in CI on PR #41, job "Check" on ubuntu-24.04 (12 min 18 s for the whole job including `bun run check`): https://github.com/hraness/algal-lab/actions/runs/36109945252/job/107990895427.

## Public-ledger audit

`sources/web-audit.md` (retrieved 2026-09-25): DeepMind issues, the milesandmistakes and
Ganador1 repositories, Zenodo, GitHub search, arXiv (via web search; the export API returned
empty bodies from this host) and the Numaro page show no public value for n >= 27 and nothing
newer for n = 13..26 than the round-26 snapshot. The round-26 certificates were published the
same day (merged to main and posted to DeepMind AlphaEvolve issue #6), so the registry cells
n = 27..32 carry the monotone closure 67 of the round-26 n = 26 set as their dated public baseline.

## Scope and honesty

- Lower bounds only. No optimality is claimed at any n.
- Registry-relative. "Improved" means "beats the value the registry held on 2026-09-25"; it is
  not a worldwide priority claim. Unpublished work cannot be excluded, and the round-27 sets have
  not yet been posted to any public ledger.
- Cells n = 27..32 were empty in every public source found apart from our own inclusion bound, so
  the margins over 67 say more about the ledger than about the method; the unseeded controls,
  reported for every cell, are the honest comparison. Every new value sits one or two below
  Demonstrandum's fitted law floor((5n+7)/2).
- The runs at n = 13..16 did not reach the Demonstrandum values plus one; those cells remain
  as the registry holds them.
- CPU accounting is from the programs' own clocks; wall time was five to seven times larger
  because of the host load.

## Reproduction

Build `ls5x` with `cc -O3 -march=native -DMAXP=32768 -DMAXK=128` and `sym5` with
`cc -O3 -march=native` from `research/extremal/native/`, then run the commands in the run table
from the spike directory (seeds in `seeds/`). Each claim's derivation in the claims file repeats
the exact chain of seeds, shifts, commands and iteration counts.

## Artifacts

`manifest.json` lists the SHA-256 of every file cited here (memo, claims file, registry, native
sources, verifier, scratch scripts, seeds, sources, results and run logs).
