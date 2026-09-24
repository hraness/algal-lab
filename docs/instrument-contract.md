# Versioned observation instruments

`@hraness/algal-lab/observation` is a narrow second-domain interface. It reuses
the lab's content-addressed `ArtifactStore`, canonical JSON admission and pinned
ALGAL runtime. It does not change graph protocols, graph selection, or `runStudy`.
The observation path has separate versioned records and does not force a
biological measurement into a graph score.

The credential-free example runs with Bun 1.3.14:

```sh
bun install --frozen-lockfile
bun run demo:observation runs/observation-example
bun test src/instruments
```

Choose a new output directory. The example registers an arithmetic prediction,
measures `[1,2,3]`, freezes the first attempt, then measures `[2,4,6]` under its
registered evaluation commitment. The mean and sample standard error are
fixture measurements, not biological findings. All inputs are intentionally
public for this software test; it does not demonstrate holdout isolation.

## The two boundaries

An `ObservationInstrument` names `algal.lab.instrument.v1`, its versioned ID,
input and output contract IDs, execution mode, complete source binding, and
domain-owned `parseInput` and `verify` hooks. `pure` adapters additionally supply
`measure`; `attachment` adapters cannot supply it. Use the exported TypeScript
types and parsers rather than importing implementation files.

| Envelope | Fields and meaning |
| --- | --- |
| Input | `contract`, bounded domain `data`, and external `artifacts` manifest. |
| Proposal | Requested `design`, `hypothesis`, structured `prediction`, `rationale`, and prior observation `parents`. Prose remains a claim. |
| Observation | `contract`, `realizedDesign`, domain `values`, `measurements`, external `artifacts`, and `limitations`. |
| Measurement | A named finite `value`, `unit`, and uncertainty `method`, `lower`, `upper`, `level`. Null bounds explicitly mean no interval; a standard error is not labeled a confidence interval. |
| External artifact | Public logical `name`, SHA-256 `digest`, byte count, and media type. No private local path is needed. |

The domain adapter must reject unknown domain fields, verify external file
contents against manifests, enforce biological sample/replicate meaning, and
document numerical tolerances. The shared parser validates structure and
manifest identities; it does not fetch external artifacts or certify that an
external measurement is true. `verify` must be bounded and offline: no provider,
job dispatch, or hidden recomputation. Reserve actual computation for `measure`
and the explicitly requested fresh-computation check.

Inputs and observations are bounded to 64 KiB, proposal output to 8 KiB, domain
design to 4 KiB, prediction to 2 KiB, and supplied context to 32 KiB. There are
at most 64 attempts, one ALGAL agent call per registration, 64 named
measurements, 32 external artifacts per envelope, and eight proposal parents.
Unknown shared fields, invalid numbers, oversized and excessively nested JSON
are rejected. Caller-owned JSON is copied before admission and frozen before
measurement. Version a changed scientific meaning rather than reusing an ID.

## Registration, recovery and evaluation

```ts
import {
  createObservationStudy, registerObservationAttempt,
  completeObservationAttempt, freezeObservationStudy,
  evaluateObservationStudy, verifyObservationStudy,
} from "@hraness/algal-lab/observation";

await createObservationStudy(protocol, directory, instrument);
await registerObservationAttempt(directory, instrument, {
  attemptId: "candidate-001", input, context, executor,
});
// This boundary can survive process death; no executor is accepted on resume.
await completeObservationAttempt(directory, instrument, "candidate-001");
await freezeObservationStudy(directory, instrument, ["candidate-001"]);
await evaluateObservationStudy(directory, instrument, evaluatorOnlyInput);
await verifyObservationStudy(directory, instrument); // receipt replay only
await verifyObservationStudy(directory, instrument, { recompute: true });
```

The protocol is `algal.lab.observation-study.v1` with `name`, `maxAttempts`, and
`evaluation: {inputDigest, specification}`. Compute the input commitment with
exported `observationDigest` over the exact admitted input envelope. The full
evaluation input is supplied only after selection freezes; the protocol's
commitment and specification are available before registration. Keep this
input in evaluator-only storage enforced by the caller's host sandbox. This
library does not isolate filesystem mounts, prevent fetching public holdout
data, or stop a privileged host from placing evaluation data in `context`.

Registration first writes an immutable intent, then executes one real ALGAL
agent cell and archives the complete ALGAL receipt. Successful proposals are
pending measurements. Invalid proposals and provider failures remain rejected
registrations with their receipts. The intent includes registration order;
parents must reference earlier observations, never future candidates.

