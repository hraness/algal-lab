# ALGAL host comparison

This experiment runs the same ALGAL program in Bun subprocesses supervised by
either a Bun host or an Elixir/OTP host. It compares host behavior without changing
the ALGAL executor, manifests, or receipt format. It makes no model calls.

Install the repository's pinned dependencies and Elixir 1.18 or newer (including
Erlang). The OTP implementation uses the standard-library JSON module and has no
Hex dependencies. Run from the repository root:

```sh
bun install --frozen-lockfile
bun test experiments/host-comparison/rss.test.ts experiments/host-comparison/protocol.test.ts
bun x tsc --noEmit -p experiments/host-comparison/tsconfig.json
bun experiments/host-comparison/compare.ts runs/host-comparison-NEW-ID
```

On Darwin, qualify the sampler on the intended machine first: the live RSS test
uses Python 3 to measure an idle Bun child and an idle OTP child through a separate
OS API. It must **pass**, not skip. The comparison harness itself uses Bun FFI
`proc_pidinfo` for current host-process RSS and checks each sample against
`proc_pid_rusage`; the two APIs must agree within 65,536 bytes of sampling drift.
On other systems the harness retains `/bin/ps` and rejects failed/empty output.
No substitute for a missing or blocked OS measurement is allowed. The failed
2026-10-08 attempt remains retained and charged, with six passed correctness
checks but zero recorded repetitions; do not reuse its output directory or start
a new full run without recording a new allowance decision in the protocol.

On a Hraness development machine, run the comparison through the installed
`host-run --mode=shared --lane=compute --label=host-comparison --` wrapper. The
harness kills only subprocesses it created and waits for their exits. Set
`ELIXIR` to the executable path when it is not on `PATH`. Every run needs a new
output directory; artifacts are ignored by Git.

`report.json` includes versions, CPU identity, workload, measurements, assertions,
and limits. `events.jsonl` is the operational transcript. Per-scenario folders
hold the durable host journal, local effect log, exact manifests, and canonical ALGAL receipts.
All successful repetitions and both hosts must produce identical receipt digests
for the same job. A failed assertion makes the command fail.

## Workload and failures

The program has one input and one host-registered tool. The tool waits 20 ms,
appends a job ID to a local file, syncs it, and returns the ID. That append is the
non-idempotent effect fixture. It is separate from the host journal so a worker
can fail after the effect but before its result is recorded.

The harness validates each log with a pure effect-log oracle before joining it to
host states. The oracle reads only `effects.jsonl`, requires complete newline-
delimited records with exactly one valid submitted ID, rejects duplicates and
foreign IDs, and returns sorted IDs plus a count. Complete jobs must have one
oracle-approved effect; cancelled or expired jobs must have none. An oracle
failure stops the run closed.

Three alternating-order repetitions run 24 jobs with four active workers and
32 waiting slots. Timing starts after host readiness, so host startup is excluded
but per-job subprocess startup and ALGAL imports are included. The harness
samples host-process RSS using the OS. It excludes worker RSS, and never equates
BEAM allocator memory with OS RSS. The OTP host uses four BEAM schedulers.

The failure suite checks queue overflow, waiting deadlines, waiting and running
cancellation, logical owner death before and after dispatch, worker crashes before
the fixture and after its effect, and abrupt host death before and after an effect.
After restart, attempts with the same IDs must be refused; a separate healthy job
must still complete. The effect log must contain no duplicate dispatches.

## Protocol and guarantees

Both hosts accept newline-delimited JSON on stdin and emit events on stdout:

```json
{"op":"submit","job":{"id":"example","owner":"session","delay_ms":20,"ttl_ms":30000,"fault":"none"}}
{"op":"observe"}
{"op":"cancel","id":"example"}
{"op":"owner_down","owner":"session"}
{"op":"stop"}
```

Job/owner IDs are 1–64 ASCII letters, digits, underscores, or hyphens. Durations
are integers from 0 to 30,000 ms. Faults are `none`, `before_dispatch`,
`after_effect`, or `hold_after_effect`. Unknown command/job fields are rejected.
Input is limited to 16 KiB; host lifetime is limited to 512 accepted job IDs.
Active work is configurable from 1–8 and waiting work from 1–64.

The hosts sync each state change before reporting it. A `running` record means
dispatch may have happened, not that the external effect completed. The queue
checks deadlines again before dispatch. Worker execution has a separate
31-second ceiling. Cancellation of waiting work is `cancelled`; cancellation or
failure after dispatch intent is `uncertain`, even if the fixture did no work.
No automatic retry is implemented.

An OS pipe links the worker lifetime to its host. The worker exits when its stdin
closes. OTP owns the port inside a supervised task; killing that task closes the
port. The OTP scheduler process is temporary: restarting it blindly would be an
unsafe recovery policy. A logical `owner_down` command models a session monitor's
notification and cancels all of that owner's jobs. It does not authenticate a
remote owner or establish a distributed lease.

The test-only `crash_owner` operation kills the Bun event-loop owner or the OTP
GenServer. OTP workers monitor that owner, close their ports when it dies, and the
service exits rather than silently restarting the scheduler. The harness also
kills the entire OS host after a fixture effect has been written.

A single-writer lock prevents simultaneous hosts from using the same directory.
The harness removes a crashed host's exact lock only after observing that host
and all of its recorded workers exit. Restart then converts queued work to
cancelled and running work to uncertain. A partial journal line fails closed.
This explicit test recovery is not a production recovery service. Unknown results
require application/provider reconciliation; submitting a different ID is not a
safe retry mechanism.

## Interpretation

This is an end-to-end host experiment on one shared machine. It includes JSON
transport, sync writes, subprocess setup, and runtime imports. It cannot establish
a general BEAM versus Bun performance advantage, production durability, provider
idempotency, or a need to migrate ALGAL. The implementations expose the code and
operational costs that would have to be justified by a real deployment.
