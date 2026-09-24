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

## Components (`research/extremal/`)

- `registry.json` — target table. Each entry records the objective, verifier
  name, parameters, the recorded best-known value, whether that value is
  exact or a reported decimal, the source, its URL, the retrieval date, and
  notes. `registry.py` validates the file and rejects unknown fields.
- `verifiers/` — one module per problem family, each exposing
  `verify(construction, parameters) -> Fraction` and a `DESCRIPTION` shown to
  the proposer. Verifiers work in exact arithmetic and reject anything
  infeasible with a reason. Present: `covering_design` (block count of a
  (v,k,t) covering, bitmask coverage over all t-subsets) and `circle_packing`
  (sum of radii of n disjoint circles in the unit square, rational
  coordinates, exact containment and non-overlap tests).
- `sandbox.py` — runs a candidate program in an isolated interpreter
  (`python3 -I`), CPU and memory limits, 16 KiB program cap, 1 MiB output cap.
  A program defines `construct(parameters, seed) -> dict`.
- `operators.py` — the scripted operator perturbs numbers in the program's
  `PARAMS = {...}` line and never edits code; the command operator sends a
  request (`algal.lab.extremal-request.v1`: target, verifier description,
  up to four parent programs with verified scores, limits, seed) to any
  stateless command on stdin and extracts one program from its stdout.
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
  manifest records the protocol, source hashes, verifier hash, registry entry,
  and wall time.
- `novelty.py` — the gate. Statuses: `improves-recorded-best` (strict
  improvement beyond reporting precision), `within-reporting-precision`
  (better than a reported decimal by less than half a unit in its last place,
  so not distinguishable), `matches-recorded-best`, `below-recorded-best`.

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
python3 -m research.extremal.evolve --protocol research/extremal/protocols/covering-scripted.json --out runs/extremal/covering-scripted
```

The local-model protocol needs the `mlx_lm` interpreter named in its command
list and the cached `mlx-community/Qwen3-8B-4bit` weights; it is not run in CI.

## First runs

Filled in below once the bounded runs finish.
