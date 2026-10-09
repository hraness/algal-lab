# Failure-aware execution: protocol freeze v1

**Status:** frozen for local correctness qualification only (oracle amendment
2026-10-08; RSS measurement amendment 2026-10-09). A host comparison is not
admitted until the bounded correctness run passes. This document is the public,
redacted protocol; private run transcripts remain under `runs/`.

## Decision and scope

**Question:** can a portable recovery protocol lower recovery cost while
retaining uncertainty and preventing duplicate non-idempotent effects?

The first decision is narrower: do the Bun and OTP fixtures obey the same
failure contract? A later descriptive comparison may measure recovery cost,
throughput, and memory only after correctness passes. This is one shared-machine
fixture experiment, not evidence for a production deployment, provider
idempotency, or a BEAM/Bun performance advantage.

The workload is synthetic and has no holdout. No model or provider call is
permitted. Model output, if a future campaign uses it, remains inert data and
cannot select commands, jobs, owners, or recovery actions.

## Frozen identities and allowance

- Campaign: `host-comparison-2026-10-08-v1`; owner: the designated ALGAL task
  writer; source base: `7ce4b68a3ebeab9e9756a1ae0d3bcd1848682d8e` (tree
  `9b7de866474d846aa0ae790d54eca5b04060c803`).
- Runtime: Bun 1.3.14; Elixir 1.20.4 on Erlang/OTP 29; four BEAM schedulers;
  package and lockfile are SHA-256 `9e3eaec7032aa8d24333896c9dfc1d2129d51404e675de4fa451a746d3a3c343`
  and `e613410e2d7612c55c1a674ba5924aff5172eb9f119fbfcd331ac525b057842d`.
- Execution-source checksums are recorded here so any edit invalidates this
  freeze: `protocol.ts`
  `995bc033a033cde66f15dbec6abca1b4b939104f8ce1613f5759dcbe9f08b1fd`,
  `protocol.test.ts`
  `6089c26c977f025370710895a25798dfa46b43cfef158877fc8e5fe4930190f2`,
  `bun-host.ts`
  `0a2e8af233ca7d3a10c720c88ae39ec52ade8b089e24a60d093134c152a7fdb7`,
  `otp-host.exs`
  `538474b6a2e430c7eef0aed9917eb58983ab7d2c9f7fd729dcbbf0da3efad640`,
  `worker.ts`
  `481f865ecdac1be9d02c63696c240a5fbab83889124b64156580914164530c12`,
  `compare.ts`
  `9a11dd786e7739aa3877bdd97ea1506d05e31cf5e77acbe8ac1fd6007fe62a9d`,
  `effect-log.ts`
  `5af94df0c82adb6ccbff00f7d39746f3f8fb136de41b70a544092c8854359e6a`,
  `rss.ts`
  `5f0e51513bd25efad4a1792190b8e2aca32a64bc3c4f0eafa3665ba120055230`, and
  `rss.test.ts`
  `2e285e01cb9edef6c1feecea50c08bc495efed834d91e8e1984bbef8208c813d`.
- Allowance: local checks and at most three alternating-order benchmark
  repetitions per host plus the bounded failure suite; zero paid calls and
  `$0` model allowance. Reservations are not refunded after a failure or
  interruption. No run output, credential, or local path is publication data.

## Baselines, unit, and controls

The baselines are (1) the Bun host, (2) the OTP host, (3) durable dispatch
intent with no automatic retry, and (4) provider idempotency only where an
external contract guarantees it (not exercised here). The independent unit is
a complete host/scenario repetition, not an individual job or reordered seed.
The benchmark has 24 jobs, four active workers, 32 waiting slots, 20 ms effect
delay, and three alternating host orders. Failure controls use one active
worker and two waiting slots. Faults are `none`, `before_dispatch`,
`after_effect`, and `hold_after_effect`.

All controls are development evidence. There is no selection, tuning, or final
holdout in this protocol. A correctness failure stops the comparison rather
than selecting a more favorable scenario.

## Failure model and crash boundaries

The journal and effect log are local files. Each append is synced before the
corresponding state is reported. The effect append is deliberately separate from
the host journal, so an effect can exist while its result is unknown.

| Boundary | Frozen event | Required classification after interruption |
| --- | --- | --- |
| Admission | strict JSON/job validation; bounded IDs, durations, input bytes, and retained jobs | reject; never create an effect |
| Queue acceptance | `queued` journal row is synced | queued work may be cancelled or expire before dispatch |
| Queue cancellation/deadline | cancellation or TTL is checked before dispatch | `cancelled` or `expired`; no effect |
| Dispatch intent | synced `running` row precedes worker spawn | any later missing result is `uncertain`, never an automatic retry |
| Worker/owner lease | worker is attached to the host pipe/port; owner loss closes it | running work is `uncertain`; queued work is `cancelled` |
| Effect commit | fixture appends one `{id}` record and syncs `effects.jsonl` | effect may be present while host state is `uncertain` |
| Delayed effect/result output | effect event, receipt, and digest travel through worker output; none is host durability | late output cannot turn an already terminal `uncertain` row into success |
| Completion | host accepts a valid digest and syncs a `complete` row | success requires both a digest and one oracle-approved effect |
| Host restart | harness kills only its owned host and workers, observes exit, then removes its exact lock | restart reclassifies queued/running rows; it does not replay them |

`before_dispatch` exits before the fixture effect. `after_effect` exits after
the synced effect and before a normal result. `hold_after_effect` permits an
explicit host kill after the synced effect. Owner loss, waiting cancellation,
running cancellation, queue expiry, malformed input, and duplicate submission
are separate controls. OTP scheduler death is terminal; supervision must not
silently restart the scheduler with retained authority.

## Owner transitions and recovery invariant

