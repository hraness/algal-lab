# Extremal-construction discovery loop

Status: loop and first bounded runs (round 25); ten certificate-backed lower
bounds for the no-five-on-a-sphere problem at n = 17–26 (round 26),
both 24 September 2026. The round-26 constructions came from a hand-written C
local search seeded with public certificates, not from the evolution loop.
Registry significance fields and a mandatory unseeded control per claim
followed on 25 September 2026, after the control runs described below.

## Why a second loop

Every theorem in this lab so far came from one narrow model family whose
literature is small and unindexed. Priority for each result rests on a
web-search audit, so the ledger can only say "not located", never "novel".
This loop targets the opposite regime: problems where a public, dated table
records the best construction anyone has certified, and where an exact
verifier decides in seconds whether a candidate beats it. There, novelty is a
strict inequality against a cited number, not a literature judgement.

The loop is deliberately cheap. Candidates are short Python programs, the
mutation operator is either a scripted parameter perturbation (no model) or a
stateless local model call (Qwen3-8B 4-bit through `mlx_lm` on this
workstation; about twenty seconds per proposal, no API credentials), and every
evaluation is an exact rational check. Nothing in the loop needs a frontier
model. A frontier model can be plugged in through the same command interface
when a target justifies the spend.

## Targets (`research/extremal/registry.json`, retrieved 24 September 2026)

Chosen from a survey of the AlphaEvolve repository of problems (67 rows),
follow-up work through September 2026, and the classical covering tables
(memo in the round-25 spike directory). Selection criteria: an exact
integer or rational verifier, a small object a short program can build, and
a public dated ledger so that "better" is a strict inequality.

