# Extremal-construction discovery loop

Status: design and first bounded runs, 24 September 2026. No novelty claim.

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
| Ring loading instance, 15 pairs | maximise the routing gap | 9/8 | EinsteinArena leaderboard (AlphaEvolve's instance verifies to 1.11904756…) | AlphaEvolve instance reproduced; the 9/8 construction is quoted in a thread and not yet re-verified here |
| Sum-difference exponent I | maximise ln(\|A+A\|/\|A\|)/ln(\|A−A\|/\|A\|) | 1.12193573748604 (recomputed from the published set; paper says 1.1219) | AlphaEvolve problem 42 | yes |
| Heilbronn problem in the unit square, n = 21 and 25 | maximise the smallest triangle area | 0.011173412…, 0.007859563… (exact rationals of the published literals) | math.tejstead.com/heilbronn record ledger, PR submission lane with exact CI verification | yes for n = 21 |
| Covering design C(33,6,4) | minimise blocks | 3310 (Pree, 2021; lower bound 2750) | La Jolla Covering Repository snapshot on GitHub; the repository was frozen 2026-03-01 and newer entries live at coveringrepository.com | not applicable (no public construction fetched); registered as a benchmark family only, the greedy seed exceeds the time budget at this size and no protocol is shipped |

The isosceles and sphere rows are the primary targets: integer verifiers,
objects of 21 to 164 grid points, and the record holder attributes its own
gains to CPU local search. The Heilbronn rows have the cleanest ledger but a
crowded, continuous search. HuggingFace certificate datasets named in the
survey could not be read without an account and must be checked before any
claim on the grid rows.

## Components (`research/extremal/`)

- `registry.json` — target table. Each entry records the objective, verifier
  name, parameters, and a `best_known` block with the value, whether it is
  exact or a reported decimal, the source, its URL, and the retrieval date.
  `registry.py` validates the file and rejects unknown fields.
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

## Reproduce

```sh
python3 -m unittest research.test_extremal
python3 -m research.extremal.evolve --protocol research/extremal/protocols/isosceles-free-64-scripted.json --out runs/extremal/isosceles-free-64-scripted
```

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
