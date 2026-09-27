# Host comparison observations, September 27, 2026

Both implementations passed the same lifecycle tests and generated identical
canonical ALGAL receipts for 144 successful jobs. No duplicate fixture effects
appeared after worker crashes, owner-process death, whole-host death, or restart.
Interrupted dispatches remained uncertain and queued jobs were cancelled on
recovery. Each host admitted a new healthy job after recovery.

The local run used Bun 1.3.14, Elixir 1.20.4, Erlang/OTP 29.1.1, four BEAM
schedulers, and ALGAL revision `f899456e497656eb292d97d7c0aef5e06f1437dc` on an
Apple M4 Max with 128 GiB RAM. Both supervisors used the same ALGAL worker and
20 ms local append fixture. Three repetitions each ran 24 jobs at concurrency
four. Startup was measured separately from job throughput.

| Measurement | Bun host | OTP host |
|---|---:|---:|
| Jobs/second, each repetition | 55.50, 53.78, 51.29 | 46.46, 48.34, 8.26 |
| Median host startup | 21.66 ms | 520.24 ms |
| Median reported queue p50 | 194.11 ms | 154 ms |
| Median reported queue p95 | 344.38 ms | 273 ms |
| Median sampled peak host RSS | 61.95 MiB | 103.98 MiB |
| Running cancellation to observed worker exit | 5.81 ms | 11.00 ms |

These measurements do not establish a general performance ranking. The third OTP
repetition had much slower startup and execution on a shared development machine.
Queue time begins when a host accepts a command, so it excludes time awaiting
parsing on stdin; the throughput measurement includes that time. RSS is sampled
host-process RSS from `ps`, excluding the common worker subprocesses. Compilation,
imports, process setup, JSON transport, and synced writes are all included where
they occur in this workload.

The operational result supports preserving the portable ALGAL executor. OTP can
supervise it through a process boundary, but it still needs explicit queue limits,
durable dispatch records, deadlines, owner lifetime monitoring, and recovery
rules. This experiment supplies neither a production OTP service nor evidence
that changing hosts would improve the portfolio.

Six scenario groups passed: queue/deadline/cancellation/worker/session-owner
tests for each host, owner-process crash before the effect for each host, and
whole-host crash after the effect for each host. The exact effect log was checked,
not inferred from exit status. All task-owned child processes exited and all
scenario locks were removed through observed-owner recovery.

The raw run is retained locally as `runs/host-comparison-v2`; generated runs stay
out of Git. SHA-256 of its `report.json` bytes:
`5428a3bc47731af4bec1586ee8879bda118b0a0073f06a3d8ca2beb4151c4a85`.
Reproduce it with the README command and a fresh directory. The failed first
attempt is also retained: its manifest allowed too little modeled work, ALGAL
returned failures, and the hosts correctly recorded uncertainty. The repaired
fixture uses a 1,000-unit budget and the full rerun passed.