`owner_down` models an authenticated session monitor notification only; it is
not a distributed lease. It cancels that owner's waiting jobs and marks its
running jobs uncertain. A host crash is recovered only after the harness has
observed the host and its recorded workers exit. A second host may then inspect
the durable journal, classify in-flight work, and accept a new healthy job.
Submitting the same ID after recovery must be reported as a duplicate, whether
the prior effect is absent or present. A different ID is not a safe retry for an
unknown external operation.

The acceptance invariant is:

- `complete` means exactly one effect record, a valid canonical receipt digest,
  and a matching result; it is never fabricated from a process exit alone.
- `uncertain` retains the unknown result and has zero or one effect record; it
  is never retried automatically.
- `cancelled` and `expired` have no effect record.
- duplicate submission creates no additional effect.
- after recovery, an unrelated healthy job completes exactly once.
- any malformed, truncated, duplicate, or unknown effect-log record fails the
  run closed; active and waiting limits remain bounded.

## Independent effect-log oracle gate

The bounded repair adds a pure oracle in `effect-log.ts`. It reads only
`effects.jsonl`, not the host journal or host event stream. It rejects incomplete
lines, unknown fields, invalid IDs, duplicate IDs, and IDs outside the
submitted-job set, and returns a deterministic sorted set/count for each log.
The harness joins that result to host states using the invariant above; an
oracle failure stops the run closed. The focused test exercises every rejection
class and the deterministic output.

The oracle is a correctness gate, not a provider reconciliation service. It
cannot prove that a real remote effect happened or did not happen; it only
checks the bounded local fixture's durable effect log. No performance number
has been selected or reported.

## RSS measurement amendment, 2026-10-09

The first attempt completed the six correctness scenario groups with no
duplicate effects, then failed at the *first* benchmark's RSS baseline because
spawning `/bin/ps` returned `EPERM`. Its ignored private failure record retains
one failed attempt, zero recorded benchmark repetitions, zero paid calls, `$0`
paid charge, and the six checks. It remains charged; it is not overwritten or
presented as timing evidence. A read-only `/bin/ps` preflight still returned
`EPERM`; `/usr/bin/top` also could not be spawned in this environment.

On Darwin, `rss.ts` now reads `proc_pidinfo(PROC_PIDTASKINFO)`
`pti_resident_size` for the *exact host PID* supplied by the harness. It
brackets an independent OS API read from `proc_pid_rusage(RUSAGE_INFO_V0)`
`ri_resident_size`. Both report current resident bytes, not BEAM allocator
memory, process-tree totals, peak `ru_maxrss`, or physical footprint. The
reference must lie within the bracketing readings plus at most 65,536 bytes
(four 16-KiB pages of sampling drift), otherwise the run stops. An invalid PID,
missing/short OS result, zero/unsafe value, or disagreement stops the run; no
zero or synthetic RSS is substituted. Off Darwin the original `/bin/ps`
endpoint remains, but nonzero exit or malformed/empty RSS now stops the run.
The report's `host_rss_*_bytes` fields remain byte-valued single-process
samples; no worker memory is added.

The read-only qualification test spawned one idle Bun child and one idle OTP
child, checked the Bun FFI sampler against a *separate Python ctypes process*
reading `proc_pid_rusage` from the same OS for each exact child PID, and
observed both comparisons within 65,536 bytes. The children exited in test
cleanup. The test also checked empty/invalid/overflowed values and sampler
disagreement. Apple xnu `bsd/sys/proc_info.h` (`proc_taskinfo`) and
`bsd/sys/resource.h` (`rusage_info_v0`) define the fields; the latter was read
from the Apple open-source primary header. The two APIs share kernel accounting,
so agreement qualifies this local measurement path, not an independent physical
RAM oracle or a performance claim. No comparison harness, timed repetition,
paid call, or provider request was run for this amendment. The failed attempt's
whole-run reservation is not restored; a further full run needs an explicitly
recorded allowance/attempt decision and a fresh ignored output directory.

## Prespecified measurements and stopping rules

After the gate passes, record per host/scenario/repetition: completion and
uncertainty counts, duplicate/malformed-log failures, time from owner/host
recovery to healthy completion, throughput, queue p50/p95, journal/effect/
receipt bytes, and sampled host RSS. Report paired descriptive values with units;
no significance claim is planned for three same-machine repetitions. Count all
failed attempts, timeouts, invalid outputs, and their full local reservations.

Stop immediately for a duplicate effect, fabricated success, lost uncertainty,
unsafe ownership transition, unresolved lock/worker, malformed durable journal,
oracle disagreement, or missing toolchain. Preserve the failure and charge it;
do not rerun an uncertain operation. A passing local fixture does not establish
practical value or generality. The harness runs the bounded correctness suite
before any benchmark loop. The next step is an explicit new-run allowance
decision, not a silent rerun of the failed directory.

## Freeze receipt

- Original focused protocol/oracle test: `bun test
  experiments/host-comparison/protocol.test.ts` — 4 passed, 0 failed.
- Original focused TypeScript check: `bun x tsc --noEmit -p
  experiments/host-comparison/tsconfig.json` — passed.
- Original repository gate: `bun run check` — exit 0 (typecheck and full Bun suite).
- No host comparison, paid request, provider request, or `runs/` artifact was
  started by the original freeze or its oracle amendment. Failed attempts at
  that point: 0; paid charge: `$0`; remaining paid allowance: `$0`.
- The five pre-existing untracked SNI/cost-aware files were preserved. The
  original amendment added only the bounded effect-log oracle, its harness join,
  focused tests, and documentation. The RSS amendment adds only the sampler,
  its qualification tests, harness import, and documentation. Source hashes
  above supersede the original `compare.ts` hash before any new benchmark.
