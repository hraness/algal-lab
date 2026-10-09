# Failure-aware execution: local measurement gate receipt

**Date:** 2026-10-09
**Campaign:** `host-comparison-2026-10-08-v1`
**Status:** the frozen *local fixture* correctness/RSS gate passed on one Darwin machine. [Independent review](failure-aware-execution-independent-review.md) found a reservation-timing provenance gap; this remains descriptive evidence, not a scientific performance ranking, a new recovery guarantee, or a deployment qualification.

## Decision and accounting

The [frozen protocol](failure-aware-execution-protocol.md) binds nine execution-source SHA-256 hashes at source base `7ce4b68a3ebeab9e9756a1ae0d3bcd1848682d8e`; all nine matched immediately before this attempt. The baselines remained Bun, OTP, durable intent without automatic retry, and provider idempotency *only where guaranteed* (not exercised). The workload is a synthetic development fixture, with no holdout, provider calls, or model-selected commands.

The designated writer reports reserving **one additional, nonrefundable full local attempt** before execution and selecting a fresh ignored output directory. The retained allowance record asserts this decision, but its current file was created after the completed report; the independent review cannot establish pre-run recording from this file. The previous attempt remains charged and failed: its six correctness groups passed, then `/bin/ps` raised `EPERM` before the first timing measurement; its zero repetitions are not reused. The new attempt ran once, completed, and consumed its whole reservation. **Total: two full local attempts charged; six timed repetitions recorded only in the second; zero further attempts available under this decision. Paid calls: 0; paid charge and remaining paid allowance: $0.** No provider result or holdout was consulted to select this attempt.

Environment recorded in the private report: Bun 1.3.14, Elixir 1.20.4 / Erlang/OTP 29 with four BEAM schedulers, Darwin 25.5.0, Apple M4 Max, pinned ALGAL dependency. The Darwin sampler had already been qualified against an independently invoked OS API for idle Bun and OTP children. The comparison used the exact host PID at each sample, checked two OS APIs for agreement within 65,536 bytes, and stopped rather than substituting missing RSS. `host-run` was not on this executor's PATH; the local run used the granted confined native executor directly. No installed scheduler was bypassed knowingly.

## Fixture observations, not a runtime ranking

The report records **six passing correctness groups** (three scenarios per host), zero duplicate fixture effects, explicit `uncertain` after dispatch where required, an independently read local effect log, and matching canonical receipt digests for all 24 benchmark job IDs across both hosts and all repeats. The alternating order was Bun/OTP, OTP/Bun, Bun/OTP; each repetition completed 24 jobs. A separate read-only, same-writer Python audit re-read the journals, effect logs, receipts, report, and event transcript. It found 75 complete, six uncertain, four cancelled, and one expired terminal jobs *per host* across the failure suite and three timed repetitions. This cross-check is not independent peer review or evidence of real external-provider outcomes.

Descriptive values from the one shared machine (repeats 0, 1, 2 in that order):

| Host | 24-job elapsed time, ms | Sampled peak **host-only** RSS, bytes | Host startup, ms |
| --- | --- | --- | --- |
| Bun | 2666.945, 2805.904, 2678.605 | 59,064,320; 57,999,360; 58,048,512 | 31.864, 38.543, 37.680 |
| OTP | 2587.005, 2542.238, 2747.677 | 107,298,816; 110,198,784; 103,710,720 | 945.369, 921.686, 873.526 |

The audit sums only journal, effect-log, and complete receipt file sizes over all six scenarios per host (failures plus three timed repetitions): Bun **133,030 bytes**, OTP **131,136 bytes**; these are not total process/storage costs (manifests and transcript excluded). From the *restarted host's ready event* to completion of a different healthy job, transcript-derived times were Bun 176.115 ms before-effect / 171.887 ms after-effect and OTP 168.750 / 225.126 ms. These intervals **exclude downtime and restart startup**, so they are not end-to-end recovery latency. The report also retains per-repeat throughput, baseline RSS and queue metrics; submission/acceptance pacing differs between hosts, so queue percentiles must not be interpreted as a matched client-latency comparison. Worker RSS is excluded from the sampled peaks. Three repetitions on one machine supply no independent uncertainty estimate or practical margin test.

Private evidence identities (SHA-256, not public raw artifacts): previous failure `b5ad2478f807f8119aa5a0b98f13f1b401bf5781f92a81223bb91d90a5114fbc`; second report `0c65cd0b8a567de03d04209d449cbde469f57c37bf4a3c42e1ffe2ec6404bb7c`; second event transcript `6e01d523ec253845fe34b21c2e1b3710357140e64293ff9558550e13a0738107`; same-writer offline audit script `c5bbe84c97ff7990f1ed5236da40bc7c8c14381a1828df282a883769d4bd93e4`. The ignored allowance record and run retain the exact inputs, manifests, receipts, failures, and charge. No `runs/` output belongs in Git.

## Boundary and next review

The sampler now permits this *descriptive local fixture measurement* without concealing the first failure. The protocol does **not** demonstrate distributed fencing, real external-effect reconciliation, power-loss persistence, provider idempotency, or a portable Bun/OTP performance ordering. [Prior-art comparison](failure-aware-prior-art.md) finds no new recovery guarantee beyond the stated baselines; it is not a novelty verdict. The held scientific headlines and author-response hold remain in force.

The separate independent review verified receipt replay and the local crash/effect classifications, while finding that the retained allowance file does not independently prove its asserted pre-run reservation time. The report retains only RSS baseline/peak, not raw readings for a post-run parity audit. These qualifications must accompany any use of the measurements; the result remains descriptive rather than confirmatory. No new benchmark attempt or paid call is authorized by this receipt. A real application test and separate failure/ownership model would require their own freeze, allowance, and review.