Completion reads the durable registration and uses a separate ALGAL tool cell.
The join binds the exact registration, input digest and instrument digest.
It preserves the original prediction, realized design, result or failed tool
receipt. A completed join is immutable: later completion calls return its
verified existing result. Pure local computation can be repeated after a crash
before its join is durable; proposal calls cannot. External effects must use
`attachment`, with already collected and reconciled output supplied as the
fourth completion argument. The library never launches or retries external
jobs. Their provider job keys, budgets, expiry and reconciliation belong to the
campaign coordinator. An omitted attachment records a failed measurement,
rather than launching work. Evaluation attachments are keyed by frozen attempt ID.

An intent without a durable registration is **ambiguous**, even if the provider
may have finished. Completion, fresh registration and verification fail closed.
Do not retry it under another attempt ID. Preserve the directory and reconcile
the provider's result separately; the v1 API deliberately offers no automatic
proposal-result replacement or guessed retry. A partial or malformed pointer
also fails closed and requires inspection.

Only one process may mutate a study. A lock left by a dead process requires
`recoverObservationStudyLock(directory)` before continuing. Designate one
recovery owner. The recovery function checks that the recorded PID is absent,
compares the exact lock contents, and removes only that lock; a live/reused PID
or malformed lock blocks recovery. This is process-crash recovery, not a
distributed lease service. No operation removes scientific evidence.

All admitted attempts must have a terminal proposal rejection or measurement
join before freezing. A freeze retains every attempt and the selected
successful attempt IDs, including an empty selection. It closes new
registration, pending completion, and selection changes. Evaluation checks the
original input commitment and operates only on that frozen selection, with
one immutable output per attempt. Repeated calls reuse completed joins; an
interrupted pure evaluation computes only missing results. Failed/rejected
attempts and negative selections remain visible.

## Evidence and archive policy

| Path | Retained evidence |
| --- | --- |
| `observation-study.json` | Protocol, source/runtime/environment identities, and canonical digest. |
| `attempts/<id>/intent.json` | Pointer to the pre-call input, context, parent references and registration sequence. |
| `attempts/<id>/registered.json` | Pointer to the real ALGAL proposal receipt and admitted prediction or rejection. |
| `attempts/<id>/observed.json` | Pointer to the immutable measurement receipt and join. |
| `freeze.json` | Pointer to the complete attempt snapshot and frozen selection. |
| `evaluation/input.json`, `evaluation/observation-<id>.json` | Committed evaluation input and selected evaluation joins. These require evaluator-only access until release. |
| `artifacts/<sha256>.json` | Canonical content for all referenced records. |

`verifyObservationStudy` checks source identity, all referenced content, order,
input/proposal joins, freeze closure, evaluation commitment, domain structural
verification, and full ALGAL receipt reconstruction. ALGAL's pinned
`verifyReceipt` replays retained agent **and tool** effects; a replay stub rejects
any attempt to invoke the measurement tool. It never reopens a provider.
Its `observations` counter counts completed measurement joins, including failed
ones whose `observation` field is null. Inspect those outcomes when counting
successful experiments.

`{recompute: true}` separately reruns pure measurements and compares the
numerical observations and success/failure state. It reports
`freshComputation: "passed"` only after those comparisons finish; receipt-only
verification reports `"not-requested"`. Attachment adapters refuse this option:
their independent numerical reproduction is domain work. Neither check
establishes empirical truth, novelty, an authenticated author, external
timestamping, or absence of unrecorded trials. A privileged operator can replace
an entirely consistent archive; these are workflow guarantees, not notarization.

Each adapter declares labeled source trees and individual files. Tree binding
recursively hashes **every file**, including nested helpers, tables and binaries;
symlinks, excessive depth, size and file count are rejected. The trusted adapter
owner must supply its entire executable dependency closure, including imported
packages, Python tools/interpreters, lockfiles and configuration outside those
trees. Source binding cannot infer or sandbox arbitrary host callbacks. Missing
dependencies must be corrected before admitting an adapter. Labels and relative
filenames are retained, not source-root paths.

The application identity also binds every file under the installed lab's `src/`,
its package manifest and lockfile, and the installed ALGAL source/wasm identity.
The archive records the exact Bun version and full ALGAL revision
`f899456e497656eb292d97d7c0aef5e06f1437dc`. The public fixture passes at that pin;
this interface introduces no runtime upgrade.

Consumers install this repository using a **full immutable Git commit pin** in
their package manifest and committed lockfile. Keep that lockfile and the
adapter's frozen environment manifest in its source binding. A study release
must retain the precise lab and adapter revisions, lockfiles, Bun version,
external tool versions and artifact hashes with the archive. Verification after
a source, nested dependency, runtime, or Bun-version change refuses to interpret
the old archive. Restore the recorded revisions and pinned environment before
verifying it; do not rewrite old observations or their hashes. The library does
not download or execute historical source automatically.