| Target | Objective | Recorded best | Ledger | Verifier reproduces the published construction |
|---|---|---|---|---|
| Isosceles-free subset of the 64×64 and 100×100 grid | maximise size | 112, 164 | AlphaEvolve problem 59 (page says "still not optimal") | yes, both |
| No five points on a sphere or plane in the n³ grid, n = 7…12 | maximise size | 21, 23, 26, 28, 31, 33 | AlphaEvolve problem 60 | yes, all six |
| Same problem, n = 13…26 (added in round 26) | maximise size | 36, 38, 40, 42, 44, 45, 49, 50, 50, 50, 51, 53, 55, 56 | Demonstrandum artifacts (n = 13–17), milesandmistakes certificates (n = 18–20), Numaro report (n = 22–26); n = 21 is the inclusion bound C(21) ≥ C(20) | yes for n = 13–20; Numaro publishes no coordinates |
| Ring loading instance, 15 pairs | maximise the routing gap | 9/8 | EinsteinArena leaderboard (AlphaEvolve's instance verifies to 1.11904756…) | AlphaEvolve instance reproduced; the 9/8 construction is quoted in a thread and not yet re-verified here |
| Sum-difference exponent I | maximise ln(\|A+A\|/\|A\|)/ln(\|A−A\|/\|A\|) | 1.12193573748604 (recomputed from the published set; paper says 1.1219) | AlphaEvolve problem 42 | yes |
| Heilbronn problem in the unit square, n = 21 and 25 | maximise the smallest triangle area | 0.011173412…, 0.007859563… (exact rationals of the published literals) | math.tejstead.com/heilbronn record ledger, PR submission lane with exact CI verification | yes for n = 21 |
| Covering design C(33,6,4) | minimise blocks | 3310 (Pree, 2021; lower bound 2750) | La Jolla Covering Repository snapshot on GitHub; the repository was frozen 2026-03-01 and newer entries live at coveringrepository.com | not applicable (no public construction fetched); registered as a benchmark family only, the greedy seed exceeds the time budget at this size and no protocol is shipped |

The isosceles and sphere rows are the primary targets: integer verifiers,
objects of 21 to 164 grid points, and the record holder attributes its own
gains to CPU local search. The Heilbronn rows have the cleanest ledger but a
crowded, continuous search. The HuggingFace sphere dataset named in the survey
(`dougdotcon/douvras-no-5-on-a-sphere-certificates`) only re-verifies the six
AlphaEvolve sets; its isosceles counterpart stays unread behind a login wall.

## Components (`research/extremal/`)

- `registry.json` — target table. Each entry records the objective, verifier
  name, parameters, and a `best_known` block with the value, whether it is
  exact or a reported decimal, the source, its URL, and the retrieval date.
  `registry.py` validates the file and rejects unknown fields. Each entry
  also carries `significance` (`crowding`, `evidence`, `open_question`) and
  `control_required`; see "Significance and controls" below.
- `verifiers/` — one module per problem family, each exposing
  `verify(construction, parameters) -> Fraction` and a `DESCRIPTION` shown to
  the proposer. All arithmetic is exact (integers, `Fraction`, or a
  40-digit truncated decimal for the one log-ratio objective); floats in a
  construction are rejected. Present: `covering_design`, `circle_packing`,
  `isosceles_free`, `no_five_on_sphere` (4×4 integer determinant of lifted
  differences for every 5-subset), `ring_loading` (exhaustive over 2^m
  assignments in scaled integers), `sum_difference`, `heilbronn_square`.
- `known/record-constructions.json` — the published record constructions
  (AlphaEvolve notebooks, Apache-2.0; Heilbronn ledger, attributed) that the
  test suite feeds to every verifier; each must reproduce its ledger value.
- `sandbox.py` — runs a candidate program with `python3 -I` in a fresh
  temporary directory under a wall-clock timeout, a CPU-time limit, an
  address-space limit where the platform enforces one (macOS does not), a
  16 KiB program cap, and a 1 MiB output cap. On macOS the process also runs
  under `sandbox-exec` with network denied and file writes confined to the
  temporary directory; the manifest records which mode applied. This
  contains programs written by the loop's own operators; it is not a
  boundary for hostile code. A program defines
  `construct(parameters, seed) -> dict`.
- `seeds/` — one investigator-written seed program per family: randomized
  greedy or hill-climbing with a `PARAMS = {...}` genome line.
- `operators.py` — the scripted operator perturbs numbers in `PARAMS` and
  never edits code; the command operator sends a request
  (`algal.lab.extremal-request.v1`: target, verifier description, up to four
  parent programs with verified scores, limits, seed) to any stateless
  command on stdin and extracts one program from its stdout. After a failed
  command proposal the next request is a repair turn that shows the failed
  program with its error.
- `local_llm.py` — the bundled command: builds a prompt from the request,
  samples one reply from a local `mlx_lm` model with the request seed, and
  prints it. Nothing persists between calls.
- `evolve.py` — a bounded (μ+λ) loop driven by a protocol file
  (`algal.lab.extremal-protocol.v1`: target, seed, evaluations ≤ 4096,
  population ≤ 64, elites, operator, construction seeds ≤ 8, timeouts, seed
  program). Selection is by the best exactly verified value over the
  construction seeds. Every candidate, including failures, is appended to
  `candidates.jsonl` with its SHA-256, parents, operator, per-seed timing,
  value or error; every distinct program is stored under `programs/`; the
  best construction is written with its value and novelty assessment; the
  manifest records the protocol, the SHA-256 of every input file (sources,
  verifier, registry, known constructions, seed program) taken before the
  run and checked again after it, the isolation mode, the registry entry,
  and wall time. Identical programs are recorded as duplicates and not
  re-evaluated.
- `novelty.py` — the gate. Statuses: `improves-recorded-best` (strict
  improvement beyond reporting precision), `within-reporting-precision`
  (better than a reported decimal by at most half a unit in its last place,
  so not distinguishable), `matches-recorded-best`, `below-recorded-best`.
- `protocols/` — one scripted and one local-model protocol per primary
  target, all bounded to 64 and 24 evaluations respectively.
- `claims/` and `claims.py` — constructions that beat a registry snapshot
  (`algal.lab.extremal-claims.v1`): target, recorded value at claim time,
  claim date, derivation, an unseeded `control` run, construction.
  `claims.check` re-runs the verifier and the gate, rejects a claim whose
  recorded value no longer matches the registry (so a registry update forces
  every claim to be re-examined), and labels the claim with a `search_status`
  from its control; see "Significance and controls" below.
- `native/` — standalone C local searches (`ls5x`, `sym5`, `iso2`) used in
  round 26, with their own brute-force self-checks. Their output is data for
  the verifiers, never a verdict.

## Honesty rules

1. A registry value is a snapshot with a URL and a date. An
   `improves-recorded-best` status is a claim against that snapshot only. Before
   reporting an improvement, re-read the source on the claim date, record the
   re-check in the run manifest, and search for later results.
2. Reported decimals are never beaten by rounding. The gate demands a margin
   larger than half a unit of the last reported place; exact tables demand a
   strict inequality.
3. The verifier is the only judge. A candidate's own claimed score is ignored;
   only the exact recomputation counts, and any rejection is archived with its
   reason.
4. Failed proposals, timeouts, and malformed replies stay in the archive. Run
   reports quote the counts.
5. Model attribution is limited to what the archive shows: which parent
   programs the model saw and what it returned. Investigator-written seed
   programs are labelled `seed`.
6. Runs live under ignored `runs/` directories; the protocol, seed programs,
   verifiers, and the findings report are committed.

## Significance and controls

Beating a recorded number is not the same as doing something hard. A cell
that one report lists without coordinates can fall to minutes of local
search; a cell that several groups have pushed cannot. Round 26 showed this
directly: cold-start runs matched or approached the seeded results at several
frontier cells, so those cells were merely under-searched. An automatic "beat
the recorded number" gate on its own therefore rewards the least meaningful
targets. Two required fields make the difference visible instead of hiding
it behind the novelty status.

`significance`, on every registry target, is an object with three fields:

- `crowding`: one of `uncontested` (a single public report, possibly
  without coordinates), `lightly-contested`, `contested`, `well-studied`
  (a value several groups have reproduced without improving it). The label
  summarises how many independent public sources have worked the cell.
- `evidence`: a short dated string naming the sources counted, so a reader
  can disagree with the label.
- `open_question`: a named conjecture or open problem the cell bears on, or
  null when none was located.

`control_required` is a boolean on every target, true for every search
target (every current target).

`control`, on every claim, records the same search started from nothing
(no public certificate, no warm start): `kind` is `unseeded`; `value` is the
exact value the cold start reached; `budget` states the budget, which must
be the seeded run's budget; `command` is the exact command; `outcome` compares
the control with the claimed value in the objective's direction: `matched`,
`below` (the control did not reach the claimed value), `above` (it beat the
claimed value), or `not-run`. A `not-run` control has null `value` and
`command`, and its `budget` states the seeded budget a control must match. A
claim without a `control` object fails parsing, and an `outcome` that
contradicts the values is rejected by `claims.check`.

`claims.check` labels each claim with a `search_status` next to the novelty
status:

| Label | Meaning |
| --- | --- |
| `under-searched` | the unseeded control reached at least the recorded best: the public cell was beatable from nothing at that budget, so the claim says more about the ledger than about the method |
| `improves-recorded-best` | the control fell short of the recorded best, so the seeded search did work that the cold start could not (the novelty status, as before) |
| `control-missing` | no control was run on a target that requires one; the gap is printed rather than passed silently |
| `control-not-required` | the target waives the control (`control_required: false`); no current target does |

The labels do not change the novelty status: a claim can be both
`improves-recorded-best` (it beats the snapshot) and `under-searched` (so
could a cold start).

## Reproduce

```sh
python3 -m unittest research.test_extremal
python3 -m research.extremal.claims
python3 -m research.extremal.evolve --protocol research/extremal/protocols/isosceles-free-64-scripted.json --out runs/extremal/isosceles-free-64-scripted
```

The claims command prints, for every claim, the novelty status and the
search status from its control.

The native tests compile `research/extremal/native/*.c` with the system C
compiler and are skipped when none is installed.

The local-model protocol needs the `mlx_lm` interpreter named in its command
list and the cached `mlx-community/Qwen3-8B-4bit` weights; it is not run in CI.

## First runs

Bounded runs on 24 September 2026 (macOS, `sandbox-exec+rlimit` isolation,
protocol seeds 0 and 1). Values are the verifier's exact recomputation; the
seed column is the investigator-written seed program's own value.

| Target | Seed program | Scripted best (64 evals) | Qwen3-8B-4bit best (24 evals) | Recorded best | Status |
| --- | --- | --- | --- | --- | --- |
| isosceles-free-64 | 73 | 74 | 79 (20 evaluable) | 112 | below |
| no-five-on-sphere-7 | 15 | 16 | not run | 21 | below |
| ring-loading-15 | 15/16 | 1 | not run | 9/8 | below |
| sum-difference-I | 1.05033 | 1.05698 | not run | 1.1219 | below |
| heilbronn-square-21 | 0.0012101 | 0.0021306 | not run | 0.0111734 | below |

Every scripted run evaluated all 64 candidates. The local model returned 20
evaluable programs out of 24 proposals (the other four were malformed or
rejected by the verifier and stay in the archive); its best program is a
mutated greedy search, not a new construction idea.

Conclusion: the loop works end to end (containment, exact verification,
archive, mechanical novelty gate), and no target moved. The scripted operator
only tunes `PARAMS`, so it cannot leave the seed program's search family, and
Qwen3-8B at 2048 tokens rewrites the same family. Both sit far below the
records, which were produced by much larger searches. The levers that remain
are program-level search (mutating the search algorithm, not its parameters),
stronger seed programs that encode the published constructions' structure,
and a frontier model behind the same command interface. Run archives are
kept locally under `research/spikes/context/runs/round25-target-survey/runs/`
with their manifests and input hashes.

## Round 26: the no-five-on-a-sphere frontier

The problem (AlphaEvolve problem 60): C(n) is the largest subset of the n³
grid with no five points on a common sphere or plane. The AlphaEvolve table
stops at n = 12. A same-day ledger audit on 24 September 2026 found three
later public sources for larger n: the Demonstrandum Research artifact bundle
(June 2026; n = 13–17, centrally symmetric certificates), the
milesandmistakes certificate repository (August 2026; n = 18–20, "apparently
new"), and a Numaro report (July 2026; n = 14–26, no coordinates). The
registry now carries n = 13–26 with the best public value per cell, including
the monotone closure C(n) ≥ C(n − 1). DeepMind issues #4, #6, #7, Zenodo, a
GitHub repository search, HuggingFace, and OEIS showed nothing stronger.

`native/ls5x.c` (tabu search over k-sets with exact incremental counts of
degenerate 5-subsets, an exact repair step, growth after each valid set) was
seeded with a public certificate, placed inside a larger grid where needed,
and run for seconds to minutes of CPU on a shared workstation. Every
construction below is in `claims/no-five-on-sphere-frontier.json` and is
re-verified in CI by the `no_five_on_sphere` verifier against the registry.

| n | Previous public best | New lower bound | Start set | Start points kept |
| --- | --- | --- | --- | --- |
| 17 | 44 (Demonstrandum; milesandmistakes independently) | 45 | milesandmistakes 44 | 2 of 44 |
| 18 | 45 (milesandmistakes) | 48 | Demonstrandum 44, inside the 18-grid | 0 of 44 |
| 19 | 49 (milesandmistakes) | 50 | milesandmistakes 49 | 1 of 49 |
| 20 | 50 (milesandmistakes) | 53 | milesandmistakes 50 | 0 of 50 |
| 21 | 50 (inclusion from n = 20; Numaro lists 46) | 55 | milesandmistakes 50, shifted | 0 of 50 |
| 22 | 50 (Numaro) | 58 | same chain | 0 of 50 |
| 23 | 51 (Numaro) | 59 | same chain | 0 of 50 |
| 24 | 53 (Numaro) | 62 | same chain | 0 of 50 |
| 25 | 55 (Numaro) | 65 | same chain | 0 of 50 |
| 26 | 56 (Numaro) | 67 | same chain | 0 of 50 |

Each derivation (commands, seeds, shifts, iteration counts) is recorded in the
claims file; runs are reproducible in iteration count, and the test suite
rebuilds `ls5x` and regenerates the n = 20 certificate from the published
50-point set. A second exact check, the full 5×5 Leibniz determinant in int64
over every 5-subset, and `ls5x`'s own brute-force check agree on every
certificate. A separate run from the Demonstrandum 44-point set also reaches
45 at n = 17.

What the numbers mean. These are lower bounds only; no optimality is claimed
at any n. The cells from n = 21 up were weak (Numaro's values, some below the
inclusion bound), so large margins there say more about the ledger than about
the method. The n = 17–20 improvements beat certificates published in
June and August 2026 that came from multi-threaded symmetric local search
(Demonstrandum) and from OpenEvolve and auxiliary searches (milesandmistakes).
Demonstrandum fitted C(n) = ⌊(5n + 7)/2⌋ to the record values for n = 7–14;
the new values meet that law exactly at n = 18, 20 and 22 and sit one below it
at the other n above 16 (two below at n = 23), where the previous gaps ran from
two to twelve. The final sets keep few or none of the
start points, so the start set matters mainly as a warm start; its authors
are credited in `known/record-constructions.json` and in each derivation.
Control runs make the same point more strongly: unseeded `ls5x` searches at
n = 18, 20 and 21 (no start set, 900 CPU seconds each against the seeded
2400) reached 47, 52 and 55 in seconds to minutes, at or above the public
value in all three cells and equal to the seeded result at n = 21, so these
frontier cells were under-searched rather than seed-dependent. Each claim now
records its control: `claims.check` labels n = 18, 20 and 21 `under-searched`
and the seven cells without a control run (n = 17, 19 and 22 to 26)
`control-missing` until one is made at the seeded budget. On the registry's
significance fields the n = 21 to 26 cells are `uncontested` (Numaro only,
no coordinates) and n = 18 to 20 `lightly-contested`, which is the same
finding stated before any search. Priority rests on the dated audit above, not on a
guarantee: unpublished work cannot be excluded, and nothing here has been
submitted to any ledger; the ten bounds were posted publicly on 2026-09-25 as a
comment on DeepMind issue #6 (lower bounds only, no priority claim; link in
`docs/novelty-ledger.md`).

What did not move. n = 7–12: asymmetric tabu runs from scratch and from the
AlphaEvolve sets at the record plus one, and a centrally symmetric search
(`native/sym5.c`), whose symmetric sets stop at 22, 24, 27, 29, 32 for
n = 8–12, below every record, as Demonstrandum reported. Those values have
also resisted Demonstrandum and Numaro. n = 13–16: runs from the
published sets at the record plus one ended with one to five degenerate
5-subsets left. Isosceles-free 64: `native/iso2.c` from the 112-point set
reached 113 points with two isosceles triples, and 114 mirror-symmetric points
with four.

A scratch predecessor of `ls5x` accepted repairs without re-checking the
remainder and missed concyclic quadruples; six of the eight sets it reported
as record-matching failed the verifier. It was never committed or reported,
and the verifier caught it. That is the reason every native program now
re-verifies before printing and the claims pass through `claims.check`.

The evolution loop contributed nothing to this round. The gain came from
choosing a target whose live ledger was thin at larger n, checking that ledger
on the day, and running a strong exact local search from the best public
certificates.
